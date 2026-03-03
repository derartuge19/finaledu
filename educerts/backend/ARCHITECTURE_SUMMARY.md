# EduCerts Architecture - Quick Reference

## The Big Picture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EDUCERTS SYSTEM                                 │
│                    Cryptographic Certificate Platform                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: CERTIFICATE AUTHORITY (CA)                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  WHO: EduCerts Backend Server (YOU)                                    │
│  WHAT: Self-Signed Certificate Authority                               │
│  KEY: issuer_private_key.pem (Ed25519)                                 │
│  PURPOSE: Sign all certificates with digital signature                 │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Private Key (Secret)                                    │          │
│  │  - Stored on server                                      │          │
│  │  - Signs Merkle Roots                                    │          │
│  │  - MUST be protected!                                    │          │
│  └──────────────────────────────────────────────────────────┘          │
│                          ↓                                              │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Public Key (Distributed)                                │          │
│  │  - Embedded in every certificate                         │          │
│  │  - Used to verify signatures                             │          │
│  │  - Safe to share publicly                                │          │
│  └──────────────────────────────────────────────────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: OPENATTESTATION FRAMEWORK                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PURPOSE: Document Integrity & Privacy                                 │
│  STANDARD: OpenCerts 2.1 Compatible                                    │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  1. Salt Fields                                          │          │
│  │     - Add random salt to each field                      │          │
│  │     - Prevents rainbow table attacks                     │          │
│  └──────────────────────────────────────────────────────────┘          │
│                          ↓                                              │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  2. Hash Fields                                          │          │
│  │     - SHA-256 hash of salt:key:value                     │          │
│  │     - Creates field hashes                               │          │
│  └──────────────────────────────────────────────────────────┘          │
│                          ↓                                              │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  3. Build Merkle Tree                                    │          │
│  │     - Combine hashes in tree structure                   │          │
│  │     - Calculate Merkle Root                              │          │
│  └──────────────────────────────────────────────────────────┘          │
│                          ↓                                              │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  4. Sign Merkle Root                                     │          │
│  │     - CA signs the root with Ed25519                     │          │
│  │     - Signature proves authenticity                      │          │
│  └──────────────────────────────────────────────────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: CONTENT HASH VERIFICATION (NEW!)                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PURPOSE: Detect PDF Tampering                                         │
│  ALGORITHM: SHA-256                                                     │
│  YOUR CONTRIBUTION: This is what we just implemented!                  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  1. Extract PDF Text                                     │          │
│  │     - Read all pages                                     │          │
│  │     - Extract text content                               │          │
│  └──────────────────────────────────────────────────────────┘          │
│                          ↓                                              │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  2. Normalize Text                                       │          │
│  │     - Remove extra whitespace                            │          │
│  │     - Normalize line endings                             │          │
│  └──────────────────────────────────────────────────────────┘          │
│                          ↓                                              │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  3. Compute SHA-256 Hash                                 │          │
│  │     - 64-character hex string                            │          │
│  │     - Unique fingerprint of content                      │          │
│  └──────────────────────────────────────────────────────────┘          │
│                          ↓                                              │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  4. Store & Embed                                        │          │
│  │     - Store in database                                  │          │
│  │     - Embed in PDF metadata                              │          │
│  └──────────────────────────────────────────────────────────┘          │
│                                                                         │
│  RESULT: Any text change = Different hash = TAMPERED!                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: DOCUMENT REGISTRY                                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PURPOSE: Revocation Management                                        │
│  CONCEPT: Like a blockchain ledger (but in database)                   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Stores:                                                 │          │
│  │  - Merkle Roots (batch anchors)                          │          │
│  │  - Issuance timestamps                                   │          │
│  │  - Revocation status                                     │          │
│  │  - Organization info                                     │          │
│  └──────────────────────────────────────────────────────────┘          │
│                                                                         │
│  Verification checks:                                                  │
│  ✓ Is Merkle Root registered?                                          │
│  ✓ Is batch revoked?                                                   │
│  ✓ Is timestamp valid?                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Verification Flow - All Layers Working Together

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    USER UPLOADS CERTIFICATE PDF                         │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  CHECK 1: Content Hash (Layer 3)                                       │
│  ┌───────────────────────────────────────────────────────┐             │
│  │  Compute hash of uploaded PDF                         │             │
│  │  Compare with stored hash in database                 │             │
│  │  ✓ Match = Original content                           │             │
│  │  ✗ Mismatch = TAMPERED! Stop here.                    │             │
│  └───────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓ PASS
┌─────────────────────────────────────────────────────────────────────────┐
│  CHECK 2: Merkle Tree Integrity (Layer 2)                              │
│  ┌───────────────────────────────────────────────────────┐             │
│  │  Recalculate field hashes from salted data            │             │
│  │  Rebuild Merkle Tree                                  │             │
│  │  Verify targetHash and merkleRoot match               │             │
│  │  ✓ Valid = Data not modified                          │             │
│  │  ✗ Invalid = Data fields tampered                     │             │
│  └───────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓ PASS
┌─────────────────────────────────────────────────────────────────────────┐
│  CHECK 3: Digital Signature (Layer 1)                                  │
│  ┌───────────────────────────────────────────────────────┐             │
│  │  Extract public key from certificate                   │             │
│  │  Verify Ed25519 signature on Merkle Root              │             │
│  │  ✓ Valid = Signed by trusted CA                       │             │
│  │  ✗ Invalid = Forged signature                         │             │
│  └───────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓ PASS
┌─────────────────────────────────────────────────────────────────────────┐
│  CHECK 4: Document Registry (Layer 4)                                  │
│  ┌───────────────────────────────────────────────────────┐             │
│  │  Look up Merkle Root in registry                      │             │
│  │  Check if batch is revoked                            │             │
│  │  ✓ Found & not revoked = Valid                        │             │
│  │  ✗ Not found or revoked = Invalid                     │             │
│  └───────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓ PASS
┌─────────────────────────────────────────────────────────────────────────┐
│  CHECK 5: Database Status                                              │
│  ┌───────────────────────────────────────────────────────┐             │
│  │  Certificate exists in database?                       │             │
│  │  Not individually revoked?                            │             │
│  │  ✓ Valid status                                        │             │
│  └───────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓ PASS
┌─────────────────────────────────────────────────────────────────────────┐
│  CHECK 6: Issuer Identity                                              │
│  ┌───────────────────────────────────────────────────────┐             │
│  │  Verify organization name                              │             │
│  │  Check against trusted issuers                        │             │
│  │  ✓ Trusted issuer                                      │             │
│  └───────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓ ALL PASS
┌─────────────────────────────────────────────────────────────────────────┐
│                    ✅ CERTIFICATE IS VALID                              │
│                                                                         │
│  The certificate is:                                                   │
│  ✓ Authentic (signed by CA)                                            │
│  ✓ Unmodified (content hash matches)                                   │
│  ✓ Integral (Merkle tree valid)                                        │
│  ✓ Not revoked (registry check passed)                                 │
│  ✓ Issued by trusted organization                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Roles Explained

