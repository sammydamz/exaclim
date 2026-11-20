from pathlib import Path
import json, re, shutil, zipfile, hashlib
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml.xmlchemy import OxmlElement

import argparse
parser=argparse.ArgumentParser(description='Populate the organizer submission template for Exaclim.')
parser.add_argument('--template',required=True,type=Path)
parser.add_argument('--output-dir',type=Path,default=Path('/workspace/artifacts/exaclim-submission'))
args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[1];OUT=args.output_dir;OUT.mkdir(parents=True,exist_ok=True)
TEMPLATE=args.template
r=Presentation(TEMPLATE)
FONT='Liberation Sans';INK='182F30';MUTED='465D5B';ACCENT='00685E';BEIGE='E6F0EC';BORDER='B8CFC8';WHITE='FFFFFF';BROWN='193E3A'
URL='https://exaclim.kasalite-business.workers.dev';REPO='https://github.com/sammydamz/exaclim/tree/exaclim-ui-sdk'
refs=[
('1','WHO / WMO, 2025','Protecting workers from increasing heat stress','https://www.who.int/news/item/22-08-2025-who-wmo-issue-new-report-and-guidance-to-protect-workers-from-increasing-heat-stress'),
('2','NIOSH, 2016','Criteria for occupational exposure to heat','https://www.cdc.gov/niosh/docs/2016-106/default.html'),
('3','NIOSH, current guidance','Workplace recommendations: water, rest, acclimatization','https://www.cdc.gov/niosh/heat-stress/recommendations/index.html'),
('4','Open-Meteo','API service terms and CC BY 4.0 attribution','https://open-meteo.com/en/terms'),
('5','Ghana Data Protection Commission','Act 843 and controller / processor obligations','https://dpc.gov.gh/'),
('6','Adafruit, product 4062','nRF52840 BLE development-board candidate','https://www.adafruit.com/product/4062'),
('7','Exaclim repository','Source, engineering audit and executed checks',REPO)]
notes={};editable=[]
def col(h):return RGBColor.from_string(h)
def text(slide,x,y,w,h,value,size=14,bold=False,color=INK,link=None):
 shape=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=shape.text_frame;tf.clear();tf.word_wrap=True
 tf.margin_left=tf.margin_right=0;tf.margin_top=tf.margin_bottom=0
 for i,line in enumerate(value.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.space_after=Pt(4);p.line_spacing=1.12
  run=p.add_run();run.text=line;run.font.name=FONT;run.font.size=Pt(size);run.font.bold=bold;run.font.color.rgb=col(color)
  if link:run.hyperlink.address=link
 return shape

def clear_body(index,title,subtitle=None):
 s=r.slides[index-1]
 for sh in list(s.shapes):
  if sh.has_text_frame:
   sh._element.getparent().remove(sh._element)
 text(s,.4,.94,9.2,.38,title,22,True,BROWN)
 if subtitle:text(s,.4,1.40,9.2,.30,subtitle,10.5,False,MUTED)
 text(s,9.23,5.25,.38,.19,str(index).zfill(2),8.5,False,MUTED)
 return s

def note(s,n,body):
 s.notes_slide.notes_text_frame.text=body
 notes[str(n)]=body

def label_block(s,x,y,w,title,body,h=1.0):
 text(s,x,y,w,.27,title,14,True,ACCENT);text(s,x,y+.34,w,h-.34,body,13.5)

# Single-stroke pictograms drawn as editable PowerPoint paths on a 24-unit grid.
PICTOGRAMS = {
 'monitor': [[(2,3),(22,3),(22,17),(2,17),(2,3)],[(12,17),(12,21)],[(7,21),(17,21)]],
 'check': [[(3,12),(9,18),(21,5)]],
 'phone': [[(7,2),(17,2),(18,3),(18,21),(17,22),(7,22),(6,21),(6,3),(7,2)],[(10,18),(14,18)]],
 'watch': [[(8,7),(8,2),(16,2),(16,7)],[(8,17),(8,22),(16,22),(16,17)],[(6,7),(18,7),(18,17),(6,17),(6,7)]],
 'shield': [[(12,2),(21,6),(20,14),(17,19),(12,22),(7,19),(4,14),(3,6),(12,2)],[(8,11),(11,14),(16,9)]],
 'battery': [[(2,7),(20,7),(20,17),(2,17),(2,7)],[(22,10),(22,14)],[(6,10),(6,14)],[(10,10),(10,14)]],
 'chart': [[(3,2),(3,21),(22,21)],[(7,16),(12,10),(16,12),(22,5)]],
}
def panel(slide,x,y,w,h,fill):
 sh=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
 sh.adjustments[0]=.09
 sh.fill.solid()
 sh.fill.fore_color.rgb=col(fill)
 sh.line.fill.background()
 sh._element.spPr.append(OxmlElement('a:effectLst'))

def card(slide,x,y,w,h,icon,title,body,fill=BEIGE):
 panel(slide,x,y,w,h,fill)
 dark=fill=='174C47'
 foreground=WHITE if dark else INK
 accent=WHITE if dark else ACCENT
 for path in PICTOGRAMS[icon]:
  points=[(Inches(x+.18+.016*px), Inches(y+.15+.016*py)) for px,py in path]
  builder=slide.shapes.build_freeform(*points[0])
  builder.add_line_segments(points[1:],close=False)
  stroke=builder.convert_to_shape()
  stroke.fill.background()
  stroke.line.color.rgb=col(accent)
  stroke.line.width=Pt(1.45)
 text(slide,x+.68,y+.18,w-.87,.31,title,15,True,foreground)
 text(slide,x+.20,y+.65,w-.40,h-.71,body,12.6,False,foreground)

def table(s,x,y,width,headers,rows,colwidths,font=12.5,row_h=.55):
 shape=s.shapes.add_table(len(rows)+1,len(headers),Inches(x),Inches(y),Inches(width),Inches(row_h*(len(rows)+1)));t=shape.table
 for i,cw in enumerate(colwidths):t.columns[i].width=Inches(cw)
 t.rows[0].height=Inches(.38)
 for rr in list(t.rows)[1:]:rr.height=Inches(row_h)
 for ri,row in enumerate([headers]+rows):
  for ci,txt in enumerate(row):
   c=t.cell(ri,ci);c.text=txt;c.margin_left=Inches(.10);c.margin_right=Inches(.09);c.margin_top=Inches(.075);c.margin_bottom=Inches(.055);c.vertical_anchor=MSO_ANCHOR.MIDDLE
   c.fill.solid();c.fill.fore_color.rgb=col('174C47' if ri==0 else (BEIGE if ci==0 else ('F7F9F8' if ri%2 else WHITE)))
   for p in c.text_frame.paragraphs:
    p.space_after=Pt(1);p.line_spacing=1.05
    for run in p.runs:run.font.name=FONT;run.font.size=Pt(font);run.font.bold=ri==0 or ci==0;run.font.color.rgb=col(WHITE if ri==0 else INK)
   tcPr=c._tc.get_or_add_tcPr()
   for edge in ['lnL','lnR','lnT','lnB']:
    ln=OxmlElement('a:'+edge);ln.set('w','4000');fill=OxmlElement('a:solidFill');rgb=OxmlElement('a:srgbClr');rgb.set('val',WHITE);fill.append(rgb);ln.append(fill);tcPr.append(ln)
 return shape

def box(s,x,y,w,h,title,body,status=None):
 sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));sh.adjustments[0]=.07;sh.fill.solid();sh.fill.fore_color.rgb=col('174C47' if status and status.startswith('DEPLOYED') else BEIGE);sh.line.color.rgb=col(BORDER);sh.line.width=Pt(.7);sh._element.spPr.append(OxmlElement('a:effectLst'))
 text(s,x+.12,y+.14,w-.24,.26,title,12.8,True,WHITE if status and status.startswith('DEPLOYED') else INK)
 text(s,x+.12,y+.48,w-.24,h-.54,body,10.8,False,WHITE if status and status.startswith('DEPLOYED') else MUTED)
 if status:text(s,x,y-.25,w,.2,status,8.5,True,ACCENT)
 return sh

