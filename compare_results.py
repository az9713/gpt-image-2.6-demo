"""Offline comparisons and frame extraction. Makes no API calls."""
import json, html, collections, xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import experiment as e

ROOT=e.OUT
try:FONT=ImageFont.truetype('DejaVuSans.ttf',16)
except OSError:FONT=ImageFont.load_default()

def contact(records,path,columns=3,tile=384):
    ims=[]
    for r in records:
        if not r.get('artifact') or r['format']=='svg':continue
        with Image.open(ROOT/r['artifact']) as src:
            im=src.convert('RGB');im.thumbnail((tile,tile))
        cell=Image.new('RGB',(tile,tile+70),'#101a29');cell.paste(im,((tile-im.width)//2,0))
        d=ImageDraw.Draw(cell)
        d.text((8,tile+5),r['id']+' '+r['name'],font=FONT,fill='white')
        d.text((8,tile+30),f"{r['elapsed_seconds']:.2f}s | ${float(r['cost_usd']):.5f}",font=FONT,fill='#8ce3d5')
        ims.append(cell)
    if not ims:return
    rows=(len(ims)+columns-1)//columns
    result=Image.new('RGB',(columns*tile,rows*(tile+70)),'#09111d')
    for n,im in enumerate(ims):result.paste(im,((n%columns)*tile,(n//columns)*(tile+70)))
    result.save(ROOT/'derived'/path)

def run():
    records=[r for r in e.ledger() if r['status']=='success']
    contact(records,'contact-sheet.jpg',4,320)
    for name,ids in [('quality-comparison.jpg',['02','03','04','05','06']),
                     ('complexity-comparison.jpg',['07','08','09']),
                     ('consistency-comparison.jpg',['03','10','11','12']),
                     ('markup-comparison.jpg',['03','17','18'])]:
        selected=[r for i in ids for r in records if r['id']==i]
        contact(selected,name,3 if name!='consistency-comparison.jpg' else 4,512)
    sprite=next((r for r in records if r['id']=='16'),None)
    if sprite:
        im=Image.open(ROOT/sprite['artifact']).convert('RGB');w,h=im.size
        frames=[im.crop((c*w//3,r*h//2,(c+1)*w//3,(r+1)*h//2)) for r in range(2) for c in range(3)]
        folder=ROOT/'derived/sprite-frames';folder.mkdir(exist_ok=True)
        for i,f in enumerate(frames):f.save(folder/f'frame-{i+1:02d}.png')
        frames[0].save(ROOT/'derived/sprite-sheet-loop.gif',save_all=True,append_images=frames[1:],duration=200,loop=0)
        e.write_json(ROOT/'derived/sprite-extraction.json',dict(source=sprite['artifact'],grid=[3,2],
            frame_size=list(frames[0].size),frame_count=6,duration_ms=200,loop=0,
            note='Fixed-grid extraction, not motion stabilization; registration errors remain visible.'))
    gif_info=[]
    for r in records:
        if r['format']!='gif':continue
        folder=ROOT/'derived'/f"{r['id']}-gif-frames";folder.mkdir(exist_ok=True)
        with Image.open(ROOT/r['artifact']) as im:
            durations=[]
            for i,f in enumerate(ImageSequence.Iterator(im)):
                durations.append(f.info.get('duration'));f.convert('RGBA').save(folder/f'frame-{i+1:02d}.png')
            gif_info.append(dict(id=r['id'],size=list(im.size),frame_count=im.n_frames,
                                 frame_durations_ms=durations,loop=im.info.get('loop')))
    e.write_json(ROOT/'derived/gif-inspection.json',gif_info)
    if all(any(r['id']==i for r in records) for i in ['03','17','18']):
        paths=[('Source image','../outputs/03-quality-medium.png'),
               ('Annotated preview (not sent flattened)','markup-annotated-preview.png'),
               ('Prompt only','../outputs/17-markup-control-prompt-only.png'),
               ('Prompt plus separate markup','../outputs/18-markup-overlay-edit.png')]
        markup_page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Markup controlled comparison</title>'
        markup_page+='<style>body{margin:28px;background:#0b1320;color:#e4e8ef;font:16px system-ui}.grid{display:grid;grid-template-columns:repeat(2,minmax(200px,1fr));gap:20px}img{width:100%}.slider{position:relative;max-width:850px}.slider img{display:block}.slider .after{position:absolute;inset:0;clip-path:inset(0 50% 0 0)}input{width:min(850px,100%)}a{color:#80dfd1}</style>'
        markup_page+='<h1>Markup: controlled two-request comparison</h1><p>Both edits independently start from source 03. Prompt, model, quality and complexity are identical. Only one request includes the transparent PNG annotation overlay.</p>'
        markup_page+='<div class="grid">'+''.join(f'<section><h2>{label}</h2><img src="{path}"></section>' for label,path in paths)+'</div>'
        markup_page+='<h2>Slide to compare: markup edit versus prompt-only control</h2><p>Left: markup edit. Right: prompt-only edit.</p><div class="slider"><img src="../outputs/17-markup-control-prompt-only.png"><img class="after" id="after" src="../outputs/18-markup-overlay-edit.png"></div>'
        markup_page+='<input aria-label="Reveal markup edit" type="range" min="0" max="100" value="50" oninput="document.getElementById(\'after\').style.clipPath=\'inset(0 \'+(100-this.value)+\'% 0 0)\'"><p><a href="../index.html">All experiments</a></p></html>'
        (ROOT/'derived/markup-comparison.html').write_text(markup_page,encoding='utf-8')
    svg_info=[];sections=[]
    for r in records:
        if r['format']!='svg':continue
        p=ROOT/r['artifact'];root=ET.parse(p).getroot()
        fills=collections.Counter(n.get('fill') for n in root.iter() if n.get('fill') not in [None,'none','white','#fff','#ffffff'])
        teal=[]
        for color in fills:
            if color.startswith('#') and len(color)==7:
                red,green,blue=[int(color[i:i+2],16) for i in (1,3,5)]
                if green>red*1.25 and blue>red*1.25:teal.append(color)
        chosen=teal[0] if teal else next(iter(fills.most_common(1)),(None,))[0]
        changed=0
        if chosen:
            for node in root.iter():
                if node.get('fill')==chosen:node.set('fill','#d36eff');changed+=1
        target=ROOT/'derived'/f'{p.stem}-recolored.svg';ET.ElementTree(root).write(target,encoding='utf-8',xml_declaration=True)
        circle=next((n for n in root.iter() if n.tag.split('}')[-1]=='circle' and n.get('r')),None)
        geometry=None
        if circle is not None:
            old=circle.get('r');new=str(round(float(old)*1.15,3));circle.set('r',new)
            geometry=dict(element='circle',attribute='r',before=old,after=new)
        shape_target=ROOT/'derived'/f'{p.stem}-shape-edited.svg'
        ET.ElementTree(root).write(shape_target,encoding='utf-8',xml_declaration=True)
        svg_info.append(dict(id=r['id'],vector_elements=r.get('svg_elements'),raster_images=r.get('svg_raster_images'),
            viewBox=root.get('viewBox'),original_fill_changed=chosen,replacement_fill='#d36eff',elements_recolored=changed,geometry_edit=geometry))
        sections.append(f'<section><h2>{html.escape(r["name"])}</h2><p>Original at 32, 128 and 512 CSS pixels</p>'+
            ''.join(f'<img src="../{r["artifact"]}" width="{size}" height="{size}">' for size in [32,128,512])+
            f'<p>Locally recolored version ({changed} elements)</p><img src="{target.name}" width="512" height="512">'+
            f'<p>Recolored plus one edited circle radius: {html.escape(str(geometry))}</p><img src="{shape_target.name}" width="512" height="512"></section>')
    e.write_json(ROOT/'derived/svg-inspection.json',svg_info)
    (ROOT/'derived/svg-comparison.html').write_text('<!doctype html><html><meta charset="utf-8"><title>SVG scale and recolor</title>'+
        '<style>body{background:#0c1320;color:#e5e8ed;font:16px system-ui;margin:30px}img{object-fit:contain;background:#15243a;margin:8px;vertical-align:middle}.light-preview img{background:#e5e1d5}section{padding:20px;border-bottom:1px solid #4a5467}button{padding:10px;background:#28425e;color:white;border:1px solid #7fa6bf}</style>'+
        '<h1>Native SVG output: scale and editable fills</h1><button onclick="document.body.classList.toggle(\'light-preview\')">Toggle light/dark artwork background</button>'+''.join(sections)+'</html>',encoding='utf-8')
    e.report()
    print(json.dumps({'outputs':len(records),'derived_contact_sheets':True,'native_gifs':gif_info,'native_svgs':svg_info}))

if __name__=='__main__':run()
