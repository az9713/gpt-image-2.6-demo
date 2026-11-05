"""User-authorized Image 2.6 experiment. Secrets are read from the environment only.

Sequential, no retries, persisted requests/responses, usage-priced ledger, conservative
pre-request reserves. An allowance is not a provider-enforced per-request price cap.
"""
from __future__ import annotations
import argparse, base64, csv, hashlib, html, io, json, os, sys, time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import httpx
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'image_26_experiment'
CAP = Decimal('4.00')
FLARE = 'gpt-image-2.6-flare'
SUN = 'gpt-image-2.6-sunburst'
BASE = ('Create a polished 3D product photograph for the fictional brand NIGHT LAB. '
        'Fixed front three-quarter camera. Two identical ivory ceramic coffee mugs sit well apart '
        'on a dark walnut laboratory desk, left mug at 28 percent of image width, right mug at 72 percent. '
        'Both mugs have a clearly printed teal owl emblem above the exact words NIGHT LAB; handles face right. '
        'Between the mugs is a small rounded teal owl mascot with amber eyes, cream belly and tiny round spectacles. '
        'A brass desk lamp is at the far right; a closed notebook lies behind the mugs. '
        'Warm studio lighting, dark navy background, premium realistic ceramic reflections, clean balanced layout. '
        'Both mugs must be completely visible with clear space around them. No other text, no watermark.')
INFO = ('Design a precise dark-mode infographic titled NIGHT LAB PIPELINE. '
        'Exactly six equal rectangular boxes arranged in two rows of three. '
        'Top row left to right: OBSERVE, ASK, TEST. Bottom row left to right: RECORD, REVIEW, SHARE. '
        'Exactly five arrows: OBSERVE to ASK; ASK to TEST; TEST vertically down then left to RECORD; '
        'RECORD to REVIEW; REVIEW to SHARE. Route the TEST-to-RECORD connector outside the boxes. '
        'Boxes 1 and 4 teal, boxes 2 and 5 amber, boxes 3 and 6 cream. '
        'Each box contains its exact uppercase label and one small matching line icon. '
        'A small owl emblem centered above the title. No extra boxes, arrows, labels, numbers or decorative text. '
        'Legible white type, dark navy background, disciplined grid, crisp professional typography.')
MARKUP_PROMPT = ('Recolor only the left mug ceramic body cobalt blue. Preserve its NIGHT LAB logo, '
                 'handle shape, reflections, the other mug, the owl mascot, lamp, notebook and background. '
                 'Remove any red annotation circle from the finished photograph. Change nothing else.')

def job(i, name, model=SUN, quality='medium', complexity='low', prompt=BASE,
        source=None, fmt='png', reserve='.25', **extra):
    return dict(id=f'{i:02d}', name=name, endpoint='edits' if source else 'generations',
                settings=dict(model=model, quality=quality, complexity=complexity,
                              size='1024x1024', output_format=fmt, n=1, **extra),
                prompt=prompt, source=source, reserve_usd=reserve)