def arrow(s,x1,y1,x2,y2,dashed=False):
 sh=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1),Inches(y1),Inches(x2),Inches(y2));sh.line.color.rgb=col(ACCENT);sh.line.width=Pt(1.5)
 if dashed:sh.line.dash_style=MSO_LINE_DASH_STYLE.DASH
 ln=sh._element.spPr.get_or_add_ln();end=OxmlElement('a:tailEnd');end.set('type','triangle');ln.append(end)
 return sh

# Cover: team fields intentionally blank.
s=r.slides[0];s.shapes[2]._element.getparent().remove(s.shapes[2]._element)
text(s,.48,3.27,9.0,.43,'Exaclim',32,True,BROWN)
text(s,.48,3.94,9.0,.35,'Heat forecasts, crew protection and timely help',16)
text(s,.48,4.36,9.0,.88,'Team Name: \nTeam Size: \nProblem Statement: Climate-Resilient Worker Health',13)
note(s,1,'Project: Exaclim. Team name and size intentionally left blank at the user’s request. Problem statement: Climate-Resilient Worker Health. This deck describes the checked hosted software separately from the intended wearable/Android workflow. It does not claim clinical validation.')
# Slide 2: preserve untouched, including all team placeholders and table.

s=clear_body(3,'Team capability summary','What the team has built, tested and identified for field review.')
cap_start = len(s.shapes)
card(s,.4,1.82,4.5,1.64,'monitor','Delivered','A supervisor dashboard and Hono API run on Cloudflare Workers. D1 stores crews, help requests and acknowledgements.','174C47')
card(s,5.04,1.82,4.54,1.64,'check','Tested','Domain, API and browser checks cover crew privacy and help response. The repository includes hardware and pilot plans.')
card(s,.4,3.60,9.18,1.42,'watch','Before a field pilot','The watch and Android link is simulated. Next steps include hardware and background BLE testing, occupational-health and language review, and site recruitment.','F4F0E9')
cap = ' '.join(shape.text for shape in list(s.shapes)[cap_start:] if shape.has_text_frame)
assert len(cap) <= 1000
note(s,3,f'Capability answer: {len(cap)} characters, below the 1,000-character limit. No member biographies, degrees, employment history, partnerships or approvals were supplied; none is invented. Team members slide is left untouched. Evidence: docs/demo/verification.md; docs/design/emil-review.md; docs/dashboard-v1/04-implementation-audit.md. Hosted release at preparation: 7c4c7a8, Cloudflare version 7409edd8-bd47-40cf-840b-a2a2987b7bc3. New operational modules in the working tree are not counted as released.')

