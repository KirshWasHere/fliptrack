# GitHub Setup Guide

This guide will help you publish FlipTrack to GitHub.

## Prerequisites

- Git installed on your system
- GitHub account created
- Repository created on GitHub (can be done via web or CLI)

## Step 1: Initialize Git Repository

If not already initialized:

```bash
git init
```

## Step 2: Add All Files

```bash
git add .
```

## Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: FlipTrack v2.0 - Reselling Profit Tracker"
```

## Step 4: Create GitHub Repository

### Option A: Via GitHub Website

1. Go to https://github.com/new
2. Repository name: `fliptrack`
3. Description: "Terminal-based profit tracking app for resellers"
4. Choose Public or Private
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

### Option B: Via GitHub CLI

```bash
gh repo create fliptrack --public --description "Terminal-based profit tracking app for resellers"
```

## Step 5: Connect to GitHub

Replace `yourusername` with your GitHub username:

```bash
git remote add origin https://github.com/yourusername/fliptrack.git
```

Or if using SSH:

```bash
git remote add origin git@github.com:yourusername/fliptrack.git
```

## Step 6: Push to GitHub

```bash
git branch -M main
git push -u origin main
```

## Step 7: Verify Upload

Visit your repository:
```
https://github.com/yourusername/fliptrack
```

You should see:
- ✅ All source files
- ✅ README.md displayed on homepage
- ✅ License file recognized
- ✅ .gitignore working (no tracker.db, data/, reports/)

## Step 8: Add Repository Topics (Optional)

On GitHub repository page:
1. Click "⚙️ Settings" (or the gear icon near About)
2. Add topics:
   - `python`
   - `terminal`
   - `tui`
   - `reselling`
   - `profit-tracker`
   - `inventory-management`
   - `textual`
   - `sqlite`

## Step 9: Enable GitHub Pages (Optional)

If you want to host documentation:

1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: main → /docs (if you create a docs folder)
4. Save

## Step 10: Add Shields/Badges (Optional)

Badges are already in README.md, but you can customize them at:
- https://shields.io/

## Repository Settings Recommendations

### General
- ✅ Allow issues
- ✅ Allow discussions (optional)
- ✅ Allow projects (optional)

### Branches
- Set `main` as default branch
- Consider branch protection rules for production

### Security
- Enable Dependabot alerts
- Enable security advisories

## Updating README with Your Username

After pushing, update the README.md clone URLs:

```bash
# Replace in README.md
git clone https://github.com/yourusername/fliptrack.git
# with your actual username
```

Then commit and push:

```bash
git add README.md
git commit -m "Update clone URL with actual username"
git push
```

## Future Updates

When you make changes:

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: description"

# Push to GitHub
git push
```

## Creating Releases

When ready for v2.0 release:

```bash
# Create and push tag
git tag -a v2.0.0 -m "FlipTrack v2.0.0 - Production Release"
git push origin v2.0.0
```

Then on GitHub:
1. Go to Releases
2. Click "Draft a new release"
3. Choose tag: v2.0.0
4. Release title: "FlipTrack v2.0.0"
5. Description: Copy from CHANGELOG.md
6. Publish release

## Recommended Repository Description

```
📦 FlipTrack - Terminal-based profit tracking application for resellers. 
Track inventory, calculate profits, generate HTML reports. 
Built with Python, Textual, and SQLite.
```

## Recommended Repository Website

If you have documentation hosted:
```
https://yourusername.github.io/fliptrack
```

Or link to main README:
```
https://github.com/yourusername/fliptrack#readme
```

## Social Preview Image (Optional)

Create a 1280x640px image showing:
- FlipTrack logo/name
- Screenshot of the TUI
- Key features

Upload in Settings → Social preview

## .github Folder (Optional)

Create `.github/` folder with:

### Issue Templates
`.github/ISSUE_TEMPLATE/bug_report.md`
`.github/ISSUE_TEMPLATE/feature_request.md`

### Pull Request Template
`.github/PULL_REQUEST_TEMPLATE.md`

### Workflows (GitHub Actions)
`.github/workflows/tests.yml` - Run tests on push

## Checklist Before Publishing

- ✅ All test data removed (tracker.db, data/, reports/)
- ✅ No personal information in code
- ✅ README.md is comprehensive
- ✅ LICENSE file is present
- ✅ .gitignore is configured
- ✅ Tests pass (`python tests.py`)
- ✅ Requirements.txt is up to date
- ✅ All documentation is complete
- ✅ No sensitive data in commit history

## After Publishing

1. Share on social media
2. Submit to:
   - Reddit: r/Python, r/Flipping
   - Hacker News
   - Product Hunt
3. Add to awesome lists:
   - awesome-python
   - awesome-tui
4. Write a blog post about it

## Getting Stars ⭐

- Share with reselling communities
- Post on Twitter/X with #Python #TUI
- Add to your GitHub profile README
- Contribute to discussions
- Keep updating with new features

---

**Good luck with your GitHub repository!** 🚀
