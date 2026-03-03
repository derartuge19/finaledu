# Cryptographic Certificate Verification

## Overview

The EduCerts system now includes **cryptographic tamper detection** for certificate PDFs. This feature prevents fraudulent modifications to certificates by computing and validating SHA-256 hashes of PDF content.

## How It Works

### 1. Certificate Issuance

When a certificate PDF is generated:
1. The system extracts all text content from the PDF
2. Normalizes the text (whitespace, line endings)
3. Computes a SHA-256 hash of the normalized content
4. Stores the hash in the database (`certificates.content_hash`)
5. Embeds the hash in the PDF metadata for offline verification

### 2. Certificate Verification

When a certificate PDF is uploaded for verification:
1. The system extracts the certificate ID from the PDF
2. Computes the hash of the uploaded PDF
3. Retrieves the stored hash from the database
4. Compares the hashes:
   - **Match**: Certificate is authentic ✓
   - **Mismatch**: Certificate has been tampered with ✗

### 3. Tamper Detection

Any modification to the PDF content will cause the hash to change:
- Changing student names
- Modifying grades or scores
- Altering course names
- Adding or removing text

The verification will **fail** if the content has been modified.

## Database Schema

### New Column

```sql
ALTER TABLE certificates ADD COLUMN content_hash VARCHAR(64);
CREATE INDEX idx_certificates_content_hash ON certificates(content_hash);
```

The `content_hash` column stores the SHA-256 hash (64 hexadecimal characters).

## API Changes

### Certificate Response

The `/api/certificates` endpoint now includes `content_hash` in responses:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "student_name": "John Doe",
  "course_name": "Computer Science",
  "content_hash": "a3f5b8c9d2e1f4a7b6c5d8e9f2a1b4c7d6e5f8a9b2c1d4e7f6a5b8c9d2e1f4a7",
  ...
}
```

### Verification Response

The `/api/verify/pdf` endpoint now includes a content integrity check:

```json
{
  "summary": {
    "all": true,
    "contentIntegrity": true,
    "documentIntegrity": true,
    ...
  },
  "data": [
    {
      "type": "CONTENT_INTEGRITY",
      "name": "PDFContentHash",
      "data": {
        "expected": "a3f5b8c9...",
        "computed": "a3f5b8c9...",
        "match": true
      },
      "status": "VALID"
    },
    ...
  ]
}
```

## Migration

### Running the Migration

```bash
cd educerts/backend
python migrate_add_content_hash.py upgrade
```

### Rollback (if needed)

```bash
python migrate_add_content_hash.py downgrade
```

## Backfilling Legacy Certificates

For existing certificates without hashes:

```bash
# Dry run (see what would be done)
python backfill_content_hashes.py --dry-run

# Actually backfill
python backfill_content_hashes.py
```

The backfill script:
- Finds certificates with `content_hash = NULL`
- Computes hashes for their PDF files
- Updates the database
- Embeds hashes in PDF metadata

## Testing

Run the verification tests:

```bash
python test_hash_verification.py
```

Tests verify:
- Hash computation is deterministic
- Tampering is detected
- Metadata embedding/extraction works
- Whitespace normalization is correct

## Security Considerations

### Hash Algorithm

- **SHA-256** provides 256-bit security
- Collision attacks are computationally infeasible (2^128 operations)
- Industry-standard cryptographic hash function

### Attack Vectors

1. **Hash Collision**: Extremely unlikely with SHA-256
2. **Database Compromise**: If attacker modifies both PDF and database hash, tampering is undetectable
   - Mitigate with database access controls and audit logs
3. **Metadata Stripping**: If attacker removes metadata, system falls back to database lookup
4. **Replay Attack**: Old valid certificate could be presented
   - Mitigate with revocation checks

### Best Practices

- Always verify against database-stored hash (source of truth)
- Don't rely solely on embedded metadata
- Monitor for suspicious verification failure patterns
- Maintain audit logs of all verification attempts

## Legacy Certificates

Certificates issued before this feature have `content_hash = NULL`. The system handles these gracefully:

- Verification skips content integrity check
- Logs a warning: "Legacy certificate - skipping content integrity check"
- Other verification checks still apply
- Use backfill script to add hashes to legacy certificates

## Monitoring

### Metrics to Track

1. **Hash Computation Time**: Monitor P50, P95, P99 latencies
2. **Verification Failure Rate**: Track hash mismatch failures
3. **Legacy Certificate Rate**: Percentage with null hashes
4. **Error Rate**: Hash computation failures

### Logging

All hash operations are logged:
```
INFO:pdf_hash_utils:Computed content hash for cert.pdf: a3f5b8c9...
INFO:pdf_hash_utils:Embedded hash a3f5b8c9... in cert.pdf
✓ Content hash verification PASSED for 550e8400...
✗ Content hash verification FAILED for 550e8400...
  Expected: a3f5b8c9...
  Computed: b4c7d6e5...
