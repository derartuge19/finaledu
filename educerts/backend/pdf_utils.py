"""
pdf_utils.py
─────────────────────────────────────────────────────────────────────
PDF template engine for EduCerts.

Workflow:
  1. extract_pdf_placeholders(pdf_path)
       → Scans every page for {{field}} patterns using PyMuPDF and pdfplumber.
       → Returns: { "field_name": [(page_idx, x0, y0, x1, y1), ...] }

  2. render_pdf_certificate(template_path, field_values, output_path)
       → Overlays field values on top of extracted positions.

  3. apply_signatures_to_pdf(...)
       → Overlays images on top of reserved signature/stamp placeholders.
"""

import re
import os
import time
import fitz
import io
import datetime
from pathlib import Path

# --- Normalization Helper ---
def normalize_field_name(name: str) -> str:
    """
    Converts 'Student Name' or 'STUDENT_NAME' or 'student-name' 
    to 'student_name' for robust matching.
    """
    if not name: return ""
    # Remove {{ }} if present
    n = name.replace("{{", "").replace("}}", "").strip()
    # Replace spaces, hyphens with underscores
    n = re.sub(r'[\s\-]+', '_', n)
    return n.lower()
import pdfplumber

# More robust regex to handle potential line breaks or weird spacing inside {{ }}
PLACEHOLDER_RE = re.compile(r"\{\{\s*([\w\s]+?)\s*\}\}")

# ──────────────────────────────────────────────────────────────────
# 0) Helpers for Font Mapping
# ──────────────────────────────────────────────────────────────────

def _map_font_name(font_name: str) -> str:
    """
    Maps extraction font names to PyMuPDF standard font names.
    Prevents 'need font file or buffer' error by ensuring we use built-in fonts.
    """
    fn = str(font_name).lower()
    
    # Check for bold and italic flags in the name
    is_bold = "bold" in fn or "black" in fn or "heavy" in fn
    is_italic = "italic" in fn or "oblique" in fn
    
    # Map serif/times
    if "times" in fn or "serif" in fn or "roman" in fn:
        if is_bold and is_italic: return "tibi"
        if is_bold: return "tibo"
        if is_italic: return "tiit"
        return "tiro"
        
    # Map monospace/courier
    if "courier" in fn or "mono" in fn or "consolas" in fn:
        if is_bold and is_italic: return "cobi"
        if is_bold: return "cobo"
        if is_italic: return "coit"
        return "cour"
        
    # Default to Helvetica/Sans-Serif
    if is_bold and is_italic: return "hebi"
    if is_bold: return "hebo"
    if is_italic: return "heit"
    return "helv"

def extract_pdf_placeholders(pdf_path: str) -> dict:
    """
    Robust extraction of placeholders with font metadata.
    """
    result: dict[str, list] = {}
    doc = fitz.open(pdf_path)

    for page_idx, page in enumerate(doc):
        # --- PASS 1: Interactive Form Fields (AcroForms) ---
        for widget in page.widgets():
            field_name = widget.field_name
            if field_name:
                if field_name not in result:
                    result[field_name] = []
                result[field_name].append({
                    "type": "acroform",
                    "page": page_idx,
                    "rect": (widget.rect.x0, widget.rect.y0, widget.rect.x1, widget.rect.y1)
                })

        # --- PASS 2: Text Layer ({{placeholder}}) ---
        page_dict = page.get_text("dict")
        page_center = page.rect.width / 2

        # Join spans in a line to detect placeholders split across spans
        for block in page_dict.get("blocks", []):
            for line in block.get("lines", []):
                # 1. First, check individual spans (optimized)
                for span in line.get("spans", []):
                    text = span["text"]
                    if "{{" in text:
                        for match in PLACEHOLDER_RE.finditer(text):
                            field_name = match.group(1).strip()
                            _add_placeholder(result, field_name, span["bbox"], span, page_center, page_idx, "span")

                # 2. Check joined line text for split placeholders
                line_text = "".join(s["text"] for s in line.get("spans", []))
                if "{{" in line_text and "}}" in line_text:
                    # If we find a placeholder in the joined text that wasn't found in individual spans
                    for match in PLACEHOLDER_RE.finditer(line_text):
                        field_name = match.group(1).strip()
                        # If this field wasn't already found on this page starting at this position
                        # Simplified: just try to find which span it starts in
                        start_idx = match.start()
                        curr_pos = 0
                        for span in line.get("spans", []):
                            if curr_pos <= start_idx < curr_pos + len(span["text"]):
                                # Found the start span. Use its bbox for rendering.
                                # Check if it's already in result to avoid duplicates
                                if not any(r["page"] == page_idx and r["rect"] == span["bbox"] for r in result.get(field_name, [])):
                                    _add_placeholder(result, field_name, span["bbox"], span, page_center, page_idx, "split_line")
                                break
                            curr_pos += len(span["text"])

    doc.close()
    found_names = list(result.keys())
    print(f"DEBUG [extract_pdf_placeholders]: Found {len(result)} unique names: {found_names}")
    return result

