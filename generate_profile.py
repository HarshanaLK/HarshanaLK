#!/usr/bin/env python3
"""Generate the Harshana GitHub profile hero as code-only SVGs.

The vector portrait uses coloured SVG path geometry sampled from a user-supplied
photo, then auto-animates its pixels into an HK monogram and back.
No <image> tags, external images, base64, JS, or embedded raster data.

python generate_profile.py --photo my-portrait.png
python generate_profile.py --photo my-portrait.png --tiles 170 --colors 110
"""
from __future__ import annotations
import argparse
import html
import json
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent
DEFAULT = ROOT / 'profile.json'

COLORS = {
    'dark': {
        'bg': '#080D19', 'panel': '#0D172A', 'bar': '#111D32', 'box': '#0C1425',
        'stroke': '#243A56', 'text': '#F0F6FF', 'muted': '#9CADC3', 'dim': '#657991',
        'accent': '#54D8F7', 'accent2': '#AE90FF', 'green': '#4CE5B1', 'label': '#A9D9F2',
        'photo_bg': (19, 31, 49), 'border': '#45749A',
    },
    'light': {
        'bg': '#F4F7FC', 'panel': '#FFFFFF', 'bar': '#E9EFF7', 'box': '#F9FBFF',
        'stroke': '#CCD7E6', 'text': '#152236', 'muted': '#405773', 'dim': '#7E91A7',
        'accent': '#087DA1', 'accent2': '#6E49CF', 'green': '#008866', 'label': '#1B587D',
        'photo_bg': (222, 230, 241), 'border': '#7297B2',
    },
}


def e(text):
    return html.escape(str(text), quote=True)


def prepare_photo(photo: Image.Image, theme: str, tile_w: int, tile_h: int, colors: int):
    """Fit without stretching; replace neutral background, preserving hair & face."""
    # Original photo is 400x400; centered portrait crop keeps eyes, hairstyle and suit.
    im = ImageOps.fit(photo.convert('RGB'), (tile_w, tile_h), method=Image.Resampling.LANCZOS,
                      centering=(0.5, 0.46))
    im = ImageEnhance.Contrast(im).enhance(1.045)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.15, percent=95, threshold=3))
    pixels = im.load()
    bg = COLORS[theme]['photo_bg']
    # Make the plain gray studio background match the dark/light GitHub theme.
    # Grayscale thresholds isolate high-key neutral background; jacket stays dark.
    for y in range(tile_h):
        for x in range(tile_w):
            r,g,b = pixels[x,y]
            avg = (r+g+b)/3
            chroma = max(r,g,b)-min(r,g,b)
            neutral_bg = (chroma < 17 and 120 <= avg <= 223)
            if neutral_bg:
                # Gentle tonal variation ensures the new background doesn't look flat.
                t = min(1.0, max(0., (avg-120)/103))
                tone = tuple(max(0, min(255, round(c + (t-.5)*12))) for c in bg)
                pixels[x,y] = tone
    q = im.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()
    pix = q.load()
    paths = defaultdict(list)
    # Draw horizontal runs of same palette index as geometrical vector paths.
    # Grouping by colour keeps SVG file sizes practical for GitHub.
    for y in range(tile_h):
        x=0
        while x<tile_w:
            idx=int(pix[x,y]); end=x+1
            while end<tile_w and int(pix[end,y])==idx: end+=1
            paths[idx].append(f'M{x},{y}h{end-x}v1h-{end-x}z')
            x=end
    parts=[]
    for idx, commands in paths.items():
        rgb=pal[idx*3:idx*3+3]
        color=f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
        parts.append(f'<path fill="{color}" d="{"".join(commands)}"/>')
    return '\n'.join(parts)


def label(x,y,title,theme):
    c=COLORS[theme]
    return (f'<text x="{x}" y="{y}" font-size="12" letter-spacing="2.1" '
            f'font-weight="700" fill="{c["accent"]}">{e(title)}</text>')


def text(x,y,value,theme,size=15,style='',accent=False):
    c=COLORS[theme]
    fill=c['accent'] if accent else c['text']
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {style}>{e(value)}</text>'


def record(y, title, value, theme, value_x=615, val_size=14):
    c=COLORS[theme]
    return (f'<text x="493" y="{y}" font-size="14" fill="{c["muted"]}">{e(title)}</text>'
            + f'<text x="{value_x}" y="{y}" font-size="{val_size}" fill="{c["text"]}">{e(value)}</text>')