s=clear_body(4,'Architecture and workflow','How a worker’s help request reaches the supervisor, and where the record is kept.')
box(s,.4,1.98,2.04,1.13,'Worker watch','Graded alert\nHelp button')
box(s,2.8,1.98,2.04,1.13,'Android gateway','Local aggregates\nQueued help')
box(s,5.2,1.98,2.04,1.13,'Workers API','Hono / TypeScript\nSite access and alerts')
box(s,7.6,1.98,2.0,1.13,'Supervisor UI','Crew overview\nHelp response')
arrow(s,2.44,2.53,2.8,2.53);arrow(s,4.84,2.53,5.2,2.53);arrow(s,7.24,2.53,7.6,2.53)
text(s,2.46,2.12,.32,.2,'BLE',8,False,MUTED);text(s,4.87,2.12,.3,.2,'TLS',8,False,MUTED)
box(s,.4,3.66,2.04,1.08,'Private context','Clothing / acclimatization\nStored on watch')
box(s,2.8,3.66,2.04,1.08,'Public weather','Open-Meteo\nHourly site forecast')
box(s,5.2,3.66,2.04,1.08,'Cloudflare D1','Sites / crews\nHelp and receipts')
text(s,7.6,3.66,2,.28,'Cloud boundary',13,True,ACCENT)
text(s,7.6,4.04,2,.79,'Routine: groups of ≥3.\nNamed identity: help only.\nACK does not clear help.',11.5)
arrow(s,4.84,4.14,5.2,3.11);arrow(s,6.22,3.11,6.22,3.66)
arrow(s,1.42,3.66,1.42,3.11)
note(s,4,'The worker requests help on the watch. The shared Android gateway queues the request and forwards it to the site API. The supervisor acknowledges receipt, and D1 keeps the request and acknowledgement. Routine crew summaries require three contributors. Clothing and acclimatization settings stay on the watch.')

