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
- Supabase access uses the service-role key server-side (RLS bypassed by design); tenant isolation is enforced at the API layer via ownership checks. Schema lives in backend/migrations/
- FastAPI routes that expose user data must require auth (`Depends(get_current_user)`) and scope queries by asset owner
- All file uploads must validate content type AND file size before processing
