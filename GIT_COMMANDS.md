# Git Commands for Deploying to GitHub

Quick reference for pushing your Cholera Prediction System to GitHub.

---

## 🚀 First Time Setup

### 1. Initialize Git (if not already done)

```bash
cd "C:\Users\victor.idakwo\Documents\ehealth Africa\ehealth Africa\eHA GitHub\Mian Disease Modelling\cholera"
git init
```

### 2. Configure Git (if not already done)

```bash
git config user.name "Victor Idakwo"
git config user.email "your-email@example.com"
```

### 3. Add Remote Repository

```bash
git remote add origin https://github.com/VictorIdakwo/Cholera_Prediction_System.git
```

---

## 📦 Prepare Files for Commit

### 4. Check Status

```bash
git status
```

This shows:
- ✅ Files ready to commit (green)
- ⚠️ Modified files (red)
- 🚫 Ignored files (won't show - good!)

### 5. Review What Will Be Committed

```bash
git status
```

**Should include:**
- ✅ Python scripts (.py files)
- ✅ Streamlit app folder
- ✅ Data files (LGA.shp, rwi.tif, etc.)
- ✅ Documentation (.md files)
- ✅ Requirements.txt
- ✅ .gitignore

**Should NOT include:**
- ❌ keys/ folder
- ❌ service_account.json
- ❌ predictions/ folder
- ❌ __pycache__/ folders
- ❌ .streamlit/secrets.toml

### 6. Add All Files

```bash
git add .
```

Or add specific files:
```bash
git add streamlit_app/
git add *.py
git add Data/
git add *.md
```

---

## 💾 Commit Changes

### 7. Create Commit

```bash
git commit -m "Initial commit - Cholera Prediction System with Streamlit app"
```

Or with detailed message:
```bash
git commit -m "Initial commit - Cholera Prediction System

Features:
- Streamlit web application with interactive dashboard
- Machine learning prediction pipeline
- Google Earth Engine integration
- PDF report generation
- Interactive maps and visualizations
- eHealth Africa branding
- Supports Streamlit Cloud secrets for GEE credentials"
```

---

## 🌐 Push to GitHub

### 8. Set Main Branch

```bash
git branch -M main
```

### 9. Push to GitHub

```bash
git push -u origin main
```

**First time you'll be asked to authenticate:**
- Enter your GitHub username
- Enter your Personal Access Token (not password!)

### 10. Verify Push

Go to: https://github.com/VictorIdakwo/Cholera_Prediction_System

You should see all your files!

---

## 🔄 Future Updates

### Add New Changes

```bash
# 1. Check what changed
git status

# 2. Add changes
git add .

# 3. Commit with message
git commit -m "Update: description of changes"

# 4. Push
git push
```

### One-Line Update

```bash
git add . && git commit -m "Update features" && git push
```

---

## 🔍 Useful Git Commands

### Check Repository Status
```bash
git status
```

### View Commit History
```bash
git log --oneline
```

### View What Will Be Committed
```bash
git diff --staged
```

### Undo Last Commit (keep changes)
```bash
git reset --soft HEAD~1
```

### Remove File from Staging
```bash
git reset HEAD filename
```

### View Remote URL
```bash
git remote -v
```

### Update Remote URL (if changed)
```bash
git remote set-url origin https://github.com/VictorIdakwo/Cholera_Prediction_System.git
```

---

## 🚨 Troubleshooting

### Issue: "fatal: repository not found"

**Solution:**
```bash
git remote set-url origin https://github.com/VictorIdakwo/Cholera_Prediction_System.git
```

### Issue: "Authentication failed"

**Solution:**
Use Personal Access Token instead of password:
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate new token with 'repo' scope
3. Use token as password when pushing

### Issue: "large files detected"

**Solution:**
```bash
# Remove large files from staging
git reset HEAD path/to/large/file

# Add to .gitignore
echo "path/to/large/file" >> .gitignore

# Commit without large files
git add .
git commit -m "Remove large files"
git push
```

### Issue: Accidentally committed secrets

**Solution:**
```bash
# Remove from Git history
git rm --cached keys/service_account.json
git commit -m "Remove sensitive files"
git push

# Immediately rotate your credentials!
```

---

## 📋 Pre-Push Checklist

Before pushing to GitHub, verify:

- [ ] `.gitignore` exists and excludes:
  - [ ] `keys/` folder
  - [ ] `service_account.json`
  - [ ] `predictions/` folder
  - [ ] `.streamlit/secrets.toml`
  - [ ] `__pycache__/` folders

- [ ] Required files included:
  - [ ] All Python scripts
  - [ ] `streamlit_app/` folder
  - [ ] `Data/` folder with LGA.shp and rwi.tif
  - [ ] `requirements.txt`
  - [ ] Documentation (.md files)
  - [ ] `gee_auth.py`
  - [ ] `.gitignore`

- [ ] Sensitive files excluded:
  - [ ] No service account JSON in repo
  - [ ] No secrets.toml in repo
  - [ ] No API keys in code

- [ ] Documentation updated:
  - [ ] README.md reflects current features
  - [ ] STREAMLIT_CLOUD_SETUP.md included
  - [ ] All guides up to date

---

## 🎯 Quick Commands Summary

```bash
# Initial setup
git init
git remote add origin https://github.com/VictorIdakwo/Cholera_Prediction_System.git

# First push
git add .
git commit -m "Initial commit - Cholera Prediction System"
git branch -M main
git push -u origin main

# Future updates
git add .
git commit -m "Update description"
git push

# Check status
git status

# View history
git log --oneline
```

---

## 🌟 After Successful Push

1. ✅ Verify files on GitHub
2. ✅ Check .gitignore worked (no secrets visible)
3. ✅ Update README.md on GitHub if needed
4. ✅ Create a release tag (optional)
5. ✅ Deploy to Streamlit Cloud

---

## 📞 Need Help?

**Git Documentation:** https://git-scm.com/doc
**GitHub Guides:** https://guides.github.com
**Streamlit Cloud:** https://docs.streamlit.io/streamlit-cloud

---

**Ready to push to GitHub! 🚀**

Run the commands in order and your code will be safely on GitHub!