JOBS = [
    job(1,'speed-flare-low',FLARE,'low',reserve='.10'),
    job(2,'speed-sunburst-low',SUN,'low',reserve='.10'),
    *[job(i,'quality-'+q,SUN,q,reserve=r) for i,q,r in
      [(3,'medium','.15'),(4,'high','.15'),(5,'xhigh','.25'),(6,'max','.50')]],
    *[job(i,'complexity-'+c,SUN,'high',c,INFO,reserve='.20') for i,c in
      [(7,'low'),(8,'medium'),(9,'high')]],
    job(10,'consistency-recolor',prompt='Change only the left mug ceramic body to deep teal. '
        'Preserve both NIGHT LAB logos, the owl, mug shapes, reflections and all scene objects.',source='03'),
    job(11,'consistency-lighting',prompt='Change only the lighting to cool blue evening light. '
        'Preserve the teal left mug, ivory right mug, both NIGHT LAB logos, owl identity, all objects and camera.',source='10'),
    job(12,'consistency-background',prompt='Replace only the background wall with a softly blurred starry observatory window. '
        'Preserve the desk, teal left mug, ivory right mug, NIGHT LAB logos, owl identity, lamp and notebook.',source='11'),
    job(13,'professional-product',FLARE,'high',prompt='Premium NIGHT LAB coffee mug advertisement. '
        'One ivory ceramic mug with teal owl emblem and exact NIGHT LAB wordmark, dark navy seamless studio background, '
        'amber rim light and physically realistic ceramic. Product left, generous negative space right. '
        'Exact headline at right: IDEAS AFTER DARK. Small exact subheading: NIGHT LAB. No other text.',reserve='.20'),
    job(14,'professional-poster',SUN,'high','high',prompt='Create a polished dark navy event poster. '
        'Exact hierarchy: large NIGHT LAB; below it IDEAS AFTER DARK; then NOVEMBER 2026; '
        'then OBSERVE. QUESTION. BUILD. A large elegant teal and amber owl illustration occupies lower half. '
        'Precise typography, generous margins, modern editorial layout. No extra text or logos.',reserve='.20'),
    job(15,'sketch-to-mascot',prompt='Use the supplied rough owl sketch as the design reference. '
        'Create one polished full-body 3D mascot: rounded teal owl, amber eyes, cream belly, tiny round brass spectacles. '
        'Preserve the sketched silhouette and wing positions. Centered front view on a plain dark navy background. '
        'Friendly premium toy render, no text.',source='inputs/owl-sketch.png'),
    job(16,'mascot-sprite-sheet',prompt='Use the input owl as the exact character reference. '
        'Create a single animation sprite sheet with EXACTLY six frames in a precise 3-column by 2-row grid, '
        'read left to right then top to bottom. All panels equal size, no gutters, no borders. '
        'The same centered full-body teal owl gently raises its right wing in greeting, blinks, lowers wing, '
        'and returns toward the original pose. Fixed camera, consistent scale, spectacles and colors, '
        'plain identical dark navy background. No text or frame labels.',source='15',reserve='.30'),
    job(17,'markup-control-prompt-only',FLARE,prompt=MARKUP_PROMPT,source='03'),
    job(18,'markup-overlay-edit',FLARE,prompt=MARKUP_PROMPT,source='03',markup='inputs/mug-markup.png'),
    job(19,'svg-flare',FLARE,'low',fmt='svg',reserve='.75',prompt='A clean editable vector logo for NIGHT LAB. '
        'Simple geometric teal owl with amber circular eyes above the exact uppercase words NIGHT LAB. '
        'Cream accents, compact centered composition. Flat vector shapes, no gradients, no shadows, no photographic texture.'),
    job(20,'svg-sunburst',SUN,'low',fmt='svg',reserve='.75',prompt='A clean editable vector logo for NIGHT LAB. '
        'Simple geometric teal owl with amber circular eyes above the exact uppercase words NIGHT LAB. '
        'Cream accents, compact centered composition. Flat vector shapes, no gradients, no shadows, no photographic texture.'),
    job(21,'gif-flare-owl',FLARE,'low',fmt='gif',reserve='.75',frame_count=6,frame_duration_ms=200,
        prompt='A seamless looping animation of one adorable rounded teal owl with amber eyes, cream belly and '
        'tiny brass spectacles. Front view, fixed camera and scale, dark navy background. '
        'The owl blinks once and gently waves its right wing, returning to its starting pose. No text.'),
    job(22,'gif-sunburst-product',SUN,'low',fmt='gif',reserve='.75',frame_count=6,frame_duration_ms=200,
        prompt='Seamless looping product animation. One ivory ceramic mug with a simple teal owl emblem and '
        'the exact words NIGHT LAB sits on a walnut desk. Delicate steam curls upward in a small continuous motion. '
        'The mug and camera stay absolutely still. Dark navy backdrop, warm amber light. No additional text.'),
]
JOBS[15]['settings']['size']='1536x1024'
JOBS[20]['settings']['size']='512x512'
JOBS[21]['settings']['size']='512x512'
for svg_job in JOBS[18:20]:
    svg_job['settings']['svg']={'model':'gpt-6-luna','reasoning':{'effort':'low'}}

def write_json(path, data):
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')

