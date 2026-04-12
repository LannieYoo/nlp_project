"""
Add a 'Demo Video' slide to the presentation with embedded video.
Inserts after slide 15 (ROS 2 Demo) as slide 16.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
import os

PPTX_IN  = r"c:\Users\40270\Desktop\workspace\nlp\guide\CST 8507_Project_Presentation.pptx"
PPTX_OUT = r"c:\Users\40270\Desktop\workspace\nlp\guide\CST 8507_Project_Presentation.pptx"
VIDEO_PATH = r"c:\Users\40270\Desktop\workspace\nlp\guide\record_nlp.mp4"
THUMB_PATH = r"c:\Users\40270\Desktop\workspace\nlp\guide\demo_thumbnail.png"

prs = Presentation(PPTX_IN)
slide_width = prs.slide_width   # 13.3in
slide_height = prs.slide_height  # 7.5in

# Use "Blank" layout so we have full control
blank_layout = prs.slide_layouts[6]

# Insert slide at position 15 (after current slide 15, before slide 16)
# python-pptx doesn't have insert_at, so we add at end and then reorder
slide = prs.slides.add_slide(blank_layout)

# ── Dark background ──
from pptx.oxml.ns import qn
bg = slide.background
fill = bg.fill
fill.solid()
fill.fore_color.rgb = RGBColor(0x1a, 0x1a, 0x2e)

# ── Title: "Live Demo" ──
from pptx.util import Inches, Pt
title_left = Inches(0.5)
title_top = Inches(0.3)
title_width = Inches(12.3)
title_height = Inches(0.9)

txBox = slide.shapes.add_textbox(title_left, title_top, title_width, title_height)
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "🎬  Live Demo"
p.font.size = Pt(40)
p.font.bold = True
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
p.alignment = PP_ALIGN.LEFT

# ── Subtitle ──
sub_top = Inches(1.1)
sub_box = slide.shapes.add_textbox(title_left, sub_top, title_width, Inches(0.5))
stf = sub_box.text_frame
sp = stf.paragraphs[0]
sp.text = "AI Textbook Q&A System — Full Walkthrough"
sp.font.size = Pt(20)
sp.font.color.rgb = RGBColor(0xA0, 0xA0, 0xC0)
sp.alignment = PP_ALIGN.LEFT

# ── Video thumbnail with play button overlay ──
# Center the video thumbnail
thumb_width_in = 10.5
thumb_height_in = 5.7  # Maintain ~16:9 aspect
thumb_left = (slide_width - Inches(thumb_width_in)) // 2
thumb_top = Inches(1.7)

pic = slide.shapes.add_picture(
    THUMB_PATH,
    thumb_left, thumb_top,
    Inches(thumb_width_in), Inches(thumb_height_in)
)

# ── Play button circle overlay (text-based) ──
play_size = Inches(1.2)
play_left = (slide_width - play_size) // 2
play_top = thumb_top + Inches(thumb_height_in // 2) - Inches(0.3)

play_shape = slide.shapes.add_shape(
    2,  # MSO_SHAPE.OVAL
    play_left, play_top,
    play_size, play_size
)
play_shape.fill.solid()
play_shape.fill.fore_color.rgb = RGBColor(0x20, 0x20, 0x20)
# Set transparency via XML
from lxml import etree
spPr = play_shape._element.find(qn('p:spPr'))
solidFill = spPr.find(qn('a:solidFill'))
if solidFill is not None:
    srgbClr = solidFill.find(qn('a:srgbClr'))
    if srgbClr is not None:
        alpha_elem = etree.SubElement(srgbClr, qn('a:alpha'))
        alpha_elem.set('val', '55000')  # 55% opacity

# Play triangle text
play_shape.text_frame.paragraphs[0].text = "▶"
play_shape.text_frame.paragraphs[0].font.size = Pt(36)
play_shape.text_frame.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
play_shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
play_shape.text_frame.paragraphs[0].font.bold = True
play_shape.line.fill.background()  # No border

# ── Bottom description ──
desc_top = Inches(7.0)
desc_box = slide.shapes.add_textbox(Inches(0.5), desc_top, Inches(12.3), Inches(0.4))
dtf = desc_box.text_frame
dp = dtf.paragraphs[0]
dp.text = "📁 Video file: record_nlp.mp4  |  Duration: 2:41  |  Resolution: 2538×1380"
dp.font.size = Pt(14)
dp.font.color.rgb = RGBColor(0x80, 0x80, 0xA0)
dp.alignment = PP_ALIGN.CENTER

# ── Move slide to position 16 (after slide 15: ROS 2 Demo) ──
# python-pptx adds slides at the end; we need to reorder
slide_list = prs.slides._sldIdLst
slide_ids = list(slide_list)
# The new slide is the last one
new_slide_elem = slide_ids[-1]
# Remove from end
slide_list.remove(new_slide_elem)
# Insert at position 15 (0-indexed, so after slide 15)
slide_list.insert(15, new_slide_elem)

# ── Save ──
prs.save(PPTX_OUT)
print(f"✅ Saved: {PPTX_OUT}")
print(f"   New slide inserted at position 16 (after 'ROS 2 Demo')")
print(f"   Total slides: {len(prs.slides)}")
