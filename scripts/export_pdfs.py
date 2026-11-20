"""Export each job as a standalone PDF. Requires optional ReportLab dependency."""
import argparse
import re
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, XPreformatted

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
if (FONT_DIR/'DejaVuSans.ttf').exists():
    for suffix, filename in [('', 'DejaVuSans.ttf'), ('-Bold','DejaVuSans-Bold.ttf'), ('-Oblique','DejaVuSans-Oblique.ttf'), ('-BoldOblique','DejaVuSans-BoldOblique.ttf')]:
        pdfmetrics.registerFont(TTFont('CG'+suffix, str(FONT_DIR/filename)))
    pdfmetrics.registerFontFamily('CG', normal='CG', bold='CG-Bold', italic='CG-Oblique', boldItalic='CG-BoldOblique')
    FONT = 'CG'
else:
    FONT = 'Helvetica'
STYLES = getSampleStyleSheet()
for name in ('BodyText','Title','Heading1','Heading2','Heading3'):
    STYLES[name].fontName = FONT
STYLES['BodyText'].fontSize=9
STYLES['BodyText'].leading=13
STYLES['BodyText'].spaceAfter=7
STYLES['Title'].fontSize=21
STYLES['Title'].leading=27
for name in ('Title','Heading1','Heading2','Heading3'):
    STYLES[name].textColor=colors.HexColor('#16555a')
STYLES.add(ParagraphStyle(name='Cell',fontName=FONT,fontSize=7.1,leading=10,spaceAfter=0))
STYLES.add(ParagraphStyle(name='CodeBlock',fontName='Courier',fontSize=7,leading=10,spaceAfter=9))

def inline(text):
    text=escape(text)
    text=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<link href="\2" color="#146b78">\1</link>',text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',text)
    return re.sub(r'`([^`]+)`',r'<font face="Courier">\1</font>',text)

def paragraph(text,style='BodyText'):
    return Paragraph(inline(text),STYLES[style])

def flowables(source):
    story=[]; lines=source.splitlines(); i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line: i+=1;continue
        if line.startswith('```'):
            block=[];i+=1
            while i<len(lines) and not lines[i].strip().startswith('```'):
                # Wrap long source lines for readable PDF margins.
                raw=lines[i]
                while len(raw)>90:
                    block.append(raw[:90]);raw=raw[90:]
                block.append(raw);i+=1
            story.append(XPreformatted(escape('\n'.join(block)),STYLES['CodeBlock']))
            i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',c) for c in cells):
                    rows.append([paragraph(c,'Cell') for c in cells])
                i+=1
            n=len(rows[0]); weights={2:[.30,.70],3:[.23,.39,.38],4:[.20,.25,.27,.28],5:[.17,.18,.25,.20,.20]}.get(n,[1/n]*n)
            table=Table(rows,colWidths=[504*w for w in weights],repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dcebea')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#bdcdce')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.extend([table,Spacer(1,10)]);continue
        if line=='---':i+=1;continue
        if line.startswith('# '):story.append(paragraph(line[2:],'Title'))
        elif line.startswith('## '):story.append(paragraph(line[3:],'Heading2'))
        elif line.startswith('### '):story.append(paragraph(line[4:],'Heading3'))
        else:story.append(paragraph(line))
        i+=1
    return story

def footer(canvas,doc):
    canvas.setFont(FONT,7)
    canvas.setFillColor(colors.HexColor('#52656b'))
    canvas.drawString(45,25,'Exaclim | Hackathon preparation | 16 November 2026')
    canvas.drawRightString(566,25,str(doc.page))


