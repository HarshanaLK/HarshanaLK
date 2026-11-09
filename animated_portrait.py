#!/usr/bin/env python3
"""Turn Harshana's EXISTING vector portrait into an animated pixel-morph hero.

Usage:
    pip install -r requirements.txt
    python animated_portrait.py

Runs on dark.svg and light.svg in this directory. It reconstructs the original
portrait from the SVG's coloured vector paths, so no source JPG/PNG is needed.
It keeps the existing terminal layout, text, profile data, and portrait paths.
The effect cycles: original photo -> neon pixels -> HK monogram -> portrait.

To rebuild after changing your source photo:
    python generate_profile.py --photo /path/to/your-photo.jpg
    # The generator invokes animate_profile() on the generated SVG automatically.

All animation uses SVG/SMIL only: no JS, GIF, external URLs, or base64 pictures.
"""
from __future__ import annotations

import argparse
import math
import random
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def q(tag: str) -> str:
    return f'{{{NS}}}{tag}'


def rgbhex(color: tuple[int, int, int]) -> str:
    return '#%02x%02x%02x' % color


def rgb(color: str) -> tuple[int, int, int]:
    return tuple(bytes.fromhex(color.lstrip('#'))[:3])


def mix(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float):
    return tuple(round(a * (1-t) + b * t) for a, b in zip(c1, c2))


def find_portrait_root(root: ET.Element) -> ET.Element:
    """Find the existing clipping group that contains the portrait."""
    for group in root.iter(q('g')):
        if group.get('clip-path') == 'url(#photoClip)':
            return group
    raise ValueError('No <g clip-path="url(#photoClip)"> found. Use Harshana profile SVG.')


