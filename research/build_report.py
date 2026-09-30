"""Build the research deliverable. No blockchain application is implemented here."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle, Preformatted

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "pdf"
QA = ROOT / "tmp" / "pdfs"
OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
PDF = OUT / "VASP_Attribution_Research_and_Implementation_Report.pdf"
SOURCES = json.loads((ROOT / "research" / "sources.json").read_text(encoding="utf-8"))
RAW = (ROOT / "research" / "report.md").read_text(encoding="utf-8")
DATE = "24 September 2026"
W, H = A4
M = 47
CW = W - 2 * M
NAVY = colors.HexColor("#112B42")
INK = colors.HexColor("#23394B")
TEAL = colors.HexColor("#087E83")
MUTED = colors.HexColor("#5A6E7E")
LIGHT = colors.HexColor("#EEF5F6")
LINE = colors.HexColor("#D5E0E5")
GOLD = colors.HexColor("#DBA349")

for name, file in [("Body", "calibri.ttf"), ("Bold", "calibrib.ttf"),
                   ("Italic", "calibrii.ttf"), ("Light", "calibril.ttf"),
                   ("Mono", "consola.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(Path("C:/Windows/Fonts") / file)))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Bold", italic="Italic", boldItalic="Bold")

def inline(t):
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r'<font name="Mono">\1</font>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    def cites(m):
        inner = m.group(1)
        inner = re.sub(r"S(\d{2})-S?(\d{2})", lambda r: ", ".join(f"S{v:02d}" for v in range(int(r[1]), int(r[2])+1)), inner)
        ids = re.findall(r"S\d{2}", inner)
        return '[' + ', '.join(f'<link href="#{s}" color="#087E83">{s}</link>' for s in ids) + ']'
    return re.sub(r"\[(S\d{2}[^\]]*)\]", cites, t)

def styles(scale=1.0):
    return {
        "body": ParagraphStyle("body", fontName="Body", fontSize=10.3*scale, leading=14.3*scale, textColor=INK, spaceAfter=7*scale, splitLongWords=True),
        "h2": ParagraphStyle("h2", fontName="Bold", fontSize=12*scale, leading=15*scale, textColor=TEAL, spaceBefore=5*scale, spaceAfter=6*scale),
        "bullet": ParagraphStyle("bullet", fontName="Body", fontSize=10.3*scale, leading=14.3*scale, textColor=INK, leftIndent=13, firstLineIndent=-13, spaceAfter=7*scale),
        "cell": ParagraphStyle("cell", fontName="Body", fontSize=9.15*scale, leading=12.0*scale, textColor=INK, splitLongWords=True),
        "head": ParagraphStyle("head", fontName="Bold", fontSize=9.0*scale, leading=11.5*scale, textColor=colors.white, splitLongWords=True),
        "quote": ParagraphStyle("quote", fontName="Bold", fontSize=10.2*scale, leading=14*scale, textColor=NAVY),
        "code": ParagraphStyle("code", fontName="Mono", fontSize=8.35*scale, leading=11.4*scale, textColor=INK),
    }

class Diagram(Flowable):
    def __init__(self, kind):
        Flowable.__init__(self)
        self.kind = kind
        self.width = CW
        self.height = 207 if kind == "trace" else 240

    def draw(self):
        c = self.canv
        def box(x,y,w,h,title,sub=None,fill=LIGHT,stroke=LINE):
            c.setFillColor(fill); c.setStrokeColor(stroke)
            c.roundRect(x,y,w,h,5,fill=1,stroke=1)
            c.setFillColor(NAVY); c.setFont("Bold",10)
            c.drawCentredString(x+w/2,y+h-(19 if sub else h/2+3),title)
            if sub:
                c.setFillColor(MUTED); c.setFont("Body",8.5)
                c.drawCentredString(x+w/2,y+12,sub)
        def arrow(x1,y1,x2,y2,dashed=False):
            c.setStrokeColor(TEAL if not dashed else MUTED); c.setLineWidth(1.4)
            if dashed: c.setDash(3,3)
            c.line(x1,y1,x2,y2)
            c.setDash()
            ang=math.atan2(y2-y1,x2-x1)
            p=c.beginPath(); p.moveTo(x2,y2)
            p.lineTo(x2-6*math.cos(ang-.45),y2-6*math.sin(ang-.45))
            p.lineTo(x2-6*math.cos(ang+.45),y2-6*math.sin(ang+.45));p.close()
            c.setFillColor(TEAL if not dashed else MUTED);c.drawPath(p,fill=1,stroke=0)
        if self.kind=="trace":
            box(0,80,112,48,"Wallet S","Incident seed")
            box(181,139,112,48,"Wallet A","Intermediary")
            box(377,139,124,48,"Exchange Beta","D2 | 2 hops")
            box(181,70,112,48,"Exchange Alpha","D1 | 1 hop")
            box(181,1,112,48,"Service U","Unresolved")
            arrow(112,117,181,161);arrow(293,163,377,163)
            arrow(112,104,181,95);arrow(112,90,181,25,True)
            c.setFont("Body",8.7);c.setFillColor(MUTED)
            c.drawString(125,149,"6,000")
            c.drawString(317,174,"5,800")
            c.drawString(125,107,"3,000")
            c.drawString(135,46,"500")
            c.setFont("Bold",8.4);c.setFillColor(TEAL)
            c.drawString(0,195,"SYNTHETIC EXAMPLE | TOKEN UNITS | GAS EXCLUDED")
            c.setFillColor(MUTED);c.setFont("Body",8.4)
            c.drawString(318,90,"500 retained at S")
            c.drawString(318,76,"200 retained at A")
            c.drawString(318,62,"No customer identity inferred")
        else:
            box(0,187,135,43,"Investigator workspace","Case / graph / evidence")
            box(181,187,140,43,"Gateway + case API","Identity / permissions")
            box(367,187,134,43,"SAHYOG boundary","Approved requests only")
            arrow(135,209,181,209);arrow(321,209,367,209)
            box(155,116,192,49,"Durable workflows + workers","Fetch / decode / attribute / trace")
            arrow(251,187,251,165)
            box(0,116,126,49,"Provider gateway","Quotas / scoped egress")
            arrow(155,140,126,140)
            box(0,49,126,42,"External sources","Chain facts / intelligence")
            arrow(62,116,62,91)
            box(166,30,142,50,"PostgreSQL","Authoritative records")
            arrow(239,116,239,80)
            box(359,116,142,49,"Evidence objects","Raw bytes / signed manifests")
            arrow(347,140,359,140)
            box(359,30,142,50,"Neo4j projection","Rebuildable case graph")
            arrow(308,55,359,55)
            c.setFillColor(MUTED);c.setFont("Body",8.4)
            c.drawCentredString(CW/2,15,"Private case data stays inside the application trust boundary.")
            c.drawCentredString(CW/2,3,"Provider assertions are evidence inputs; dispatch requires a separate approval.")

def table_widths(headers):
    n=len(headers)
    if n==2: return [CW*.28,CW*.72]
    if n==3: return [CW*.215,CW*.375,CW*.410]
    return [CW/n]*n

def parse_blocks(text,scale=1):
    st=styles(scale); result=[]; lines=text.strip().splitlines(); i=0
    def gap(v=3): result.append(Spacer(1,v*scale))
    while i<len(lines):
        line=lines[i].strip()
        if not line: i+=1; continue
        if line.startswith("## "):
            result.append(Paragraph(inline(line[3:]),st["h2"]));i+=1
        elif line.startswith("[DIAGRAM:"):
            result.append(Diagram(line[9:-1]));gap(7);i+=1
        elif line.startswith("```"):
            i+=1; code=[]
            while i<len(lines) and not lines[i].startswith("```"):
                code.append(lines[i]); i+=1
            pre=Preformatted('\n'.join(code),st["code"],maxLineLength=89)
            t=Table([[pre]],colWidths=[CW])
            t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),LIGHT),("BOX",(0,0),(-1,-1),.5,LINE),("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
            result.append(t);gap(8);i+=1
        elif line.startswith("| "):
            rows=[]
            while i<len(lines) and lines[i].lstrip().startswith('|'):
                cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r":?-+:?",c) for c in cells): rows.append(cells)
                i+=1
            widths=table_widths(rows[0])
            data=[[Paragraph(inline(c),st['head' if r==0 else 'cell']) for c in row] for r,row in enumerate(rows)]
            t=Table(data,colWidths=widths,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6*scale),('BOTTOMPADDING',(0,0),(-1,-1),6*scale),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#F0F5F7'),colors.white]),('LINEBELOW',(0,0),(-1,-1),.35,LINE)]))
            result.append(t);gap(9)
        elif line.startswith("> "):
            t=Table([[Paragraph(inline(line[2:]),st['quote'])]],colWidths=[CW])
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('LINEBEFORE',(0,0),(0,-1),3,TEAL),('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
            result.append(t);gap(8);i+=1
        elif re.match(r"^\d+\. ",line):
            result.append(Paragraph(inline(line),st['bullet']));i+=1
        else:
            para=[line];i+=1
            while i<len(lines) and lines[i].strip() and not re.match(r"^(## |\| |```|> |\[DIAGRAM:|\d+\. )",lines[i].strip()):
                para.append(lines[i].strip());i+=1
            result.append(Paragraph(inline(' '.join(para)),st['body']))
    return result

def height_of(flowables):
    total=0
    for f in flowables:
        total+=f.getSpaceBefore()+f.wrap(CW,10000)[1]+f.getSpaceAfter()
    return total

def draw_flowables(c,flowables,y):
    for f in flowables:
        y-=f.getSpaceBefore();w,h=f.wrap(CW,10000);y-=h
        f.drawOn(c,M,y);y-=f.getSpaceAfter()
    return y

chapters=[]
for chunk in re.split(r"(?m)^# ",RAW):
    if not chunk.strip():continue
    title,body=chunk.split('\n',1)
    number,name=title.split(' | ',1)
    chapters.append({'number':number,'title':name,'body':body,'bookmark':f'chapter{number}'})

source_groups=[]
source_offset=0
for source_count in [6,7,7,6,6,6,6]:
    source_groups.append(SOURCES[source_offset:source_offset+source_count])
    source_offset+=source_count
assert source_offset==len(SOURCES)
TOTAL=2+len(chapters)+len(source_groups)
diagnostics=[]

def frame(c,page,kicker):
    c.setFillColor(NAVY);c.rect(0,H-8,W,8,fill=1,stroke=0)
    c.setFillColor(MUTED);c.setFont('Bold',8)
    c.drawString(M,H-31,'VASP ATTRIBUTION | RESEARCH + IMPLEMENTATION')
    c.setFont('Body',8);c.drawRightString(W-M,H-31,'24 SEP 2026')
    c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(M,41,W-M,41)
    c.setFillColor(MUTED);c.setFont('Body',8)
    c.drawString(M,27,kicker[:78]);c.drawRightString(W-M,27,f'{page:02d} / {TOTAL:02d}')

def title_block(c,number,title):
    c.setFillColor(TEAL);c.setFont('Bold',10)
    c.drawString(M,H-61,f'{number} / IMPLEMENTATION BLUEPRINT')
    p=Paragraph(html.escape(title),ParagraphStyle('title',fontName='Bold',fontSize=23,leading=26,textColor=NAVY))
    _,h=p.wrap(CW,80);p.drawOn(c,M,H-76-h)
    return H-88-h

def cover(c):
    c.setFillColor(NAVY);c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(TEAL);c.rect(0,H-14,W,14,fill=1,stroke=0)
    c.setFillColor(colors.HexColor('#83CED0'));c.setFont('Bold',11)
    c.drawString(M,H-74,'SIH | BLOCKCHAIN & CYBERSECURITY')
    t=Paragraph('Automated<br/>VASP Attribution',ParagraphStyle('cover',fontName='Bold',fontSize=39,leading=42,textColor=colors.white))
    _,th=t.wrap(CW,180);t.drawOn(c,M,H-123-th)
    c.setFillColor(colors.HexColor('#D3E4EB'));c.setFont('Light',20)
    c.drawString(M,H-258,'Research and implementation report')
    c.setFont('Body',12);c.drawString(M,H-291,'From unknown cryptocurrency wallets to')
    c.drawString(M,H-309,'evidence-backed service attribution and lawful routing')
    # Purpose-built vector motif: no actual wallet or service attribution.
    pts=[(65,386),(161,448),(255,389),(341,448),(484,395),(162,320),(341,316),(480,291)]
    c.setStrokeColor(colors.HexColor('#326079'));c.setLineWidth(1.4)
    for a,b in [(0,1),(1,2),(2,3),(3,4),(0,5),(5,2),(2,6),(6,7),(4,7)]:
        c.line(*pts[a],*pts[b])
    for n,(x,y) in enumerate(pts):
        c.setFillColor(GOLD if n in (4,7) else TEAL);c.circle(x,y,7,fill=1,stroke=0)
        c.setFillColor(NAVY);c.circle(x,y,3,fill=1,stroke=0)
    c.setFillColor(colors.HexColor('#83CED0'));c.setFont('Bold',10)
    c.drawString(M,238,'41 DESIGN SECTIONS   /   6 REQUIRED CHAINS   /   44 SOURCES')
    c.setStrokeColor(colors.HexColor('#476579'));c.line(M,210,W-M,210)
    text=Paragraph('Prepared for planning against the user-supplied MHA / I4C problem statement.<br/>Independent platform design with an official SAHYOG integration gate.',ParagraphStyle('meta',fontName='Body',fontSize=11,leading=16,textColor=colors.HexColor('#D3E4EB')))
    _,hh=text.wrap(CW,100);text.drawOn(c,M,184-hh)
    c.setFillColor(colors.white);c.setFont('Bold',11);c.drawString(M,88,DATE+'  |  Version 1.0')
    c.setFillColor(colors.HexColor('#AFC7D4'));c.setFont('Body',9)
    c.drawString(M,67,'Public-source research and proposed engineering specification.')
    c.drawString(M,53,'Not an official ministry publication or a claim of deployed software.')
    c.showPage()

def contents(c):
    frame(c,2,'Reading guide | Click a section or source reference to navigate')
    y=title_block(c,'MAP','Read the plan from evidence to release')
    p=Paragraph('The design is proposed. Documentation supports component feasibility; measured accuracy, commercial access and official integration remain explicit release gates. Sources are linked in the text and annotated at the end.',styles()['body'])
    _,hh=p.wrap(CW,90);p.drawOn(c,M,y-hh);y-=hh+16
    entries=[(f'{ch["number"]}  {ch["title"]}',ch['bookmark'],i+3) for i,ch in enumerate(chapters)]
    entries.append(('Sources  |  Evidence and access notes','sources',3+len(chapters)))
    cols=[entries[:21],entries[21:]]
    colw=(CW-24)/2
    for col,items in enumerate(cols):
        xx=M+col*(colw+24);yy=y
        for label,bm,page in items:
            pp=Paragraph(f'<link href="#{bm}" color="#23394B">{html.escape(label)}</link>',ParagraphStyle('toc',fontName='Body',fontSize=9.4,leading=11.8,textColor=INK))
            _,ht=pp.wrap(colw-25,40);pp.drawOn(c,xx,yy-ht)
            c.setFillColor(TEAL);c.setFont('Bold',9);c.drawRightString(xx+colw,yy-10,str(page))
            c.setStrokeColor(LINE);c.setLineWidth(.25);c.line(xx,yy-ht-5,xx+colw,yy-ht-5)
            yy-=max(ht+13,27)
        if yy<54: raise RuntimeError(f'TOC column overflow: {yy}')
    c.showPage()

c=canvas.Canvas(str(PDF),pagesize=A4,pageCompression=1)
c.setTitle('Automated VASP Attribution: Research and Implementation Report')
c.setAuthor('Prepared with Codex for the SIH 2026 project')
c.setSubject('Evidence-backed architecture and full-release implementation plan for multi-chain VASP attribution')
c.setKeywords('VASP, SAHYOG, I4C, blockchain intelligence, implementation plan, research')
c.setViewerPreference('DisplayDocTitle','true')
cover(c);contents(c)

for i,ch in enumerate(chapters):
    page=i+3
    frame(c,page,'Proposed design | No deployed-system or measured-accuracy claim')
    c.bookmarkPage(ch['bookmark']);c.addOutlineEntry(f'{ch["number"]} {ch["title"]}',ch['bookmark'],0)
    top=title_block(c,ch['number'],ch['title'])
    available=top-56
    scale=1.0
    while True:
        blocks=parse_blocks(ch['body'],scale)
        bh=height_of(blocks)
        if bh<=available:break
        scale-=.015
        if scale<.88:raise RuntimeError(f'Chapter {ch["number"]} overfull: {bh:.1f} > {available:.1f}; split/edit content')
    bottom=draw_flowables(c,blocks,top)
    diagnostics.append({'page':page,'chapter':ch['number'],'title':ch['title'],'scale':round(scale,3),'body_font':round(10.3*scale,2),'table_font':round(9.15*scale,2),'bottom':round(bottom,1),'content_height':round(bh,1)})
    c.showPage()

for gi,group in enumerate(source_groups):
    page=3+len(chapters)+gi
    frame(c,page,'Source register | All sources accessed/reviewed 24 September 2026')
    if gi==0:c.bookmarkPage('sources');c.addOutlineEntry('Sources and evidence notes','sources',0)
    y=title_block(c,'SOURCES',f'Evidence register / {gi+1:02d}')
    if gi==0:
        pp=Paragraph('Primary documentation establishes what is documented, not what this project has tested. Supplier claims, legal review requirements and retrieval limits are identified below. URLs are clickable; no paid account or official integration was accessed.',styles()['body'])
        _,hh=pp.wrap(CW,100);pp.drawOn(c,M,y-hh);y-=hh+7
    for s in group:
        c.bookmarkHorizontalAbsolute(s['id'],y)
        hst=ParagraphStyle('refhead',fontName='Bold',fontSize=10.2,leading=12.5,textColor=NAVY,spaceAfter=3)
        bst=ParagraphStyle('refbody',fontName='Body',fontSize=9.0,leading=11.6,textColor=INK,spaceAfter=3)
        ust=ParagraphStyle('refurl',fontName='Body',fontSize=8.0,leading=10.3,textColor=TEAL,splitLongWords=True,spaceAfter=4)
        fs=[Paragraph(f'{s["id"]} / {html.escape(s["publisher"])}',hst),
            Paragraph(f'<link href="{html.escape(s["url"],quote=True)}" color="#087E83">{html.escape(s["title"])}</link>',bst),
            Paragraph(f'{html.escape(s["type"])}. {html.escape(s["supports"])}',bst),
            Paragraph(f'<b>Limit:</b> {html.escape(s["limit"])} <b>Access:</b> {html.escape(s["access"])}',bst),
            Paragraph(f'<link href="{html.escape(s["url"],quote=True)}">{html.escape(s["url"])}</link>',ust)]
        for f in fs:
            _,hh=f.wrap(CW,1000);y-=hh;f.drawOn(c,M,y);y-=f.getSpaceAfter()
        c.setStrokeColor(LINE);c.setLineWidth(.4);c.line(M,y-1,W-M,y-1);y-=11
    if y<54:raise RuntimeError(f'Source page overflow: {page}, bottom={y}')
    diagnostics.append({'page':page,'sources':[s['id'] for s in group],'bottom':round(y,1)})
    c.showPage()
c.save()

# A portable, editable companion and tabular source register.
md='# Automated VASP Attribution\n\nResearch and implementation report | '+DATE+' | v1.0\n\n'+RAW
md+='\n# Sources and evidence notes\n\nAll sources accessed/reviewed 24 September 2026.\n'
for s in SOURCES:
    md+=f'\n## {s["id"]}: {s["title"]}\n\n{s["publisher"]} | {s["type"]}\n\n[{s["title"]}]({s["url"]})\n\nSupports: {s["supports"]}\n\nLimit: {s["limit"]}\n\nAccess: {s["access"]}\n'
(OUT/'VASP_Attribution_Implementation_Report.md').write_text(md,encoding='utf-8')
with (OUT/'VASP_Attribution_Source_Register.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(SOURCES[0])+['reviewed_on'])
    writer.writeheader()
    for s in SOURCES:writer.writerow({**s,'reviewed_on':'2026-09-24'})
(QA/'layout_diagnostics.json').write_text(json.dumps(diagnostics,indent=2),encoding='utf-8')
summary={'pdf':str(PDF),'pages':TOTAL,'chapters':len(chapters),'sources':len(SOURCES),'words_approx':len(RAW.split()),'sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'compressed_pages':[d for d in diagnostics if d.get('scale',1)<1]}
(QA/'build_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
