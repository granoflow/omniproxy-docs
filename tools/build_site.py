#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the OmniProxy Markdown manual for GitHub Pages using Python's standard library.

Maintainer commands: tools/build_site.py build _site, or tools/build_site.py serve.
"""

import os
import re
import sys
import html
import shutil
import argparse
import tempfile
import webbrowser
import posixpath
from urllib.parse import urlsplit, urlunsplit
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(os.path.dirname(HERE), "manual")
SITE_PORT = 17890
PREVIEW_DIRNAME = "_site"
DEFAULT_TITLE = "OmniProxy 手册"
# 编译 docs/ 根设计文档集时排除的子目录（manual 独立成站；prototypes/journal/tools 非文档）
EXCLUDE_DIRS = {"manual", "prototypes", "journal", "tools"}

# ---------------------------------------------------------------------------
# Markdown -> HTML（GFM 子集）
# ---------------------------------------------------------------------------

def _escape(text: str) -> str:
    return html.escape(text, quote=False)


def _slug(text: str) -> str:
    s = re.sub(r'[^\w\u4e00-\u9fff\- ]+', '', text.strip().lower())
    s = s.replace(' ', '-')
    return s or 'section'


def inline(text: str) -> str:
    """行内格式。先整体转义，再注入标签，避免用户内容破坏 HTML。"""
    text = _escape(text)
    # 代码段（内容已转义，直接包裹）
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # 图片
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', _img_repl, text)
    # 链接：.md -> .html
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _link_repl, text)
    # 粗体 / 斜体
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text


def _link_repl(m):
    label, url = m.group(1), m.group(2)
    parts = urlsplit(html.unescape(url))
    if not parts.scheme and not parts.netloc and parts.path.endswith('.md'):
        url = html.escape(urlunsplit(parts._replace(path=parts.path[:-3] + '.html')), quote=True)
    return f'<a href="{url}">{label}</a>'


def _img_repl(m):
    alt, url = m.group(1), m.group(2)
    alt = html.escape(html.unescape(alt), quote=True)
    url = html.escape(html.unescape(url), quote=True)
    return f'<a href="{url}"><img alt="{alt}" src="{url}" loading="lazy"></a>'


def _is_block_start(line: str) -> bool:
    s = line.lstrip()
    if s.startswith('```'):
        return True
    if re.match(r'^#{1,6}\s', line):
        return True
    if re.match(r'^(\-\-\-|\*\*\*|___)\s*$', line):
        return True
    if s.startswith('>'):
        return True
    if re.match(r'^(\s*[\-\*]\s+)', line):
        return True
    if re.match(r'^(\s*\d+\.\s+)', line):
        return True
    return False


def _split_row(line: str):
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return [c.strip().replace(r'\|', '|') for c in re.split(r'(?<!\\)\|', line)]


def _render_table(header, rows):
    th = ''.join(f'<th>{inline(c)}</th>' for c in header)
    body = ''
    for r in rows:
        body += '<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>'
    return f'<table class="md-table"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'


def _parse_list(lines, start, ordered):
    items = []
    pat = r'^(\s*)' + (r'\d+\.' if ordered else r'[\-\*]') + r'\s+(.*)$'
    base_indent = len(lines[start]) - len(lines[start].lstrip())
    i = start
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.strip() == '':
            j = i + 1
            while j < n and lines[j].strip() == '':
                j += 1
            if j < n and re.match(pat, lines[j]) and (len(lines[j]) - len(lines[j].lstrip())) >= base_indent:
                i = j
                continue
            break
        m = re.match(pat, line)
        if not m:
            break
        indent = len(m.group(1))
        if indent < base_indent:
            break
        if indent > base_indent:
            break
        content = m.group(2)
        i += 1
        nested = None
        if i < n and lines[i].strip() != '':
            nm = re.match(pat, lines[i])
            if nm and (len(lines[i]) - len(lines[i].lstrip())) > base_indent:
                nested, i = _parse_list(lines, i, ordered)
        items.append((inline(content), nested))
    return items, i


def _render_list(items, ordered):
    tag = 'ol' if ordered else 'ul'
    out = f'<{tag}>'
    for content, nested in items:
        out += f'<li>{content}'
        if nested:
            out += _render_list(nested, ordered)
        out += '</li>'
    out += f'</{tag}>'
    return out


def md_to_html(md: str):
    """返回 (body_html, first_h1_title)。"""
    lines = md.split('\n')
    n = len(lines)
    out = []
    title = None
    i = 0
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # 代码围栏
        if stripped.startswith('```'):
            lang = stripped[3:].strip()
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1  # 跳过结束围栏
            code = _escape('\n'.join(buf))
            cls = f' class="lang-{_escape(lang)}"' if lang else ''
            out.append(f'<pre><code{cls}>{code}</code></pre>')
            continue

        # 空行
        if stripped == '':
            i += 1
            continue

        # 标题
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            lvl = len(m.group(1))
            txt = m.group(2).strip()
            if title is None and lvl == 1:
                title = txt
            out.append(f'<h{lvl} id="{_slug(txt)}">{inline(txt)}</h{lvl}>')
            i += 1
            continue

        # 分隔线
        if re.match(r'^(\-\-\-|\*\*\*|___)\s*$', line):
            out.append('<hr>')
            i += 1
            continue

        # 引用
        if line.lstrip().startswith('>'):
            buf = []
            while i < n and lines[i].lstrip().startswith('>'):
                buf.append(lines[i].lstrip()[1:].lstrip())
                i += 1
            quote_html = md_to_html("\n".join(buf))[0]
            out.append(f'<blockquote>{quote_html}</blockquote>')
            continue

        # 表格
        if '|' in line and i + 1 < n and re.match(r'^\s*\|?[\s:\-\|]+\|?\s*$', lines[i + 1]) and '|' in lines[i + 1]:
            header = _split_row(line)
            i += 2
            rows = []
            while i < n and '|' in lines[i] and lines[i].strip() != '':
                rows.append(_split_row(lines[i]))
                i += 1
            out.append(_render_table(header, rows))
            continue

        # 无序列表
        if re.match(r'^(\s*[\-\*]\s+)', line):
            items, i = _parse_list(lines, i, ordered=False)
            out.append(_render_list(items, False))
            continue

        # 有序列表
        if re.match(r'^(\s*\d+\.\s+)', line):
            items, i = _parse_list(lines, i, ordered=True)
            out.append(_render_list(items, True))
            continue

        # 段落
        buf = [line]
        i += 1
        while i < n and lines[i].strip() != '' and not _is_block_start(lines[i]):
            buf.append(lines[i])
            i += 1
        out.append(f'<p>{inline(" ".join(buf))}</p>')
        continue

    return '\n'.join(out), (title or 'OmniProxy 手册')


# ---------------------------------------------------------------------------
# 站点组装
# ---------------------------------------------------------------------------

PAGE_CSS = """
:root{
  --bg:#ffffff; --fg:#1d1d1f; --muted:#6b7280; --line:#e5e7eb;
  --accent:#0a84ff; --accent-weak:#e8f1ff; --code-bg:#f5f5f7; --sidebar:#fafafa;
}
@media (prefers-color-scheme: dark){
  :root{ --bg:#1c1c1e; --fg:#f5f5f7; --muted:#9ca3af; --line:#38383a;
    --accent:#0a84ff; --accent-weak:#16314f; --code-bg:#2c2c2e; --sidebar:#232325; }
}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
  color:var(--fg);background:var(--bg);line-height:1.7;font-size:15px}
