"""Build a compact lab report using the captured application screenshots."""
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import pypdfium2 as pdfium

root = Path(__file__).parent / 'report'
root.mkdir(exist_ok=True)
styles = getSampleStyleSheet()
styles['Normal'].fontName = 'Helvetica'
styles['Normal'].fontSize = 11
styles['Normal'].leading = 16
styles['Normal'].spaceAfter = 9
for name in ['Title', 'Heading1', 'Heading2']:
    styles[name].textColor = colors.black
styles['Title'].fontSize = 25
styles['Title'].leading = 30
styles['Heading1'].fontSize = 16
styles['Heading1'].spaceBefore = 13
styles['Heading1'].spaceAfter = 8
styles.add(ParagraphStyle('CaptionText', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=16))
styles.add(ParagraphStyle('TableText', parent=styles['Normal'], fontSize=9.5, leading=13, spaceAfter=0))
story = []
def para(text, style='Normal'):
    story.append(Paragraph(text, styles[style]))
def heading(text):
    para(text, 'Heading1')

para('MoodSense Project Report', 'Title')
para('Emotion Adaptive User Interface', 'Heading2')
para('MoodSense detects a mood from typed English text or an emoji selection and adapts the interface through colors, a 3D facial expression, and a suitable message. This report describes the implemented application and presents screenshots captured from six successful text-analysis runs.')
heading('Objective')
para('Design a Python-based application that accepts text or an emoji, identifies Happy, Sad, Angry, Love, Surprised, or Neutral, and changes the user interface accordingly. The application operates locally without API keys or an internet connection at runtime.')
heading('Technology and implementation')
para('<b>Backend:</b> Python 3 with a local HTTP server and the VADER sentiment library.<br/><b>Frontend:</b> HTML, CSS, JavaScript, and a locally bundled Three.js library.<br/><b>Interface:</b> empty text input, Analyze button, six emoji buttons, animated face, result message, and Reset.')
para('The initial lab implementation used CustomTkinter. Following the requested visual upgrade, the current main.py launches a browser interface with Three.js. The earlier CustomTkinter interface remains in ui.py; the screenshots in this report show the current browser version.')
heading('How it works')
para('The browser sends the typed text to the local Python endpoint. The detector combines VADER sentiment with emotion keywords and supported emojis. Nearby negation is checked before counting keyword cues. The strongest weighted category is returned; text without a meaningful signal falls back to Neutral. These weights are heuristic scores, not confidence probabilities.')
para('The returned emotion updates the page theme, face, selected mood, and message. Emoji buttons select a mood immediately. Reset clears the input and restores the welcome state. Empty input displays a validation message. If 3D is unavailable, the controls continue to work with a regular emoji display.')
heading('Main project files')
para('<b>main.py</b> launches the application; <b>web_app.py</b> serves the local interface and analysis endpoint; <b>emotion_detector.py</b> analyzes text; <b>emotion_data.py</b> stores emotion metadata; <b>web/controller.js</b> manages interactions; <b>web/app.js</b> draws the animated face; <b>web/styles.css</b> controls the responsive layout.')

cases = [
    ('happy', 'I am very happy today', 'Warm colors and a small open smile.'),
    ('sad', 'I feel lonely and sad', 'Soft blue colors, raised inner brows, a gentle frown, and a small tear.'),
    ('angry', 'I am extremely angry', 'Angled eyebrows and a calming message.'),
    ('love', 'I love this so much', 'Pink colors, heart eyes, and a warm message.'),
    ('surprised', "Wow, I didn't expect this!", 'Purple colors, widened eyes, and a small open mouth.'),
    ('neutral', 'I am okay', 'A balanced theme and a quiet facial expression.'),
]
for start in range(0, 6, 2):
    story.append(PageBreak())
    heading('Application screenshots')
    if start == 0:
        para('Actual browser captures at a 1093 by 614 viewport. Each result was obtained by entering the shown text and clicking Analyze my mood.', 'CaptionText')
    for index in range(start, start + 2):
        key, sentence, detail = cases[index]
        story.append(Image(str(root / 'screenshots' / f'{key}.png'), width=499, height=499 * 614 / 1093))
        para(f'<b>Figure {index + 1} {key.title()}</b><br/>Input: {sentence}<br/>{detail}', 'CaptionText')

story.append(PageBreak())
heading('Testing and results')
para('Browser regression checks passed for the cases below. The six screenshots provide evidence of the requested mood outputs. Additional checks exercise the actual controls and failure messages.')
rows = [ ['Check', 'Observed result'] ]
for key, sentence, _ in cases:
    rows.append([sentence, key.title() + ' displayed'])
rows += [
    ['Empty or whitespace-only input', 'Validation shown; no analysis sent'],
    ['Unknown sentence', 'Neutral returned'],
    ['I am not happy about this', 'Sad returned'],
    ['Supported emoji-only input', 'Corresponding mood returned'],
    ['All six emoji buttons', 'Immediate mood and theme update'],
    ['Reset', 'Empty input and welcome state restored'],
    ['3D script unavailable', 'Text analysis works with emoji fallback'],
    ['Analysis request fails', 'Visible error; Analyze stays usable'],
    ['Desktop viewports from 1024 by 600', 'Controls fit without page scrolling'],
]
table = Table([[Paragraph(cell, styles['TableText']) for cell in row] for row in rows], colWidths=[247,252], repeatRows=1)
table.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9edf3')),
    ('GRID',(0,0),(-1,-1),.5,colors.HexColor('#d9d9d9')),
    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),8),
    ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6),
]))
story.append(table)
heading('How to run')
para('Open the project folder in VS Code. In its terminal, run <b>python -m pip install -r requirements.txt</b>, then <b>python main.py</b>. Keep the terminal open and use the browser URL printed by Python. VS Code Live Server alone does not run the Python analyzer.')
heading('Limitations and conclusion')
para('VADER and keyword rules do not reliably interpret sarcasm, complex mixed emotions, or unsupported languages. Results are an interface demonstration, not a psychological assessment. Within these limits, MoodSense demonstrates the complete interaction from text or emoji input to an adaptive, animated result.')

def footer(canvas, document):
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.HexColor('#687080'))
    canvas.drawString(48, 25, 'MoodSense project report')
    canvas.drawRightString(547, 25, str(document.page))

output = root / 'MoodSense_Project_Report.pdf'
doc = SimpleDocTemplate(str(output), pagesize=(595,842), rightMargin=48, leftMargin=48, topMargin=38, bottomMargin=42)
doc.build(story, onFirstPage=footer, onLaterPages=footer)
pdf = pdfium.PdfDocument(str(output))
qa = root / 'qa'
qa.mkdir(exist_ok=True)
for i, page in enumerate(pdf):
    page.render(scale=1.4).to_pil().save(qa / f'page-{i+1}.png')
print(f'Created {output} with {len(pdf)} pages')