def init():
    for folder in ['inputs','outputs','requests','responses','logs','derived','docs']:
        (OUT/folder).mkdir(parents=True,exist_ok=True)
    write_json(OUT/'manifest.json',dict(budget_usd=str(CAP),jobs=JOBS,
        notes=['Costs are calculated from returned usage and published rates; not an invoice.',
               'Sequential requests; no retries. Uncertain-charge errors block further spending.',
               'A pre-request reserve is a local guard, not a server-enforced price ceiling.',
               'All comparisons are single trials with stochastic variation; no seed control.',
               'Markup pair starts independently from output 03. Only request difference is markup.',
               'Speed and quality baselines have identical prompt, size and complexity.']))
    write_json(OUT/'pricing.json',dict(source='https://developers.openai.com/api/docs/pricing',
        image_rates_per_million=dict(text_input=5,image_input=8,image_output=30),
        svg_author_rates_per_million={'gpt-6-luna':[.10,.50],'gpt-6.1-terra':[1,5],
          'gpt-6.1-sol':[2,10],'gpt-6-astra':[10,50],'gpt-5.4-mini':[.75,4.5]},
        calculator_1024_square_output_usd={'low':.02469,'medium':.04347,'high':.05268,'xhigh':.09366,'max':.21072}))
    for j in JOBS:
        (OUT/'requests'/f"{j['id']}-{j['name']}.prompt.txt").write_text(j['prompt'],encoding='utf-8')
    sketch=OUT/'inputs/owl-sketch.png'
    if not sketch.exists():
        im=Image.new('RGB',(1024,1024),'white'); d=ImageDraw.Draw(im)
        d.ellipse((260,210,760,850),outline='black',width=10)
        d.polygon([(280,300),(270,130),(410,250)],outline='black',width=9)
        d.polygon([(615,250),(760,130),(740,320)],outline='black',width=9)
        for x in [395,625]:
            d.ellipse((x-90,320,x+90,500),outline='black',width=8)
            d.ellipse((x-14,385,x+14,420),fill='black')
        d.line((485,400,535,400),fill='black',width=8)
        d.polygon([(480,500),(545,500),(513,552)],outline='black',width=7)
        d.arc((280,500,470,760),70,250,fill='black',width=9)
        d.arc((550,500,740,760),-70,110,fill='black',width=9)
        d.ellipse((370,610,650,790),outline='black',width=6)
        im.save(sketch)
    report()

def ledger():
    p=OUT/'ledger.jsonl'
    return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines()] if p.exists() else []

def artifact(source):
    if '/' in source: return OUT/source
    records=[r for r in ledger() if r['id']==source and r['status']=='success']
    if not records: raise RuntimeError('Source output is not ready: '+source)
    return OUT/records[-1]['artifact']

def cost(data):
    u=data.get('usage')
    if not u: return None,{'reason':'Response did not include usage; billing reconciliation required.'}
    detail=u.get('input_tokens_details') or {}
    if not all(k in detail for k in ['text_tokens','image_tokens']):
        return None,{'reason':'Missing input token breakdown.'}
    parts=dict(text_input=Decimal(detail['text_tokens'])*5/1000000,
               image_input=Decimal(detail['image_tokens'])*8/1000000,
               image_output=Decimal(u['output_tokens'])*30/1000000)
    su=data.get('svg_usage')
    if su:
        rates=json.loads((OUT/'pricing.json').read_text())['svg_author_rates_per_million']
        model=su['model']; match=next((k for k in rates if model==k or model.startswith(k+'-')),None)
        if not match:return None,{'reason':'Unpriced SVG author: '+model,'image_cost_usd':str(sum(parts.values()))}
        ri,ro=map(Decimal,map(str,rates[match]))
        parts['svg_author']=(Decimal(su['input_tokens'])*ri+Decimal(su['output_tokens'])*ro)/1000000
    return sum(parts.values()),{k:str(v) for k,v in parts.items()}