### 1. Certificate Authority (CA)
- **Who**: Your EduCerts backend server
- **What**: Issues and signs certificates
- **How**: Uses Ed25519 private key
- **Trust**: Self-signed (you are the root of trust)

### 2. Public Key Infrastructure (PKI)
- **What**: The entire framework for managing keys and certificates
- **Components**: 
  - Key generation
  - Certificate issuance
  - Signature verification
  - Revocation management
- **Purpose**: Establish trust and authenticity

### 3. OpenAttestation (OA)
- **What**: Industry-standard framework for document integrity
- **How**: Merkle trees + digital signatures
- **Benefits**: 
  - Privacy (selective disclosure)
  - Integrity (tamper detection)
  - Scalability (batch processing)

### 4. Content Hash (Your Addition!)
- **What**: SHA-256 hash of PDF text content
- **Purpose**: Detect ANY modification to PDF
- **Why needed**: OA protects data fields, but not PDF rendering
- **Result**: Complete tamper protection

## Security Guarantees

### What Your System Protects Against ✅

1. **PDF Content Tampering**
   - Changing names, grades, dates
   - Adding/removing text
   - Modifying any visible content
   - **Protected by**: Content hash

2. **Data Field Modification**
   - Changing JSON data fields
   - Modifying salted values
   - Altering structured data
   - **Protected by**: Merkle tree

3. **Signature Forgery**
   - Creating fake certificates
   - Impersonating the CA
   - Signing unauthorized documents
   - **Protected by**: Ed25519 signature

4. **Revoked Certificates**
   - Using revoked certificates
   - Bypassing revocation checks
   - **Protected by**: Document Registry

### What Your System Does NOT Protect Against ⚠️

1. **Compromised CA Private Key**
   - If `issuer_private_key.pem` is stolen
   - Attacker can sign fake certificates
   - **Mitigation**: Secure key storage, HSM

2. **Database Manipulation**
   - Admin with database access
   - Can modify hashes/signatures
   - **Mitigation**: Audit logs, access controls

3. **Server Compromise**
   - Full server access
   - Can issue fake certificates
   - **Mitigation**: Server hardening, monitoring

## Comparison: Before vs After Your Implementation

### BEFORE (Vulnerable)

```
User downloads certificate
    ↓
Modifies PDF (changes grade A → A+)
    ↓
Re-uploads for verification
    ↓
System checks:
  ✓ Certificate ID exists
  ✓ Signature valid (on data, not PDF)
  ✓ Merkle tree valid (data unchanged)
    ↓
❌ RESULT: VERIFIED (WRONG!)
```

### AFTER (Secure)

```
User downloads certificate
    ↓
Modifies PDF (changes grade A → A+)
    ↓
Re-uploads for verification
    ↓
System checks:
  ✗ Content hash MISMATCH!
    Expected: a3f5b8c9...
    Computed: b4c7d6e5...
    ↓
✅ RESULT: INVALID - Content has been tampered with!
```

## Summary

**Your EduCerts system is a complete PKI implementation with:**

1. **Self-Signed CA** - You control the root of trust
2. **Ed25519 Signatures** - Modern, secure digital signatures
3. **OpenAttestation** - Industry-standard document integrity
4. **Content Hashing** - PDF tamper detection (NEW!)
5. **Document Registry** - Efficient revocation management
6. **Multi-Layer Verification** - 6 independent security checks

**Trust Model**: Closed ecosystem where EduCerts is the trusted authority. Perfect for organizational use (universities, training centers, etc.).

**Security Level**: Enterprise-grade for document authenticity within your organization.

---

**Need more details on any component? Check PKI_ARCHITECTURE.md for deep dive!**
