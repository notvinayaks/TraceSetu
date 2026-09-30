from pathlib import Path
import re, html, json, hashlib
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'research/method-review-20260929/TraceSetu_Forensic_Method_Research_Paper.md'
OUT=ROOT/'output/pdf/TraceSetu_Forensic_Method_Research_Paper.pdf'
TMP=Path(__file__).parent
result=json.loads((ROOT/'research/method-review-20260929/reference/results.json').read_text())
assert result['tests']['all_passed']
text=SOURCE.read_text(encoding='utf-8').replace('{{TEST_COUNT}}',str(result['tests']['run']))
SOURCE.write_text(text,encoding='utf-8')
for name,file in [('Body','calibri.ttf'),('BodyBold','calibrib.ttf'),('BodyItalic','calibrii.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
NAVY=HexColor('#1c3d60');INK=HexColor('#172534');MUTED=HexColor('#536373');LINE=HexColor('#c6d2dd')
width,height=A4
CW=width-100
styles={
 'body':ParagraphStyle('body',fontName='Body',fontSize=11,leading=14.2,spaceAfter=7,textColor=INK),
 'small':ParagraphStyle('small',fontName='Body',fontSize=10.25,leading=12.8,spaceAfter=7,textColor=INK),
 'h1':ParagraphStyle('h1',fontName='BodyBold',fontSize=24,leading=28,spaceAfter=12,textColor=NAVY),
 'h2':ParagraphStyle('h2',fontName='BodyBold',fontSize=15,leading=18,spaceBefore=7,spaceAfter=8,textColor=NAVY),
 'table':ParagraphStyle('table',fontName='Body',fontSize=10.1,leading=12.5,textColor=INK),
 'th':ParagraphStyle('th',fontName='BodyBold',fontSize=10.1,leading=12.5,textColor=white),
 'list':ParagraphStyle('list',fontName='Body',fontSize=11,leading=14.2,spaceAfter=7,leftIndent=12,firstLineIndent=-12,textColor=INK),
}

def markup(s):
    s=html.escape(s,quote=False)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',lambda m:f'<link href="{m[2]}" color="#245b88"><u>{m[1]}</u></link>',s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'`(.+?)`',r'<font name="Body">\1</font>',s)
    return s

class Example(Flowable):
    def __init__(self):super().__init__();self.width=CW;self.height=145
    def draw(self):
        c=self.canv
        def box(x,y,w,lines,dashed=False):
            c.setFillColor(HexColor('#f2f6f9'));c.setStrokeColor(NAVY);c.setLineWidth(0.8)
            if dashed:c.setDash(3,2)
            c.rect(x,y,w,40,fill=1,stroke=1);c.setDash()
            c.setFillColor(INK)
            for i,line in enumerate(lines):c.setFont('BodyBold' if i==0 else 'Body',10);c.drawCentredString(x+w/2,y+25-i*13,line)
        def arrow(x1,y1,x2,y2,label=None,lx=None,ly=None):
            import math
            c.setStrokeColor(NAVY);c.setFillColor(NAVY);c.setLineWidth(1.2);c.line(x1,y1,x2,y2)
            a=math.atan2(y2-y1,x2-x1)
            p=c.beginPath();p.moveTo(x2,y2);p.lineTo(x2-6*math.cos(a-.4),y2-6*math.sin(a-.4));p.lineTo(x2-6*math.cos(a+.4),y2-6*math.sin(a+.4));p.close();c.drawPath(p,fill=1,stroke=0)
            if label:c.setFont('Body',9.4);c.drawCentredString(lx,ly,label)
        box(0,20,101,['Reported S','customer unknown'])
        box(173,20,133,['Unlabelled D','deposit hypothesis'],True)
        box(379,20,116,['Known hot H','Exchange Alpha'])
        box(173,100,133,['Known gas feeder G','Exchange Alpha'])
        arrow(102,40,171,40,'token',137,49)
        arrow(307,40,377,40,'sweep',343,49)
        arrow(239.5,98,239.5,62,'fee top-up',285,78)
        c.setFont('BodyItalic',9);c.setFillColor(MUTED);c.drawString(0,3,'Fictional example. Arrows are transfers; they are not ownership proof.')

def algorithm():
    lines=[
        '1  Begin at the reported address/output within the chosen asset and window.',
        '2  Expand only successful, later ledger events. Keep distinct arrival states.',
        '3  Stop at a supported custodian; keep uncertain earlier candidates unresolved.',
        '4  Do not cross private service ledgers or unsupported protocol transitions.',
        '5  Return paths, sources, candidate roles, missing coverage and search limits.'
    ]
    cell=[Paragraph(markup(s),styles['small']) for s in lines]
    tab=Table([[cell]],colWidths=[CW]);tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),HexColor('#f2f6f9')),('BOX',(0,0),(-1,-1),0.5,LINE),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    return tab

def footer(c,doc):
    c.saveState();c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(50,height-37,width-50,height-37)
    c.setFillColor(MUTED);c.setFont('Body',9);c.drawString(50,height-28,'TRACESETU  /  FORENSIC METHOD REVIEW')
    c.drawRightString(width-50,height-28,'29 SEPTEMBER 2026')
    c.line(50,37,width-50,37);c.drawString(50,24,'Research proposal + synthetic reference; no measured live attribution accuracy')
    c.drawRightString(width-50,24,str(doc.page));c.restoreState()

story=[]
pages=text.split('<!-- pagebreak -->')
for pi,chunk in enumerate(pages):
    if pi:story.append(PageBreak())
    lines=chunk.strip().splitlines();i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line=='<!-- diagram:example -->':story+=[Example(),Spacer(1,6)];i+=1;continue
        if line=='<!-- algorithm -->':story+=[algorithm(),Spacer(1,8)];i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',x) for x in cells):rows.append(cells)
                i+=1
            widths=[CW*.31,CW*.69] if pi==6 else [CW*.37,CW*.63]
            data=[[Paragraph(markup(t),styles['th'] if ri==0 else styles['table']) for t in row] for ri,row in enumerate(rows)]
            table=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#f3f6f8')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.4,LINE),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7)]))
            if pi==6:table.setStyle(TableStyle([('TOPPADDING',(0,0),(-1,-1),4.5),('BOTTOMPADDING',(0,0),(-1,-1),4.5)]))
            story.extend([table,Spacer(1,10)]);continue
        if line.startswith('# '):style=styles['h1'];content=line[2:]
        elif line.startswith('## '):style=styles['h2'];content=line[3:]
        else:
            content=line
            while i+1<len(lines) and lines[i+1].strip() and not lines[i+1].startswith(('#','|','<!--')) and not re.match(r'^\d+\. ',lines[i+1]):
                i+=1;content+=' '+lines[i].strip()
            style=styles['small'] if pi==7 else styles['list'] if re.match(r'^\d+\. ',content) else styles['body']
        story.append(Paragraph(markup(content),style));i+=1

OUT.parent.mkdir(exist_ok=True,parents=True)
doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=50,leftMargin=50,topMargin=49,bottomMargin=49,title='TraceSetu: a concrete method for finding the first receiving VASP',author='Team ANANTHA',subject='Research review, proposed method and synthetic reference experiment')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
r=PdfReader(OUT)
manifest={'pdf':str(OUT),'pages':len(r.pages),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'reference_tests':result['tests']['run'],'word_count_markdown':len(text.split()),'page_text_lengths':[len(p.extract_text()) for p in r.pages],'link_annotations':sum(len(p.get('/Annots',[])) for p in r.pages)}
(TMP/'paper-build.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
