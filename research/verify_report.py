"""Structural and layout checks for the research PDF, plus visual QA sheets."""
import json
import re
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import pdfplumber
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent.parent
QA=ROOT/'tmp'/'pdfs'
PDF=ROOT/'output'/'pdf'/'VASP_Attribution_Research_and_Implementation_Report.pdf'
reader=PdfReader(PDF)
pages=[p.extract_text() for p in reader.pages]
raw=(ROOT/'research'/'report.md').read_text(encoding='utf-8')
sources=json.loads((ROOT/'research'/'sources.json').read_text(encoding='utf-8'))
citations=set()
for expr in re.findall(r'\[(S\d{2}[^\]]*)\]',raw):
    expr=re.sub(r'S(\d{2})-S?(\d{2})',lambda m: ','.join(f'S{n:02d}' for n in range(int(m[1]),int(m[2])+1)),expr)
    citations.update(re.findall(r'S\d{2}',expr))
source_ids={s['id'] for s in sources}
out_of_bounds=[]
with pdfplumber.open(PDF) as pdf:
    for i,p in enumerate(pdf.pages):
        for char in p.chars:
            if char['x0']<0 or char['x1']>p.width+.2 or char['top']<0 or char['bottom']>p.height+.2:
                out_of_bounds.append({'page':i+1,'text':char['text'],'box':[char['x0'],char['top'],char['x1'],char['bottom']]})
bad_glyphs=[i+1 for i,t in enumerate(pages) if '\ufffd' in t or '\u25a0' in t]
images=sorted(QA.glob('final-*.png'))
assert len(images)==len(pages),(len(images),len(pages))
font=ImageFont.truetype('C:/Windows/Fonts/calibri.ttf',18)
thumb_w=300
thumb_h=424
for k in range(0,len(images),9):
    batch=images[k:k+9]
    sheet=Image.new('RGB',(3*(thumb_w+20)+20,3*(thumb_h+34)+20),'#dce4e9')
    draw=ImageDraw.Draw(sheet)
    for j,path in enumerate(batch):
        im=Image.open(path).convert('RGB')
        im.thumbnail((thumb_w,thumb_h),Image.Resampling.LANCZOS)
        x=20+(j%3)*(thumb_w+20);y=20+(j//3)*(thumb_h+34)
        sheet.paste(im,(x,y))
        draw.text((x,y+thumb_h+4),f'Page {k+j+1:02d}',font=font,fill='#112b42')
    sheet.save(QA/f'contact-{k//9+1:02d}.jpg',quality=92)
result={
    'pages':len(pages),'rendered_pages':len(images),
    'all_pages_have_text':all(len(x)>100 for x in pages),
    'source_ids':len(source_ids),'source_ids_cited':len(citations),
    'missing_sources':sorted(citations-source_ids),'uncited_sources':sorted(source_ids-citations),
    'link_annotations':sum(len(p.get('/Annots',[])) for p in reader.pages),
    'out_of_page_characters':out_of_bounds,'missing_glyph_pages':bad_glyphs,
    'outline_entries':len(reader.outline),'contact_sheets':len(list(QA.glob('contact-*.jpg'))),
    'visual_review':'Contact sheets and selected full-page renders must be reviewed after these automated checks.'
}
(QA/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
assert not out_of_bounds and not bad_glyphs and not (citations-source_ids)
assert len(pages)==50 and len(source_ids)==44