s=clear_body(5,'Target users and intended outcome','Initial use case: outdoor construction crews in the Accra area, Ghana.')
card(s,.4,1.80,5.15,1.48,'monitor','Supervisor','Check the two-day heat forecast and crew status. Plan heavier work, breaks and rotation.','174C47')
card(s,5.69,1.80,3.89,1.48,'watch','Worker','Receive graded warnings and request help from the watch.')
card(s,.4,3.41,5.15,1.48,'phone','Crew lead or site responder','Carry the shared Android phone, check devices and follow the site emergency procedure.','F4F0E9')
card(s,5.69,3.41,3.89,1.48,'shield','Intended outcome','Recognize risk earlier while keeping individual exposure private.')
text(s,.45,5.00,8.9,.23,'Construction first. Logistics and commercial farms require separate site and worker validation.',10.5,False,MUTED)
note(s,5,'The primary dashboard role is supervisor; crew lead and responder are operational responsibilities, not extra analytics portals. Ghana is the proposed first setting, not a confirmed pilot partner or exclusive market. English is currently implemented; Twi or another language requires worker-led selection and fluent-speaker review. Intended benefits are hypotheses: no measured reduction in illness, injury or lost work is claimed. Source context: WHO/WMO [1]; prevention actions: NIOSH [2,3].')

s=clear_body(6,'How success will be measured','Proposed acceptance criteria and pilot measures, not reported field outcomes.')
table(s,.42,1.87,9.15,['Measure','Definition / test','Acceptance or interpretation'],[
['Help delivery','Backend durable receipt → visible banner; ≥20 runs.','Target p95 ≤2 seconds on a healthy link; report offline delay separately.'],
['Delivery integrity','Missed / duplicate events; ACK and replay fault tests.','No lost accepted help; one canonical ACK; unresolved help stays Red.'],
['Privacy and freshness','API field audit, low counts, outages and sample age.','No routine individual health fields; suppress <3; caution after 120s.'],
['Usability and action','Workers explain alerts; supervisors complete key tasks.','Record comprehension, task completion and errors; review access needs.'],
['Pilot effectiveness','Alert lead time, false alarms, control adherence and incidents.','Predefine reference / denominators; independently review. No causal claim from a small pilot.']],[1.55,3.35,4.25],11.7,.59)
note(s,6,'Target p95 ≤2 seconds is the project’s proposed healthy-network backend-to-dashboard target (PRD section 13), not a measured achieved value and not end-to-end offline radio latency. At least 20 runs are required. Log p50/p95 and missed/duplicate denominators. A separate weak-link cold render target is ≤5s p95 under 400kbps down/100kbps up/400ms RTT plus an outage. These targets are not yet established by the recorded browser checks. Pilot false alarms need an expert-reviewed reference definition, not app-generated labels. Exposure and incident rates require worker-hours / work context and a prospective protocol. Rest adherence is an observation/research measure, not an implemented productivity tracker. No safety control may be withheld for evaluation.')

s=clear_body(7,'Evidence supporting the approach','External evidence motivates the design; software checks establish only software behaviour.')
text(s,.45,1.85,4.3,.65,'Over 2.4 billion',31,True,ACCENT)
text(s,.45,2.59,4.2,.88,'workers worldwide are exposed to excessive heat, according to WHO and WMO, citing ILO [1].',14)
label_block(s,.45,3.62,4.2,'Prevention guidance [2, 3]','NIOSH recommends acclimatization, hydration, rest, training and supervision.',1.1)
text(s,5.03,1.94,4.15,.32,'Software checks passed [7]',15,True,INK)
for y,count,description in [(2.47,'72','Python reference tests'),(3.13,'16','TypeScript domain tests'),(3.79,'27','Chromium workflow checks')]:
 text(s,5.03,y,.72,.49,count,23,True,ACCENT)
 text(s,5.87,y+.09,3.55,.38,description,13)
text(s,.45,4.94,9,.30,'Checks used generated scenarios. Field reliability, clinical accuracy and health outcomes remain unverified.',10.8,False,MUTED)
note(s,7,'[1] WHO/WMO news release, 22 August 2025, verified 20 November 2026. It reports >2.4 billion exposed workers and attributes estimates to ILO. No Ghana-specific prevalence or project-specific effect size is inferred. [2] NIOSH Criteria, 2016 publication 2016-106. [3] Current NIOSH workplace recommendations verified 20 November 2026. [7] Existing released/reference evidence: 72 Python tests; 16 deployed-domain tests; 27 local Chromium workflow assertions. Earlier hosted version passed 25 browser checks; counts are different test runs, not 115 independent requirements or a clinical trial. The 48 planned acceptance cases are not all signed off. Working-tree operational extensions have additional unit checks but lack a complete released integration run; omitted from this proof claim. Do not present simulated fault injection as physical field testing.')

