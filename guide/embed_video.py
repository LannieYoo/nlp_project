"""
Embed video into PowerPoint using COM automation.
This uses PowerPoint's own API to properly embed the video.
PowerPoint must be CLOSED before running this script.
"""
import win32com.client
import os
import time

PPTX_PATH = os.path.abspath(r"c:\Users\40270\Desktop\workspace\nlp\guide\CST 8507_Project_Presentation.pptx")
VIDEO_PATH = os.path.abspath(r"c:\Users\40270\Desktop\workspace\nlp\guide\record_nlp_final.mp4")

print(f"PPTX: {PPTX_PATH}")
print(f"Video: {VIDEO_PATH}")
print(f"Video size: {os.path.getsize(VIDEO_PATH) / 1024 / 1024:.1f} MB")

# Launch PowerPoint
print("\nLaunching PowerPoint...")
ppt = win32com.client.Dispatch("PowerPoint.Application")
ppt.Visible = True  # Must be visible for AddMediaObject2

# Open presentation
print("Opening presentation...")
prs = ppt.Presentations.Open(PPTX_PATH)

# Find the Live Demo slide (slide 19)
demo_slide_idx = None
for i in range(1, prs.Slides.Count + 1):
    slide = prs.Slides(i)
    for j in range(1, slide.Shapes.Count + 1):
        shape = slide.Shapes(j)
        if shape.HasTextFrame:
            if "Live Demo" in shape.TextFrame.TextRange.Text:
                demo_slide_idx = i
                break
    if demo_slide_idx:
        break

if not demo_slide_idx:
    print("ERROR: Live Demo slide not found!")
    prs.Close()
    ppt.Quit()
    exit(1)

print(f"Found Live Demo at slide {demo_slide_idx}")

slide = prs.Slides(demo_slide_idx)

# Remove old shapes except title and subtitle (keep first 2 text shapes)
shapes_to_delete = []
text_count = 0
for i in range(slide.Shapes.Count, 0, -1):
    shape = slide.Shapes(i)
    if shape.HasTextFrame:
        text = shape.TextFrame.TextRange.Text.strip()
        if text in ["Live Demo", "AI Textbook Q&A System  -  Full Walkthrough"]:
            continue  # Keep title and subtitle
    shapes_to_delete.append(i)

for idx in shapes_to_delete:
    slide.Shapes(idx).Delete()

print("Cleared old shapes, keeping title/subtitle")

# Slide dimensions
slide_width = prs.PageSetup.SlideWidth  # in points
slide_height = prs.PageSetup.SlideHeight

# Add video - centered on slide
# Position: leave space for title at top
video_width = slide_width * 0.78  # 78% of slide width
video_height = video_width * (1380 / 2538)  # maintain aspect ratio
video_left = (slide_width - video_width) / 2
video_top = 110  # points from top (below title)

print(f"Adding video at ({video_left:.0f}, {video_top:.0f}) size ({video_width:.0f} x {video_height:.0f}) points")

# AddMediaObject2(FileName, LinkToFile, SaveWithDocument, Left, Top, Width, Height)
video_shape = slide.Shapes.AddMediaObject2(
    VIDEO_PATH,
    False,   # LinkToFile = False (embed it)
    True,    # SaveWithDocument = True
    video_left,
    video_top,
    video_width,
    video_height
)

print("Video embedded successfully!")

# Add bottom description text
desc_left = 20
desc_top = slide_height - 40
desc_width = slide_width - 40
desc_height = 30

desc_shape = slide.Shapes.AddTextbox(1, desc_left, desc_top, desc_width, desc_height)
desc_shape.TextFrame.TextRange.Text = "Click to play demo video  |  Duration: 2:41"
desc_shape.TextFrame.TextRange.Font.Size = 12
desc_shape.TextFrame.TextRange.Font.Color.RGB = 0xB0A090  # Light gray (BGR in COM)
desc_shape.TextFrame.TextRange.ParagraphFormat.Alignment = 2  # Center

# Save
print("Saving...")
prs.Save()
print(f"\n✅ Done! Video embedded in slide {demo_slide_idx}")
print(f"   File size: {os.path.getsize(PPTX_PATH) / 1024 / 1024:.1f} MB")
print(f"   Play in slideshow mode (F5) - video will play on click!")

# Don't close PowerPoint - let the user see the result
