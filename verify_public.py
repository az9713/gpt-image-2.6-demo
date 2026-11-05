"""Offline public-export checks. No network access and no API credentials needed."""
from pathlib import Path
from decimal import Decimal
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import collections, hashlib, json, re
from PIL import Image
import experiment as e

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'image_26_experiment'
records=e.ledger();success=[r for r in records if r['status']=='success']
assert len(success)==22 and len({r['id'] for r in success})==22
assert len(records)==23
assert collections.Counter(r['format'] for r in success)=={'png':18,'svg':2,'gif':2}
total=sum(Decimal(r['cost_usd']) for r in records)
assert total==Decimal('1.1632870') and total<Decimal('4.00')
for r in success:
    artifact=DATA/r['artifact'];assert artifact.is_file()
    assert hashlib.sha256(artifact.read_bytes()).hexdigest()==r['sha256']
    stem=r['id']+'-'+r['name']
    response=DATA/r.get('response_file',f'responses/{stem}.json')
    amount,_=e.cost(json.loads(response.read_text(encoding='utf-8'))['body'])
    assert amount==Decimal(r['cost_usd'])
    if r['format']!='svg':
        with Image.open(artifact) as image:
            assert not image.getexif()
            if r['format']=='gif':
                assert image.n_frames==6 and image.info['loop']==0
                for i in range(6):image.seek(i);assert image.info['duration']==200

a,b=[json.loads((DATA/f'requests/{s}.json').read_text(encoding='utf-8')) for s in
     ['17-markup-control-prompt-only','18-markup-overlay-edit']]
assert a['parameters']==b['parameters'] and a['input_sha256']==b['input_sha256'] and b['markup_sha256']

class Refs(HTMLParser):
    def __init__(self):super().__init__();self.refs=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if attrs.get('id'):self.ids.append(attrs['id'])
        for key in ['src','href']:
            if attrs.get(key):self.refs.append(attrs[key])
broken=[]
for p in ROOT.rglob('*.html'):
    parser=Refs();parser.feed(p.read_text(encoding='utf-8'))
    assert len(parser.ids)==len(set(parser.ids)),f'Duplicate HTML IDs: {p.name}'
    for ref in parser.refs:
        url=urlsplit(ref)
        if url.scheme or not url.path:continue
        if not (p.parent/unquote(url.path)).resolve().is_file():broken.append((str(p.relative_to(ROOT)),ref))
assert not broken,broken

for path in ROOT.rglob('*'):
    if not path.is_file() or '.git' in path.parts or '__pycache__' in path.parts:continue
    if path.suffix.lower() not in ['.json','.jsonl','.csv','.txt','.md','.html','.css','.js','.py','.svg']:continue
    content=path.read_text(encoding='utf-8-sig')
    # The rules are split to avoid matching their own definitions.
    forbidden=[r'(?i)[A-Z]:[/\\]'+'Users'+r'[/\\]',r'(?i)/'+'Users/',
               'req'+r'_[a-f0-9]{20,}', 'sk'+r'-(?:proj-)?[A-Za-z0-9_-]{20,}',
               'gh'+r'[opusr]_[A-Za-z0-9]{25,}']
    assert not any(re.search(rule,content) for rule in forbidden),f'Private metadata pattern in {path.relative_to(ROOT)}'
    if path.suffix in ['.json','.jsonl']:
        def check(value):
            if isinstance(value,dict):
                for key,item in value.items():
                    assert key not in ['request_id','x-request-id','organization_id','project_id','started_utc','completed_utc'],(path.name,key)
                    check(item)
            elif isinstance(value,list):
                for item in value:check(item)
        if path.suffix=='.json':check(json.loads(content))
        else:
            for line in content.splitlines():check(json.loads(line))

print(json.dumps({'successful_outputs':22,'attempts':23,'cost_usd':str(total),
                  'original_hashes':'verified','usage_costs':'verified',
                  'markup_control':'verified','GIF_structure':'verified',
                  'HTML_links':'verified','public_metadata':'verified'},indent=2))
