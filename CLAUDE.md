# CLAUDE.md - AI Assistant Guide

This document provides comprehensive guidance for AI assistants working with the Hajartbl personal portfolio repository.

## Repository Overview

**Repository Name:** Hajartbl/Hajartbl
**Type:** Personal Portfolio/Professional Profile (GitHub Profile Repository)
**Owner:** Hajar Toubali
**Primary Language:** French (with English elements)
**Last Updated:** October 2025

### Purpose
This is a GitHub profile repository that serves as a personal brand showcase for Hajar Toubali, a Data Analyst based in Lyon, France. The repository emphasizes:
- Professional expertise in data analysis, BI, and ML
- Technical skills (Python, SQL, Power BI)
- Work experience and achievements
- Personal brand and approachable professional identity

## Repository Structure

```
/home/user/Hajartbl/
├── README.md          # Main profile content (the showcase)
├── CLAUDE.md          # This file - AI assistant guide
└── .git/              # Git version control metadata
```

### Key Files

| File | Purpose | Language | Importance |
|------|---------|----------|------------|
| `README.md` | Primary portfolio content displayed on GitHub profile | French (primary) + English | **CRITICAL** |
| `CLAUDE.md` | Documentation for AI assistants | English | Reference |

## Content Guidelines

### Writing Style & Tone

The README.md follows a specific style that should be preserved:

1. **Tone:** Casual, confident, and engaging
   - Uses French colloquialisms and modern expressions
   - Includes emojis strategically for visual appeal
   - Balances professionalism with personality
   - Self-aware humor ("meta, non ?")

2. **Language:**
   - **Primary:** French (for main content)
   - **Secondary:** English (for technical terms, badges, "Quick Facts")
   - **Bilingual elements:** LinkedIn badges, technical keywords

3. **Formatting Conventions:**
   - Use emojis in headers (📊, 🐍, 📈, 🚀, etc.)
   - Code blocks for structured information (Python dict format)
   - Bullet points for lists
   - Markdown badges for social links
   - Clear section hierarchy with ###

4. **Content Structure:**
   ```
   # Title + Introduction
   ## Role/Title with emojis
   > Tagline/Value proposition
   ### Quick Facts (code block)
   ### What I do best
   ### Fun Facts
   ### Contact section
   --- (separator)
   Footer with current status
   ```

### Technical Accuracy

When updating content, ensure:
- **Skills** listed are accurate and current
- **Experience** mentions are factual (Schlumberger, SEW-USOCOME)
- **Location** remains Lyon, France
- **Contact links** remain functional
- **Technical terms** are accurate (Python, SQL, Power BI, ML, Apache Spark, Tableau)

## Development Workflows

### Git Branch Strategy

**IMPORTANT:** This repository uses a specific branching convention:

- **Development branches:** Always prefixed with `claude/` and include a session ID
  - Format: `claude/claude-md-<session-id>`
  - Example: `claude/claude-md-mkn0to9mt266dywh-4MrbS`

- **Main branch:** Not explicitly named in current configuration
  - Typically would be `main` or `master`
  - Should be used for stable, published content

### Git Operations

**Push Protocol:**
```bash
# Always use -u flag for new branches
git push -u origin <branch-name>

# Branch MUST start with 'claude/' and end with session ID
# Otherwise push will fail with 403 error
```

**Retry Logic:**
- For network failures, retry up to 4 times
- Use exponential backoff: 2s, 4s, 8s, 16s

**Fetch/Pull:**
```bash
# Prefer specific branch fetches
git fetch origin <branch-name>

# Pull specific branches
git pull origin <branch-name>
```

### Commit Message Conventions

Based on existing commits, follow these patterns:

```
# Format: Imperative mood, descriptive
✓ "Revamp README with personal and professional details"
✓ "Create README.md"
✓ "Update contact information"
✓ "Add new skill section"

# Avoid:
✗ "Updated stuff"
✗ "Fixed things"
✗ "Changes"
```

**Guidelines:**
- Use clear, descriptive messages
- Start with action verbs (Create, Update, Add, Revamp, Fix)
- Be specific about what changed
- Keep messages concise but informative

## Common Tasks

### 1. Updating Professional Information

**When updating experience, skills, or status:**

```markdown
# Update the Python dictionary in Quick Facts section
hajar = {
    "role": "Data Analyst",
    "location": "Lyon, France 🇫🇷",
    "status": "Disponible immédiatement 🟢",  # Update availability here
    "experience": {
        # Add new companies here
    },
    "superpowers": ["Python", "SQL", "Power BI", "ML"],  # Update skills
    ...
}
```

