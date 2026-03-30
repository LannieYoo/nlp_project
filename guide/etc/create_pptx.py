"""
Generate PowerPoint Presentation for CST8507 Assignment 2
AI Textbook Q&A System - Part 1 (RAG) + Part 2 (ROS 2)
EXPANDED VERSION - screenshop0, 3, 4, 5 only
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import os

DARK_BG = RGBColor(0x1A, 0x1A, 0x2E)
ACCENT = RGBColor(0x5B, 0x6A, 0xBF)
ACCENT2 = RGBColor(0xE8, 0x4D, 0x4D)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xCC, 0xCC, 0xCC)
MED_GRAY = RGBColor(0x99, 0x99, 0x99)
HIGHLIGHT = RGBColor(0xFF, 0xD7, 0x00)
GREEN = RGBColor(0x4E, 0xC9, 0xB0)
ORANGE = RGBColor(0xFF, 0xA5, 0x00)
DARK_CARD = RGBColor(0x25, 0x25, 0x40)

BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(BASE)
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)


def set_bg(slide, color=DARK_BG):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color

def tb(slide, l, t, w, h, text, sz=18, c=WHITE, b=False, al=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    box.text_frame.word_wrap = True
    p = box.text_frame.paragraphs[0]
    p.text = text; p.font.size = Pt(sz); p.font.color.rgb = c
    p.font.bold = b; p.font.name = "Segoe UI"; p.alignment = al
    return box

def ml(slide, l, t, w, h, lines, sz=18, c=WHITE, sp=8):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if line.startswith(">>"):
            p.text = line[2:].strip(); p.font.bold = True; p.font.color.rgb = HIGHLIGHT
        else:
            p.text = line; p.font.color.rgb = c
        p.font.size = Pt(sz); p.font.name = "Segoe UI"; p.space_after = Pt(sp)
    return box

def bar(slide, t=1.85, l=1.0, w=2.5):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(0.06))
    s.fill.solid(); s.fill.fore_color.rgb = ACCENT; s.line.fill.background()

def title_slide(slide, title, sub=""):
    set_bg(slide)
    tb(slide, 1.0, 0.6, 11.0, 0.8, title, sz=36, b=True)
    bar(slide)
    if sub: tb(slide, 1.0, 2.0, 11.0, 0.5, sub, sz=18, c=LIGHT_GRAY)

def bx(slide, l, t, w, h, text, fc=ACCENT, tc=WHITE, sz=14):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = fc; s.line.fill.background()
    tf = s.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = text; p.font.size = Pt(sz)
    p.font.color.rgb = tc; p.font.bold = True; p.font.name = "Segoe UI"
    p.alignment = PP_ALIGN.CENTER
    return s

def arrow(slide, l, t, w=0.6):
    s = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(l), Inches(t), Inches(w), Inches(0.35))
    s.fill.solid(); s.fill.fore_color.rgb = HIGHLIGHT; s.line.fill.background()

def card(slide, l, t, w, h):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = DARK_CARD
    s.line.color.rgb = RGBColor(0x3A, 0x3A, 0x55); s.line.width = Pt(1)

def img(name):
    return os.path.join(PROJECT, name)


###############################################################
# 1. TITLE
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s)
tb(s, 1.5, 1.2, 10, 1.2, "AI Textbook Q&A System", sz=52, b=True, al=PP_ALIGN.CENTER)
tb(s, 1.5, 2.6, 10, 0.8,
   "A RAG-Based Educational Question Answering System\nwith Deep Source Tracing & ROS 2 Voice Integration",
   sz=24, c=ACCENT, al=PP_ALIGN.CENTER)
sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.5), Inches(3.8), Inches(4), Inches(0.06))
sh.fill.solid(); sh.fill.fore_color.rgb = ACCENT; sh.line.fill.background()
tb(s, 1.5, 4.2, 10, 0.5, "Hye Ran Yoo (041145212)  |  Peng Wang (041145555)", sz=22, al=PP_ALIGN.CENTER)
tb(s, 1.5, 5.2, 10, 0.8,
   "CST8507: Natural Language Processing\nApril 3, 2026", sz=16, c=LIGHT_GRAY, al=PP_ALIGN.CENTER)
bx(s, 4.0, 6.2, 2.2, 0.5, "Part 1: RAG Pipeline", fc=ACCENT, sz=12)
bx(s, 7.0, 6.2, 2.2, 0.5, "Part 2: ROS 2 Voice", fc=ACCENT2, sz=12)


###############################################################
# 2. AGENDA
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6]); title_slide(s, "Agenda")
ml(s, 1.0, 2.3, 5.5, 4.5, [
    ">> Part 1: RAG Pipeline",
    "  1. Introduction & Motivation",
    "  2. Dataset (46 Textbooks)",
    "  3. Preprocessing Pipeline",
    "  4. Hybrid Retrieval Architecture",
    "  5. Deep Source Tracing",
    "  6. Streamlit UI Demo",
    "  7. Evaluation (20 Questions)",
], sz=18)
ml(s, 7.0, 2.3, 5.5, 4.5, [
    ">> Part 2: ROS 2 Integration",
    "  8. ROS 2 Architecture (5 Nodes)",
    "  9. Implementation Details",
    "  10. Live Demo",
    "",
    ">> Wrap-Up",
    "  11. Challenges & Solutions",
    "  12. Discussion & Future Work",
], sz=18)


###############################################################
# 3. INTRODUCTION
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "1. Introduction & Motivation", "Problem > Goal > Our Solution")

card(s, 0.5, 2.3, 3.8, 3.5)
tb(s, 0.7, 2.4, 3.4, 0.4, "PROBLEM", sz=16, b=True, c=ACCENT2)
ml(s, 0.7, 2.9, 3.4, 2.5, [
    "Students face 46+ AI/ML textbooks",
    "Hard to navigate across books",
    "No unified search system",
    "No way to verify answer sources",
], sz=14, c=LIGHT_GRAY, sp=6)

card(s, 4.7, 2.3, 3.8, 3.5)
tb(s, 4.9, 2.4, 3.4, 0.4, "GOAL", sz=16, b=True, c=GREEN)
ml(s, 4.9, 2.9, 3.4, 2.5, [
    "Ask natural language questions",
    "Get accurate, sourced answers",
    "Deep source tracing:",
    "  Book > Chapter > Page > Region",
    "Click to see original PDF",
], sz=14, c=LIGHT_GRAY, sp=6)

card(s, 8.9, 2.3, 3.8, 3.5)
tb(s, 9.1, 2.4, 3.4, 0.4, "SOLUTION", sz=16, b=True, c=HIGHLIGHT)
ml(s, 9.1, 2.9, 3.4, 2.5, [
    "RAG pipeline with 4 retrievers",
    "RRF fusion for ranking",
    "Ollama LLM (qwen2.5:0.5b)",
    "Streamlit UI + PDF viewer",
    "ROS 2 voice integration",
], sz=14, c=LIGHT_GRAY, sp=6)

# Research Question (from PDF)
card(s, 0.5, 5.9, 12.3, 0.8)
tb(s, 0.7, 6.0, 12.0, 0.6,
   "Research Question: How can we build a transparent, traceable educational Q&A system for AI/ML learning?",
   sz=16, c=GREEN, b=True, al=PP_ALIGN.CENTER)


###############################################################
# 4. DATASET
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "2. Dataset - 46 AI/ML Textbooks",
            "Curated collection of canonical educational resources")

cats = [
    ("Machine Learning", "8 books", "ISLR, ESL, PRML\nPML, Deep Learning", ACCENT),
    ("NLP", "4 books", "SLP3, Eisenstein\nManning IR", RGBColor(0x2E, 0x86, 0xAB)),
    ("Mathematics", "5 books", "MML, Boyd\nMacKay, Snell", RGBColor(0x7B, 0x68, 0xEE)),
    ("Vision / RL", "3 books", "Szeliski, Sutton\n& Barto, GRL", ACCENT2),
    ("Programming", "5+ books", "Fluent Python\nClean Code, DDIA", GREEN),
]
for i, (t, cnt, bks, col) in enumerate(cats):
    x = 0.5 + i * 2.5
    bx(s, x, 2.4, 2.2, 0.6, f"{t}\n({cnt})", fc=col, sz=12)
    tb(s, x, 3.2, 2.2, 1.0, bks, sz=13, c=LIGHT_GRAY, al=PP_ALIGN.CENTER)

tb(s, 1, 4.6, 11, 0.5,
   "46 BOOKS  |  85,356 CHUNKS  |  ~500MB PDFs  |  Open-access / educational copies",
   sz=18, b=True, c=HIGHLIGHT, al=PP_ALIGN.CENTER)

tb(s, 0.5, 5.4, 12, 0.4, "Preprocessing Pipeline", sz=18, b=True, c=ACCENT)
steps = ["MinerU\n(DocLayout-YOLO)", "Layout\nAnalysis", "Text/Table/\nFormula Extract",
         "Intelligent\nChunking", "Dual Indexing"]
cols = [ACCENT, RGBColor(0x2E,0x86,0xAB), RGBColor(0x7B,0x68,0xEE), GREEN, ORANGE]
for i, (st, cl) in enumerate(zip(steps, cols)):
    x = 0.5 + i * 2.5
    bx(s, x, 5.9, 2.0, 0.8, st, fc=cl, sz=11)
    if i < 4: arrow(s, x + 2.1, 6.1, w=0.3)


###############################################################
# 5. LIBRARY SCREENSHOT (screenshop5)
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "2. Dataset - Library View",
            "Browse all 46 textbooks with cover art, author, and page count")
if os.path.exists(img("screenshop5.png")):
    s.shapes.add_picture(img("screenshop5.png"), Inches(1.5), Inches(2.2), width=Inches(10))
tb(s, 1.5, 6.8, 10, 0.4,
   "Streamlit Library tab - 46 textbooks with metadata, cover art, and page counts",
   sz=13, c=MED_GRAY, al=PP_ALIGN.CENTER)


###############################################################
# 6. RAG ARCHITECTURE
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "3. RAG Architecture",
            "4-Method Hybrid Retrieval + Reciprocal Rank Fusion")

bx(s, 0.3, 2.8, 1.8, 0.8, "User Query\n(Natural Language)",
   fc=HIGHLIGHT, tc=DARK_BG, sz=11)
arrow(s, 2.2, 3.0, w=0.4)

methods = [
    ("1. BM25 Keyword\n(SQLite FTS5)", ACCENT),
    ("2. Semantic Vector\n(ChromaDB + MiniLM)", RGBColor(0x2E, 0x86, 0xAB)),
    ("3. TOC Tree\n(LLM Reasoning)", RGBColor(0x7B, 0x68, 0xEE)),
    ("4. Metadata Filter\n(Structured)", GREEN),
]
for i, (nm, cl) in enumerate(methods):
    bx(s, 2.7, 2.3 + i*0.85, 2.5, 0.7, nm, fc=cl, sz=11)

arrow(s, 5.3, 3.3, w=0.4)
bx(s, 5.8, 2.9, 2.0, 1.2, "RRF Fusion\n(Reciprocal\nRank Fusion)", fc=ORANGE, tc=DARK_BG, sz=12)
arrow(s, 7.9, 3.3, w=0.4)
bx(s, 8.4, 2.9, 2.0, 1.2, "Ollama LLM\nqwen2.5:0.5b\n(~0.4 GB RAM)", fc=ACCENT2, sz=12)
arrow(s, 10.5, 3.3, w=0.4)
bx(s, 11.0, 2.9, 1.8, 1.2, "Answer\n+ Source\nTracing", fc=GREEN, tc=DARK_BG, sz=12)

descs = [
    "BM25: Fast exact keyword matching via SQLite FTS5 extension",
    "Semantic: Embedding-based retrieval with all-MiniLM-L6-v2 + ChromaDB",
    "TOC Tree: Hierarchical TOC navigation using LLM reasoning per book",
    "Metadata: Structured filtering by book, chapter, page, content type",
]
for i, d in enumerate(descs):
    tb(s, 0.5 + i*3.0, 5.2, 3.0, 1.5, d, sz=12, c=LIGHT_GRAY)


###############################################################
# 7. DEEP SOURCE TRACING
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "4. Key Feature - Deep Source Tracing",
            "Not just citations - pixel-level traceability to original documents")

trace = [
    ("User asks:\n\"What is SVM?\"", HIGHLIGHT, DARK_BG),
    ("RAG retrieves\nfrom 46 textbooks", ACCENT, WHITE),
    ("Answer generated\nwith source refs", GREEN, DARK_BG),
    ("Click source ->\nOriginal PDF page", ACCENT2, WHITE),
    ("Highlighted\nbounding box", ORANGE, DARK_BG),
]
for i, (txt, bg, fg) in enumerate(trace):
    x = 0.5 + i * 2.5
    bx(s, x, 2.4, 2.2, 0.9, txt, fc=bg, tc=fg, sz=12)
    if i < 4: arrow(s, x + 2.3, 2.7, w=0.3)

ml(s, 1.0, 4.0, 11, 2.5, [
    ">> What makes this different from basic RAG?",
    "",
    "  Standard RAG: \"According to textbook X, SVM is...\"",
    "  Our system: Click \"View PDF (p.354)\" -> opens original page with yellow highlight",
    "",
    "  Each chunk stores: book_title, chapter, page_number, bounding_box (x, y, w, h)",
    "  MinerU (DocLayout-YOLO) extracts spatial coordinates during preprocessing",
    "  Enables instant visual verification against original source material",
], sz=16)


###############################################################
# 8. UI SCREENSHOT - Search Page (screenshop0)
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "5. Streamlit UI - Search Interface")
if os.path.exists(img("screenshop0.png")):
    s.shapes.add_picture(img("screenshop0.png"), Inches(1.5), Inches(2.0), width=Inches(10))
tb(s, 1.5, 6.6, 10, 0.6,
   "Main search page: Model selector, 4 retrieval toggles, "
   "adjustable source count (1-20), library filter (46/46 books)",
   sz=14, c=MED_GRAY, al=PP_ALIGN.CENTER)


###############################################################
# 9. UI SCREENSHOT - Results + PDF (screenshop4)
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "5. Streamlit UI - Results & PDF Viewer")
if os.path.exists(img("screenshop4.png")):
    s.shapes.add_picture(img("screenshop4.png"), Inches(0.8), Inches(2.0), width=Inches(11.5))
tb(s, 0.8, 6.6, 11.5, 0.6,
   "\"What is SVM?\" -> RAG answer + Related topics + 6 source books with relevance scores + "
   "PDF viewer with page navigation (p.354 of 758)",
   sz=14, c=MED_GRAY, al=PP_ALIGN.CENTER)


###############################################################
# 10. UI FEATURES DETAIL
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "5. Streamlit UI - Feature Details",
            "All features of the interactive search interface")

tb(s, 0.8, 2.3, 5.5, 0.4, "Search Features", sz=20, b=True, c=ACCENT)
ml(s, 0.8, 2.8, 5.5, 3.5, [
    "  4 retrieval methods with individual toggles",
    "  Adjustable top-K sources (1-20 slider)",
    "  Library collection filter (select books)",
    "  Model selector (qwen2.5:0.5b)",
    "  Related topic tag suggestions",
    "  Answer with full-text generation",
    "  Source documents with relevance scores",
], sz=16)

tb(s, 7.0, 2.3, 5.5, 0.4, "PDF Viewer Features", sz=20, b=True, c=ACCENT)
ml(s, 7.0, 2.8, 5.5, 3.5, [
    "  Click \"View PDF\" -> opens inline viewer",
    "  Page navigation (prev/next, page input)",
    "  Zoom controls (fit width, zoom in/out)",
    "  One-page / two-page spread mode",
    "  Highlighted source region (yellow bbox)",
    "  Full-screen viewing mode",
    "  Scroll to navigate through pages",
], sz=16)

tb(s, 0.8, 6.2, 11.5, 0.5,
   "Tech: Streamlit + FastAPI backend + SQLite FTS5 + ChromaDB + Ollama + MuPDF",
   sz=15, c=HIGHLIGHT, al=PP_ALIGN.CENTER)


###############################################################
# 11. EVALUATION
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "6. Evaluation - 20 Test Questions",
            "Manual assessment across AI/ML/NLP domains")

tb(s, 0.8, 2.3, 5.5, 0.4, "Scoring Method", sz=20, b=True, c=ACCENT)
ml(s, 0.8, 2.8, 5.5, 2.5, [
    "  1.0 = Correct answer with relevant sources",
    "  0.5 = Partially correct / incomplete",
    "  0.0 = Incorrect or irrelevant",
    "",
    "  Each question: top 3 retrieved documents",
    "  Relevance marked for each source chunk",
    "  Final accuracy = mean score across 20 Qs",
], sz=15)

tb(s, 7.0, 2.3, 5.5, 0.4, "20 Test Questions", sz=20, b=True, c=ACCENT)
ml(s, 7.0, 2.8, 2.8, 4.0, [
    "1. What is neural attention?",
    "2. Generative vs discriminative?",
    "3. Gradient for logistic regression?",
    "4. What is an N-gram LM?",
    "5. What is skip-gram?",
    "6. RNNs as language models?",
    "7. 3D rigid body transformation?",
    "8. Weight initialization?",
    "9. Network depth?",
    "10. Cost-sensitive classification?",
], sz=12, c=LIGHT_GRAY, sp=4)
ml(s, 9.8, 2.8, 2.8, 4.0, [
    "11. What is TF-IDF?",
    "12. What is backpropagation?",
    "13. Transformer architecture?",
    "14. What is Word2Vec?",
    "15. Named Entity Recognition?",
    "16. What is beam search?",
    "17. Dropout regularization?",
    "18. Batch normalization?",
    "19. What is transfer learning?",
    "20. What is BLEU score?",
], sz=12, c=LIGHT_GRAY, sp=4)

tb(s, 0.8, 6.2, 11.5, 0.5,
   "Target accuracy: >80%  |  Domains: ML, NLP, CV, Math, Deep Learning",
   sz=15, c=HIGHLIGHT, al=PP_ALIGN.CENTER)


###############################################################
# 12. PART 2 DIVIDER
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s)
tb(s, 1.5, 2.0, 10, 1.0, "Part 2", sz=56, b=True, c=ACCENT2, al=PP_ALIGN.CENTER)
tb(s, 1.5, 3.2, 10, 0.8, "ROS 2 Voice Integration", sz=40, b=True, al=PP_ALIGN.CENTER)
sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.5), Inches(4.3), Inches(4), Inches(0.06))
sh.fill.solid(); sh.fill.fore_color.rgb = ACCENT2; sh.line.fill.background()
tb(s, 1.5, 4.8, 10, 1.0,
   "Converting the RAG pipeline into a voice-interactive system\n"
   "using ROS 2 Humble on Ubuntu 22.04", sz=20, c=LIGHT_GRAY, al=PP_ALIGN.CENTER)


###############################################################
# 13. ROS 2 ARCHITECTURE
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "7. ROS 2 Architecture - 5-Node Pipeline",
            "Voice input -> STT -> RAG -> TTS -> Voice output")

nodes = [
    ("1/5 MICROPHONE\nRecordingPublisher", RGBColor(0x2E, 0x86, 0xAB)),
    ("2/5 WHISPER STT\nWordsPublisher", GREEN),
    ("3/5 RAG + LLM\nOllamaPublisher", ACCENT2),
    ("4/5 SPEAKER\nSpeakClient", RGBColor(0x7B, 0x68, 0xEE)),
    ("5/5 TTS ENGINE\nSpeakService", ORANGE),
]
topics = ["/recording", "/words", "/ollama_reply", "/speak (srv)"]
for i, (nm, cl) in enumerate(nodes):
    x = 0.3 + i * 2.6
    bx(s, x, 2.5, 2.3, 1.0, nm, fc=cl, sz=12)
    if i < 4:
        arrow(s, x + 2.35, 2.8, w=0.3)
        tb(s, x + 2.0, 3.5, 1.0, 0.3, topics[i], sz=9, c=HIGHLIGHT, al=PP_ALIGN.CENTER)

bx(s, 0.3, 4.2, 9.4, 0.5, "aisd_hearing package (our code)", fc=DARK_CARD, sz=13)
bx(s, 10.0, 4.2, 2.6, 0.5, "aisd_speaking (provided)", fc=DARK_CARD, sz=13)

ml(s, 0.5, 5.0, 5.5, 2.0, [
    ">> Node Details:",
    "  1. RecordingPublisher: Mic input + Silero VAD",
    "  2. WordsPublisher: faster-whisper (int8, auto-lang)",
    "  3. OllamaPublisher: RAG + qwen2.5:0.5b (our node)",
    "  4. SpeakClient: Receives reply, calls TTS service",
    "  5. SpeakService: gTTS -> audio playback",
], sz=14, sp=4)

ml(s, 7.0, 5.0, 5.5, 2.0, [
    ">> Deployment:",
    "  Platform: Ubuntu 22.04 (loaner laptop)",
    "  ROS 2 Humble + colcon build",
    "  Process mgmt: tmux (5 panes)",
    "  Deploy: SCP from Windows -> laptop",
    "  One-click: start_loaner.bat",
], sz=14, sp=4)


###############################################################
# 14. IMPLEMENTATION DETAILS
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "8. Implementation Details",
            "ollama_publisher.py - The bridge between Part 1 and Part 2")

ml(s, 0.8, 2.3, 5.5, 4.5, [
    ">> ollama_publisher.py (our new node):",
    "",
    "  Subscribes to: /words (STT output)",
    "  Publishes to: /ollama_reply (LLM answer)",
    "",
    "  Loads knowledge.txt at startup",
    "  Constructs system prompt with RAG context",
    "  Queries local Ollama API (localhost:11434)",
    "  15s cooldown between replies",
    "  Hallucination filtering on input",
], sz=16, sp=5)

ml(s, 7.0, 2.3, 5.5, 4.5, [
    ">> Deployment Automation:",
    "",
    "  start_loaner.bat (Windows -> laptop):",
    "    Step 1: SCP sync (4 .py + knowledge.txt)",
    "    Step 2: Stop existing tmux session",
    "    Step 3: colcon build --symlink-install",
    "    Step 4: tmux launch 5 panes",
    "",
    "  stop_loaner.bat:",
    "    Kill tmux + cleanup orphan processes",
], sz=16, sp=5)


###############################################################
# 15. ROS 2 DEMO SCREENSHOT (screenshop3 ONLY)
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "9. ROS 2 Demo - Live Voice Q&A")
if os.path.exists(img("screenshop3.png")):
    s.shapes.add_picture(img("screenshop3.png"), Inches(0.5), Inches(2.0), width=Inches(12))
tb(s, 0.5, 6.4, 12, 0.8,
   "5-pane tmux session on loaner laptop: Mic recording | Whisper STT | "
   "Ollama RAG | TTS Engine | SpeakClient\n"
   "Full pipeline: Voice input -> Whisper transcription -> RAG answer -> gTTS audio playback",
   sz=13, c=MED_GRAY, al=PP_ALIGN.CENTER)


###############################################################
# 15b. RESULTS - KEY ACHIEVEMENTS (from PDF)
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "Results - Key Achievements")

achievements = [
    ("Hybrid RAG", "Successfully implemented hybrid RAG architecture\nwith 4 retrieval methods + RRF fusion", ACCENT),
    ("Deep Source Tracing", "Deep source tracing with clickable PDF references\nand highlighted bounding box regions", GREEN),
    ("Layout-Aware", "Layout-aware document processing preserving\ntables, formulas, and figures", RGBColor(0x7B, 0x68, 0xEE)),
    ("ROS 2 Integration", "Full ROS 2 integration with vocal interaction\npipeline (5-node architecture)", ACCENT2),
    ("Low Memory", "Low memory footprint (<1.5GB total)\nsuitable for robot deployment", ORANGE),
]
for i, (t, d, cl) in enumerate(achievements):
    y = 2.2 + i * 1.0
    bx(s, 0.8, y, 2.8, 0.5, t, fc=cl, sz=14)
    tb(s, 3.8, y, 8.8, 0.8, d, sz=15, c=LIGHT_GRAY)

tb(s, 0.8, 7.0, 12, 0.3,
   "Tech Stack:  Python | Ollama | ChromaDB | SQLite | Streamlit | ROS 2 | MinerU | Whisper | gTTS",
   sz=13, c=MED_GRAY, al=PP_ALIGN.CENTER)


###############################################################
# 16. CHALLENGES & SOLUTIONS
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "10. Challenges & Solutions")

challenges = [
    ("Whisper Hallucinations",
     "Silero VAD pre-filtering + custom hallucination detector "
     "(repetition check, known phrases, trigram analysis)", GREEN),
    ("Echo Loop (TTS to Mic)",
     "15-second cooldown timer after each reply "
     "prevents system from hearing its own TTS output", RGBColor(0x2E, 0x86, 0xAB)),
    ("Resource Constraints",
     "qwen2.5:0.5b (0.4GB) + faster-whisper int8 -- "
     "3 AI models (Whisper + Ollama + gTTS) on one CPU laptop", RGBColor(0x7B, 0x68, 0xEE)),
    ("Cross-Platform Deploy",
     "Automated bat/sh scripts: SCP sync -> colcon build -> tmux launch -- "
     "one-click deployment from Windows to Ubuntu laptop", ORANGE),
    ("PDF Layout Parsing",
     "MinerU + DocLayout-YOLO detects 10 element categories -- "
     "preserves tables, formulas, figures with bounding box coordinates", ACCENT),
]
for i, (t, d, cl) in enumerate(challenges):
    y = 2.2 + i * 1.0
    bx(s, 0.8, y, 3.2, 0.5, t, fc=cl, sz=13)
    tb(s, 4.2, y, 8.5, 0.8, d, sz=14, c=LIGHT_GRAY)


###############################################################
# 17. DISCUSSION & FUTURE WORK
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6])
title_slide(s, "11. Discussion & Future Work")

card(s, 0.5, 2.2, 5.8, 3.8)
tb(s, 0.7, 2.3, 5.4, 0.4, "Current Limitations", sz=20, b=True, c=ACCENT2)
ml(s, 0.7, 2.8, 5.4, 3.0, [
    "  Small LLM (0.5B params) - limited generation quality",
    "  Single-turn Q&A only (no conversation memory)",
    "  Static knowledge file (no live updates)",
    "  CPU inference is slow (~10-15s per response)",
    "  ROS 2 Part 2 uses simplified knowledge base",
    "  English-only knowledge base content",
], sz=15, sp=6)

card(s, 6.8, 2.2, 5.8, 3.8)
tb(s, 7.0, 2.3, 5.4, 0.4, "Future Work", sz=20, b=True, c=GREEN)
ml(s, 7.0, 2.8, 5.4, 3.0, [
    "  Upgrade to qwen2.5:3b with GPU support",
    "  Multi-turn conversation with context memory",
    "  Dynamic knowledge base updates via API",
    "  Multi-language support (KR, CN, EN)",
    "  Integration with iRobot Create 3 hardware",
    "  Fine-tuning on educational domain data",
], sz=15, sp=6)

###############################################################
# 18. CONCLUSION (from PDF - separate slide)
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s)
tb(s, 1.5, 0.8, 10, 1.0, "Conclusion", sz=48, b=True, al=PP_ALIGN.CENTER)
tb(s, 1.5, 2.0, 10, 0.6,
   "We built a RAG-based educational Q&A system that:",
   sz=22, c=LIGHT_GRAY, al=PP_ALIGN.CENTER)

conc = [
    "Answers AI/ML questions using 46 canonical textbooks",
    "Provides deep source tracing to exact PDF pages with highlighted regions",
    "Implements 4-method hybrid retrieval with RRF fusion",
    "Integrates seamlessly with ROS 2 for voice-interactive robot deployment",
    "Runs locally with low memory footprint (<1.5GB)",
]
ml(s, 2.0, 3.0, 9.0, 3.5, conc, sz=20, c=WHITE, sp=12)

tb(s, 0.5, 6.3, 12, 0.8,
   "A complete voice-interactive RAG pipeline - from 46 textbooks to real-time "
   "voice Q&A on a ROS 2 platform.",
   sz=16, b=True, c=HIGHLIGHT, al=PP_ALIGN.CENTER)


###############################################################
# 19. THANK YOU
###############################################################
s = prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s)
tb(s, 1.5, 1.5, 10, 1.0, "Thank You!", sz=56, b=True, c=GREEN, al=PP_ALIGN.CENTER)
sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5), Inches(2.8), Inches(3), Inches(0.06))
sh.fill.solid(); sh.fill.fore_color.rgb = ACCENT; sh.line.fill.background()
tb(s, 1.5, 3.2, 10, 0.6, "Questions?", sz=36, c=ACCENT, al=PP_ALIGN.CENTER)
tb(s, 1.5, 4.2, 10, 1.0,
   "Hye Ran Yoo (041145212)  |  Peng Wang (041145555)\n"
   "CST8507: Natural Language Processing\n"
   "GitHub: github.com/LannieYoo/nlp_project",
   sz=18, c=LIGHT_GRAY, al=PP_ALIGN.CENTER)

# Tech stack bar at bottom
bx(s, 0.5, 5.8, 12.3, 0.7,
   "Python | Ollama | ChromaDB | SQLite | Streamlit | FastAPI | ROS 2 | MinerU | Whisper | gTTS",
   fc=DARK_CARD, sz=14)


###############################################################
# SAVE
###############################################################
out = os.path.join(PROJECT, "guide", "AI_Textbook_QA_System_Presentation.pptx")
prs.save(out)
print(f"[OK] Saved: {out}")
print(f"     Total slides: {len(prs.slides)}")
