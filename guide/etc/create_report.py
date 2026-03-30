"""
Generate Final Report DOCX for CST8507 Assignment 2
AI Textbook Q&A System
"""
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(BASE)

doc = Document()

# ── Page setup ──────────────────────────────────────────
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.54)
    section.right_margin = Cm(2.54)

# ── Default font ────────────────────────────────────────
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(12)
style.paragraph_format.space_after = Pt(6)
style.paragraph_format.line_spacing = 1.15

# ── Heading styles ──────────────────────────────────────
for i in range(1, 4):
    h = doc.styles[f'Heading {i}']
    h.font.name = 'Times New Roman'
    h.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
    if i == 1:
        h.font.size = Pt(18)
        h.font.bold = True
    elif i == 2:
        h.font.size = Pt(14)
        h.font.bold = True
    else:
        h.font.size = Pt(12)
        h.font.bold = True

def add_page_numbers(doc):
    """Add page numbers to header (top right)"""
    for section in doc.sections:
        header = section.header
        header.is_linked_to_previous = False
        p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.style.font.size = Pt(10)
        p.style.font.name = 'Times New Roman'
        
        run = p.add_run()
        fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
        run._r.append(fldChar1)
        
        run2 = p.add_run()
        instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
        run2._r.append(instrText)
        
        run3 = p.add_run()
        fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
        run3._r.append(fldChar2)

def add_figure(doc, img_path, caption, width=6.0):
    """Add image with caption"""
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(img_path, width=Inches(width))
        
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = cap.add_run(caption)
        run.font.size = Pt(10)
        run.font.italic = True
        run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    else:
        doc.add_paragraph(f"[Image not found: {img_path}]")

def add_table_row(table, cells_data, bold=False, bg_color=None):
    row = table.add_row()
    for i, text in enumerate(cells_data):
        cell = row.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        run = p.add_run(str(text))
        run.font.size = Pt(10)
        run.font.name = 'Times New Roman'
        if bold:
            run.font.bold = True
        if bg_color:
            shading = parse_xml(
                f'<w:shd {nsdecls("w")} w:fill="{bg_color}"/>'
            )
            cell._tc.get_or_add_tcPr().append(shading)


# ═══════════════════════════════════════════════════════════
#  COVER PAGE
# ═══════════════════════════════════════════════════════════
for _ in range(6):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('AI Textbook Q&A System')
run.font.size = Pt(28)
run.font.bold = True
run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('A RAG-Based Educational Question Answering System\nwith Deep Source Tracing & ROS 2 Voice Integration')
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0x5B, 0x6A, 0xBF)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('CST8507: Natural Language Processing\nAssignment 2 — Final Report')
run.font.size = Pt(14)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Hye Ran Yoo (041145212)\nPeng Wang (041145555)')
run.font.size = Pt(14)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('April 3, 2026')
run.font.size = Pt(12)
run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Algonquin College')
run.font.size = Pt(12)
run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════
#  TABLE OF CONTENTS
# ═══════════════════════════════════════════════════════════
doc.add_heading('Table of Contents', level=1)
toc_items = [
    ("1. Abstract", "3"),
    ("2. Introduction", "3"),
    ("3. Dataset", "4"),
    ("4. Method", "5"),
    ("   4.1 Preprocessing Pipeline", "5"),
    ("   4.2 Hybrid Retrieval Architecture", "5"),
    ("   4.3 Deep Source Tracing", "6"),
    ("5. User Interface", "6"),
    ("6. Evaluation", "7"),
    ("7. Part 2: ROS 2 Integration", "8"),
    ("   7.1 Architecture", "8"),
    ("   7.2 Implementation", "8"),
    ("8. Reproducibility Details", "9"),
    ("9. Challenges and Solutions", "9"),
    ("10. Discussion and Future Work", "10"),
    ("11. References", "10"),
]

for item, page in toc_items:
    p = doc.add_paragraph()
    run = p.add_run(item)
    run.font.size = Pt(12)
    if not item.startswith("   "):
        run.font.bold = True
    p.add_run('\t' * 8 + page).font.size = Pt(12)

doc.add_page_break()