s=clear_body(8,'Data sources and legal right to use them','Data minimization applies across ingestion, storage, browser access and future device provisioning.')
table(s,.42,1.86,9.15,['Source / type','Owner / right to use','Sensitivity and permitted use'],[
['Project fixtures','Team-created synthetic workers, watches and scenarios.','No real worker data in the submission; use only to exercise workflows.'],
['Weather forecast [4]','Open-Meteo / underlying providers; CC BY 4.0 attribution.','Public grid-weather data. Free API is non-commercial; commercial service needs suitable access.'],
['Account / assignment / help','Future worker / site data under agreed roles and lawful basis.','Identity and health-related context: restrict access, retention and cross-border processing.'],
['Private watch context','Future worker-provided clothing and acclimatization settings.','Planned local-only provisioning; exclude from routine cloud payloads and logs.']],[1.7,3.45,4.0],11.8,.68)
note(s,8,'Open-Meteo terms and licence pages were directly verified on 20 November 2026: https://open-meteo.com/en/terms and https://open-meteo.com/en/licence. Distinguish the CC BY 4.0 data licence from the Free API’s non-commercial service restriction. Attribution and change indications must be retained; underlying-provider conditions should be checked. Commercial use or higher volume requires a suitable subscription or self-hosted arrangement. No third-party personal dataset, pretrained clinical model or claimed patient-data consent is used. Any real pilot requires a Ghana Act 843 review, controller/processor allocation, registration obligations where applicable, lawful basis, purpose limitation, worker information, retention and cross-border-hosting review. A three-person threshold is an engineering safeguard, not proof of anonymization or legal compliance. Personal setup/response identity remains personal data even when routine summaries are aggregated.')

s=clear_body(9,'Risks and safeguards','Human safety decisions remain with workers, site responders and the supervisor.')
table(s,.42,1.86,9.15,['Risk','Safeguard / response'],[
['False reassurance or poor model fit','Treat missing / stale data cautiously. Forecast heat screening is not WBGT, diagnosis or a safe-work allowance.'],
['Offline phone, watch or power failure','Show age and delayed delivery; queue/retry by design. Use water, shade, buddy checks and the site emergency plan independently.'],
['Privacy, security or employment misuse','Group ≥3; no routine individual score/history. Limited named-help exception, site scopes and durable ACK. No disciplinary use.'],
['Bias, accessibility and over-reliance','Review workload/PPE, sun exposure, acclimatization and language needs. Show reasons; supervisor can choose a safer action.']],[2.25,6.9],12.2,.72)
note(s,9,'Currently implemented safeguards include scope checks, bounded allowlisted requests, session protections, no-store protected responses, non-overlapping groups, count suppression and receipt semantics. Hardware autonomy, phone outbox hop receipts, credential lifecycle, production identity integration, retention/deletion automation and full security assurance remain development/pilot gates. Do not claim a formal security audit, medical-device certification or clinical validation. Acknowledging receipt must never resolve an active worker help state. Reconnection must not reset the sample time of old data. Red is preserved under uncertainty. On the radio/power failure path, no software queue can guarantee immediate offline delivery. Worker consent does not by itself resolve employment power imbalance or every legal basis.')

s=clear_body(10,'Hardware requirements','Current submission: watch link simulated; Android is the intended shared-phone platform.')
card(s,.4,1.8,4.5,1.48,'watch','Watch prototype','Test a Feather nRF52840 board [6] with a help button, visual alerts and vibration. Wrist hardware selection is pending.','174C47')
card(s,5.04,1.8,4.54,1.48,'phone','Shared Android phone','Check background BLE, reconnection, watch capacity and charging on the selected handset.')
card(s,.4,3.41,4.5,1.48,'battery','Power and enclosure','Review battery and driver compatibility, PPE fit, skin contact, heat and dust.','F4F0E9')
card(s,5.04,3.41,4.54,1.48,'chart','Reference instrument','Borrow or rent a calibrated WBGT instrument to compare heat conditions on site.')
text(s,.45,5.05,8.9,.18,'No procurement, battery-life, IP-rating, range or delivered-price claim. Quotes and exact models remain pending.',9.7,False,MUTED)
note(s,10,'The user explicitly chose to simulate watch/phone connectivity for this submission and identified Android as the target. This is not a native Android BLE qualification claim. Verified manufacturer candidate: Adafruit Feather nRF52840 Express product 4062, BLE and supported development tooling, accessed 20 November 2026. It is a development board, not a finished certified wrist wearable. No price is quoted because freight, taxes, battery carriage, revision and local availability have not been confirmed. Source actual batteries/drivers/actuators with matched electrical ratings and qualified assembly review. New architecture does not require the older zone-station kit, so its historical budget is not copied. Bench and human-factor trials must verify independent alarms, queue/reboot integrity, runtime, charge safety and glove/sunlight use before any field-reliance statement.')