def make_svg(photo_svg, theme, config, tile_w, tile_h):
    c=COLORS[theme]
    name=config['name']
    contact=config['contact']
    profile=config['profile']
    tech=config['technology']
    svg=[]
    add=svg.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="690" viewBox="0 0 1180 690" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" role="img" '
        f'aria-label="{e(name)} - Code-generated GitHub profile">')
    add('<defs>')
    add(f'<linearGradient id="barline" x1="0" y1="0" x2="1" y2="0">'
        f'<stop stop-color="{c["accent2"]}"/><stop offset="0.55" stop-color="{c["accent"]}"/>'
        f'<stop offset="1" stop-color="{c["green"]}"/></linearGradient>')
    add('<clipPath id="photoClip"><rect x="57" y="159" width="358" height="408" rx="8"/></clipPath>')
    add('<clipPath id="windowClip"><rect x="2" y="2" width="1176" height="686" rx="18"/></clipPath>')
    add('</defs>')
    add(f'<rect width="1180" height="690" rx="18" fill="{c["bg"]}"/>')
    add('<g clip-path="url(#windowClip)">')
    add(f'<rect x="2" y="2" width="1176" height="46" fill="{c["bar"]}"/>')
    add(f'<line x1="2" y1="48" x2="1178" y2="48" stroke="{c["stroke"]}"/>')
    for x,color in [(28,'#FF5F56'),(48,'#FEBC2E'),(68,'#27C93F')]:
        add(f'<circle cx="{x}" cy="26" r="5.5" fill="{color}"/>')
    add(text(92,31,'harshana@github:~  /profile.sh --live',theme,13))
    add(text(1142,30,'[ SVG • CODE-ONLY ]',theme,11,'text-anchor="end"',accent=True))
    # Left vector portrait panel
    add(f'<rect x="28" y="68" width="415" height="597" rx="13" fill="{c["box"]}" stroke="{c["stroke"]}"/>')
    add(label(47,103,'VISUAL.PORTRAIT',theme))
    add(text(414,104,'// source: uploaded photo',theme,10,'text-anchor="end"'))
    add(f'<line x1="47" y1="118" x2="422" y2="118" stroke="url(#barline)" stroke-width="1.5"/>')
    add(f'<rect x="57" y="159" width="358" height="408" rx="8" fill="{c["panel"]}"/>')
    # Photo content is only paths filled with SVG colours. No embedded raster anywhere.
    add('<g clip-path="url(#photoClip)">')
    add(f'<g transform="translate(57 159) scale({358/tile_w:.8f} {408/tile_h:.8f})" shape-rendering="auto">')
    add(photo_svg)
    add('</g></g>')
    add(f'<rect x="57" y="159" width="358" height="408" rx="8" fill="none" stroke="{c["border"]}" stroke-width="1.2"/>')
    add(text(58,592,'COLOR-QUANTIZED VECTOR PORTRAIT',theme,11,'letter-spacing=".9"',accent=True))
    add(text(58,612,'Rendered entirely with SVG path data',theme,11))
    add(text(58,635,'No embedded raster / no photo files',theme,10))
    # Right terminal panel
    add(f'<rect x="462" y="68" width="688" height="597" rx="13" fill="{c["panel"]}" stroke="{c["stroke"]}"/>')
    add(label(488,101,'SYSTEM.INFO',theme))
    add(f'<line x1="624" y1="97" x2="1096" y2="97" stroke="{c["stroke"]}"/>')
    add(f'<circle cx="1112" cy="97" r="4" fill="{c["green"]}"><animate attributeName="opacity" values="1;0.35;1" dur="2.2s" repeatCount="indefinite"/></circle>')
    add(text(1121,102,'LIVE',theme,11,accent=True))
    add(text(489,141,name,theme,24,'font-weight="750"'))
    add(text(491,166,profile['role'],theme,16,accent=True))
    add(record(201,'Location :',profile['location'],theme))
    add(record(226,'Degree   :',profile['degree'],theme,val_size=13))
    add(record(250,'University:',profile['university'],theme,val_size=13))
    add(f'<line x1="487" y1="269" x2="1127" y2="269" stroke="url(#barline)" opacity=".66"/>')
    add(label(489,291,'CORE.TOOLCHAIN',theme))
    for y,label_text,key in [
        (319,'Languages :','languages'), (344,'Frontend  :','frontend'),
        (369,'Backend   :','backend'), (394,'Database  :','database'),
        (419,'Cloud/Dev :','cloud')]:
        add(record(y,label_text,tech[key],theme,val_size=13))
    add(f'<line x1="487" y1="437" x2="1127" y2="437" stroke="{c["stroke"]}"/>')
    add(label(489,460,'CURRENT.FOCUS',theme))
    add(text(490,485,profile['focus'],theme,13))
    add(f'<line x1="487" y1="503" x2="1127" y2="503" stroke="{c["stroke"]}"/>')
    add(label(489,526,'CONTACT.ENDPOINTS',theme))
    for y,key,code in [(552,'Email  :','email'),(575,'GitHub :','github'),(598,'LinkedIn:','linkedin'),(621,'X      :','twitter')]:
        add(record(y,key,contact[code].replace('https://',''),theme,val_size=12))
    add(f'<line x1="487" y1="641" x2="1127" y2="641" stroke="url(#barline)" opacity=".7"/>')
    add(text(489,654,'$ explore --projects | connect --social',theme,11,accent=True))
    add('</g>')
    add(f'<rect x="2" y="2" width="1176" height="686" rx="18" fill="none" stroke="url(#barline)" stroke-width="2"/>')
    add('</svg>')
    return '\n'.join(svg)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--photo',required=True,help='Path to the portrait to turn into SVG paths')
    parser.add_argument('--config',default=str(DEFAULT))
    parser.add_argument('--output',default=str(ROOT))
    parser.add_argument('--tiles',type=int,default=156,help='Columns of color sample cells (default 156)')
    parser.add_argument('--colors',type=int,default=110,help='Color palette size (2-256)')
    args=parser.parse_args()
    conf=json.loads(Path(args.config).read_text(encoding='utf-8'))
    photo=Image.open(args.photo)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    # Exactly 156x177 image sample, resized in SVG with isotropic scale.
    # Both dark and light recompute studio background; same real-person face.
    for mode in ('dark','light'):
        tile_w=args.tiles
        tile_h=round(args.tiles*177/156)
        vec=prepare_photo(photo,mode,tile_w,tile_h,args.colors)
        svg=make_svg(vec,mode,conf,tile_w,tile_h)
        path=out/f'{mode}.svg'
        path.write_text(svg,encoding='utf8')
        # Animate the generated colour-vector portrait without embedding a photo.
        from animated_portrait import animate_profile
        pixels = animate_profile(path)
        print(f'Created {path.name}: {path.stat().st_size/1024:.0f} KiB, {pixels} animated pixels, no embedded raster')

if __name__=='__main__':main()
