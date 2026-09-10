"""Validate generated local links, anchors and assets without network access."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys


class Links(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids = set()
        self.links = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for name in ('href', 'src'):
            if name in attrs:
                self.links.append(attrs[name])


def check(root):
    root = Path(root).resolve()
    pages = {p: Links(p.read_text(encoding='utf-8')) for p in root.rglob('*.html')}
    failures = []
    if root / 'index.html' not in pages:
        failures.append('missing index.html')
    for page, parsed in pages.items():
        for link in parsed.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = (page.parent / unquote(url.path)).resolve() if url.path else page
            if not target.is_relative_to(root):
                failures.append(f'{page.name}: outside site: {link}')
                continue
            if target.is_dir():
                target /= 'index.html'
            if not target.is_file():
                failures.append(f'{page.name}: missing: {link}')
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                failures.append(f'{page.name}: missing anchor: {link}')
    return failures


if __name__ == '__main__':
    failures = check(sys.argv[1])
    if failures:
        raise SystemExit('\n'.join(failures))
    print('PASS: generated links, anchors and assets')