s=clear_body(11,'Application access','Hosted sign-in verified during preparation on 20 November 2026.')
text(s,.5,1.95,8.8,.28,'Open Exaclim',14,True,ACCENT)
text(s,.5,2.34,8.8,.34,URL,18,True,INK,URL)
table(s,.5,3.02,8.8,['Email','Password'],[['demo@exaclim.test','Exaclim2026!']],[5.0,3.8],16,.5)
text(s,.5,4.24,8.8,.62,'Sign in → review forecast and crews → open Scenarios → request help → acknowledge receipt.',14)
text(s,.5,5.0,8.8,.22,'Use fictional information only. Public evaluation account; not a real-worker deployment.',10.5,False,MUTED)
note(s,11,'Valid hosted access was tested with HTTP 200 login and logout while preparing this document. Credentials are intentionally included to meet the template requirement. No private Cloudflare account token or administrator secret from the development environment is included. This published evaluation account is not suitable for real worker information. The public running release may change; recheck login and all links just before portal upload. Account recovery/site CRUD/gateway upgrades in the uncommitted working tree are not presented as available on the checked release. Repository: '+REPO)

s=clear_body(12,'Path to pilot and scale','Indicative sequence after submission, dependent on people, equipment and approvals.')
table(s,.42,1.86,9.15,['Stage','Work and stakeholders','Exit gate'],[
['1. Bench / governance','2–4 weeks after parts arrive. Embedded / Android leads, occupational reviewer and worker representatives.','Verified alerts, power and delivery; agreed privacy, language and response plans.'],
['2. Shadow feasibility','4–6 weeks at one consenting construction site. Proposed 3 crews; recruitment and sample size to be agreed.','Observe usability, availability, alerts and response. Existing controls remain authoritative.'],
['3. Controlled expansion','Safety and governance review, independent evaluation, then a second site / sector.','Resolve failures and regulatory needs; use a study suited to any effectiveness claim.']],[1.65,4.55,2.95],11.8,.78)
text(s,.45,4.91,8.95,.33,'Sustainability hypothesis: site subscription + maintained devices. Validate willingness to pay, supplier costs and paid weather access.',11.2,False,ACCENT)
note(s,12,'No pilot partner, clinician, worker representative, ethics approval or supplier commitment is secured by this document. Proposed sequence, not booked dates. Site permission, appropriate institutional ethics determination, Ghana Act 843/DPC obligations, controller/processor agreements, cross-border hosting and intended-use/device classification review are prerequisites where applicable. Begin in shadow mode; never increase heat exposure, withhold controls or delay care to test Exaclim. A small feasibility study cannot establish reduced heat illness. Scale only after reliability, worker acceptability, equitable access and site response capacity are demonstrated. Commercial use needs a viable maintenance/support model and appropriate weather-service access. Do not reuse the old station/two-badge allowance as a final price per worker.')

s=clear_body(13,'Pre-existing IP and third-party materials','Retain notices and confirm contributor / employer rights before commercial licensing.')
table(s,.42,1.87,9.15,['Material','Ownership / licence','Restriction / action'],[
['Exaclim source and content','Project repository; contributor / employer rights require confirmation.','No project-wide open-source licence selected. Confirm rights and hackathon terms.'],
['UI SDK','Apache-2.0, verified in installed package metadata.','Retain licence, copyright and applicable NOTICE; identify modifications.'],
['Hono, React, Material UI','MIT. Material UI interface upgrade is in development.','Retain MIT notices. Earlier hosted release also uses MIT Web Awesome components.'],
['Fonts, weather, template','Inter: OFL-1.1; weather: CC BY 4.0 / API terms; organizer-supplied template.','Preserve required attribution and font conditions; organizer logos are not Exaclim IP.']],[2.0,3.55,3.6],11.6,.69)
note(s,13,'Local package licence metadata verified on 20 November 2026: @ui-sdk/core/react/web 0.1.0-beta.3 Apache-2.0; hono 4.13.19 MIT; react 19.3.1 MIT; @mui/material 9.5.0 MIT; @awesome.me/webawesome 3.15.0 MIT; @fontsource/inter 5.3.0 OFL-1.1; cf 1.0.0-rc.2 MIT OR Apache-2.0. The UI SDK licence is Apache-2.0, not MIT. Material UI/React code is a working-tree upgrade, not a claim that the checked hosted release has finished migration. This editable deck adds native PowerPoint shapes and text; it retains organizer-provided artwork. No training dataset, clinical model weights or clinical certification is claimed. The team must verify actual contributor ownership and any employer/institution assignment or organizer entry-IP terms; those cannot be inferred from Git authorship. Design reference and skill guidance do not grant ownership of Deel branding. Font text uses Liberation Sans on export; organizer artwork remains as supplied.')

