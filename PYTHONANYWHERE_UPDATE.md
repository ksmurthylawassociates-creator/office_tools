# 🔄 Updating PythonAnywhere Deployment with Invoice Generator

This guide will help you update your existing PythonAnywhere deployment to include the new Invoice Generator feature.

---

## 📋 What's New

Your updated app now includes:
- ✅ Document Generator (existing - already working)
- ✅ Invoice Generator (NEW - requires password)
- ✅ Firebase integration for invoice storage
- ✅ Unified UI/UX across both features

---

## 🚀 Step-by-Step Update Instructions

### Step 1: Prepare Your Updated Files

Make sure you have these updated/new files ready:
- ✅ `app.py` (updated with invoice generator)
- ✅ `config.py` (updated with invoice password setting)
- ✅ `requirements.txt` (updated with firebase-admin)
- ✅ `firebase-key.json` (NEW - Firebase credentials)
- ✅ `templates/` folder (updated with invoice templates)
  - `invoice_password.html` (NEW)
  - `invoice_list.html` (NEW)
  - `invoice_form.html` (NEW)
  - `invoice_edit.html` (NEW)
  - `invoice_print.html` (NEW)
  - `home.html` (updated with invoice card)

---

### Step 2: Upload Updated Files to PythonAnywhere

**Option A - Using GitHub (Recommended if you use Git):**
1. Push your updated code to GitHub
2. In PythonAnywhere, go to **Consoles** tab
3. Start a **Bash** console
4. Navigate to your project folder: `cd your-repo-name`
5. Pull the latest changes: `git pull origin main` (or `git pull origin master`)

**Option B - Manual Upload:**
1. Go to **Files** tab in PythonAnywhere
2. Navigate to your project folder (e.g., `/home/yourusername/your-repo-name`)
3. Upload/Replace these files:
   - `app.py`
   - `config.py`
   - `requirements.txt`
   - `firebase-key.json` (NEW - important!)
4. Upload/Replace the entire `templates/` folder (or individual template files)

---

### Step 3: Install New Dependencies

1. In PythonAnywhere, go to **Consoles** tab
2. Start a **Bash** console
3. Navigate to your project: `cd your-repo-name`
4. Install the new dependency (firebase-admin):
   ```bash
   pip3.10 install --user firebase-admin==6.4.0
   ```
   (Replace `3.10` with your Python version if different)

   **OR** reinstall all dependencies:
   ```bash
   pip3.10 install --user -r requirements.txt
   ```

---

### Step 4: Update WSGI Configuration File

1. Go to **Web** tab in PythonAnywhere
2. Click on your web app's WSGI configuration file link
3. **Add the Invoice Generator password** to environment variables:

   Find this section:
   ```python
   # Set environment variables
   os.environ['FLASK_ENV'] = 'production'
   os.environ['FLASK_DEBUG'] = 'False'
   os.environ['SECRET_KEY'] = 'YOUR_SECRET_KEY_HERE'
   ```

   **Add this line** (after SECRET_KEY):
   ```python
   os.environ['INVOICE_GENERATOR_PASSWORD'] = 'your_invoice_password_here'
   ```

   **Complete example:**
   ```python
   import sys
   import os

   # Add your project directory to the path
   project_home = '/home/yourusername/your-repo-name'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)

   # Set environment variables
   os.environ['FLASK_ENV'] = 'production'
   os.environ['FLASK_DEBUG'] = 'False'
   os.environ['SECRET_KEY'] = 'YOUR_SECRET_KEY_HERE'
   os.environ['INVOICE_GENERATOR_PASSWORD'] = 'your_invoice_password_here'  # NEW!

   # Import your Flask app
   from app import app as application
   ```

4. **Important**: Replace `your_invoice_password_here` with a strong password (e.g., `Invoice2024!Secure`)
5. Click **Save**

---

### Step 5: Verify Firebase Key File

1. In **Files** tab, navigate to your project folder
2. Make sure `firebase-key.json` is present
3. **Security Note**: This file contains sensitive credentials - never share it publicly

---

### Step 6: Reload Your Web App

1. Go to **Web** tab
2. Click the green **Reload** button
3. Wait a few seconds for the app to restart

---

### Step 7: Test Your Updated App

1. Visit your app: `https://yourusername.pythonanywhere.com`
2. You should see:
   - ✅ Document Generator card (existing - should work as before)
   - ✅ Invoice Generator card (NEW - with 💰 icon)
3. Click on **Invoice Generator** card
4. Enter the password you set in Step 4
5. You should be able to create and manage invoices

---

## 🔍 Troubleshooting

### App won't start after update:

1. **Check Error Log:**
   - Go to **Web** tab
   - Click on **Error log** link
   - Look for error messages

2. **Common Issues:**

   **Issue: "ModuleNotFoundError: No module named 'firebase_admin'"**
   - **Fix**: Run `pip3.10 install --user firebase-admin==6.4.0` in a Bash console

   **Issue: "FileNotFoundError: firebase-key.json"**
   - **Fix**: Make sure `firebase-key.json` is uploaded to your project folder

   **Issue: "Firebase not initialized"**
   - **Fix**: Check that `firebase-key.json` is in the correct location (same folder as `app.py`)

   **Issue: "CSRF token missing"**
   - **Fix**: This should be fixed in the updated templates. Make sure all template files are uploaded.

   **Issue: "Invoice password not working"**
   - **Fix**: Check that `INVOICE_GENERATOR_PASSWORD` is set correctly in WSGI file
   - Make sure you're using the same password you set in the WSGI file

---

## 📝 Quick Checklist

Before reloading, make sure:

- [ ] All updated files are uploaded (app.py, config.py, requirements.txt)
- [ ] `firebase-key.json` is uploaded
- [ ] All template files are uploaded (especially invoice templates)
- [ ] `firebase-admin` is installed (`pip3.10 install --user firebase-admin==6.4.0`)
- [ ] `INVOICE_GENERATOR_PASSWORD` is added to WSGI file
- [ ] WSGI file is saved
- [ ] Web app is reloaded

---

## 🔐 Security Reminders

1. **Invoice Password**: Choose a strong password for `INVOICE_GENERATOR_PASSWORD`
2. **Firebase Key**: Never commit `firebase-key.json` to public repositories
3. **SECRET_KEY**: Keep your SECRET_KEY secure and don't share it

---

## ✅ Success Indicators

After updating, you should be able to:

1. ✅ Access the home page with both cards visible
2. ✅ Click "Invoice Generator" and see password prompt
3. ✅ Enter password and access invoice list
4. ✅ Create new invoices
5. ✅ View, edit, and delete invoices
6. ✅ Document Generator still works as before

---

## 🆘 Need Help?

If something doesn't work:

1. Check the **Error log** in PythonAnywhere **Web** tab
2. Verify all files are uploaded correctly
3. Make sure dependencies are installed
4. Check that environment variables are set in WSGI file
5. Try reloading the web app again

---

**Your updated app should now be live with both Document Generator and Invoice Generator!** 🎉

