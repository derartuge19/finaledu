@app.post("/api/templates/bulk-issue-excel")
async def bulk_issue_from_excel(
    file: UploadFile = File(...),
    cert_type: str = Form("certificate"),
    db: Session = Depends(get_db)
):
    """
    Reads an Excel (.xlsx) OR CSV file and issues one certificate per row.
    Works the same as /api/templates/bulk-issue but supports Excel in addition to CSV.
    """
    try:
        print(f"DEBUG: Received bulk-issue-excel request")
        print(f"DEBUG: Filename: {file.filename}")
        print(f"DEBUG: Cert type: {cert_type}")
        
        import re
        filename_lower = file.filename.lower()
        if not (filename_lower.endswith(".xlsx") or filename_lower.endswith(".csv")):
            raise HTTPException(status_code=400, detail="Only .xlsx or .csv files are allowed")

        # Determine which template to use
        pdf_template_path = "user_templates/template.pdf"
        html_template_path = "user_templates/custom_certificate.html"
        use_pdf = os.path.exists(pdf_template_path)
        use_html = os.path.exists(html_template_path)

        if not use_pdf and not use_html:
            raise HTTPException(status_code=400, detail="No template uploaded. Upload a PDF or HTML template first.")

        template_path = pdf_template_path if use_pdf else html_template_path
        if use_pdf:
            # USE ROBUST PDF EXTRACTION
            placeholder_map = pdf_utils.extract_pdf_placeholders(template_path)
            template_fields = set(placeholder_map.keys())
        else:
            with open(template_path, "r", encoding="utf-8") as tf:
                template_text = tf.read()
            template_fields = set(re.findall(r"\{\{\s*([\w\s]+?)\s*\}\}", template_text))
            template_fields = {f.strip() for f in template_fields}

        # Parse the file
        content_bytes = await file.read()
        if filename_lower.endswith(".xlsx"):
            import pandas as pd
            df = pd.read_excel(content_bytes)
            rows = df.to_dict('records')
        else:  # CSV
            content_str = content_bytes.decode('utf-8')
            df = pd.read_csv(StringIO(content_str))
            rows = df.to_dict('records')

        total_rows = len(rows)
        if total_rows == 0:
            raise HTTPException(status_code=400, detail="No data rows found in file")

        # Normalize column names
        headers = list(rows[0].keys()) if rows else []
        name_col = next((h for h in headers if normalize_column_name(h) == "student_name"), None)
        if not name_col:
            name_col = next((h for h in headers if "name" in h.lower() or "roll" in h.lower() or "id" in h.lower()), None)

        curr_organization = "EduCerts Academy"
        issued_certs = []
        target_hashes = []

        for idx, row in enumerate(rows):
            print(f"DEBUG: Processing row {idx+1}/{total_rows}...")
            student_name = row.get(name_col, "").strip() if name_col else "Student"
            
            data_payload_fields = {}
            row_keys_normalized = {normalize_column_name(k): k for k in row.keys()}
            
            for field in template_fields:
                f_norm = normalize_column_name(field)
                if f_norm == "student_name" and name_col:
                    data_payload_fields[field] = str(row[name_col]).strip() if row[name_col] is not None else ""

            curr_cert_type = row.get("cert_type", cert_type).strip() or cert_type

            cert_id = str(uuid.uuid4())
            raw_data = {
                "id": cert_id[:12],
                "type": curr_cert_type,
                "name": "Certificate",  # Use generic name instead of course_name
                "issuedOn": datetime.datetime.now().isoformat(),
                "recipient": {"name": student_name, "studentId": row.get("student_id", "N/A")},
                **{k: v for k, v in data_payload_fields.items() if k not in ("student_id", "organization")}
            }
            issuers = [{"name": curr_organization, "url": "https://educerts.io",
                        "documentStore": "0x007d40224f6562461633ccfbaffd359ebb2fc9ba",
                        "identityProof": {"type": "DNS-TXT", "location": "educerts.io"}}]

            oa_doc = oa_logic.wrap_document(raw_data, issuers=issuers)
            target_hashes.append(oa_doc["signature"]["targetHash"])
            
            batch_data.append({
                "cert_id": cert_id,
                "student_name": student_name,
                "curr_cert_type": curr_cert_type,
                "curr_organization": curr_organization,
                "oa_doc": oa_doc,
                "data_payload_fields": data_payload_fields
            })

        # Create batch signature for all certificates
        batch_id = str(uuid.uuid4())
        batch_sig = crypto_utils.sign_batch(target_hashes)
        
        # Create document registry entry
        registry_entry = models.DocumentRegistry(
            id=batch_id,
            merkle_root=batch_sig,
            anchored_at=datetime.datetime.now(),
            created_by="bulk_issue_excel",
            certificate_count=len(batch_data)
        )
        db.add(registry_entry)
        db.commit()

        # Process each certificate
        for idx, item in enumerate(batch_data):
            print(f"DEBUG: Processing certificate {idx+1}/{len(batch_data)}...")
            
            # Render PDF
            rendered_path = None
            try:
                field_values = {
                    f"{{ {k} }}": str(v) for k, v in item["data_payload_fields"].items()
                }
                
                out_path = f"generated_certs/{item['cert_id']}_rendered.pdf"
                pdf_utils.render_pdf_certificate(
                    template_path, 
                    field_values, 
                    out_path, 
                    placeholder_map=placeholder_map,
                    metadata={"cert_id": item["cert_id"]}
                )
                rendered_path = out_path
                print(f"DEBUG: PDF rendered successfully: {out_path}")
            except Exception as e:
                import traceback
                print(f"DEBUG: PDF RENDER ERROR: {e}")
                traceback.print_exc()
                rendered_path = None

            db_cert = models.Certificate(
                id=item["cert_id"], 
                student_name=item["student_name"], 
                cert_type=item["curr_cert_type"], 
                data_payload=item["oa_doc"], 
                signature=batch_sig,
                claim_pin=None,
                organization=item["curr_organization"], 
                batch_id=batch_id,
                template_type="pdf" if use_pdf else "html",
                rendered_pdf_path=rendered_path,
                signing_status="unsigned"
            )
            
            db.add(db_cert)
            issued_certs.append({
                "id": item["cert_id"], 
                "student_name": item["student_name"],
                "signing_status": "unsigned"
            })
            
            if idx % 10 == 0:
                print(f"DEBUG: Committing progress at row {idx+1}...")
                db.commit()

        db.commit()
        print(f"DEBUG: Finished bulk issuance. {len(issued_certs)} certs created.")
        return {
            "message": f"{len(issued_certs)} certificates issued",
            "count": len(issued_certs),
            "certificates": issued_certs
        }
    
    except Exception as e:
        import traceback
        print(f"ERROR in bulk_issue_from_excel: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