def _add_placeholder(result, field_name, bbox, span, page_center, page_idx, source_type):
    span_center = (bbox[0] + bbox[2]) / 2
    is_centered = abs(span_center - page_center) < (page_center * 0.2)
    
    style = {
        "font": span["font"],
        "size": span["size"],
        "color": span["color"],
        "flags": span["flags"],
        "align": "center" if is_centered else "left"
    }
    
    if field_name not in result:
        result[field_name] = []
    result[field_name].append({
        "type": "text_overlay",
        "page": page_idx,
        "rect": bbox,
        "style": style,
        "source": source_type
    })


# ──────────────────────────────────────────────────────────────────
# 2) Render a certificate PDF by overlaying values on the template
# ──────────────────────────────────────────────────────────────────

def render_pdf_certificate(
    template_path: str,
    field_values: dict,
    output_path: str,
    signature_img_path: str | None = None,
    stamp_img_path: str | None = None,
    placeholder_map: dict | None = None,
    widget_index: dict | None = None,
    metadata: dict | None = None,
) -> str:
    """
    Fills forms and overlays text/images on the PDF.
    If placeholder_map is provided, skip the expensive extraction scan.
    If widget_index is provided, skip the widget indexing loop.
    If metadata is provided, apply it to the document.
    """
    import time
    start_time = time.time()
    
    if placeholder_map is None:
        placeholder_map = extract_pdf_placeholders(template_path)

    doc = fitz.open(template_path)
    
    # --- PASS 1: Define what counts as an image field ---
    def is_signature(name: str) -> bool:
        n = name.lower()
        # Be strict: if it has 'name', 'text', 'line', or 'date', it's probably NOT an image field
        if any(x in n for x in ["name", "text", "line", "date", "role"]):
            return False
        return "signature" in n or "sign" in n or n == "sig"

    def is_stamp(name: str) -> bool:
        n = name.lower()
        if any(x in n for x in ["name", "text", "date"]):
            return False
        return "stamp" in n or "seal" in n or "logo" in n

    # Pre-index widgets by name for each page to avoid O(N*W) complexity
    if widget_index is None:
        page_widgets = {}
        for i in range(len(doc)):
            page_widgets[i] = {w.field_name: w for w in doc[i].widgets() if w.field_name}
    else:
        page_widgets = widget_index

    # ── Build a per-page draw plan ─────────────────────────────────
    # Each entry: {"rect": fitz.Rect, "type": "text"|"image", "value": ..., "style": ..., "img_path": ...}
    draw_plan: dict[int, list] = {}  # page_idx -> list of draw ops

    for field_name, occurrences in placeholder_map.items():
        # 1. Try exact match
        value = field_values.get(field_name)
        
        # 2. Try normalized match
        if value is None:
            norm_target = normalize_field_name(field_name)
            # Find any key in field_values that, when normalized, matches norm_target
            for k, v in field_values.items():
                if normalize_field_name(str(k)) == norm_target:
                    value = v
                    break

        if value is None:
            value = ""

        is_sig_field = is_signature(field_name)
        is_stamp_field = is_stamp(field_name)
        is_image_field = is_sig_field or is_stamp_field

        for occ in occurrences:
            page_idx = occ["page"]
            rect = fitz.Rect(occ["rect"])

            print(f"DEBUG [render_pdf]: Mapping field '{field_name}' to value '{value}' (type={occ['type']}, page={page_idx})")

            if page_idx not in draw_plan:
                draw_plan[page_idx] = []

            if occ["type"] == "acroform":
                # AcroForm fields: fill directly (no redact needed)
                draw_plan[page_idx].append({
                    "type": "acroform",
                    "field_name": field_name,
                    "rect": rect,
                    "value": value,
                    "is_image_field": is_image_field,
                    "is_sig_field": is_sig_field,
                })
            else:
                if is_image_field:
                    img_path = signature_img_path if is_sig_field else stamp_img_path
                    draw_plan[page_idx].append({
                        "type": "image",
                        "rect": rect,
                        "img_path": img_path,
                    })
                else:
                    # Resolve styles for the text field
                    style = occ.get("style", {})
                    font_size = max(style.get("size", 14), 8)
                    ext_font = style.get("font", "helv")
                    font_name = _map_font_name(ext_font)
                    alignment = style.get("align", "center")

                    # Resolve color
                    color_int = style.get("color", 0)
                    r = (color_int >> 16) & 255
                    g = (color_int >> 8) & 255
                    b = color_int & 255
                    color_tuple = (r/255, g/255, b/255)
                    if all(c > 0.90 for c in color_tuple):
                        color_tuple = (0.05, 0.05, 0.05)

                    # ALWAYS add to draw_plan so PASS 1 handles redaction
                    draw_plan[page_idx].append({
                        "type": "text",
                        "rect": rect,
                        "value": str(value) if value else "",
                        "font_name": font_name,
                        "font_size": font_size,
                        "color": color_tuple,
                        "alignment": alignment,
                        "is_empty": not bool(value)
                    })


    # ── PASS 1: Redact placeholder text per page (preserves background images/colors) ──
    # In PyMuPDF 1.27+, the correct API is page.apply_redactions() (plural).
    for page_idx, ops in draw_plan.items():
        page = doc[page_idx]
        has_text_or_image = any(op["type"] in ("text", "image") for op in ops)
        if has_text_or_image:
            for op in ops:
                if op["type"] in ("text", "image"):
                    # ONLY redact if we actually have a value to fill
                    # This prevents erasing signature placeholders during base issuance
                    should_redact = False
                    if op["type"] == "text" and not op.get("is_empty"):
                        should_redact = True
                    elif op["type"] == "image" and op.get("img_path"):
                        should_redact = True
                    
                    if should_redact:
                        r = op["rect"]
                        # Slightly expand rect to catch all placeholder glyph pixels
                        expanded = fitz.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1)
                        page.add_redact_annot(quad=expanded, fill=None)
            try:
                # Use a specific fill (white) for redactions to ensure they "erase" correctly
                # but ONLY if the value is NOT empty (or if we want to erase placeholders always)
                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
                print(f"DEBUG [render_pdf]: Redactions applied on page {page_idx}.")
            except Exception as re:
                print(f"DEBUG [render_pdf]: apply_redactions failed ({re}), continuing with overlay.")

    # ── PASS 2: Draw replacement values on top ──
    for page_idx, ops in draw_plan.items():
        page = doc[page_idx]
        
        # Sort ops to ensure images (especially signatures) are drawn on top.
        # Order: acroform (text) -> text -> image (stamp) -> image (signature)
        def sort_key(op):
            if op["type"] == "acroform":
                return 0 if not op.get("is_image_field") else (2 if "stamp" in op["field_name"].lower() else 3)
            if op["type"] == "text":
                return 1
            if op["type"] == "image":
                # Check img_path or rect metadata to distinguish if possible
                return 3 if "signature" in str(op.get("img_path", "")).lower() else 2
            return 4

        sorted_ops = sorted(ops, key=sort_key)
        
        for op in sorted_ops:
            rect = op["rect"]

            if op["type"] == "acroform":
                target_widget = page_widgets.get(page_idx, {}).get(op["field_name"])
                if target_widget:
                    if op["is_image_field"]:
                        img_path = signature_img_path if op["is_sig_field"] else stamp_img_path
                        if img_path and Path(img_path).exists():
                            # Formal sizing: 51mm x 18mm
                            tw, th = 144.5, 51.0
                            cx, cy = rect.x0 + rect.width/2, rect.y0 + rect.height/2
                            target_rect = fitz.Rect(cx - tw/2, cy - th/2, cx + tw/2, cy + th/2)
                            page.insert_image(target_rect, filename=img_path, keep_proportion=True)
                    else:
                        target_widget.field_value = op["value"]
                        target_widget.update()

            elif op["type"] == "image":
                img_path = op.get("img_path")
                if img_path and Path(img_path).exists():
                    # Formal sizing: 51mm x 18mm
                    tw, th = 144.5, 51.0
                    cx, cy = rect.x0 + rect.width/2, rect.y0 + rect.height/2
                    target_rect = fitz.Rect(cx - tw/2, cy - th/2, cx + tw/2, cy + th/2)
                    page.insert_image(target_rect, filename=img_path, keep_proportion=True)

            elif op["type"] == "text":
                if op.get("is_empty"):
                    continue
                alignment = op["alignment"]
                font_size = op["font_size"]
                font_name = op["font_name"]
                color_tuple = op["color"]
                value = op["value"]

                # Force centering
                padding = 50
                render_rect = fitz.Rect(max(0, rect.x0 - padding), rect.y0 - 2, min(page.rect.width, rect.x1 + padding), rect.y1 + font_size)
                align_val = fitz.TEXT_ALIGN_CENTER

                try:
                    overflow = page.insert_textbox(
                        rect=render_rect,
                        buffer=value,
                        fontsize=font_size,
                        fontname=font_name,
                        color=color_tuple,
                        align=align_val,
                        overlay=True,
                    )
                    if overflow < 0:
                        # Text didn't fit — try a slightly smaller font
                        smaller = max(font_size * 0.8, 7)
                        print(f"DEBUG: Text overflow ({overflow:.1f}), retrying at {smaller:.1f}pt", flush=True)
                        page.insert_textbox(
                            rect=render_rect,
                            buffer=value,
                            fontsize=smaller,
                            fontname=font_name,
                            color=color_tuple,
                            align=align_val,
                            overlay=True,
                        )
                except Exception as e:
                    print(f"DEBUG: insert_textbox failed: {e} — using insert_text fallback", flush=True)
                    page.insert_text(
                        point=fitz.Point(rect.x0, rect.y0 + font_size),
                        text=value,
                        fontsize=font_size,
                        fontname="helv",
                        color=color_tuple,
                        overlay=True,
                    )

    doc.need_appearances(True)
    if metadata:
        current_meta = doc.metadata
        if "cert_id" in metadata:
            current_meta["subject"] = metadata["cert_id"]
        
        # Add educational signing practices
        current_meta["producer"] = "EduCert Secure Verification System"
        current_meta["creator"] = "EduCert Engine v2.0"
        
        for k in ["title", "author", "keywords"]:
            if k in metadata:
                current_meta[k] = metadata[k]
        try:
            doc.set_metadata(current_meta)
        except Exception as me:
            print(f"DEBUG: Could not set metadata: {me}")

    # --- Add Blue 'Verified' Ribbon + Clickable Metadata ---
    try:
        # Only add ribbon if signature or stamp is present (implies signed/official)
        if signature_img_path or stamp_img_path:
            ribbon_path = os.path.join(os.getcwd(), "static", "verified_ribbon-removebg-preview.png")
            if os.path.exists(ribbon_path):
                # Make it large and prominent, square aspect ratio
                ribbon_w, ribbon_h = 240, 240
                margin_x = 40
                margin_y = 40
                page = doc[0]
                
                # Top-left corner
                ribbon_rect = fitz.Rect(margin_x, margin_y, margin_x + ribbon_w, margin_y + ribbon_h)
                
                # 1. Image
                page.insert_image(ribbon_rect, filename=ribbon_path, keep_proportion=True, overlay=True)
                
                # 2. Clickable Metadata Annotation
                cert_id = metadata.get("cert_id") if metadata else "N/A"
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                meta_text = (
                    f"Certificate ID: {cert_id}\n"
                    f"Where: EduCert Secure Verification System\n"
                    f"When: {now_str}\n"
                    f"Best Practice: This document is digitally verified. "
                    f"Ensure the details match the issuing authority's records."
                )
                
                # Add text annotation near the ribbon
                annot = page.add_text_annot(fitz.Point(ribbon_rect.x0 + 5, ribbon_rect.y0 + 5), meta_text, icon="Note")
                annot.set_info(title="Verification Metadata")
                annot.update()
                
                print(f"DEBUG: Added Verified Ribbon and metadata annotation")
    except Exception as ree:
        print(f"DEBUG: Failed to add ribbon: {ree}")
            
    doc.save(output_path)
    doc.close()
    
    elapsed = time.time() - start_time
    print(f"DEBUG: PDF Rendered in {elapsed:.3f}s: {output_path}")
    return output_path