.layout{display:flex;min-height:100vh}
.sidebar{width:280px;flex:0 0 280px;background:var(--sidebar);border-right:1px solid var(--line);
  padding:22px 16px;position:sticky;top:0;height:100vh;overflow-y:auto}
.sidebar h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:0 0 10px}
.sidebar h3{font-size:13px;color:var(--muted);margin:20px 10px 6px}
.sidebar a{display:block;color:var(--fg);text-decoration:none;padding:6px 10px;border-radius:8px;font-size:14px}
.sidebar a:hover{background:var(--accent-weak)}
.sidebar a.active{background:var(--accent);color:#fff}
.content{flex:1;min-width:0;width:100%;overflow-wrap:anywhere;max-width:860px;margin:0 auto;padding:40px 48px 80px}
.content h1{font-size:30px;margin:0 0 18px;letter-spacing:-.01em}
.content h2{font-size:22px;margin:34px 0 12px;border-bottom:1px solid var(--line);padding-bottom:6px}
.content h3{font-size:18px;margin:26px 0 10px}
.content p{margin:12px 0}
.content ul,.content ol{margin:12px 0;padding-left:26px}
.content li{margin:5px 0}
.content code{background:var(--code-bg);padding:2px 6px;border-radius:5px;font-size:13px;
  font-family:"SF Mono",Menlo,Consolas,monospace}
.content pre{background:var(--code-bg);padding:16px;border-radius:10px;overflow:auto}
.content pre code{background:none;padding:0}
.content blockquote{margin:14px 0;padding:10px 16px;border-left:4px solid var(--accent);
  background:var(--accent-weak);border-radius:0 8px 8px 0;color:var(--fg)}
.content table.md-table{display:block;overflow-x:auto;border-collapse:collapse;width:100%;margin:16px 0;font-size:14px}
.content table.md-table th,.content table.md-table td{border:1px solid var(--line);padding:8px 12px;text-align:left}
.content table.md-table th{background:var(--sidebar)}
.content hr{border:none;border-top:1px solid var(--line);margin:28px 0}
.content a{color:var(--accent);text-decoration:none}
.content a:hover{text-decoration:underline}
.content img{max-width:100%}
.pager{display:flex;justify-content:space-between;margin-top:48px;border-top:1px solid var(--line);padding-top:20px;gap:12px}
.pager a{color:var(--accent);text-decoration:none;font-size:14px;max-width:48%}
.pager .next{text-align:right;margin-left:auto}
@media (max-width:760px){
  .layout{flex-direction:column}
  .sidebar{position:static;width:100%;flex:none;height:auto;max-height:35vh;border-right:0;border-bottom:1px solid var(--line)}
  .content{padding:24px 20px 48px}
}
.pager .label{display:block;color:var(--muted);font-size:12px}
.badge{display:inline-block;font-size:12px;color:var(--muted);border:1px solid var(--line);
  border-radius:999px;padding:2px 10px;margin-bottom:14px}
"""


def _page_html(title, body, nav, current_idx, prev_item, next_item,
               site_title=DEFAULT_TITLE, chapter_groups=()):
    nav_parts = []
    current_group = ''
    for idx, (label, href) in enumerate(nav):
        group = chapter_groups[idx] if chapter_groups else ''
        if group != current_group:
            if current_group:
                nav_parts.append('</section>')
            if group:
                nav_parts.append(f'<section><h3>{html.escape(group)}</h3>')
            current_group = group
        active = 'active' if idx == current_idx else ''
        current = ' aria-current="page"' if idx == current_idx else ''
        nav_parts.append(f'<a class="{active}" href="{href}"{current}>{label}</a>')
    if current_group:
        nav_parts.append('</section>')
    nav_html = '\n'.join(nav_parts)
    prev = ''
    if prev_item:
        prev = f'<a href="{prev_item[1]}"><span class="label">上一页</span>{prev_item[0]}</a>'
    nxt = ''
    if next_item:
        nxt = f'<a class="next" href="{next_item[1]}"><span class="label">下一页</span>{next_item[0]}</a>'
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:,">
<title>{title} · {site_title}</title>
<style>{PAGE_CSS}</style>
</head>
<body>
<div class="layout">
<nav class="sidebar">
  <h2>{site_title}</h2>
  {nav_html}
</nav>
<main class="content">
  <span class="badge">{site_title}</span>
  {body}
  <div class="pager">{prev}{nxt}</div>
</main>
</div>
</body>
</html>"""


def _chapter_navigation(root):
    """首页二级标题拥有章节分组，章节首次链接拥有归属和顺序。"""
    chapters = {"index.md": ''}
    index_path = os.path.join(root, "index.md")
    if not os.path.isfile(index_path):
        return chapters
    group = ''
    with open(index_path, encoding='utf-8') as f:
        for line in f:
            heading = re.match(r'^##\s+(.+?)\s*$', line)
            if heading:
                group = heading.group(1)
            for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', line):
                url = urlsplit(target)
                path = posixpath.normpath(url.path)
                if not url.scheme and not url.netloc and path.endswith('.md'):
                    chapters.setdefault(path, group)
    return chapters


def collect_pages(root, exclude_dirs=frozenset(), chapter_groups=None):
    """按首页章节链接顺序返回页面，未列出的页面按路径排在最后。"""
    files = []
    for dirpath, dirnames, fnames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for fn in fnames:
            if fn.endswith('.md'):
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root)
                files.append(rel)
    chapter_groups = chapter_groups if chapter_groups is not None else _chapter_navigation(root)
    chapter_order = {path: idx for idx, path in enumerate(chapter_groups)}
    files.sort(key=lambda path: (chapter_order.get(path, len(chapter_order)), path))
    pages = []
    for rel in files:
        with open(os.path.join(root, rel), encoding='utf-8') as f:
            body, title = md_to_html(f.read())
        noext = os.path.splitext(rel)[0]
        pages.append((title, noext, body))
    return pages