```

## Performance

- Hash computation: < 100ms for typical certificates (< 1MB)
- Verification overhead: Minimal (single hash computation)
- Database index ensures fast hash lookups

## Files

- `pdf_hash_utils.py` - Core hash computation and validation
- `migrate_add_content_hash.py` - Database migration script
- `backfill_content_hashes.py` - Legacy certificate backfill
- `test_hash_verification.py` - Verification tests
- `main.py` - Updated issuance and verification endpoints
- `models.py` - Updated Certificate model
- `schemas.py` - Updated Certificate schema

## Example Usage

### Python API

```python
import pdf_hash_utils

# Compute hash
hash_val = pdf_hash_utils.compute_pdf_content_hash("certificate.pdf")
print(f"Hash: {hash_val}")

# Embed in metadata
pdf_hash_utils.embed_hash_in_pdf_metadata(
    "certificate.pdf",
    hash_val,
    "550e8400-e29b-41d4-a716-446655440000"
)

# Extract from metadata
metadata = pdf_hash_utils.extract_hash_from_pdf_metadata("certificate.pdf")
print(f"Stored hash: {metadata['content_hash']}")
print(f"Cert ID: {metadata['cert_id']}")

# Verify
is_valid = pdf_hash_utils.verify_pdf_content_hash("certificate.pdf", hash_val)
if is_valid:
    print("✓ Certificate is authentic")
else:
    print("✗ Certificate has been tampered with!")
```

## Troubleshooting

### Hash Computation Fails

**Error**: `ValueError: Cannot compute PDF hash`

**Solutions**:
- Verify PDF file exists and is readable
- Check PDF is not corrupted
- Ensure PyMuPDF is installed: `pip install PyMuPDF`

### Metadata Embedding Fails

**Error**: `ValueError: Cannot embed hash in PDF metadata`

**Solutions**:
- Verify PDF is not password-protected
- Check file permissions (write access required)
- Ensure PDF is not open in another application

### Verification Always Fails

**Possible Causes**:
- PDF was modified after issuance
- Hash was not computed during issuance (legacy certificate)
- Database hash is incorrect

**Solutions**:
- Check if `content_hash` is NULL in database
- Run backfill script for legacy certificates
- Verify PDF file matches the issued version

## Future Enhancements

Potential improvements:
1. **Digital Signatures**: Add PKI-based signatures to PDFs
2. **Blockchain Anchoring**: Store hashes on blockchain for immutability
3. **Batch Verification**: Verify multiple certificates at once
4. **Hash Caching**: Cache frequently verified certificate hashes
5. **Async Processing**: Compute hashes asynchronously for large batches

## Support

For issues or questions:
1. Check logs for error messages
2. Run test suite: `python test_hash_verification.py`
3. Verify database migration completed successfully
4. Review this documentation

---

**Last Updated**: 2024
**Version**: 2.0
**Status**: Production Ready ✓
