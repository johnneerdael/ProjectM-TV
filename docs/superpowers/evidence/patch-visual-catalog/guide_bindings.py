"""Validate the HTML actually embedded in the guide against frozen gallery roles."""
from html.parser import HTMLParser
from pathlib import PurePosixPath
import re


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []

    def nodes(self, tag=None, css_class=None):
        for child in self.children:
            if isinstance(child, Node):
                if ((tag is None or child.tag == tag) and
                        (css_class is None or css_class in child.attrs.get('class', '').split())):
                    yield child
                yield from child.nodes(tag, css_class)

    def text(self):
        if self.tag == 'br':
            return ' '
        return ''.join(child.text() if isinstance(child, Node) else child
                       for child in self.children)


class Fragment(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(source)
        assert len(self.stack) == 1, 'guide HTML has unclosed tags'

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in {'img', 'br', 'hr', 'input', 'meta', 'link'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        assert self.stack[-1].tag == tag, f'guide HTML mismatched closing tag: {tag}'
        self.stack.pop()

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, attrs))

    def handle_data(self, value):
        self.stack[-1].children.append(value)


def normalized(value):
    return ' '.join(value.split())


def verify_guide(source, gallery, captures):
    # Split Markdown sections; parse their embedded HTML with the standard HTML parser.
    sections = re.split(r'^## ', source, flags=re.MULTILINE)
    observed = []
    total_refs = 0
    for section in sections:
        heading, _, body = section.partition('\n')
        if '/images/patches/audit/' not in body:
            continue
        tree = Fragment(body).root
        refs = [node for node in tree.nodes() if any(
            '/images/patches/audit/' in node.attrs.get(key, '') for key in ('href', 'src'))]
        total_refs += len(refs)
        for figure in tree.nodes('figure'):
            if any('/images/patches/audit/' in node.attrs.get('src', '')
                   for node in figure.nodes('img')):
                observed.append((heading, figure))
    expected = [(entry['patch'], pair) for entry in gallery for pair in [entry, *entry['extras']]]
    assert len(observed) == len(expected), 'guide gallery figure count'
    expected_refs = 0
    for (heading, figure), (patch, pair) in zip(observed, expected):
        case = pair['case']
        assert heading.startswith(f'{patch:04d} — '), f'guide patch section: {case}'
        assert 'patch-comparison' in figure.attrs.get('class', '').split(), f'guide figure class: {case}'
        capture = captures[case]
        panels = list(figure.nodes('div', 'patch-panel'))
        assert len(panels) == (4 if pair['crop'] else 2), f'guide panel count: {case}'
        captured_preset = PurePosixPath(capture['preset_relative_path']).name + (
            ' (synthetic)' if '/fixtures/' in capture['preset_relative_path'] else '')
        preset = pair.get('preset', captured_preset)
        assert preset == captured_preset, f'guide preset identity: {case}'
        for i, panel in enumerate(panels):
            role = ('upstream', 'patched')[i % 2]
            zoom = i >= 2
            label = ('Before · same zoom' if role == 'upstream' else 'After · same zoom') if zoom else (
                'Before · upstream master' if role == 'upstream' else 'After · ProjectM TV')
            strong, links, imgs = (list(panel.nodes(tag)) for tag in ('strong', 'a', 'img'))
            assert len(strong) == len(links) == len(imgs) == 1, f'guide panel structure: {case}/{role}'
            assert normalized(strong[0].text()) == label, f'guide role label: {case}/{role}'
            target = f'../../images/patches/audit/{case}-{role}.png'
            assert links[0].attrs.get('href') == imgs[0].attrs.get('src') == target, f'guide role reference: {case}/{role}'
            source_label = 'Before · upstream master' if role == 'upstream' else 'After · ProjectM TV'
            accessible_name = (f'Open original full-resolution {source_label} frame for zoom' if zoom
                               else f'Open full-resolution {source_label} image')
            assert links[0].attrs.get('aria-label') == accessible_name, f'guide accessible role name: {case}/{role}'
            assert ('aria-labelledby' not in links[0].attrs and
                    links[0].attrs.get('aria-hidden', 'false') == 'false'), f'guide accessible role name: {case}/{role}'
            assert links[0].attrs.get('tabindex', '0') == '0', f'guide keyboard link: {case}/{role}'
            expected_alt = ('Matched crop of ' if zoom else '') + preset + ' — ' + label
            assert imgs[0].attrs.get('alt') == expected_alt, f'guide image label: {case}/{role}'
            assert all('style' not in node.attrs for node in [panel, *panel.nodes()]
                       if node is not links[0]), f'guide panel style: {case}/{role}'
            expected_refs += 2
            if zoom:
                assert 'patch-crop' in links[0].attrs.get('class', '').split(), f'guide crop class: {case}'
                x, y, width, height = pair['crop']
                assert 0 <= x < x + width <= capture['width'] and 0 <= y < y + height <= capture['height'], f'guide crop bounds: {case}'
                expected_style = {'--crop-ratio': f'{width}/{height}',
                                  '--image-width': f"{capture['width']/width*100:.9f}%",
                                  '--image-left': f'{-x/width*100:.9f}%',
                                  '--image-top': f'{-y/height*100:.9f}%'}
                style = dict(part.strip().split(':', 1) for part in
                             links[0].attrs.get('style', '').split(';') if part.strip())
                assert style == expected_style, f'guide crop rectangle: {case}/{role}'
            else:
                assert (imgs[0].attrs.get('width'), imgs[0].attrs.get('height')) == (
                    str(capture['width']), str(capture['height'])), f'guide image dimensions: {case}/{role}'
                assert 'style' not in links[0].attrs and 'style' not in imgs[0].attrs, f'guide full image style: {case}'
        captions = list(figure.nodes('figcaption'))
        assert len(captions) == 1, f'guide caption count: {case}'
        caption = normalized(captions[0].text())
        prefix = f"{preset} · {capture['width']}×{capture['height']}, frame {pair['frame']} at 30 Hz."
        assert caption.startswith(prefix), f'guide frame caption: {case}'
        expected_caption = prefix + ' ' + pair['caption']
        if pair['crop']:
            x, y, width, height = pair['crop']
            expected_caption += (f' Zoom rectangle: ({x}, {y}), {width}×{height} source pixels;'
                                 ' identical crop and nearest-neighbour display, with no brightness adjustment.')
        assert caption == normalized(expected_caption), f'guide description caption: {case}'
    assert total_refs == expected_refs, 'guide has unbound audit image references'
    assert source.count('/images/patches/audit/') == expected_refs, 'guide has unbound audit image references'
