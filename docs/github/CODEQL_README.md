# CodeQL Security Analysis for askai-cli

## Overview

This directory contains documentation about CodeQL security analysis for the askai-cli project.

## Expected CodeQL Warnings (False Positives)

CodeQL reports 7 path injection warnings (`py/path-injection`). These are **expected false positives** for this application.

**📄 See [FALSE_POSITIVES.md](./FALSE_POSITIVES.md) for detailed documentation.**

### Quick Summary - Why These Are False Positives

#### 1. `src/askai/utils/helpers.py`

**Context**: CLI file input handling

**Why It's Safe**:
- This is a **command-line tool** where users explicitly specify file paths they want to read
- Path traversal to user-specified files is **by design** - users should be able to access any file their OS account has permissions for
- All paths are **canonicalized** with `os.path.realpath()` to prevent symlink-based attacks
- Comprehensive validation includes:
  - File existence check
  - File type verification (must be a regular file)
  - Read permission verification
  - Size limit enforcement (100MB max)

**Security Model**: The security boundary is the OS user's file permissions, not the application. This is appropriate for a CLI tool.

#### 2. `src/askai/presentation/api/routes/patterns.py`

**Context**: API file upload handling

**Why It's Safe**:
- File extensions are **sanitized** with a character whitelist (alphanumeric + '.-_' only)
- Extension length is **limited** to 10 characters
- Uses secure `tempfile.mkstemp()` which creates files in the system temp directory
- **Defense in depth**: Validates that created temp files are actually within the temp directory using canonical path comparison
- Does not accept user-controlled paths - only sanitized extensions for secure temp files

**Security Model**: Multiple layers of validation prevent any path traversal or directory escape.

## CLI Tools vs Web Applications

This distinction is important:

### Web Applications
- Should restrict file access to specific directories
- Path traversal is a serious vulnerability
- User-controlled paths are dangerous

### CLI Tools (like askai-cli)
- Users intentionally specify files they want to access
- Path traversal to user files is **the intended functionality**
- Users already have OS-level access to the files
- Security boundary is the OS user permissions

## Verification

To verify these security measures are working:

```bash
# Run security scan
make security-check

# Or manually:
bandit -r src/ -f json -o bandit-report.json
```

All path operations use `# nosec B108` comments to indicate they've been reviewed and are intentionally accessing user-specified paths.

## References

- [GitHub CodeQL Documentation](https://docs.github.com/en/code-security/code-scanning)
- [CodeQL Python Query Help](https://codeql.github.com/codeql-query-help/python/)
- [Path Injection Rule](https://codeql.github.com/codeql-query-help/python/py-path-injection/)