**Checklist:**
- [ ] Update Python dict in Quick Facts
- [ ] Update "Ce que je fais de mieux" if relevant
- [ ] Update footer "Currently" section
- [ ] Update "Learning" section with current goals
- [ ] Verify all information is accurate

### 2. Adding New Projects or Achievements

**Location:** Consider adding a new section after "Ce que je fais de mieux"

**Format:**
```markdown
### 🎯 Projets récents
- 📊 **Project Name** - Brief description
- 🔧 **Another Project** - Brief description
```

### 3. Updating Skills

**Locations to update:**
1. The "superpowers" list in the Python dict
2. The tagline (## 📊 Data Analyst | ...)
3. The "Learning" section in footer
4. The "Ask me about" section in footer

### 4. Modifying Contact Information

**Current contact methods:**
- LinkedIn: https://linkedin.com/in/hajar-toubali
- Email: hajartbl20@gmail.com

**Format for badges:**
```markdown
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Let's_Connect-blue?style=for-the-badge&logo=linkedin)](URL)
[![Email](https://img.shields.io/badge/Email-Say_Hi-red?style=for-the-badge&logo=gmail)](mailto:EMAIL)
```

## Content Principles

### What to PRESERVE

✓ **Creative personality** - The casual, engaging tone is intentional
✓ **French language** - Primary language for main content
✓ **Emoji usage** - Part of the visual brand
✓ **Code block format** - The Python dict is a unique feature
✓ **Humor elements** - "meta, non ?", "∞ coffee", etc.
✓ **Professional credibility** - Balance personality with expertise

### What to AVOID

✗ **Over-formalization** - Don't make it too corporate
✗ **Removing emojis** - They're part of the brand
✗ **English-only** - Keep French as primary language
✗ **Generic corporate speak** - Keep it authentic
✗ **Excessive length** - Keep it concise and scannable
✗ **Unverified claims** - Only add true achievements/skills

## Technical Details

### Dependencies
**None.** This is a static content repository with no build process or external dependencies.

### Build Process
**None required.** The README.md is rendered directly by GitHub.

### Testing
- Preview markdown changes locally or in a markdown editor
- Verify badges render correctly
- Check that links are functional
- Ensure emojis display properly

### Deployment
Content is automatically displayed on GitHub profile when pushed to the main branch.

## Assistance Guidelines

### When Helping with Content Updates

1. **Always read README.md first** before making changes
2. **Preserve the voice and tone** - Don't anglicize or formalize
3. **Maintain bilingual elements** - Keep French primary, English secondary
4. **Keep it scannable** - Use formatting, emojis, and structure
5. **Be specific** - Avoid generic statements
6. **Verify accuracy** - Only add true information

### When Helping with Structure Changes

1. **Maintain visual hierarchy** - Use consistent heading levels
2. **Keep sections balanced** - Don't create one overly long section
3. **Preserve formatting** - Match existing style
4. **Test markdown** - Ensure proper rendering

### When Helping with Git Operations

1. **Always use claude/ branch prefix** with session ID
2. **Commit frequently** with clear messages
3. **Push only when ready** to the specified branch
4. **Follow retry protocol** for network errors

## Quick Reference

### File Locations
```bash
Profile content:     /home/user/Hajartbl/README.md
AI guide:            /home/user/Hajartbl/CLAUDE.md
Git config:          /home/user/Hajartbl/.git/config
```

### Key Commands
```bash
# View current status
git status

# Check current branch
git branch --show-current

# View recent commits
git log --oneline -5

# Push changes
git push -u origin claude/claude-md-<session-id>
```

### Contact Information
- **Professional:** hajar-toubali (LinkedIn)
- **Email:** hajartbl20@gmail.com
- **Location:** Lyon, France

## Version History

| Date | Change | Author |
|------|--------|--------|
| 2026-01-20 | Created CLAUDE.md | AI Assistant |
| 2025-10-20 | Revamped README with professional details | Hajar Toubali |
| 2022-08-30 | Initial README creation | Hajartbl |

## Notes for AI Assistants

### Understanding the Context

This repository is **personal brand focused**, not a code project. Your assistance should:
- Prioritize **communication clarity** over technical complexity
- Maintain **authentic voice** over corporate polish
- Focus on **visual appeal** and scannability
- Respect the **bilingual nature** (French primary)
- Preserve the **personality** that makes it unique

### When in Doubt

1. **Read the existing content** to understand tone
2. **Ask the user** for preferences on style/language
3. **Preserve existing patterns** unless explicitly asked to change
4. **Keep it simple** - this is a showcase, not a novel
5. **Test your changes** before committing

---

**Remember:** This repository represents someone's professional identity. Treat updates with care, accuracy, and respect for the established voice and brand.
