"""Cover project-site navigation and fail-closed publishing, without a server."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build_site
import check_site


class SiteTests(unittest.TestCase):
    def test_nested_navigation_and_markdown_anchor_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'manual'
            (root / 'guide').mkdir(parents=True)
            (root / 'index.md').write_text('# Home\n\n[Guide](guide/start.md#details)\n')
            (root / 'guide/start.md').write_text('# Guide\n\n## Details\n\n[Home](../index.md)\n')
            out = Path(tmp) / 'omniproxy-docs'
            build_site.build(str(root), str(out))
            self.assertIn('guide/start.html#details', (out / 'index.html').read_text())
            self.assertEqual(check_site.check(out), [])
            (out / 'guide/start.html').write_text('<h1 id="other">Changed</h1>')
            self.assertTrue(any('missing anchor' in error for error in check_site.check(out)))
            (out / 'guide/start.html').unlink()
            self.assertTrue(any('missing:' in error for error in check_site.check(out)))

    def test_missing_home_and_in_source_output_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'manual'
            root.mkdir()
            self.assertIn('missing index.html', check_site.check(root))
            with self.assertRaises(ValueError):
                build_site.build(str(root), str(root / '_site'))
            with self.assertRaises(ValueError):
                build_site.build(str(root), str(Path(tmp) / 'out'))

    def test_escaped_table_separator_keeps_command_in_one_cell(self):
        self.assertEqual(build_site._split_row(r'| `a\|b` | label |'), ['`a|b`', 'label'])

    def test_home_directory_controls_sidebar_and_pager_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'manual'
            root.mkdir()
            (root / 'index.md').write_text(
                '# Home\n\n[Outside](https://example.com/a.md)\n'
                '## Getting started\n[Start](z.md#start)\n'
                '## Configuration & tools\n[Again](z.md)\n[Next](a.md)\n')
            (root / 'z.md').write_text('# Start\n\n## Start\n')
            (root / 'a.md').write_text('# Next\n')
            (root / 'appendix.md').write_text('# Appendix\n')
            out = Path(tmp) / 'out'

            build_site.build(str(root), str(out))

            page = (out / 'z.html').read_text()
            sidebar = page.split('<nav class="sidebar">', 1)[1].split('</nav>', 1)[0]
            sections = sidebar.split('<section>')[1:]
            self.assertEqual(len(sections), 2)
            self.assertIn('<h3>Getting started</h3>', sections[0])
            self.assertIn('href="z.html" aria-current="page"', sections[0])
            self.assertNotIn('href="a.html"', sections[0])
            self.assertIn('<h3>Configuration &amp; tools</h3>', sections[1])
            self.assertIn('href="a.html"', sections[1])
            self.assertNotIn('href="z.html"', sections[1])
            pager = page.split('<div class="pager">', 1)[1].split('</div>', 1)[0]
            self.assertIn('href="index.html"', pager)
            self.assertIn('href="a.html"', pager)
            self.assertIn('href="appendix.html"', sidebar)
            self.assertEqual(check_site.check(out), [])