# ═══════════════════════════════════════════════════════════
#  1. ABSTRACT
# ═══════════════════════════════════════════════════════════
doc.add_heading('1. Abstract', level=1)
doc.add_paragraph(
    'This report presents the design, implementation, and evaluation of an AI Textbook Q&A System '
    'that leverages Retrieval-Augmented Generation (RAG) to answer educational questions across 46 '
    'canonical AI/ML textbooks containing 85,356 text chunks. Our system implements a hybrid retrieval '
    'architecture combining four complementary methods: BM25 keyword search (SQLite FTS5), semantic '
    'vector search (ChromaDB with all-MiniLM-L6-v2), hierarchical TOC tree navigation, and structured '
    'metadata filtering. Results are fused using Reciprocal Rank Fusion (RRF) before answer generation '
    'via a local Ollama LLM (qwen2.5:0.5b, ~0.4GB). A key innovation is deep source tracing, which '
    'provides pixel-level traceability to the original PDF page and highlighted bounding box region. '
    'The system features a Streamlit web interface with an integrated PDF viewer and is extended in '
    'Part 2 as a ROS 2 Humble voice-interactive pipeline deployed on an Ubuntu 22.04 loaner laptop.'
)


# ═══════════════════════════════════════════════════════════
#  2. INTRODUCTION
# ═══════════════════════════════════════════════════════════
doc.add_heading('2. Introduction', level=1)
doc.add_paragraph(
    'Students studying AI and machine learning face a significant challenge: navigating across dozens '
    'of textbooks to find relevant information for specific topics. With over 46 textbooks spanning '
    'machine learning, natural language processing, computer vision, mathematics, and software '
    'engineering, manually searching through thousands of pages is impractical and time-consuming.'
)
doc.add_paragraph(
    'This project addresses this problem by building a RAG-based educational Q&A system that enables '
    'users to ask natural language questions and receive accurate, sourced answers derived from a '
    'curated collection of canonical textbooks. Unlike standard RAG implementations that merely cite '
    'book titles, our system provides deep source tracing with clickable references that open the '
    'original PDF page with the relevant region highlighted via bounding box coordinates.'
)

p = doc.add_paragraph()
run = p.add_run('Research Question: ')
run.font.bold = True
run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
p.add_run(
    'How can we build a transparent, traceable educational Q&A system for AI/ML learning that '
    'provides verifiable answers with pixel-level source tracing?'
)

doc.add_paragraph(
    'The system is implemented in two parts: Part 1 focuses on the RAG pipeline with a Streamlit '
    'web interface, while Part 2 extends it as a ROS 2 Humble voice-interactive pipeline that enables '
    'spoken questions and synthesized speech answers, suitable for robot deployment.'
)


# ═══════════════════════════════════════════════════════════
#  3. DATASET
# ═══════════════════════════════════════════════════════════
doc.add_heading('3. Dataset', level=1)
doc.add_paragraph(
    'Our dataset consists of 46 open-access and educational-use AI/ML textbooks, totaling approximately '
    '500MB of PDF documents. The textbooks were processed using MinerU with DocLayout-YOLO to extract '
    'text, tables, formulas, and figures while preserving layout information and spatial coordinates. '
    'After preprocessing, the dataset yields 85,356 text chunks stored in a SQLite database with '
    'corresponding vector embeddings in ChromaDB.'
)

# Dataset table
table = doc.add_table(rows=1, cols=4)
table.style = 'Light Grid Accent 1'
table.alignment = WD_TABLE_ALIGNMENT.CENTER

hdr = table.rows[0].cells
for i, text in enumerate(['Domain', 'Books', 'Examples', 'Key Topics']):
    hdr[i].text = text
    for p in hdr[i].paragraphs:
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(10)

data = [
    ['Machine Learning', '8', 'ISLR, ESL, PRML, PML, Deep Learning', 'Classification, regression, neural networks'],
    ['Mathematics', '5', 'MML, Convex Optimization, Snell Probability', 'Linear algebra, optimization, statistics'],
    ['NLP', '4', 'SLP3, Eisenstein NLP, Manning IR', 'Language models, parsing, information retrieval'],
    ['Computer Vision', '1', 'Szeliski Computer Vision', '3D reconstruction, image processing'],
    ['Reinforcement Learning', '2', 'Sutton & Barto, Hamilton GRL', 'MDPs, policy gradient, graph RL'],
    ['Programming', '5+', 'Fluent Python, Clean Code, DDIA', 'Software design, systems, databases'],
    ['Security / Web', '5+', 'Black Hat Python, SRE, SWE', 'Security, reliability, web engineering'],
]
for row_data in data:
    add_table_row(table, row_data)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('\nTable 1: Dataset composition by domain (46 textbooks, 85,356 chunks, ~500MB)')
