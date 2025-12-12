# ⚡ Quick Start Guide

Get up and running with Advanced Document Generator in 5 minutes!

## 🚀 Windows Users

### Method 1: Use the Startup Script (Easiest)

1. **Open Command Prompt or PowerShell** in the project folder
2. **Run the startup script**:
   ```cmd
   run.bat
   ```
3. **Open your browser** to `http://localhost:5000`
4. **Done!** 🎉

### Method 2: Manual Setup

```cmd
:: Create virtual environment
python -m venv venv

:: Activate it
venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt

:: Run the app
python app.py
```

---

## 🍎 macOS/Linux Users

### Method 1: Use the Startup Script (Easiest)

1. **Open Terminal** in the project folder
2. **Make script executable**:
   ```bash
   chmod +x run.sh
   ```
3. **Run the script**:
   ```bash
   ./run.sh
   ```
4. **Open your browser** to `http://localhost:5000`
5. **Done!** 🎉

### Method 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

---

## 📝 First Time Use

### 1. Home Page
- You'll see available document templates
- Currently supports **Writ Petition (WP)**

### 2. Create a Document
1. Click on **"Writ Petition"**
2. Fill in the form:
   - **Date**: Use the date picker
   - **District**: Enter district name
   - **Main Prayer**: Use rich text editor (bold, italic, lists, etc.)
   - **Interim Prayer**: Same as main prayer
   - **Petitioners**: Click "Add Petitioner" to add parties
   - **Respondents**: Click "Add Respondent" to add opposing parties

### 3. Generate Document
- Click **"Generate Document"** button
- Your .docx file will download automatically

---

## 🔧 Common Issues & Solutions

### Issue: "Module not found" error
**Solution**:
```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Then reinstall:
pip install -r requirements.txt
```

### Issue: "Template not found" error
**Solution**: Make sure you have `WP.docx` in the `doc_templates/` folder

### Issue: Can't access localhost:5000
**Solution**: 
- Check if port 5000 is already in use
- Try a different port:
  ```bash
  # Set in .env file
  PORT=8000
  ```

### Issue: CSRF token error
**Solution**: Clear browser cookies and reload

---

## 🎯 Next Steps

1. **Read the full documentation**: See `README.md`
2. **Customize templates**: Add your own .docx templates
3. **Configure for production**: See `DEPLOYMENT.md`
4. **Learn about the fixes**: See `FIXES_SUMMARY.md`

---

## 💡 Pro Tips

### Tip 1: Use the Rich Text Editor
- **Bold**: Ctrl+B
- **Italic**: Ctrl+I
- **Undo**: Ctrl+Z

### Tip 2: Multiple Parties
- Add as many petitioners/respondents as needed
- Use "Minimize" button to collapse entries
- Use "Delete" to remove unwanted entries

### Tip 3: Date Format
- Use DD/MM/YYYY format (e.g., 25/12/2024)
- Or use the date picker for convenience

---

## 📞 Need Help?

- **Documentation**: Check `README.md`
- **Deployment**: Check `DEPLOYMENT.md`
- **Contributing**: Check `CONTRIBUTING.md`
- **Changes**: Check `CHANGELOG.md`

---

## ✅ Checklist

Before using the application, make sure:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Template files in `doc_templates/` folder
- [ ] Port 5000 available (or change in .env)

---

**Happy Document Generating! 📄✨**

