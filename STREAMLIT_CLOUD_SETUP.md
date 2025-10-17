# Streamlit Cloud Deployment Guide

Complete guide for deploying the Cholera Prediction System to Streamlit Cloud.

---

## 📋 Prerequisites

- GitHub account
- Streamlit Cloud account (free at https://share.streamlit.io)
- Google Earth Engine service account credentials

---

## 🚀 Step 1: Push to GitHub

### 1.1 Initialize Git Repository (if not already done)

```bash
cd "C:\Users\victor.idakwo\Documents\ehealth Africa\ehealth Africa\eHA GitHub\Mian Disease Modelling\cholera"
git init
```

### 1.2 Add Remote Repository

```bash
git remote add origin https://github.com/VictorIdakwo/Cholera_Prediction_System.git
```

### 1.3 Stage Files

**Important:** The `.gitignore` file will automatically exclude:
- ✅ `keys/` folder (sensitive credentials)
- ✅ Large data files
- ✅ Generated outputs
- ✅ Python cache files

```bash
git add .
```

### 1.4 Commit and Push

```bash
git commit -m "Initial commit - Cholera Prediction System with Streamlit app"
git branch -M main
git push -u origin main
```

---

## 🔐 Step 2: Prepare GEE Service Account Credentials

### 2.1 Get Your Service Account JSON

Your service account file looks like this:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

### 2.2 Format for Streamlit Secrets

Keep this file handy - you'll paste its contents in Streamlit Cloud.

---

## ☁️ Step 3: Deploy to Streamlit Cloud

### 3.1 Go to Streamlit Cloud

1. Visit https://share.streamlit.io
2. Sign in with your GitHub account
3. Click **"New app"**

### 3.2 Configure App

**Repository:**
- Repository: `VictorIdakwo/Cholera_Prediction_System`
- Branch: `main`
- Main file path: `streamlit_app/app.py`

**Advanced settings:**
- Python version: 3.9 or higher
- Click **"Advanced settings"**

### 3.3 Add Secrets

In the **Secrets** section, paste the following format:

```toml
[gee]
type = "service_account"
project_id = "your-project-id"
private_key_id = "abc123..."
private_key = """-----BEGIN PRIVATE KEY-----
your-private-key-here
-----END PRIVATE KEY-----
"""
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

**⚠️ Important Notes:**
- Replace all values with your actual service account credentials
- Use triple quotes `"""` for the private_key (it's multiline)
- Keep all newlines in the private key
- Don't add extra quotes or spaces

### 3.4 Deploy

Click **"Deploy!"**

The app will:
1. ✅ Clone your repository
2. ✅ Install dependencies from `requirements.txt`
3. ✅ Load secrets securely
4. ✅ Start the Streamlit app

---

## 📦 Step 4: Required Files in Repository

Make sure these files are in your repository:

### Core Files:
```
cholera/
├── streamlit_app/
│   ├── app.py              ✅ Main application
│   ├── pipeline_runner.py  ✅ Pipeline orchestration
│   ├── requirements.txt    ✅ Dependencies
│   ├── eHA-logo.png        ✅ Logo
│   └── .streamlit/
│       └── config.toml     ✅ App configuration
├── gee_auth.py             ✅ GEE authentication (supports secrets)
├── 01_extract_socioeconomic_data.py  ✅
├── 02_merge_all_data.py    ✅
├── 03_train_predict_visualize.py     ✅
├── 04_generate_pdf_report.py         ✅
├── Data/
│   ├── LGA.shp             ✅ Shapefile (and .shx, .dbf, .prj)
│   ├── rwi.tif             ✅ Wealth index raster
│   └── [Cholera data].xlsx ✅ Epidemiological data
└── .gitignore              ✅ Excludes sensitive files
```

### Files to EXCLUDE (already in .gitignore):
```
❌ keys/service_account.json  (use Streamlit secrets instead)
❌ predictions/               (generated outputs)
❌ model_output/              (generated outputs)
❌ __pycache__/               (Python cache)
```

---

## 🔧 Step 5: Update Scripts to Use New Auth

The following scripts need to use the new `gee_auth.py` module:

### For any script using GEE:

**OLD CODE:**
```python
import ee
service_account_file = 'keys/service_account.json'
credentials = ee.ServiceAccountCredentials(email, service_account_file)
ee.Initialize(credentials)
```

**NEW CODE:**
```python
from gee_auth import initialize_gee

# This works both locally and on Streamlit Cloud
if not initialize_gee():
    print("Failed to initialize GEE")
    exit(1)
```

The `gee_auth.py` module automatically:
1. ✅ Tries Streamlit secrets first (for cloud)
2. ✅ Falls back to local file (for development)
3. ✅ Provides clear error messages

---

## 🧪 Step 6: Test Locally Before Deploying

### 6.1 Test with Local Secrets (Optional)

Create `.streamlit/secrets.toml` in your `streamlit_app/` folder:

```toml
[gee]
type = "service_account"
project_id = "your-project-id"
# ... (same format as cloud secrets)
```

**⚠️ This file is in .gitignore - never commit it!**

### 6.2 Run Locally

```bash
cd streamlit_app
streamlit run app.py
```

If it works locally with secrets, it will work on Streamlit Cloud!

---

## 📊 Step 7: Monitor Deployment

### Check Deployment Status

In Streamlit Cloud dashboard:
- ✅ **Building** - Installing dependencies
- ✅ **Running** - App is live
- ❌ **Error** - Check logs

### View Logs

Click on **"Manage app"** → **"Logs"** to see:
- Installation progress
- Runtime errors
- GEE initialization status

You should see:
```
✅ GEE initialized with Streamlit secrets
```

---

## 🐛 Troubleshooting

### Issue: "GEE initialization failed"

**Solution:**
1. Check secrets format in Streamlit Cloud
2. Ensure private_key has all newlines
3. Verify client_email is correct
4. Make sure `gee_auth.py` is in repository

### Issue: "ModuleNotFoundError"

**Solution:**
1. Check `streamlit_app/requirements.txt` includes all dependencies
2. Make sure requirements.txt is committed to Git
3. Redeploy the app

### Issue: "File not found: LGA.shp"

**Solution:**
1. Ensure Data/ folder is in repository
2. Check .gitignore isn't excluding required files
3. Make sure all shapefile components (.shp, .shx, .dbf, .prj) are present

### Issue: Large Files

**Solution:**
If files are > 100MB:
1. Use Git LFS (Large File Storage)
2. Or compress files
3. Or store in external storage and download on startup

---

## 🔒 Security Best Practices

### ✅ DO:
- Use Streamlit secrets for credentials
- Add `keys/` to .gitignore
- Never commit service account files
- Regularly rotate service account keys
- Use read-only GEE permissions

### ❌ DON'T:
- Commit credentials to Git
- Share secrets in public repos
- Use admin service accounts
- Hard-code API keys in code
- Push large data files unnecessarily

---

## 🔄 Step 8: Update Deployment

### To Update Your App:

1. **Make changes locally**
2. **Commit and push:**
   ```bash
   git add .
   git commit -m "Update app features"
   git push
   ```
3. **Streamlit Cloud auto-deploys** - No manual action needed!

### To Update Secrets:

1. Go to Streamlit Cloud dashboard
2. Click **"Manage app"**
3. Click **"⚙️ Settings"**
4. Update secrets
5. Click **"Save"**
6. App will restart automatically

---

## 🌐 Step 9: Share Your App

Your app will be available at:
```
https://share.streamlit.io/victoridakwo/cholera_prediction_system/main/streamlit_app/app.py
```

Or get a custom subdomain:
```
https://cholera-prediction.streamlit.app
```

### Share the Link:
- 📧 Email colleagues
- 📱 Share on social media
- 📄 Add to reports and presentations
- 🔗 Embed in websites

---

## 📈 Step 10: Monitor Usage

### Streamlit Cloud Dashboard Shows:
- 👥 Number of users
- 📊 App uptime
- 💾 Resource usage
- 🔧 Error logs
- 📈 Usage analytics

### Free Tier Limits:
- 1GB RAM
- 1 CPU
- Unlimited viewers
- Auto-sleep after inactivity (wakes up on access)

---

## 🎉 Success Checklist

Before going live, ensure:

- [ ] Code pushed to GitHub
- [ ] .gitignore excludes sensitive files
- [ ] Streamlit secrets configured
- [ ] All required data files included
- [ ] Requirements.txt is complete
- [ ] App tested locally
- [ ] GEE authentication works
- [ ] Logo displays correctly
- [ ] All pages functional
- [ ] Error handling in place

---

## 📞 Support

### Resources:
- **Streamlit Docs:** https://docs.streamlit.io
- **Streamlit Cloud:** https://docs.streamlit.io/streamlit-cloud
- **GEE Docs:** https://developers.google.com/earth-engine
- **GitHub Docs:** https://docs.github.com

### Issues:
Report issues at: https://github.com/VictorIdakwo/Cholera_Prediction_System/issues

---

## 🚀 Next Steps

Once deployed:

1. **Test all features** on the live app
2. **Monitor logs** for any errors
3. **Share with team** for feedback
4. **Add custom domain** (optional, paid feature)
5. **Set up monitoring** and alerts
6. **Document usage** for end users

---

**Your Cholera Prediction System is now ready for Streamlit Cloud! 🎉**

For questions, contact: eHealth Africa Disease Modelling Team