def run(j,retry_rejected=False):
    records=ledger()
    previous=[r for r in records if r['id']==j['id']]
    if previous and not (retry_rejected and all(r['status']=='rejected_unbilled' for r in previous)):
        print(json.dumps({'id':j['id'],'skip':'already attempted','status':previous[-1]['status']}),flush=True);return
    if any(r['status'] not in ('success','rejected_unbilled') or r.get('cost_usd') is None for r in records):
        raise RuntimeError('Unreconciled request in ledger. Stop before another paid call.')
    spent=sum((Decimal(r['cost_usd']) for r in records),Decimal(0))
    if spent+Decimal(j['reserve_usd'])>CAP:
        raise RuntimeError(f'Budget reserve guard: spent {spent}; next reserve {j["reserve_usd"]}; cap {CAP}')
    p=dict(j['settings'],prompt=j['prompt']); markup=p.pop('markup',None)
    source=artifact(j['source']) if j['source'] else None
    if markup and not (OUT/markup).is_file():raise RuntimeError('Markup overlay has not been prepared.')
    req=dict(endpoint='https://api.openai.com/v1/images/'+j['endpoint'],parameters=p,
             input_file=str(source.relative_to(OUT)) if source else None,markup_file=markup,
             input_sha256=hashlib.sha256(source.read_bytes()).hexdigest() if source else None,
             markup_sha256=hashlib.sha256((OUT/markup).read_bytes()).hexdigest() if markup else None,
             spend_before_usd=str(spent),reserved_usd=j['reserve_usd'])
    stem=j['id']+'-'+j['name']
    attempt_stem=stem+(f'-attempt-{len(previous)+1:02d}' if previous else '')
    write_json(OUT/'requests'/f'{attempt_stem}.json',req)
    start=datetime.now(timezone.utc).isoformat();tick=time.perf_counter()
    rec=dict(id=j['id'],name=j['name'],started_utc=start,model=p['model'],quality=p['quality'],
             complexity=p['complexity'],format=p['output_format'],status='unknown',cost_usd=None,
             attempt=len(previous)+1,request_file=f'requests/{attempt_stem}.json',response_file=f'responses/{attempt_stem}.json')
    print(json.dumps({'id':j['id'],'starting':j['name'],'spent_usd':str(spent)}),flush=True)
    try:
        with httpx.Client(timeout=httpx.Timeout(600,connect=30),follow_redirects=False) as client:
            headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY']}
            if source:
                with source.open('rb') as f:
                    files={'image':(source.name,f,'image/png')}
                    if markup: files['markup']=((OUT/markup).name,(OUT/markup).read_bytes(),'image/png')
                    resp=client.post(req['endpoint'],headers=headers,data={k:str(v) for k,v in p.items()},files=files)
            else:
                resp=client.post(req['endpoint'],headers=headers,json=p)
        rec.update(elapsed_seconds=round(time.perf_counter()-tick,3),http_status=resp.status_code,
                   request_id=None,completed_utc=datetime.now(timezone.utc).isoformat())
        try:data=resp.json()
        except ValueError:data={'error':{'message':'Non-JSON response','body_bytes':len(resp.content)}}
        # Persist before decoding/validation so an artifact error never hides billing evidence.
        metadata=json.loads(json.dumps(data))
        for item in metadata.get('data',[]):
            if item.get('b64_json'): item['b64_json']='[image bytes saved separately]'
        write_json(OUT/'responses'/f'{attempt_stem}.json',dict(response_headers={k:v for k,v in resp.headers.items()
                   if k.lower() in ['openai-processing-ms','openai-model','content-type']},body=metadata))
        if resp.status_code>=400:
            rec['status']='rejected_unbilled' if resp.status_code in [400,401,403,404,422,429] else 'uncertain_error'
            rec['cost_usd']='0' if rec['status']=='rejected_unbilled' else None
            rec['error']=data.get('error',{})
        else:
            images=data.get('data',[])
            if len(images)!=1 or not images[0].get('b64_json'):raise RuntimeError('Expected one base64 artifact.')
            blob=base64.b64decode(images[0]['b64_json'],validate=True)
            dest=OUT/'outputs'/f'{stem}.{p["output_format"]}';dest.write_bytes(blob)
            data['data'][0]['b64_json']='[decoded into '+dest.name+']'
            rec.update(status='success',artifact=str(dest.relative_to(OUT)).replace('\\','/'),
                       sha256=hashlib.sha256(blob).hexdigest(),bytes=len(blob),usage=data.get('usage'),svg_usage=data.get('svg_usage'))
            value,parts=cost(data);rec.update(cost_usd=str(value) if value is not None else None,cost_breakdown=parts)
            if p['output_format']!='svg':
                with Image.open(dest) as im:rec.update(dimensions=list(im.size),frame_count=getattr(im,'n_frames',1))
            else:
                import xml.etree.ElementTree as ET
                root=ET.fromstring(blob);rec['svg_elements']=len(list(root.iter()))
                rec['svg_raster_images']=sum(1 for n in root.iter() if n.tag.split('}')[-1]=='image')
        write_json(OUT/'responses'/f'{attempt_stem}.json',dict(response_headers={k:v for k,v in resp.headers.items()
                   if k.lower() in ['openai-processing-ms','openai-model','content-type']},body=data))
    except Exception as e:
        rec.update(status='uncertain_error',elapsed_seconds=round(time.perf_counter()-tick,3),
                   error={'type':type(e).__name__,'message':'Request or artifact handling failed. Inspect saved response; do not retry automatically.'})
    with (OUT/'ledger.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(rec,ensure_ascii=False)+'\n')
    report()
    print(json.dumps(rec),flush=True)
    if rec['status']!='success' or rec['cost_usd'] is None:raise RuntimeError('Stopped for inspection; no automatic retry.')
    if sum(Decimal(r['cost_usd']) for r in ledger())>CAP:raise RuntimeError('Spending cap reached; stop.')

def report():
    rows=ledger(); spent=sum((Decimal(r['cost_usd']) for r in rows if r.get('cost_usd') is not None),Decimal(0))
    summary=dict(limit_usd=str(CAP),usage_priced_cost_usd=str(spent),remaining_under_limit_usd=str(CAP-spent),
       successful_outputs=sum(r['status']=='success' for r in rows),attempted_requests=len(rows),
       invoice_reconciled=False,unknown_cost_requests=[r['id'] for r in rows if r.get('cost_usd') is None])
    write_json(OUT/'summary.json',summary)
    fields=['id','name','status','model','quality','complexity','format','elapsed_seconds','cost_usd','artifact']
    with (OUT/'comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    cards=[]
    for j in JOBS:
        r=next((x for x in reversed(rows) if x['id']==j['id']),None)
        media=f'<img loading="lazy" src="{r["artifact"]}" alt="{html.escape(j["name"])}">' if r and r.get('artifact') else '<div class="pending">Pending</div>'
        meta='Pending' if not r else f'{r["status"]} · {r.get("elapsed_seconds","?")} s · ${r.get("cost_usd","unknown")}'
        cards.append(f'<article><h2>{j["id"]} · {html.escape(j["name"])}</h2>{media}<p>{html.escape(meta)}</p>'
          f'<p>{html.escape(j["settings"]["model"])} · {j["settings"]["quality"]} quality · {j["settings"]["complexity"]} complexity</p>'
          f'<details><summary>Prompt and settings</summary><pre>{html.escape(j["prompt"])}</pre><pre>{html.escape(json.dumps(j["settings"],indent=2))}</pre></details></article>')
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Image 2.6 · Night Lab</title>'
    page+='<style>body{margin:32px;background:#0b101a;color:#e6e9ee;font:16px system-ui}a{color:#6fe0cb}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:22px}article{background:#151e2c;padding:18px;border-radius:12px}h2{font-size:18px}img{width:100%;aspect-ratio:1;object-fit:contain;background:#09111c}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}p{color:#b8c5d3}.pending{padding:70px;text-align:center;color:#7d8ca2}</style>'
    page+=f'<h1>Night Lab · Image 2.6 experiments</h1><p>{summary["successful_outputs"]}/22 outputs · usage-priced cost ${spent:.6f} · limit $4.00. Costs computed from returned tokens; invoice reconciliation pending.</p>'
    page+='<p><a href="comparison.csv">Comparison CSV</a> · <a href="manifest.json">Full manifest</a> · <a href="ledger.jsonl">Detailed ledger</a> · <a href="../EXPERIMENT_README.md">Experiment notes</a></p>'
    page+='<p><a href="derived/markup-comparison.html">Markup comparison and slider</a> · <a href="derived/svg-comparison.html">SVG scale and recoloring</a> · <a href="derived/sprite-sheet-loop.gif">Locally assembled sprite GIF</a> · <a href="FINDINGS.md">Findings</a></p>'
    page+='<div class="grid">'+''.join(cards)+'</div></html>'
    (OUT/'index.html').write_text(page,encoding='utf-8')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--init',action='store_true');ap.add_argument('--ids');ap.add_argument('--retry-rejected',action='store_true');args=ap.parse_args()
    if args.init:init()
    if args.ids:
        for selected in args.ids.split(','):
            run(next(j for j in JOBS if j['id']==selected.zfill(2)),retry_rejected=args.retry_rejected)