run.font.size = Pt(10)
run.font.italic = True

# Library screenshot
add_figure(doc, os.path.join(PROJECT, 'screenshop5.png'),
           'Figure 1: Library View showing all 46 textbooks with cover art, author, and page count',
           width=5.5)


# ═══════════════════════════════════════════════════════════
#  4. METHOD
# ═══════════════════════════════════════════════════════════
doc.add_heading('4. Method', level=1)

doc.add_heading('4.1 Preprocessing Pipeline', level=2)
doc.add_paragraph(
    'Each PDF textbook is processed through a 5-stage pipeline:'
)
doc.add_paragraph('1. MinerU + DocLayout-YOLO: Layout analysis detecting 10 element categories '
                  '(text, title, figure, table, formula, header, footer, caption, reference, equation)', style='List Number')
doc.add_paragraph('2. Text/Table/Formula Extraction: Content is extracted with spatial coordinates '
                  '(bounding boxes) preserved for each element', style='List Number')
doc.add_paragraph('3. Intelligent Chunking: Text is split into semantically meaningful chunks using '
                  'section boundaries with metadata (book, chapter, page, content type)', style='List Number')
doc.add_paragraph('4. Dual Indexing: Each chunk is indexed in both SQLite FTS5 (for keyword search) '
                  'and ChromaDB (for semantic vector search using all-MiniLM-L6-v2 embeddings)', style='List Number')
doc.add_paragraph('5. TOC Tree Construction: Hierarchical table-of-contents trees are built for each '
                  'book to enable structured navigation and LLM-guided retrieval', style='List Number')

doc.add_heading('4.2 Hybrid Retrieval Architecture', level=2)
doc.add_paragraph(
    'Our system employs a 4-method hybrid retrieval architecture, each method contributing unique '
    'strengths to maximize recall and precision:'
)

# Architecture description table
arch_table = doc.add_table(rows=1, cols=3)
arch_table.style = 'Light Grid Accent 1'
hdr = arch_table.rows[0].cells
for i, text in enumerate(['Method', 'Technology', 'Description']):
    hdr[i].text = text
    for p in hdr[i].paragraphs:
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(10)

arch_data = [
    ['1. BM25 Keyword', 'SQLite FTS5', 'Fast exact keyword matching using TF-IDF-like scoring'],
    ['2. Semantic Vector', 'ChromaDB + MiniLM', 'Embedding-based similarity using all-MiniLM-L6-v2 (384-dim)'],
    ['3. TOC Tree', 'LLM Reasoning', 'Hierarchical TOC navigation using LLM to identify relevant sections'],
    ['4. Metadata Filter', 'Structured Query', 'Filtering by book title, chapter, page number, content type'],
]
for row_data in arch_data:
    add_table_row(arch_table, row_data)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Table 2: Four retrieval methods in the hybrid architecture')
run.font.size = Pt(10)
run.font.italic = True

doc.add_paragraph(
    '\nResults from all four methods are combined using Reciprocal Rank Fusion (RRF), which produces '
    'a unified ranking by computing: RRF_score(d) = sum(1 / (k + rank_i(d))) for each document d '
    'across all methods i, where k=60 is the smoothing constant. This fused ranking is then passed '
    'to the Ollama LLM (qwen2.5:0.5b, ~0.4GB memory footprint) to generate a contextual answer.'
)

doc.add_heading('4.3 Deep Source Tracing', level=2)
doc.add_paragraph(
    'A key innovation of our system is deep source tracing. Unlike standard RAG systems that only '
    'cite book titles, our approach stores bounding box coordinates (x1, y1, x2, y2) for each text '
    'chunk extracted during preprocessing. When a user clicks "View PDF" on a search result, the '
    'system opens an inline PDF viewer at the exact page with the source region highlighted in yellow. '
    'This enables instant visual verification against the original source material, ensuring '
    'transparency and academic integrity.'
)


