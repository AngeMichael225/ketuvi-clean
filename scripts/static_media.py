"""Assemble the Vercel export from prepared, public-facing assets."""

import json
import re
import shutil


def prepare_static_media(root, output):
    if output.is_symlink() or output.resolve() != root / 'dist':
        raise ValueError('Le dossier de publication doit être dist dans ce dépôt.')
    output.mkdir(exist_ok=True)
    photos = json.loads((root / 'scripts/site-photos.json').read_text(encoding='utf-8'))
    dimensions = {key: item['dimensions'] for key, item in photos.items()}
    widths = {}
    for image in (root / 'site/public/assets/photos').glob('*.webp'):
        match = re.fullmatch(r'(.+)-(\d+)\.webp', image.name)
        if not match:
            continue
        key, width = match.groups()
        if key.endswith('-portrait') and key[:-9] in photos:
            width_full, height = dimensions[key[:-9]]
            dimensions[key] = (min(width_full, round(height * 4 / 5)), height)
        if key in dimensions:
            widths.setdefault(key, []).append(int(width))
    return photos, dimensions, {key: sorted(values) for key, values in widths.items()}


def public_logo(source, destination):
    # Client artwork can carry authoring paths in optional PNG text chunks.
    raw = source.read_bytes()
    result = bytearray(raw[:8])
    start = 8
    while start < len(raw):
        size = int.from_bytes(raw[start:start + 4], 'big')
        end = start + size + 12
        if end > len(raw):
            raise ValueError(f'PNG incomplet : {source.name}')
        if raw[start + 4:start + 8] not in (b'tEXt', b'zTXt', b'iTXt'):
            result.extend(raw[start:end])
        start = end
    destination.write_bytes(result)


def publish_assets(root, output, routes):
    source = root / 'site/public/assets'
    paths = {output / route / 'index.html' for route in routes} | {output / '404.html'}
    assets = set()
    for page in paths:
        assets.update(re.findall(r'/assets/([\w./-]+\.(?:css|js|png|svg|webp))\b', page.read_text(encoding='utf-8')))
    for name in sorted(assets | {'icons/LICENSE-Phosphor.txt', 'icons/NOTICE.md'}):
        original = source / name
        dest = output / 'assets' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if name == 'styles.css':
            css = original.read_text(encoding='utf-8')
            css = re.sub(r'@font-face\s*\{[^}]*\}', '', css)
            css = css.replace('"Ketuvi Sans"', '"Helvetica Neue"')
            dest.write_text(css, encoding='utf-8')
        elif name in {'brandmark.png', 'brandmark-white.png'}:
            public_logo(original, dest)
        elif name == 'icons/NOTICE.md':
            dest.write_text('Les icônes de KetuviClean adaptent les icônes Phosphor Fill. '
                            'Copyright (c) 2023 Phosphor Icons. [Licence MIT](LICENSE-Phosphor.txt).\n'
                            '[Source officielle](https://github.com/phosphor-icons/core).\n', encoding='utf-8')
        else:
            shutil.copyfile(original, dest)
        paths.add(dest)
    paths.add(output / 'robots.txt')
    paths.add(output / 'sitemap.xml')
    # Remove obsolete image variants after a content edit; reject unrelated files in this dedicated export.
    for path in output.rglob('*'):
        if path.is_file() and path not in paths:
            if path.parent == output / 'assets/photos' and path.suffix == '.webp' and not path.is_symlink():
                path.unlink()
            else:
                raise ValueError(f'Fichier inattendu dans le dossier de publication : {path.relative_to(output)}')
    count = sum(name.endswith('.webp') for name in assets)
    print(f'Publication statique : {len(routes)} pages, 404 personnalisée, {count} variantes WebP dans dist.')