# ──────────────────────────────────────────────────────────────────
# 3) Apply signature/stamp to an *already-rendered* certificate PDF
# ──────────────────────────────────────────────────────────────────

def apply_signatures_to_pdf(
    pdf_path: str,
    signature_img_path: str | None,
    stamp_img_path: str | None,
    template_path: str,
    output_path: str,
    signer_info: dict | None = None,
    metadata: dict | None = None,
) -> str:
    """
    Applies images to an already rendered PDF using the original template's coordinates.
    Also updates document metadata if provided.
    """
    placeholder_map = extract_pdf_placeholders(template_path)
    doc = fitz.open(pdf_path)

    # Helpers for identifying signer-related fields
    SIGNER_KEYWORDS = ["principal", "director", "head", "authority", "registrar", "dean", "manager", "chairman", "president", "signatory", "issuer", "authorized", "teacher", "dept"]

    def is_signer_related(name: str) -> bool:
        n = name.lower()
        return any(k in n for k in SIGNER_KEYWORDS) or "signer" in n

    def is_signature_field(name: str) -> bool:
        n = name.lower()
        if any(x in n for x in ["name", "text", "line", "date", "role", "title"]):
            return False
        return "signature" in n or "sign" in n or n == "sig" or n == "s"

    def is_stamp_field(name: str) -> bool:
        n = name.lower()
        if any(x in n for x in ["name", "text", "date"]):
            return False
        return "stamp" in n or "seal" in n or "logo" in n or "stmp" in n

    def is_name_field(name: str) -> bool:
        n = name.lower()
        if "role" in n or "title" in n or "position" in n or "dept" in n:
            return False
        return "name" in n or n.endswith("_n") or n == "names" or n == "signer" or n == "approver"

    def is_role_field(name: str) -> bool:
        n = name.lower()
        return "role" in n or "title" in n or "dept" in n or "position" in n or n == "role"

    # Collect items to apply first so we can sort them (Stamp on top of Signature)
    apply_items = []

    # Map the signer_info to the best possible placeholders
    signer_name_val = (signer_info.get("name") or "") if signer_info else ""
    signer_role_val = (signer_info.get("role") or "") if signer_info else ""

    for field_name, occurrences in placeholder_map.items():
        n = field_name.lower()
        
        # 1. Signer Name Placeholder (e.g. {{signer_name}}, {{principal_name}})
        if is_name_field(field_name) and is_signer_related(field_name):
            for occ in occurrences:
                apply_items.append({
                    "type": "text", "value": signer_name_val, "occ": occ, "z": 0
                })

        # 2. Signer Role Placeholder (e.g. {{signer_role}}, {{principal_role}})
        elif is_role_field(field_name) and is_signer_related(field_name):
            for occ in occurrences:
                apply_items.append({
                    "type": "text", "value": signer_role_val, "occ": occ, "z": 0
                })

        # 3. Fallback Signer Name (if matches related but not explicitly name/role/sig)
        elif is_signer_related(field_name) and not is_signature_field(field_name) and not is_stamp_field(field_name):
             for occ in occurrences:
                apply_items.append({
                    "type": "text", "value": signer_name_val, "occ": occ, "z": 0
                })

        # 4. Dedicated Signature Placeholder
        elif is_signature_field(field_name):
            if signature_img_path and os.path.exists(signature_img_path):
                for occ in occurrences:
                    apply_items.append({
                        "type": "image", "path": signature_img_path, "occ": occ, "z": 1, "is_sig": True
                    })

        # 5. Dedicated Stamp Placeholder
        elif is_stamp_field(field_name):
            if stamp_img_path and os.path.exists(stamp_img_path):
                for occ in occurrences:
                    apply_items.append({
                        "type": "image", "path": stamp_img_path, "occ": occ, "z": 2, "is_stmp": True
                    })

    # Sort items by Z-index: Text (0) -> Signature (1) -> Stamp (2)
    apply_items.sort(key=lambda x: x["z"])

    # Track which pages need redaction
    pages_to_redact = set()
    for item in apply_items:
        occ = item["occ"]
        page = doc[occ["page"]]
        rect = fitz.Rect(occ["rect"])
        
        # ONLY redact if we have a value to apply
        if item.get("value") or item.get("path"):
            expanded = fitz.Rect(rect.x0 - 0.5, rect.y0 - 0.5, rect.x1 + 0.5, rect.y1 + 0.5)
            page.add_redact_annot(quad=expanded, fill=None)
            pages_to_redact.add(occ["page"])

    # Apply redactions to all affected pages
    for pidx in pages_to_redact:
        try:
            doc[pidx].apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
            print(f"DEBUG [apply_sigs]: Redactions applied on page {pidx}")
        except Exception as e:
            print(f"DEBUG [apply_sigs]: Redaction failed on page {pidx}: {e}")

    for item in apply_items:
        occ = item["occ"]
        page = doc[occ["page"]]
        rect = fitz.Rect(occ["rect"])

        if item["type"] == "text" and item["value"]:
            print(f"DEBUG [apply_sigs]: Drawing text '{item['value']}' at {rect} on page {occ['page']}")
            style = occ.get("style", {})
            font_size = style.get("size", min(rect.height * 0.8, 12))
            font_name = _map_font_name(style.get("font", "helv"))
            alignment = style.get("align", "center") # Default to center
            color_int = style.get("color", 0)
            color_tuple = (((color_int >> 16) & 255)/255, ((color_int >> 8) & 255)/255, (color_int & 255)/255)

            # Force centering within the rect
            render_rect = rect
            align_val = fitz.TEXT_ALIGN_CENTER
            
            # Special logic for centering: expand rect horizontally to ensure it centers nicely if the placeholder is small
            if alignment == "center":
                padding = 50
                render_rect = fitz.Rect(max(0, rect.x0 - padding), rect.y0, min(page.rect.width, rect.x1 + padding), rect.y1 + 10)

            try:
                page.insert_textbox(rect=render_rect, buffer=str(item["value"]), fontsize=font_size, fontname=font_name, color=color_tuple, align=align_val)
            except:
                page.insert_text(point=fitz.Point(rect.x0, rect.y1), text=str(item["value"]), fontsize=font_size, fontname="helv", color=color_tuple)

        elif item["type"] == "image":
            # Target formal size: 51mm x 18mm ≈ 144.5pt x 51.0pt
            target_w, target_h = 144.5, 51.0
            
            # Center the formal rect within the placeholder rect
            w, h = rect.width, rect.height
            
            # center coordinates
            cx, cy = rect.x0 + w/2, rect.y0 + h/2
            
            # New rect centered at (cx, cy)
            target_rect = fitz.Rect(cx - target_w/2, cy - target_h/2, cx + target_w/2, cy + target_h/2)
            
            # If it's a dedicated placeholder (z > 0), shift it slightly up to sit better on the line if needed
            # but usually dedicated placeholders for sig/stamp are boxes.
            
            try:
                print(f"DEBUG [apply_sigs]: Inserting image '{item['path']}' at {target_rect} on page {occ['page']}")
                # Use overlay=True to ensure it sits on top of everything
                page.insert_image(target_rect, filename=item["path"], keep_proportion=True, overlay=True)
            except Exception as e:
                print(f"DEBUG [apply_sigs]: Image insert failed: {e}")

    if metadata:
        current_meta = doc.metadata
        if "cert_id" in metadata:
            current_meta["subject"] = metadata["cert_id"]
        
        # Add educational signing practices metadata
        current_meta["producer"] = "EduCert Secure Verification System"
        current_meta["creator"] = "EduCert Engine v2.0"
        
        if signer_info:
            current_meta["author"] = signer_info.get("name") or "EduCert Signatory"
            
        for k in ["title", "keywords"]:
            if k in metadata:
                current_meta[k] = metadata[k]
        try:
            doc.set_metadata(current_meta)
        except Exception as e:
            print(f"DEBUG [apply_sigs]: Could not set metadata: {e}")

    # --- Add Blue 'Verified' Ribbon + Clickable Metadata ---
    try:
        ribbon_path = os.path.join(os.getcwd(), "static", "verified_ribbon-removebg-preview.png")
        if os.path.exists(ribbon_path):
            # Make it large and prominent, square aspect ratio
            ribbon_w, ribbon_h = 240, 240
            margin_x = 40
            margin_y = 40
            page = doc[0] # Always first page
            
            # Top-left corner
            ribbon_rect = fitz.Rect(margin_x, margin_y, margin_x + ribbon_w, margin_y + ribbon_h)
            
            # 1. Overlay the ribbon image
            page.insert_image(ribbon_rect, filename=ribbon_path, keep_proportion=True, overlay=True)
            
            # 2. Add clickable metadata
            cert_id = metadata.get("cert_id") if metadata else "N/A"
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            meta_text = (
                f"Certificate ID: {cert_id}\n"
                f"Where: EduCert Secure Verification System\n"
                f"When: {now_str}\n"
                f"Best Practice: This document is digitally verified. "
                f"Ensure the details match the issuing authority's records."
            )
            
            annot = page.add_text_annot(fitz.Point(ribbon_rect.x0 + 5, ribbon_rect.y0 + 5), meta_text, icon="Note")
            annot.set_info(title="Verification Metadata")
            annot.update()
                
            print(f"DEBUG [apply_sigs]: Added Verified Ribbon and metadata annotation")
    except Exception as ree:
        print(f"DEBUG [apply_sigs]: Failed to add ribbon: {ree}")

    doc.save(output_path)
    doc.close()
    return output_path