# ═══════════════════════════════════════════════════════════
#  5. USER INTERFACE
# ═══════════════════════════════════════════════════════════
doc.add_heading('5. User Interface', level=1)
doc.add_paragraph(
    'The system provides a Streamlit-based web interface running at http://localhost:5173, featuring:'
)
doc.add_paragraph('Search Interface: Natural language query input with 4 retrieval method toggles, '
                  'adjustable top-K sources slider (1-20), and library collection filter for selecting '
                  'specific textbooks', style='List Bullet')
doc.add_paragraph('System Answer: AI-generated response with related topic tag suggestions for '
                  'follow-up exploration', style='List Bullet')
doc.add_paragraph('Source Documents: Ranked list of retrieved chunks with book title, chapter, page number, '
                  'section heading, relevance score, and a "View PDF" button', style='List Bullet')
doc.add_paragraph('PDF Viewer: Inline document viewer with page navigation, zoom controls, '
                  'one-page/two-page modes, full-screen mode, and highlighted source region overlay',
                  style='List Bullet')
doc.add_paragraph('Library Tab: Browse all 46 textbooks with cover art, author, year, and page count',
                  style='List Bullet')

# Screenshots
add_figure(doc, os.path.join(PROJECT, 'screenshop0.png'),
           'Figure 2: Search interface with model selector, 4 retrieval toggles, source slider, and library filter',
           width=5.5)

add_figure(doc, os.path.join(PROJECT, 'screenshop4.png'),
           'Figure 3: Search results for "What is SVM?" showing RAG answer, related topics, source books '
           'with relevance scores, and inline PDF viewer (Pattern Recognition and Machine Learning, p.354)',
           width=6.0)


# ═══════════════════════════════════════════════════════════
#  6. EVALUATION
# ═══════════════════════════════════════════════════════════
doc.add_heading('6. Evaluation', level=1)
doc.add_paragraph(
    'To evaluate system performance, we prepared 20 test questions spanning multiple AI/ML domains. '
    'Each question was run through the system and manually assessed using the following scoring criteria:'
)

# Scoring table
score_table = doc.add_table(rows=1, cols=2)
score_table.style = 'Light Grid Accent 1'
hdr = score_table.rows[0].cells
hdr[0].text = 'Score'
hdr[1].text = 'Meaning'
for p in hdr[0].paragraphs:
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(10)
for p in hdr[1].paragraphs:
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(10)

add_table_row(score_table, ['1.0', 'Correct - Answer fully addresses the question with relevant sources'])
add_table_row(score_table, ['0.5', 'Partially Correct - Answer partially addresses the question'])
add_table_row(score_table, ['0.0', 'Incorrect - Answer does not address the question'])

p = doc.add_paragraph()
run = p.add_run('\nTable 3: Scoring criteria for manual evaluation')
run.font.size = Pt(10)
run.font.italic = True
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 20 Questions table
doc.add_paragraph()
doc.add_heading('6.1 Test Questions', level=2)

q_table = doc.add_table(rows=1, cols=4)
q_table.style = 'Light Grid Accent 1'
hdr = q_table.rows[0].cells
for i, text in enumerate(['#', 'Question', 'Domain', 'Score']):
    hdr[i].text = text
    for p in hdr[i].paragraphs:
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(10)

