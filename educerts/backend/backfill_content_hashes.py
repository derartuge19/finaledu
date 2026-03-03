"""
Backfill script to compute content hashes for legacy certificates.

This script processes existing certificates that don't have content_hash values
and computes hashes for their PDF files. This allows legacy certificates to
benefit from tamper detection.

Usage:
    python backfill_content_hashes.py [--dry-run]
"""

import os
import sys
from sqlalchemy.orm import Session
import models
import database
import pdf_hash_utils

def backfill_hashes(dry_run=False):
    """
    Backfill content hashes for legacy certificates.
    
    Args:
        dry_run: If True, only report what would be done without making changes
    """
    db: Session = database.SessionLocal()
    
    try:
        # Query certificates with null content_hash and existing PDF files
        certs = db.query(models.Certificate).filter(
            models.Certificate.content_hash == None,
            models.Certificate.rendered_pdf_path != None
        ).all()
        
        total = len(certs)
        print(f"Found {total} legacy certificates without content hashes")
        
        if total == 0:
            print("No certificates need backfilling. All done!")
            return
        
        if dry_run:
            print("\n=== DRY RUN MODE - No changes will be made ===\n")
        
        success_count = 0
        error_count = 0
        missing_file_count = 0
        
        for i, cert in enumerate(certs, 1):
            cert_id_short = cert.id[:8]
            pdf_path = cert.rendered_pdf_path
            
            print(f"[{i}/{total}] Processing certificate {cert_id_short}...")
            
            # Check if PDF file exists
            if not os.path.exists(pdf_path):
                print(f"  ✗ PDF file not found: {pdf_path}")
                missing_file_count += 1
                continue
            
            try:
                # Compute content hash
                content_hash = pdf_hash_utils.compute_pdf_content_hash(pdf_path)
                print(f"  ✓ Computed hash: {content_hash[:16]}...")
                
                if not dry_run:
                    # Update database
                    cert.content_hash = content_hash
                    
                    # Also embed in PDF metadata for offline verification
                    try:
                        pdf_hash_utils.embed_hash_in_pdf_metadata(
                            pdf_path,
                            content_hash,
                            cert.id
                        )
                        print(f"  ✓ Embedded hash in PDF metadata")
                    except Exception as e:
                        print(f"  ⚠ Could not embed hash in PDF: {e}")
                        # Continue anyway - database hash is most important
                    
                    db.commit()
                    print(f"  ✓ Updated database")
                else:
                    print(f"  → Would update database (dry run)")
                
                success_count += 1
                
            except Exception as e:
                print(f"  ✗ Failed to process: {e}")
                error_count += 1
                if not dry_run:
                    db.rollback()
                continue
        
        # Print summary
        print("\n" + "="*60)
        print("BACKFILL SUMMARY")
        print("="*60)
        print(f"Total certificates processed: {total}")
        print(f"Successfully hashed: {success_count}")
        print(f"Errors: {error_count}")
        print(f"Missing PDF files: {missing_file_count}")
        
        if dry_run:
            print("\nThis was a dry run. Run without --dry-run to apply changes.")
        else:
            print("\nBackfill completed!")
        
    finally:
        db.close()

if __name__ == "__main__":
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("Running in DRY RUN mode...\n")
    
    backfill_hashes(dry_run=dry_run)