def recover_vector_paths(group: ET.Element) -> tuple[Image.Image, ET.Element]:
    """Extract exact sampled RGB pixels from SVG paths without rasterizing the SVG."""
    # On repeated invocations, find the original (not animated) vector content.
    static = next((el for el in group if el.get('id') == 'portraitColorPhoto'), None)
    if static is None:
        static = ET.Element(q('g'))
        for node in list(group):
            # Original generator has exactly one transform group here.
            if node.tag == q('g') and node.get('id') != 'pixelMorphLayer':
                group.remove(node)
                static.append(node)
        if len(static) == 0:
            raise ValueError('No original vector portrait found in SVG.')
        static.set('id', 'portraitColorPhoto')
        group.insert(0, static)

    runs: list[tuple[int, int, int, tuple[int, int, int]]] = []
    max_x = max_y = 0
    for path in static.iter(q('path')):
        fill = path.get('fill')
        if not fill or not re.fullmatch(r'#[0-9a-fA-F]{6}', fill):
            continue
        col = rgb(fill)
        d = path.get('d', '')
        # Existing photo generator encodes each contiguous pixel row as a vector run.
        for m in re.finditer(r'M\s*(\d+)[, ]\s*(\d+)h(\d+)v1h-\d+z', d):
            x, y, width = (int(v) for v in m.groups())
            runs.append((x, y, width, col))
            max_x = max(max_x, x + width)
            max_y = max(max_y, y + 1)
    if not runs or not max_x or not max_y:
        raise ValueError('Could not reconstruct portrait pixels from the original SVG paths.')

    img = Image.new('RGB', (max_x, max_y))
    draw = ImageDraw.Draw(img)
    for x, y, width, color in runs:
        draw.line([(x, y), (x+width-1, y)], fill=color)
    return img, static


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    names = (
        ['DejaVuSansMono-Bold.ttf', 'DejaVuSans-Bold.ttf', 'LiberationMono-Bold.ttf']
        if bold else ['DejaVuSansMono.ttf', 'DejaVuSans.ttf']
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_monogram(width: int, height: int) -> Image.Image:
    """Build the target shape with image processing; output embeds no raster data."""
    im = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(im)
    # Fit an HK mark and name in the same coordinate space as the original photo.
    size = max(30, int(width * 0.63))
    for _ in range(35):
        f = font(size)
        box = draw.textbbox((0, 0), 'HK', font=f, stroke_width=0)
        if box[2] - box[0] <= width * 0.89 and box[3] - box[1] <= height * 0.44:
            break
        size -= 2
    tw = box[2]-box[0]
    tx = round((width-tw)/2-box[0])
    # Set the large initials in the central section of the portrait frame.
    ty = round(height * 0.48 - (box[1]+box[3])/2)
    draw.text((tx, ty), 'HK', font=f, fill=255)

    tag = 'HARSHANA'
    label_size = max(8, int(width * 0.12))
    lf = font(label_size)
    tb = draw.textbbox((0,0),tag,font=lf)
    while (tb[2]-tb[0]) > width * 0.86 and label_size > 7:
        label_size-=1
        lf=font(label_size)
        tb = draw.textbbox((0,0),tag,font=lf)
    label_x=round((width-(tb[2]-tb[0]))/2-tb[0])
    label_y=round(height*.71 - tb[1])
    draw.text((label_x,label_y),tag,fill=255,font=lf)
    draw.line((round(width*.16),round(height*.68),round(width*.84),round(height*.68)),fill=255,width=max(1,width//65))
    return im


def distribute_targets(mask: Image.Image, count: int, seed=2124) -> list[tuple[float,float]]:
    """Evenly scatter exactly count squares over letters, with deterministic output."""
    width,height=mask.size
    px=mask.load()
    # Scramble candidates in each 2x2 tile, preventing a dense clump of points.
    randomizer=random.Random(seed)
    blocks=[]
    for y in range(0,height,2):
        for x in range(0,width,2):
            cand=[(xx,yy) for yy in range(y,min(y+2,height))
                  for xx in range(x,min(x+2,width)) if px[xx,yy]>128]
            if cand:
                blocks.append(cand)
    randomizer.shuffle(blocks)
    targets=[]
    for cand in blocks:
        targets.append(randomizer.choice(cand))
    # If more points are required, fill with the remaining mask pixels.
    if len(targets)<count:
        used=set(targets)
        more=[(x,y) for y in range(height) for x in range(width)
              if px[x,y]>128 and (x,y) not in used]
        randomizer.shuffle(more)
        targets.extend(more[:count-len(targets)])
    if len(targets)<count:
        # Dense portraits can contain more points than mark pixels: repeating targets
        # is harmless but keep individual pixels slightly staggered.
        while len(targets) < count:
            targets.extend(targets[:min(len(targets), count-len(targets))])
    if len(targets)>count:
        targets=randomizer.sample(targets,count)
    # Match top-to-bottom order so pixels travel in a coherent wave.
    targets.sort(key=lambda p:(p[1]//7,p[0],p[1]))
    return [(float(x),float(y)) for x,y in targets]


def sample_portrait(image: Image.Image, density: int = 3):
    """Ignore empty studio background, retain facial features and clothing."""
    w,h=image.size
    px=image.load()
    corners=[px[0,0],px[w-1,0],px[0,h//4],px[w-1,h//4]]
    background=tuple(sorted(c[k] for c in corners)[len(corners)//2] for k in range(3))
    points=[]
    for y in range(0,h,density):
        for x in range(0,w,density):
            sx=min(w-1,x+density//2)
            sy=min(h-1,y+density//2)
            color=px[sx,sy]
            delta=max(abs(a-b) for a,b in zip(color,background))
            if delta<19:
                continue
            points.append((x+0.15,y+0.15,color))
    points.sort(key=lambda item:(int(item[1])//6,item[0]))
    return points


def make_pixel_group(image: Image.Image, theme: str, cycle: float, density=3):
    w,h=image.size
    c1=rgb('#AE90FF' if theme=='dark' else '#6E49CF')
    c2=rgb('#54D8F7' if theme=='dark' else '#087DA1')
    c3=rgb('#4CE5B1' if theme=='dark' else '#008866')
    sampled=sample_portrait(image,density)
    target=distribute_targets(make_monogram(w,h),len(sampled))
    group=ET.Element(q('g'),{'id':'pixelMorphLayer',
                                  'transform':f'translate(57 159) scale({358/w:.8f} {408/h:.8f})',
                                  'shape-rendering':'crispEdges',
                                  'opacity':'0'})
    ET.SubElement(group,q('animate'),{
        'attributeName':'opacity',
        'values':'0;0;1;1;1;1;1;0;0',
        'keyTimes':'0;.18;.25;.34;.45;.64;.75;.84;1',
        'dur':f'{cycle:g}s', 'repeatCount':'indefinite'
    })
    for n,((x,y,pixel),(tx,ty)) in enumerate(zip(sampled,target)):
        blend_x=min(1,max(0,x/max(1,w-1)))
        main=mix(c1,c2,blend_x)
        if y>h*.74:
            main=mix(main,c3,.33)
        # Brightness modulation lets facial structure stay recognizable as pixels.
        luminance=(pixel[0]*.299+pixel[1]*.587+pixel[2]*.114)/255
        opacity=min(.99,max(.47,.60 + .37*luminance))
        delta_x=round(tx-x,2)
        delta_y=round(ty-y,2)
        rect=ET.SubElement(group,q('rect'),{
            'x':f'{x:.2f}','y':f'{y:.2f}',
            'width':f'{density*.77:.2f}', 'height':f'{density*.77:.2f}',
            'rx':'.18','fill':rgbhex(main),'opacity':f'{opacity:.2f}'
        })
        # Staggering along diagonal makes the logo assemble in a cascading wave.
        lag=.022 * (x/max(1,w-1)+y/max(1,h-1)-1)
        s=.34+lag; e=.47+lag; hold=.65+lag; end=.77+lag
        times=f'0;{s:.5f};{e:.5f};{hold:.5f};{end:.5f};1'
        ET.SubElement(rect,q('animateTransform'),{
            'attributeName':'transform','type':'translate',
            'values':f'0 0;0 0;{delta_x:.2f} {delta_y:.2f};{delta_x:.2f} {delta_y:.2f};0 0;0 0',
            'keyTimes':times,
            'calcMode':'spline',
            'keySplines':'0 0 1 1;.22 .68 .18 1;0 0 1 1;.24 .68 .18 1;0 0 1 1',
            'dur':f'{cycle:g}s','repeatCount':'indefinite'
        })
    return group,len(sampled)


def animate_profile(path: Path | str, *, cycle:float=15, density:int=3) -> int:
    path=Path(path)
    if not path.is_file():
        raise FileNotFoundError(f'{path} does not exist')
    if density not in (2,3,4,5):
        raise ValueError('density must be one of 2, 3, 4, 5')
    theme='light' if 'light' in path.stem.lower() else 'dark'
    tree=ET.parse(path)
    root=tree.getroot()
    group=find_portrait_root(root)
    im,static=recover_vector_paths(group)
    # Remove older animations so the command is safe to rerun repeatedly.
    for child in list(group):
        if child.get('id')=='pixelMorphLayer':
            group.remove(child)
    for child in list(static):
        if child.tag==q('animate'):
            static.remove(child)
    static.set('opacity','1')
    photo_timeline=ET.Element(q('animate'),{
        'attributeName':'opacity',
        'values':'1;1;0;0;0;0;0;1;1',
        'keyTimes':'0;.18;.25;.34;.45;.64;.75;.84;1',
        'dur':f'{cycle:g}s','repeatCount':'indefinite'
    })
    static.insert(0,photo_timeline)
    dot_group,num=make_pixel_group(im,theme,cycle,density=density)
    group.append(dot_group)
    # Keep existing colour scheme and profile content, only update photo captions.
    for text in root.iter(q('text')):
        if text.text=='COLOR-QUANTIZED VECTOR PORTRAIT':
            text.text='ANIMATED PORTRAIT / PIXEL MORPH'
        elif text.text=='Rendered entirely with SVG path data':
            text.text='Portrait  →  pixels  →  HK  →  portrait'
    label = root.get('aria-label','Developer profile')
    label = label.split('; animated portrait morphs into HK')[0]
    root.set('aria-label', label+'; animated portrait morphs into HK')
    path.write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True))
    return num


def main():
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--directory',type=Path,default=ROOT,help='Folder containing dark.svg and light.svg')
    p.add_argument('--cycle',type=float,default=15.0,help='Animation loop length in seconds (default: 15)')
    p.add_argument('--density',type=int,choices=(2,3,4,5),default=3,
                   help='Pixel grid size: 2=high detail, 3=balanced, 4=smaller files (default: 3)')
    args=p.parse_args()
    for name in ('dark.svg','light.svg'):
        path=args.directory/name
        count=animate_profile(path,cycle=args.cycle,density=args.density)
        print(f'{name}: {count} animated pixels; {path.stat().st_size/1024:.1f} KiB')


if __name__=='__main__':
    main()