s=clear_body(14,'Conflict of interest declaration','Confirmed by the team on 20 November 2026.')
text(s,.5,2.0,8.8,.36,'No relationships to disclose',20,True,ACCENT)
text(s,.5,2.68,8.75,1.2,'The team declares no relationships with the organizers, partners or judges that require disclosure.',17)
text(s,.5,4.37,8.75,.52,'If a relevant relationship arises before judging, the team will update the declaration and notify the organizers.',13,False,MUTED)
note(s,14,'The user explicitly confirmed “No relationships to disclose” on 20 November 2026 in response to the required conflict-of-interest question. This declaration records that confirmation; it is not an independent investigation or an invented assertion. Update if circumstances change before judging.')

s=clear_body(15,'Sources and evidence register','Primary sources checked on 20 November 2026. Full URLs and claim notes are in the speaker notes.')
for i,(num,owner,title,url) in enumerate(refs):
 y=1.85+i*.43
 text(s,.45,y,.32,.24,num,11,True,ACCENT)
 text(s,.87,y,3.0,.26,owner,12,True)
 text(s,3.85,y,5.55,.29,title,11.8,False,MUTED,url)
text(s,.45,5.03,8.9,.20,'Evidence supports the rationale and tested workflows; it does not validate physical hardware or clinical effectiveness.',10,False,MUTED)
note(s,15,'\n\n'.join(f'[{n}] {owner}: {title}\n{u}\nAccessed 20 November 2026.' for n,owner,title,u in refs)+'\n\nAdditional data licence detail: https://open-meteo.com/en/licence. All listed primary web pages were retrieved successfully during preparation except the repository link, which is the user-authorized project source. A separate attempted NOAA equation page returned HTTP 403 and an attempted ILO publication URL returned 404; neither is used as verified direct-source evidence. The WHO/WMO release supplies the ILO-attributed global exposure statistic. No references are evidence of endorsement of Exaclim.')
# Closing slide 16 retains the supplied organizer artwork.

r.core_properties.title='Exaclim | Future Health Digital Innovation Challenge'
r.core_properties.subject='Climate-Resilient Worker Health'
r.core_properties.author='Exaclim project'
r.core_properties.keywords='occupational heat; shared Android gateway; worker privacy; Cloudflare'
ppt=OUT/'Exaclim_Future_Health_Submission.pptx';r.save(ppt)
# Preserve deck content as an editable machine-readable drafting record.
for i,s in enumerate(r.slides,1):
 editable.append({'slide':i,'text':[sh.text for sh in s.shapes if sh.has_text_frame],'notes':notes.get(str(i),'Original template retained; team details intentionally unfilled.' if i==2 else 'Organizer closing artwork retained.')})
(OUT/'submission-content.json').write_text(json.dumps(editable,indent=2,ensure_ascii=False)+'\n')
(ROOT/'docs/submission/submission-content.json').write_text(json.dumps(editable,indent=2,ensure_ascii=False)+'\n')
validation={'slides':len(r.slides),'capability_characters':len(cap),'team_slide_unchanged':False,'team_fields_intentionally_blank':True,'conflict_declaration':'No relationships to disclose; explicitly confirmed by user','deployed_signin':'Verified HTTP 200 login/logout on 20 November 2026','unreleased_features_not_claimed':True}
with zipfile.ZipFile(TEMPLATE) as a,zipfile.ZipFile(ppt) as b:validation['team_slide_unchanged']=etree.tostring(etree.fromstring(a.read('ppt/slides/slide2.xml')),method='c14n')==etree.tostring(etree.fromstring(b.read('ppt/slides/slide2.xml')),method='c14n')
assert validation['team_slide_unchanged']
(OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
print(ppt);print(json.dumps(validation))