def system_overview(target):
    canvas=pdfcanvas.Canvas(str(target),pagesize=(612,792))
    canvas.setTitle('Exaclim — One-page system overview')
    def text(x,y,w,value,style='BodyText'):
        para=paragraph(value,style);_,height=para.wrap(w,700)
        para.drawOn(canvas,x,y-height)
        return height
    def box(x,y,w,h,title,body):
        canvas.setStrokeColor(colors.HexColor('#bbcdca'))
        canvas.setFillColor(colors.HexColor('#edf3ef'))
        canvas.roundRect(x,y,w,h,8,fill=1,stroke=1)
        text(x+10,y+h-12,w-20,title,'Heading3')
        text(x+10,y+h-39,w-20,body)
    def arrow(x1,y1,x2,y2):
        canvas.setStrokeColor(colors.HexColor('#16555a'));canvas.setLineWidth(1.5)
        canvas.line(x1,y1,x2,y2)
        canvas.setFillColor(colors.HexColor('#16555a'))
        path=canvas.beginPath()
        if x2>x1:
            path.moveTo(x2,y2);path.lineTo(x2-5,y2+3);path.lineTo(x2-5,y2-3)
        else:
            path.moveTo(x2,y2);path.lineTo(x2-3,y2+5);path.lineTo(x2+3,y2+5)
        path.close();canvas.drawPath(path,fill=1,stroke=0)
    text(45,750,515,'Exaclim','Title')
    text(45,711,515,'One-page system overview','Heading2')
    text(45,682,515,'Proposed hardware architecture; current submission simulates devices in software. No tested wearable or validated safety limit is claimed.')
    box(45,524,150,112,'Zone station','SHT4x temperature/humidity telemetry. Timestamp and quality flag. Reference WBGT validation needed.')
    box(225,524,150,112,'Worker badge','Declared task context + local index. LED, buzzer, vibration. Separate acknowledge/help buttons.')
    box(405,524,150,112,'Gateway','Authenticated radio design. Consented contributions. Emergency channel when reachable.')
    arrow(195,575,225,575);arrow(375,575,405,575)
    text(45,511,150,'Zone data: BLE contract; radio/security untested.')
    text(225,511,150,'Alerts remain local when Internet is unavailable.')
    text(405,511,150,'No remote rescue delivery guarantee.')
    box(45,348,150,103,'Weather provider','Open-Meteo candidate. Preserve source, timestamp and freshness. Synthetic fallback explicitly labeled.')
    box(225,348,150,103,'Worker action','Graded messages/icons. Help overrides index. Acknowledge never clears emergency.')
    box(405,348,150,103,'Crew dashboard','Aggregates only. Suppress below five. Forecast planning; no personal drilldown.')
    arrow(300,524,300,451);arrow(480,524,480,451)
    text(45,330,510,'Failure rule: stale/invalid data is at least amber; preserve prior red/emergency. Use the site fallback plan. Emergency resolution is separate from acknowledgement.')
    box(45,115,510,151,'Built for the hackathon','Local Python server + responsive crew dashboard + private badge simulator. Transparent illustrative engine and optional synthetic look-ahead. English / draft French messages. 23 Python tests and 22 Chromium checks passed. No clinical effectiveness, field hardware, SMS or BLE operation demonstrated.')
    text(45,96,510,'Post-hackathon: expert-approved model, reference measurement comparison, physical power/radio/environmental tests, worker consultation and appropriate pilot approvals.')
    canvas.setFont(FONT,7);canvas.setFillColor(colors.HexColor('#52656b'))
    canvas.drawString(45,25,'Exaclim | System overview | 16 November 2026');canvas.drawRightString(566,25,'1')
    canvas.save()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default=str(ROOT/'deliverables'))
    args=parser.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    for path in sorted((ROOT/'docs'/'jobs').glob('*.md')):
        target=out/(path.stem+'.pdf')
        doc=SimpleDocTemplate(str(target),pagesize=(612,792),leftMargin=45,rightMargin=63,topMargin=42,bottomMargin=43,title=path.stem,author='Exaclim Team')
        doc.build(flowables(path.read_text()),onFirstPage=footer,onLaterPages=footer)
        print(target)
    system_overview(out/'03a-system-overview.pdf')
    print(out/'03a-system-overview.pdf')

if __name__=='__main__':main()
