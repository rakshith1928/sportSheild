# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| `main` branch | ✅ |
| Feature branches | ❌ |

## Reporting a Vulnerability

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Instead, email us directly at: **security@sportshield.ai**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Any suggested fix (optional)

We will acknowledge your report within **48 hours** and aim to release a patch within **7 days** for critical issues.

## Security Best Practices for Contributors

- Never commit `.env`, `.env.local`, or any file containing API keys
- All Supabase Row Level Security (RLS) policies must be reviewed before merging
- FastAPI routes that expose user data must have JWT verification (`Depends(verify_jwt)`)
- All file uploads must validate content type AND file size before processing