questions = [
    ('1', 'What is neural attention?', 'Deep Learning', ''),
    ('2', 'What is the difference between generative and discriminative classifiers?', 'ML', ''),
    ('3', 'What is the gradient for logistic regression?', 'ML / Math', ''),
    ('4', 'What is an N-gram language model?', 'NLP', ''),
    ('5', 'What is skip-gram in Word2Vec?', 'NLP', ''),
    ('6', 'How do RNNs work as language models?', 'Deep Learning', ''),
    ('7', 'What is a 3D rigid body transformation?', 'CV / Math', ''),
    ('8', 'Why is weight initialization important in deep learning?', 'Deep Learning', ''),
    ('9', 'What is network depth in neural networks?', 'Deep Learning', ''),
    ('10', 'What is cost-sensitive classification?', 'ML', ''),
    ('11', 'What is TF-IDF?', 'NLP / IR', ''),
    ('12', 'What is backpropagation?', 'Deep Learning', ''),
    ('13', 'What is the Transformer architecture?', 'NLP / DL', ''),
    ('14', 'What is Word2Vec?', 'NLP', ''),
    ('15', 'What is Named Entity Recognition?', 'NLP', ''),
    ('16', 'What is beam search?', 'NLP', ''),
    ('17', 'What is dropout regularization?', 'Deep Learning', ''),
    ('18', 'What is batch normalization?', 'Deep Learning', ''),
    ('19', 'What is transfer learning?', 'ML / DL', ''),
    ('20', 'What is the BLEU score?', 'NLP', ''),
]
for q in questions:
    add_table_row(q_table, q)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Table 4: 20 evaluation questions across AI/ML/NLP domains (Score column: fill after testing)')
run.font.size = Pt(10)
run.font.italic = True

doc.add_paragraph(
    '\nFor each question, the top 3 retrieved documents are listed and marked for relevance. '
    'The final accuracy score is calculated as the mean score across all 20 questions. '
    'Target accuracy: >80%.'
)


# ═══════════════════════════════════════════════════════════
#  7. PART 2: ROS 2 INTEGRATION
# ═══════════════════════════════════════════════════════════
doc.add_heading('7. Part 2: ROS 2 Integration', level=1)

doc.add_heading('7.1 Architecture', level=2)
doc.add_paragraph(
    'The RAG pipeline is extended into a voice-interactive system using ROS 2 Humble on Ubuntu 22.04. '
    'The system consists of 5 ROS 2 nodes communicating via topics and services:'
)

# Node table
node_table = doc.add_table(rows=1, cols=4)
node_table.style = 'Light Grid Accent 1'
hdr = node_table.rows[0].cells
for i, text in enumerate(['Node', 'Package', 'Input', 'Output']):
    hdr[i].text = text
    for p in hdr[i].paragraphs:
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(10)

nodes = [
    ['1. RecordingPublisher', 'aisd_hearing', 'Microphone + Silero VAD', '/recording topic'],
    ['2. WordsPublisher', 'aisd_hearing', '/recording', '/words topic (Whisper STT)'],
    ['3. OllamaPublisher', 'aisd_hearing', '/words', '/ollama_reply topic (RAG + LLM)'],
    ['4. SpeakClient', 'aisd_hearing', '/ollama_reply', '/speak service call'],
    ['5. SpeakService', 'aisd_speaking', '/speak service', 'Audio output (gTTS)'],
]
for n in nodes:
    add_table_row(node_table, n)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Table 5: ROS 2 pipeline nodes and their communication flow')
run.font.size = Pt(10)
run.font.italic = True

doc.add_paragraph(
    '\nThe pipeline flow is: Voice Input -> Silero VAD -> Whisper STT -> RAG + Ollama LLM -> '
    'gTTS -> Speaker Output. All 5 nodes run concurrently in a tmux session with labeled panes '
    'for real-time monitoring.'
)

doc.add_heading('7.2 Implementation', level=2)
doc.add_paragraph(
    'The key contribution is ollama_publisher.py, a new ROS 2 node that bridges Part 1 (RAG) '
    'and Part 2 (ROS 2). It subscribes to the /words topic (Whisper output), loads a knowledge.txt '
    'file at startup, constructs a system prompt with RAG context, queries the local Ollama API '
    '(localhost:11434) using qwen2.5:0.5b, and publishes the response to /ollama_reply. '
    'A 15-second cooldown timer prevents the system from processing its own TTS output (echo loop). '
    'Custom hallucination filtering checks for repetition patterns, known Whisper artifacts, and '
    'trigram analysis before forwarding input to the LLM.'
)

doc.add_paragraph(
    'Deployment is automated via start_loaner.bat which: (1) SCP syncs source files to the laptop, '
    '(2) kills any existing tmux session, (3) runs colcon build --symlink-install, and '
    '(4) launches 5 tmux panes with labeled node identifiers (e.g., "[1/5 MICROPHONE]").'
)

