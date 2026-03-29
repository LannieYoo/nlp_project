"""Debug bbox values and coordinate conversion for reported pages."""
import sys, json, os, sqlite3
sys.path.insert(0, '.')
import pymupdf

def check_page(book_id, page_idx):
    print(f"\n{'='*60}")
    print(f"  Book: {book_id}, Page: {page_idx}")
    print(f"{'='*60}")

    # 1. Get chunks from DB for this page
    conn = sqlite3.connect('data/chunks.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT chunk_id, bbox_x1, bbox_y1, bbox_x2, bbox_y2, 
               chapter, section, text
        FROM chunks 
        WHERE book_id = ? AND page_idx = ?
        LIMIT 5
    """, (book_id, page_idx))
    
    rows = cur.fetchall()
    print(f"\n  Chunks on this page: {len(rows)} (showing max 5)")
    for r in rows:
        bbox = [r['bbox_x1'], r['bbox_y1'], r['bbox_x2'], r['bbox_y2']]
        print(f"  chunk: {r['chunk_id'][:40]}")
        print(f"    bbox (MinerU pixels): {bbox}")
        print(f"    chapter: {r['chapter'][:60] if r['chapter'] else ''}")
        print(f"    text: {r['text'][:100]}")
        print()
    conn.close()

    # 2. Get PDF page dimensions
    pdf_path = f"mineru_output/textbooks/{book_id}/{book_id}/auto/{book_id}_origin.pdf"
    if not os.path.exists(pdf_path):
        print(f"  PDF not found: {pdf_path}")
        return
    
    doc = pymupdf.open(pdf_path)
    if page_idx >= len(doc):
        print(f"  Page {page_idx} out of range (total: {len(doc)})")
        doc.close()
        return
    
    page = doc[page_idx]
    pdf_w = page.rect.width
    pdf_h = page.rect.height
    print(f"  PDF dimensions: {pdf_w:.1f} x {pdf_h:.1f} points")
    doc.close()

    # 3. Get MinerU model.json page dimensions
    model_path = f"mineru_output/textbooks/{book_id}/{book_id}/auto/{book_id}_model.json"
    if os.path.exists(model_path):
        with open(model_path, 'r', encoding='utf-8') as f:
            model = json.load(f)
        if page_idx < len(model):
            pi = model[page_idx]['page_info']
            img_w, img_h = pi['width'], pi['height']
            print(f"  MinerU dimensions: {img_w} x {img_h} pixels")
            
            sx = pdf_w / img_w
            sy = pdf_h / img_h
            print(f"  Scale factors: sx={sx:.4f}, sy={sy:.4f}")
            
            # Convert each chunk's bbox
            for r in rows:
                bbox = [r['bbox_x1'], r['bbox_y1'], r['bbox_x2'], r['bbox_y2']]
                converted = [
                    round(bbox[0] * sx, 1),
                    round(bbox[1] * sy, 1),
                    round(bbox[2] * sx, 1),
                    round(bbox[3] * sy, 1),
                ]
                print(f"  bbox {bbox} -> PDF {converted}")
        else:
            print(f"  model.json has only {len(model)} pages, requested {page_idx}")
    else:
        print(f"  model.json not found")

    # 4. Check content_list.json entries for this page
    cl_path = f"mineru_output/textbooks/{book_id}/{book_id}/auto/{book_id}_content_list.json"
    if os.path.exists(cl_path):
        with open(cl_path, 'r', encoding='utf-8') as f:
            entries = json.load(f)
        page_entries = [e for e in entries if e.get('page_idx') == page_idx]
        print(f"\n  content_list entries on page {page_idx}: {len(page_entries)}")
        for e in page_entries[:3]:
            print(f"    type={e.get('type')}, bbox={e.get('bbox')}")
            print(f"    text={e.get('text','')[:80]}")


# Check the two problematic pages from user's screenshots
check_page("deisenroth_mml", 128)
check_page("hastie_esl", 452)
check_page("barber_brml", 344)  # the one that worked
