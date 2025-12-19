# Known CodeQL Warnings - False Positives

This document explains CodeQL security warnings that are **expected and safe** for the askai-cli project.

## ⚠️ Quick Action Required

**CodeQL will report 7 "Uncontrolled data used in path expression" warnings.**

These are **FALSE POSITIVES** - not actual security vulnerabilities.

**To dismiss them on GitHub:**
1. Go to the Security tab → Code scanning alerts
2. For each of the 7 alerts, click "Dismiss alert"
3. Select "False positive" as the reason
4. Add comment: `CLI tool - users explicitly specify files to access. All paths validated. See .github/codeql/FALSE_POSITIVES.md`

## Summary

CodeQL reports 7 "Uncontrolled data used in path expression" warnings. These are **false positives** because askai is a tool where users intentionally specify file paths they want to access.

## Why These Are Safe

### CLI Tool vs Web Application

The key distinction:

- **Web Applications**: Should restrict file access to specific directories. Path traversal is a vulnerability.
- **CLI Tools** (like askai-cli): Users explicitly provide file paths they want to access. Path traversal is the intended functionality.

**Security Boundary**: The OS user's file permissions, not the application. Users can only access files they already have permission to read via the OS.

## Affected Files and Mitigations

### 1. `src/askai/utils/helpers.py` (5 warnings - lines 171, 175, 179, 184, 212)

**Function**: `_validate_file_access()` and `_read_file_content()`

**Purpose**: CLI file input - users specify files to read

**Security Measures**:
- ✅ Path canonicalization with `os.path.realpath()` prevents symlink attacks
- ✅ File existence validation
- ✅ File type validation (must be regular file, not directory/device)
- ✅ Read permission check
- ✅ Size limit enforcement (100MB maximum)

**Why Safe**: All paths are validated before use. Users can only access what they already have OS permissions for.

### 2. `src/askai/presentation/api/routes/patterns.py` (2 warnings - lines 66, 80)

**Function**: `_save_uploaded_file()`

**Purpose**: API file upload handling

**Security Measures**:
- ✅ File extension sanitization (character whitelist: alphanumeric + '.-_')
- ✅ Extension length limit (10 characters)
- ✅ Secure temp file creation with `tempfile.mkstemp()`
- ✅ Temp directory validation (canonical path must be within temp dir)
- ✅ Does NOT accept user-controlled paths (only sanitized extensions)

**Why Safe**: Multiple layers of validation prevent directory escape. Uses secure OS temp directory.

## CodeQL Comments in Code

All flagged locations have been documented with inline comments:

```python
# CodeQL [py/path-injection]: <explanation of why this is safe>
```

These comments serve as documentation for future maintainers.

## Suppression Options

CodeQL doesn't support easy inline suppressions in configuration files. Options are:

1. **Accept as known issues** (recommended) - Document in this file
2. **Dismiss on GitHub** - Mark alerts as "False positive" with justification
3. **Custom CodeQL queries** - Complex, requires QL expertise

We choose option 1: Document as known and expected behavior.

## Verification

To verify security measures are working:

```bash
# Run all security scans
make security-check

# Or manually:
bandit -r src/ -f json -o bandit-report.json

# All path operations are marked with # nosec B108
```

## References

- **This is a feature, not a bug**: CLI tools intentionally allow file system access
- **OS permissions are the security boundary**: Users access files they own
- **Validation is comprehensive**: Canonicalization, type checks, permission checks, size limits
- **Bandit (Python security linter)**: Also flags these, suppressed with `# nosec B108`

## Recommendation

When reviewing these CodeQL warnings on GitHub:
1. Click "Dismiss alert"
2. Select "False positive"
3. Add comment: "CLI tool where users explicitly specify files to access. All paths validated. See .github/codeql/FALSE_POSITIVES.md"

This documents the decision and prevents these from being counted as security issues.
