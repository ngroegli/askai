# Template for Dismissing CodeQL Alerts

When dismissing the 7 CodeQL path injection warnings, use this template comment:

---

**Reason for dismissal:** False positive

**Comment:**

```
This is a false positive for a CLI tool context.

Context: askai is a tool where users explicitly specify file paths they want to access. Path traversal to user-specified files is the intended functionality, not a vulnerability.

Security measures in place:
- Path canonicalization with os.path.realpath() prevents symlink attacks
- File existence, type, and permission validation
- Size limit enforcement (100MB)
- For API uploads: Extension sanitization with character whitelist
- Security boundary: OS user file permissions (appropriate for CLI)

See comprehensive documentation: .github/codeql/FALSE_POSITIVES.md

Status: Documented and approved as expected behavior.
```

---

## Alternative Short Comment

For a shorter dismissal comment:

```
CLI tool - users explicitly specify files to access. All paths validated. See .github/codeql/FALSE_POSITIVES.md
```
