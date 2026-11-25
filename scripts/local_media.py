from pathlib import Path
from datetime import datetime, timezone
import json
import shutil

from PIL import Image
from PIL.PngImagePlugin import PngInfo


def prepare_local_media(ROOT, ASSETS):
    SOURCE=Path(r'D:\PC GSF\Ketuvi')
    photo_prompts=json.loads((ROOT/'brand-guidelines/assets/photos/prompts.json').read_text(encoding='utf-8'))
    photo_provenance={item['key']:item for item in json.loads((ROOT/'brand-guidelines/assets/photos/provenance.json').read_text(encoding='utf-8'))}
    PHOTO_WIDTHS = (480, 768, 1024, 1440, 2304, 3840)
    PORTRAIT_WIDTHS = (512, 1024, 1536)
    photo_dimensions = {}
    photo_widths = {}
    COVER_PHOTOS = {'hero-editorial', 'modern-office-meeting', 'detail-editorial'}
    for manifest in ('editorial-provenance.json','residential-comparison-provenance.json',
                     'people-series-provenance.json','residential-series-provenance.json','space-series-provenance.json',
                     'cabinet-care-provenance.json','floor-stripping-provenance.json','careers-group-provenance.json',
                     'realism-interiors-provenance.json','condo-postconstruction-provenance.json','modern-office-provenance.json'):
        for item in json.loads((ROOT/'brand-guidelines/assets/photos'/manifest).read_text(encoding='utf-8')):
            photo_provenance[item['key']]=item
            photo_prompts[item['key']]=item['prompt']
    for key, provenance in photo_provenance.items():
        source = ROOT / 'brand-guidelines/assets/photos' / f'{key}.png'
        with Image.open(source) as master:
            variants = [(key, PHOTO_WIDTHS, None)]
            if key in COVER_PHOTOS:
                # Keep the 76% horizontal focal point used by the mobile cover.
                crop_width = min(master.width, round(master.height * 4 / 5))
                left = round((master.width - crop_width) * .76)
                variants.append((f'{key}-portrait', (*PORTRAIT_WIDTHS, crop_width), (left, 0, left + crop_width, master.height)))
            for stem, widths, crop in variants:
                native_width = crop[2] - crop[0] if crop else master.width
                photo_dimensions[stem] = (native_width, master.height)
                photo_widths[stem] = sorted({min(width, native_width) for width in widths})
                for width in photo_widths[stem]:
                    target = ASSETS / 'photos' / f'{stem}-{width}.webp'
                    if not target.exists() or target.stat().st_mtime < source.stat().st_mtime:
                        frame = master.crop(crop) if crop else master
                        if width < frame.width:
                            height = round(width * frame.height / frame.width)
                            frame = frame.resize((width, height), Image.Resampling.LANCZOS)
                        frame.save(target, 'WEBP', quality=87, method=6)
                    transform = '4:5 portrait crop' if crop else 'Full frame'
                    metadata = {
                        'prompt': photo_prompts[key],
                        'origin': f'brand-guidelines/assets/photos/{key}.png',
                        'model': provenance['model'],
                        'job_id': provenance['job_id'],
                        'derivative': (f'{transform}, encoded at its native width of {width}px as WebP.'
                                       if width == native_width else f'{transform}, resized to {width}px wide and encoded as WebP.'),
                        'createdAt': datetime.fromtimestamp(source.stat().st_mtime,timezone.utc).isoformat(),
                    }
                    target.with_suffix('.webp.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    for source,name in [('Helvetica Neue Roman.otf','helvetica-roman.otf'),('Helvetica Neue Medium.otf','helvetica-medium.otf'),('Helvetica Neue Light.otf','helvetica-light.otf')]:
        original_font=SOURCE/'helvetica neue'/source
        local_font=ASSETS/'fonts'/name
        if original_font.is_file() or not local_font.is_file():
            shutil.copy2(original_font,local_font)
    icon_source=SOURCE/'Graphics/Logo/Icon/KetuviClean Flavicon Purple 256 x 256.png'
    icon_target=ASSETS/'brandmark.png'
    if icon_source.is_file() or not icon_target.is_file():
        with Image.open(icon_source) as brandmark:
            brandmark_metadata=PngInfo()
            brandmark_metadata.add_text('impeccable:prompt','Client-supplied Ketuvi official identity symbol, preserved with authorization. Origin: D:/PC GSF/Ketuvi/Graphics/Logo/Icon/KetuviClean Flavicon Purple 256 x 256.png. Brand asset, not reused photography.')
            brandmark.save(icon_target,pnginfo=brandmark_metadata)
    white_mark_source = SOURCE/'Graphics/Logo/KetuviClean logo Symbole.png'
    white_mark_target = ASSETS/'brandmark-white.png'
    if not white_mark_target.is_file() or (white_mark_source.is_file() and white_mark_target.stat().st_mtime < white_mark_source.stat().st_mtime):
        with Image.open(white_mark_source) as original:
            white_mark = original.crop(original.getchannel('A').getbbox())
            white_mark.thumbnail((174, 160), Image.Resampling.LANCZOS)
            white_mark.save(white_mark_target, optimize=True)
    for source in (ROOT/'brand-guidelines/assets/icons').glob('*.svg'):
        shutil.copy2(source,ASSETS/'icons'/source.name)
    for name in ('NOTICE.md','LICENSE-Phosphor.txt'):
        shutil.copy2(ROOT/'brand-guidelines/assets/icons'/name,ASSETS/'icons'/name)

    # Portable builds only need the public descriptions and native dimensions.
    catalog = {}
    for key, item in sorted(photo_provenance.items()):
        catalog[key] = {'dimensions': photo_dimensions[key]}
        if item.get('description'):
            catalog[key]['description'] = item['description']
    (ROOT / 'scripts/site-photos.json').write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
    )
    return photo_provenance, photo_dimensions, photo_widths
