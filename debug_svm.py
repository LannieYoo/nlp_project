"""Verify bbox coordinate conversion."""
import sys, json, os
sys.path.insert(0, '.')

import pymupdf

book_id = "google_swe"
pdf_path = f"mineru_output/textbooks/{book_id}/{book_id}/auto/{book_id}_origin.pdf"
model_path = f"mineru_output/textbooks/{book_id}/{book_id}/auto/{book_id}_model.json"

doc = pymupdf.open(pdf_path)
page = doc[90]
print(f"PDF page 90 rect: {page.rect}")
print(f"PDF width={page.rect.width:.1f}, height={page.rect.height:.1f}")
doc.close()

with open(model_path, 'r', encoding='utf-8') as f:
    model = json.load(f)
p90 = model[90]
pi = p90["page_info"]
print(f"MinerU page 90: width={pi['width']}, height={pi['height']}")

scale_x = page.rect.width / pi['width']
scale_y = page.rect.height / pi['height']
print(f"Scale factors: sx={scale_x:.4f}, sy={scale_y:.4f}")

# Test with a sample bbox from content_list
cl_path = f"mineru_output/textbooks/{book_id}/{book_id}/auto/{book_id}_content_list.json"
with open(cl_path, 'r', encoding='utf-8') as f:
    entries = json.load(f)

# Find entries on page 90
p90_entries = [e for e in entries if e.get('page_idx') == 90]
print(f"\nEntries on page 90: {len(p90_entries)}")
for e in p90_entries[:3]:
    bbox = e.get('bbox', [])
    txt = e.get('text', '')[:80]
    print(f"  bbox={bbox}")
    if bbox and len(bbox) == 4:
        converted = [bbox[0]*scale_x, bbox[1]*scale_y, bbox[2]*scale_x, bbox[3]*scale_y]
        print(f"  converted={[round(c,1) for c in converted]}")
    print(f"  text={txt}")
    print()
