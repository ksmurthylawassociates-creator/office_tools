# 📝 PythonAnywhere: Upload firebase-key.json & Update WSGI

## 🔐 Step 1: Upload firebase-key.json

### Where to Upload:

**Location:** Same folder as your `app.py` file

**Path Format:** `/home/yourusername/your-project-folder/firebase-key.json`

**Example:**
- If your project is in `/home/ksmuser/office_tools/`
- Upload to: `/home/ksmuser/office_tools/firebase-key.json`
- (Same folder where `app.py` is located)

### How to Upload:

1. **Go to PythonAnywhere Dashboard**
   - Log in to [pythonanywhere.com](https://www.pythonanywhere.com/)
   - Click on **Files** tab (top menu)

2. **Navigate to Your Project Folder**
   - Click on `home` folder
   - Click on your username folder (e.g., `ksmuser`)
   - Click on your project folder (e.g., `office_tools` or `adv_doc_gen`)
   - You should see `app.py` in this folder

3. **Upload firebase-key.json**
   - Click **Upload a file** button (top right)
   - Select `firebase-key.json` from your local computer
   - Wait for upload to complete
   - Verify it appears in the file list (same folder as `app.py`)

**Important:** The file must be in the **same directory** as `app.py` for the app to find it.

---

## ⚙️ Step 2: Update WSGI Configuration File

### How to Find and Edit WSGI File:

1. **Go to Web Tab**
   - In PythonAnywhere dashboard, click **Web** tab (top menu)
   - You should see your web app listed

2. **Open WSGI Configuration File**
   - Scroll down to find **"WSGI configuration file"** section
   - Click on the file link (usually shows something like `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
   - This opens the WSGI file in an editor

3. **Edit the WSGI File**

   **Find this section:**
   ```python
   # Set environment variables
   os.environ['FLASK_ENV'] = 'production'
   os.environ['FLASK_DEBUG'] = 'False'
   os.environ['SECRET_KEY'] = 'your_secret_key_here'
   ```

   **Add this line after SECRET_KEY:**
   ```python
   os.environ['INVOICE_GENERATOR_PASSWORD'] = 'your_secure_password_here'
   ```

   **Complete Example:**
   ```python
   import sys
   import os

   # Add your project directory to the path
   project_home = '/home/yourusername/your-project-folder'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)

   # Set environment variables
   os.environ['FLASK_ENV'] = 'production'
   os.environ['FLASK_DEBUG'] = 'False'
   os.environ['SECRET_KEY'] = 'your_existing_secret_key_here'
   os.environ['INVOICE_GENERATOR_PASSWORD'] = 'Invoice2024!Secure'  # NEW LINE - Change this password!

   # Import your Flask app
   from app import app as application
   ```

4. **Important - Replace These Values:**
   - `yourusername` → Your PythonAnywhere username
   - `your-project-folder` → Your actual project folder name
   - `your_existing_secret_key_here` → Keep your existing SECRET_KEY (don't change it)
   - `Invoice2024!Secure` → **Change this to a strong password of your choice**

5. **Choose a Strong Password:**
   - Use at least 8-12 characters
   - Mix of letters, numbers, and special characters
   - Example: `KSM_Invoice_2024!Secure`
   - **Remember this password** - you'll need it to access Invoice Generator

6. **Save the File**
   - Click **Save** button (top right of editor)
   - Or press `Ctrl+S` (Windows) / `Cmd+S` (Mac)

---

## 🔄 Step 3: Reload Your Web App

1. **Go back to Web Tab**
   - Click **Web** tab in PythonAnywhere dashboard

2. **Reload the App**
   - Find the green **Reload** button
   - Click it
   - Wait 10-15 seconds for the app to restart

3. **Test Your App**
   - Visit: `https://yourusername.pythonanywhere.com`
   - You should see both Document Generator and Invoice Generator cards
   - Click Invoice Generator → Enter the password you set in WSGI file

---

## ✅ Verification Checklist

After completing the steps, verify:

- [ ] `firebase-key.json` is in the same folder as `app.py`
- [ ] WSGI file has `INVOICE_GENERATOR_PASSWORD` environment variable
- [ ] Password in WSGI file is strong and you remember it
- [ ] Web app has been reloaded
- [ ] Invoice Generator card appears on home page
- [ ] Password prompt works when clicking Invoice Generator

---

## 🆘 Troubleshooting

### "Firebase not initialized" error:
- **Check:** Is `firebase-key.json` in the correct folder? (same as `app.py`)
- **Check:** File name is exactly `firebase-key.json` (not `firebase-key.json.txt`)

### "Incorrect password" when accessing Invoice Generator:
- **Check:** Password in WSGI file matches what you're entering
- **Check:** WSGI file was saved after editing
- **Check:** Web app was reloaded after saving WSGI file

### App won't start:
- **Check:** Error log in Web tab for specific error messages
- **Check:** All syntax in WSGI file is correct (no typos)
- **Check:** Environment variable names are correct (case-sensitive)

---

## 📍 Quick Reference: File Locations

**On PythonAnywhere:**
```
/home/yourusername/your-project-folder/
├── app.py                    ← Your main app file
├── firebase-key.json         ← Upload here (same folder as app.py)
├── config.py
├── requirements.txt
├── templates/
└── doc_templates/
```

**WSGI File Location:**
```
/var/www/yourusername_pythonanywhere_com_wsgi.py
```
(Found in Web tab → WSGI configuration file link)

---

**That's it! Your Invoice Generator should now be working on PythonAnywhere!** 🎉