# ROS 2 Demo screenshot
add_figure(doc, os.path.join(PROJECT, 'screenshop3.png'),
           'Figure 4: ROS 2 tmux session showing all 5 nodes in operation - voice input to speech output pipeline',
           width=5.5)


# ═══════════════════════════════════════════════════════════
#  8. REPRODUCIBILITY
# ═══════════════════════════════════════════════════════════
doc.add_heading('8. Reproducibility Details', level=1)

doc.add_heading('Platform and System Setup', level=3)
doc.add_paragraph('Part 1 (RAG + Web UI):', style='List Bullet')
doc.add_paragraph('  - OS: Windows 11 with Python 3.10+', style='List Bullet')
doc.add_paragraph('  - Backend: FastAPI server on port 8000', style='List Bullet')
doc.add_paragraph('  - Frontend: Streamlit (Vite-based) on port 5173', style='List Bullet')
doc.add_paragraph('  - Database: SQLite FTS5 + ChromaDB', style='List Bullet')
doc.add_paragraph('  - LLM: Ollama with qwen2.5:0.5b (localhost:11434)', style='List Bullet')

doc.add_paragraph('Part 2 (ROS 2 Voice Pipeline):', style='List Bullet')
doc.add_paragraph('  - OS: Ubuntu 22.04 (loaner laptop)', style='List Bullet')
doc.add_paragraph('  - ROS 2: Humble Hawksbill', style='List Bullet')
doc.add_paragraph('  - STT: faster-whisper (int8 quantization)', style='List Bullet')
doc.add_paragraph('  - TTS: gTTS (Google Text-to-Speech)', style='List Bullet')
doc.add_paragraph('  - VAD: Silero VAD for voice activity detection', style='List Bullet')

doc.add_heading('Execution Steps', level=3)
doc.add_paragraph('Part 1: pip install -r requirements.txt && ollama pull qwen2.5:0.5b && '
                  'python backend/main.py (start API) && cd frontend && npm run dev (start UI)')
doc.add_paragraph('Part 2: Run start_loaner.bat from Windows to deploy and launch on the laptop')

doc.add_heading('Source Code', level=3)
doc.add_paragraph('GitHub: github.com/LannieYoo/nlp_project')
doc.add_paragraph('Key files: backend/main.py, frontend/src/*, ros2/ollama_publisher.py, '
                  'ros2/knowledge.txt, ros2/run_loaner.sh')


# ═══════════════════════════════════════════════════════════
#  9. CHALLENGES
# ═══════════════════════════════════════════════════════════
doc.add_heading('9. Challenges and Solutions', level=1)

challenges = [
    ('Whisper Hallucinations',
     'Whisper generates phantom text on silence or background noise.',
     'Implemented Silero VAD pre-filtering + custom hallucination detector with repetition checking, '
     'known artifact phrase matching, and trigram frequency analysis.'),
    ('Echo Loop (TTS to Mic)',
     'The microphone picks up the TTS audio output, creating an infinite feedback loop.',
     'Added a 15-second cooldown timer after each LLM reply publication, during which all incoming '
     'Whisper transcriptions are ignored.'),
    ('Resource Constraints',
     'Three AI models (Whisper, Ollama, gTTS) must run simultaneously on a single CPU laptop.',
     'Selected qwen2.5:0.5b (0.4GB) for LLM and faster-whisper with int8 quantization. Total memory '
     'footprint stays under 1.5GB, meeting the assignment requirement.'),
    ('Cross-Platform Deployment',
     'Development on Windows but deployment target is Ubuntu 22.04 laptop.',
     'Created automated batch/shell scripts: SCP file sync, colcon build, and tmux session management. '
     'One-click deployment via start_loaner.bat from Windows.'),
    ('Complex PDF Layout Parsing',
     'Academic textbooks contain complex layouts with tables, formulas, figures, and multi-column text.',
     'Adopted MinerU with DocLayout-YOLO which detects 10 element categories and preserves spatial '
     'bounding box coordinates for each element during extraction.'),
]

ch_table = doc.add_table(rows=1, cols=3)
ch_table.style = 'Light Grid Accent 1'
hdr = ch_table.rows[0].cells
for i, text in enumerate(['Challenge', 'Problem', 'Solution']):
    hdr[i].text = text
    for p in hdr[i].paragraphs:
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(10)

