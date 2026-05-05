# Contributing to SportShield AI

Thank you for your interest in contributing! Here's how to get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/sportshield.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Commit: `git commit -m "feat: describe your change"`
6. Push: `git push origin feature/your-feature-name`
7. Open a Pull Request

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to use |
|---|---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `style:` | Formatting, no logic change |
| `refactor:` | Code restructure, no new feature |
| `chore:` | Dependency updates, config |

## Branch Naming

- `feature/` — new features
- `fix/` — bug fixes  
- `docs/` — documentation updates

## Code Style

- **Frontend**: Follow the existing Tailwind + TypeScript conventions. Use `var(--css-variable)` for colors, not hardcoded hex.
- **Backend**: PEP8 compliant Python. Add docstrings to all new service functions.

## Reporting Bugs

Open an [Issue](../../issues) with:
- Steps to reproduce
- Expected vs actual behavior
- Your OS and Node/Python version