def build(root, out_dir, exclude_dirs=frozenset(), site_title=DEFAULT_TITLE):
    root = os.path.realpath(root)
    out_dir = os.path.realpath(out_dir)
    if os.path.commonpath([root, out_dir]) == root:
        raise ValueError('output must be outside the manual source directory')
    chapter_groups = _chapter_navigation(root)
    pages = collect_pages(root, exclude_dirs, chapter_groups)
    if not any(name == 'index' for _, name, _ in pages):
        raise ValueError('manual index.md is required')
    nav = [(title, noext + '.html') for (title, noext, _) in pages]
    groups = [chapter_groups.get(noext + '.md', '') for _, noext, _ in pages]
    os.makedirs(out_dir, exist_ok=True)
    for idx, (title, noext, body) in enumerate(pages):
        prev_item = nav[idx - 1] if idx > 0 else None
        next_item = nav[idx + 1] if idx < len(nav) - 1 else None
        page_dir = posixpath.dirname(noext) or '.'
        local_nav = [(label, posixpath.relpath(href, page_dir)) for label, href in nav]
        prev_item = local_nav[idx - 1] if idx > 0 else None
        next_item = local_nav[idx + 1] if idx < len(local_nav) - 1 else None
        html_doc = _page_html(title, body, local_nav, idx, prev_item, next_item, site_title, groups)
        destination = os.path.join(out_dir, noext + '.html')
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, 'w', encoding='utf-8') as f:
            f.write(html_doc)
    # 复制非 md 静态资源（如图片）保持原结构
    for dirpath, dirnames, fnames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != '__pycache__' and not d.startswith('.')]
        for fn in fnames:
            if os.path.splitext(fn)[1].lower() not in {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.css', '.js', '.ico'}:
                continue
            src = os.path.join(dirpath, fn)
            rel = os.path.relpath(src, root)
            dst = os.path.join(out_dir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    return out_dir, len(pages)


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def _serve(out_dir, port):
    os.chdir(out_dir)
    handler = SimpleHTTPRequestHandler
    httpd = None
    while port < 65535:
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
            break
        except OSError:
            port += 1
    if httpd is None:
        print("无法绑定端口", file=sys.stderr)
        sys.exit(1)
    url = f"http://127.0.0.1:{port}/"
    print(f"\nOmniProxy 手册预览已启动：{url}")
    print("按 Ctrl+C 停止。\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


def main():
    ap = argparse.ArgumentParser(description="OmniProxy 文档站本地预览/编译（零依赖）")
    ap.add_argument('--root', default=ROOT, help='文档源目录（默认 manual）')
    ap.add_argument('--title', default=None, help='站点标题（默认按目录：manual→手册，docs→设计文档）')
    sub = ap.add_subparsers(dest='cmd')
    sp = sub.add_parser('serve', help='构建并启动本地预览（默认）')
    sp.add_argument('--port', type=int, default=SITE_PORT, help='预览端口（默认 17890）')
    bp = sub.add_parser('build', help='仅导出静态站点到目录')
    bp.add_argument('out', nargs='?', default=os.path.join(os.path.dirname(HERE), PREVIEW_DIRNAME),
                    help=f'输出目录（默认 {PREVIEW_DIRNAME}/）')
    args = ap.parse_args()
    cmd = args.cmd or 'serve'
    root = os.path.abspath(args.root)
    # docs 根编译设计文档集时跳过独立成站的子目录
    exclude = EXCLUDE_DIRS if os.path.basename(root) == 'docs' else frozenset()
    title = args.title or ('OmniProxy 手册' if os.path.basename(root) == 'manual' else 'OmniProxy 设计文档')

    if cmd == 'build':
        out, count = build(root, args.out, exclude, title)
        print(f"已导出静态站点：{out}（{count} 页 · {title}）")
        return

    # serve：构建到临时目录
    tmp = tempfile.mkdtemp(prefix="omniproxy_site_")
    out, count = build(root, tmp, exclude, title)
    print(f"已构建 {count} 页到临时目录（{title}）。")
    _serve(out, args.port)


if __name__ == '__main__':
    main()
