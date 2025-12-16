# 🌐 Easy Deployment Guide - Make Your App Accessible to Others

This guide shows you the **easiest ways** to make your app accessible to others without technical knowledge.

---

## 📝 Understanding Environment Variables

Before deploying, you need to understand **Environment Variables**. These are settings that tell your app how to behave:

### Required Environment Variables:

1. **`FLASK_ENV`** = `production`
   - Tells Flask you're running in production (not development)
   - This enables security features and optimizations

2. **`FLASK_DEBUG`** = `False`
   - Turns off debug mode (important for security!)
   - Debug mode shows error details - never enable in production

3. **`SECRET_KEY`** = `<a long random string>`
   - **What is it?** A secret password used to encrypt sessions and protect against attacks
   - **Why needed?** Flask uses this to keep your app secure
   - **How to generate?** Run `python generate_secret_key.py` on your computer
   - **Important:** Keep this secret! Don't share it publicly

### How to Generate SECRET_KEY:

1. Open terminal/command prompt in your project folder
2. Run: `python generate_secret_key.py`
3. You'll see output like:
   ```
   ============================================================
   Generated SECRET_KEY for production:
   ============================================================
   a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6...
   ============================================================
   ```
4. Copy that entire long string
5. Use it as the value for `SECRET_KEY` when setting environment variables in your hosting platform

**Note:** For local development, you don't need to set these - the app uses safe defaults. But for cloud hosting (production), you MUST set them.

---

## 🎯 Option 1: Free Cloud Hosting (RECOMMENDED - Easiest!)

### Why This is Best:
- ✅ **FREE** (with limitations)
- ✅ No server management needed
- ✅ Automatic HTTPS (secure)
- ✅ Works from anywhere
- ✅ Easy setup (15 minutes)

### Choose a Platform:

#### **A. PythonAnywhere.com** (Recommended - Very Easy)
1. **Sign up**: Go to [pythonanywhere.com](https://www.pythonanywhere.com/) and create a free account
   - Your username will be part of your URL: `yourusername.pythonanywhere.com`

2. **Upload Your Files**:
   - **Option 1 (GitHub - Recommended)**: 
     - Push your code to GitHub first
     - In PythonAnywhere, go to **Consoles** tab → Start a **Bash** console
     - Run: `git clone https://github.com/yourusername/your-repo-name.git`
   - **Option 2 (Manual Upload)**:
     - Go to **Files** tab in PythonAnywhere
     - Upload all your project files (drag and drop or use upload button)
     - Make sure to upload: `app.py`, `config.py`, `requirements.txt`, `templates/`, `doc_templates/`, etc.

3. **Install Dependencies**:
   - Go to **Consoles** tab → Start a **Bash** console
   - Navigate to your project: `cd your-repo-name` (or wherever you uploaded files)
   - Install dependencies: `pip3.10 install --user -r requirements.txt`
   - (Replace `3.10` with your Python version if different)

4. **Configure Web App**:
   - Go to **Web** tab in PythonAnywhere dashboard
   - Click **Add a new web app**
   - Choose **Manual configuration** (not Flask)
   - Select Python version (3.10 recommended)
   - Click **Next** → **Next** until you reach the WSGI configuration

5. **Edit WSGI Configuration File**:
   - In the **Web** tab, click on the WSGI configuration file link
   - Delete all the default code
   - Replace with this (adjust paths to match your username and folder):
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
     os.environ['SECRET_KEY'] = 'YOUR_SECRET_KEY_HERE'  # See below

     # Import your Flask app
     from app import app as application
     ```
   - **Important**: Replace:
     - `yourusername` with your PythonAnywhere username
     - `your-repo-name` with your actual folder name
     - `YOUR_SECRET_KEY_HERE` with the key from `generate_secret_key.py`

6. **Set Environment Variables**:
   - **How to generate SECRET_KEY:**
     1. On your computer, run: `python generate_secret_key.py`
     2. Copy the long random string it shows
     3. Paste it in the WSGI file where it says `YOUR_SECRET_KEY_HERE`
   - The `FLASK_ENV` and `FLASK_DEBUG` are already set in the WSGI file above

7. **Configure Static Files** (if needed):
   - In **Web** tab, scroll to **Static files** section
   - Add mapping: URL = `/static/`, Directory = `/home/yourusername/your-repo-name/static`
   - (Only if you have a static folder)

8. **Reload Web App**:
   - Go to **Web** tab
   - Click the green **Reload** button
   - Wait a few seconds

9. **Done!** Your app will be live at `https://yourusername.pythonanywhere.com`

**Free Tier Limits:**
- 1 web app
- 512 MB disk space
- Limited CPU time (enough for small apps)
- Your app URL: `yourusername.pythonanywhere.com`
- Perfect for personal/small team use!

---

#### **B. Railway.app** (Also Easy)
1. **Sign up**: Go to [railway.app](https://railway.app) and create account
2. **New Project** → "Deploy from GitHub repo" (or upload)
3. **Add Environment Variables** (in Railway dashboard):
   ```
   FLASK_ENV = production
   FLASK_DEBUG = False
   SECRET_KEY = <see instructions below to generate>
   ```
   
   **How to generate SECRET_KEY:**
   1. On your computer, run: `python generate_secret_key.py`
   2. Copy the long random string it shows
   3. Paste it as the value for `SECRET_KEY` in Railway
4. **Deploy**: Railway auto-detects Python and deploys
5. **Done!** Your app gets a URL like `https://your-app.up.railway.app`

**Free Tier:**
- $5 credit/month (usually enough for small apps)
- No sleep (always on)

---

#### **C. Fly.io** (Good Alternative)
1. **Install Fly CLI**: Follow [fly.io/docs](https://fly.io/docs)
2. **Deploy**:
   ```bash
   fly launch
   fly deploy
   ```
3. **Done!** App at `https://your-app.fly.dev`

---

## 🏠 Option 2: Share on Local Network (Same WiFi)

If everyone is on the same WiFi network:

### Steps:
1. **Find your computer's IP address**:
   - **Windows**: Open Command Prompt, type `ipconfig`, look for "IPv4 Address" (e.g., `192.168.1.100`)
   - **Mac/Linux**: Open Terminal, type `ifconfig` or `ip addr`, look for your WiFi IP
   
2. **Run your app** (already configured):
   ```bash
   python app.py
   ```

3. **Share the URL**: 
   - Give others: `http://YOUR-IP:5000`
   - Example: `http://192.168.1.100:5000`

4. **Important**: 
   - Your computer must stay on
   - Everyone must be on same WiFi
   - Windows Firewall may block - allow Python through firewall

**Windows Firewall Fix:**
- Windows Security → Firewall → Allow an app
- Find Python → Check both Private and Public

---

## 🔗 Option 3: Temporary Public Access (ngrok)

For quick testing or temporary access:

### Steps:
1. **Download ngrok**: [ngrok.com/download](https://ngrok.com/download)
2. **Sign up** (free) and get your auth token
3. **Run your app**:
   ```bash
   python app.py
   ```
4. **In another terminal, run ngrok**:
   ```bash
   ngrok http 5000
   ```
5. **Share the URL**: ngrok gives you a public URL like `https://abc123.ngrok.io`

**Limitations:**
- Free tier: URL changes each time
- Session timeout after inactivity
- Good for testing only

---

## 📋 Pre-Deployment Checklist

Before deploying, make sure:

- [ ] Generate a strong `SECRET_KEY`:
  ```bash
  python generate_secret_key.py
  ```
  (This will show you a secure random key - copy it for use in environment variables)
- [ ] Test your app locally first
- [ ] Make sure `doc_templates/` folder has your Word templates
- [ ] Check that all features work

---

## 🚀 Quick Deploy to PythonAnywhere (Step-by-Step)

### Step 1: Prepare Your Code

Make sure you have these files:
- ✅ `app.py`
- ✅ `config.py`
- ✅ `requirements.txt`
- ✅ `doc_templates/` folder
- ✅ `templates/` folder

### Step 2: Generate SECRET_KEY

On your computer, run:
```bash
python generate_secret_key.py
```
Copy the long random string it shows - you'll need it in Step 5.

### Step 3: Sign Up for PythonAnywhere

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com/)
2. Sign up for a free account
3. Note your username (it will be part of your URL)

### Step 4: Upload Your Code

**Option A - Using GitHub (Recommended):**
1. Push your code to GitHub first
2. In PythonAnywhere, go to **Consoles** tab
3. Start a **Bash** console
4. Run: `git clone https://github.com/yourusername/your-repo-name.git`

**Option B - Manual Upload:**
1. Go to **Files** tab in PythonAnywhere
2. Navigate to `/home/yourusername/`
3. Upload all your project files (drag and drop)

### Step 5: Install Dependencies

1. In **Consoles** tab, start a **Bash** console
2. Navigate: `cd your-repo-name` (or your folder name)
3. Install: `pip3.10 install --user -r requirements.txt`

### Step 6: Configure Web App

1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration** (NOT Flask)
4. Select Python version (3.10 recommended)
5. Click **Next** → **Next** until you see WSGI configuration

### Step 7: Edit WSGI File

1. In **Web** tab, click the WSGI configuration file link
2. Delete all default code
3. Paste this (replace `yourusername` and `your-repo-name`):
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
   os.environ['SECRET_KEY'] = 'PASTE_YOUR_SECRET_KEY_HERE'  # From Step 2

   # Import your Flask app
   from app import app as application
   ```
4. Replace `PASTE_YOUR_SECRET_KEY_HERE` with the key from Step 2
5. Click **Save**

### Step 8: Reload Web App

1. Go to **Web** tab
2. Click the green **Reload** button
3. Wait a few seconds

### Step 9: Done!

Your app is live at: `https://yourusername.pythonanywhere.com`

---

## 🔧 Troubleshooting

### App won't start on PythonAnywhere:
- Check **Error log** in the **Web** tab
- Verify WSGI file paths are correct (match your username and folder)
- Make sure SECRET_KEY is set in WSGI file
- Check that all dependencies are installed (`pip3.10 install --user -r requirements.txt`)
- Verify `doc_templates/` folder is uploaded

### Can't access on local network:
- Check Windows Firewall settings
- Make sure you're on the same WiFi
- Verify IP address is correct
- Try `http://localhost:5000` on your computer first

### App works locally but not deployed:
- Check that `doc_templates/` folder is included
- Verify all files are committed to Git
- Check deployment logs for errors

---

## 💡 Recommendation

**For non-technical users**: Use **PythonAnywhere.com**
- Free tier available
- Automatic HTTPS
- No server management
- Easy file upload (GitHub or manual)
- Perfect for Flask apps
- Your URL: `yourusername.pythonanywhere.com`

---

## 📞 Need Help?

1. Check deployment logs in your hosting platform
2. Test locally first: `python app.py`
3. Make sure all files are in your Git repository
4. Verify environment variables are set correctly

---

**Good luck with your deployment!** 🎉