for ch in challenges:
    add_table_row(ch_table, ch)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Table 6: Key challenges encountered and their solutions')
run.font.size = Pt(10)
run.font.italic = True


# ═══════════════════════════════════════════════════════════
#  10. DISCUSSION & FUTURE WORK
# ═══════════════════════════════════════════════════════════
doc.add_heading('10. Discussion and Future Work', level=1)

doc.add_heading('Current Limitations', level=2)
doc.add_paragraph('Small LLM (0.5B parameters) limits generation quality for complex multi-hop questions',
                  style='List Bullet')
doc.add_paragraph('Single-turn Q&A only; no conversation memory or context carryover',
                  style='List Bullet')
doc.add_paragraph('Static knowledge file for ROS 2 Part 2 (simplified from full RAG pipeline)',
                  style='List Bullet')
doc.add_paragraph('CPU-only inference results in ~10-15 second response latency',
                  style='List Bullet')
doc.add_paragraph('English-only knowledge base content', style='List Bullet')

doc.add_heading('Future Work', level=2)
doc.add_paragraph('Upgrade to larger model (qwen2.5:3b) with GPU acceleration for faster, '
                  'higher-quality responses', style='List Bullet')
doc.add_paragraph('Multi-turn conversation support with context memory for follow-up questions',
                  style='List Bullet')
doc.add_paragraph('Dynamic knowledge base updates via API integration',
                  style='List Bullet')
doc.add_paragraph('Multi-language support (Korean, Chinese, English) for international students',
                  style='List Bullet')
doc.add_paragraph('Integration with iRobot Create 3 hardware for physical robot deployment',
                  style='List Bullet')
doc.add_paragraph('Fine-tuning on educational domain data to improve answer accuracy',
                  style='List Bullet')
doc.add_paragraph('Real-time collaborative Q&A and mobile app integration',
                  style='List Bullet')

doc.add_heading('Conclusion', level=2)
doc.add_paragraph(
    'We successfully built a complete voice-interactive RAG pipeline spanning from 46 AI/ML textbooks '
    'to real-time voice Q&A on a ROS 2 platform. The system demonstrates that meaningful AI-powered '
    'educational assistance is achievable with a memory footprint under 1.5GB, using a 0.4GB language '
    'model combined with hybrid retrieval and deep source tracing for transparency and verifiability.'
)


# ═══════════════════════════════════════════════════════════
#  11. REFERENCES
# ═══════════════════════════════════════════════════════════
doc.add_heading('11. References', level=1)

refs = [
    '[1] Ollama. "Ollama - Local Large Language Models." https://ollama.com/',
    '[2] ChromaDB. "Chroma - the AI-native open-source embedding database." https://www.trychroma.com/',
    '[3] SQLite FTS5. "Full-Text Search Extension." https://www.sqlite.org/fts5.html',
    '[4] Reimers, N. and Gurevych, I. "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." EMNLP 2019.',
    '[5] MinerU. "Open-source tool for document layout analysis." https://github.com/opendatalab/MinerU',
    '[6] ROS 2 Humble. "Robot Operating System 2." https://docs.ros.org/en/humble/',
    '[7] Radford, A. et al. "Robust Speech Recognition via Large-Scale Weak Supervision." OpenAI 2023.',
    '[8] Cormack, G. et al. "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods." SIGIR 2009.',
    '[9] Streamlit. "The fastest way to build and share data apps." https://streamlit.io/',
    '[10] Qwen Team. "Qwen2.5: A Large Language Model Series." Alibaba Cloud 2024.',
]

for ref in refs:
    p = doc.add_paragraph(ref)
    p.paragraph_format.space_after = Pt(4)
    for run in p.runs:
        run.font.size = Pt(11)


# ═══════════════════════════════════════════════════════════
#  ADD PAGE NUMBERS
# ═══════════════════════════════════════════════════════════
add_page_numbers(doc)

# ═══════════════════════════════════════════════════════════
#  SAVE
# ═══════════════════════════════════════════════════════════
out = os.path.join(PROJECT, 'guide', 'AI_Textbook_QA_System_Report.docx')
doc.save(out)
print(f'[OK] Report saved to: {out}')
