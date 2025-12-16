# ⚖️ Advanced Document Generator

A modern Flask-based web application for generating legal documents from Word templates. Currently supports Writ Petition (WP) document generation with rich text editing capabilities.

## ✨ Features

- 📝 **Rich Text Editing**: Built-in WYSIWYG editor with formatting options (bold, italic, underline, lists, alignment)
- 📅 **Date Picker**: User-friendly date selection with flatpickr
- 👥 **Dynamic Parties**: Add multiple petitioners and respondents with accordion UI
- 🔒 **Security**: CSRF protection, secure session management, input validation
- 📄 **Word Template Processing**: Generate professional .docx documents
- 🧹 **Auto Cleanup**: Automatic removal of old temporary files
- 📊 **Logging**: Comprehensive logging for debugging and monitoring
- 🎨 **Modern UI**: Clean, responsive design with smooth animations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd adv_doc_gen
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (Optional)
   
   Create a `.env` file in the root directory:
   ```env
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=your-secret-key-here-change-in-production
   PORT=5000
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   
   Navigate to `http://localhost:5000`

## 📁 Project Structure

```
adv_doc_gen/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── Procfile               # Production server config (for deployment)
├── runtime.txt            # Python version (for deployment)
├── render.yaml            # Render.com deployment config
├── generate_secret_key.py # Utility to generate SECRET_KEY
├── run.bat                # Windows startup script
├── run.sh                 # Linux/Mac startup script
├── doc_templates/         # Word document templates
├── templates/             # HTML templates
├── static/                # Static files (CSS, JS, images)
├── temp/                  # Temporary files (auto-created)
└── tests/                 # Unit tests (optional)
├── README.md             # This file
├── doc_templates/        # Word document templates
│   ├── WP.docx           # Writ Petition template
│   └── complaint.docx    # Complaint template
├── templates/            # HTML templates
│   ├── base.html         # Base template with header/footer
│   ├── home.html         # Home page
│   └── form.html         # Document generation form
├── static/               # Static files (CSS, JS, images)
└── temp/                 # Temporary generated documents (auto-cleaned)
```

## 🔧 Configuration

### Environment Variables

- `FLASK_ENV`: Environment (development/production/testing)
- `FLASK_DEBUG`: Enable debug mode (True/False)
- `SECRET_KEY`: Secret key for session security (MUST change in production)
- `PORT`: Port number for the server (default: 5000)
- `SESSION_COOKIE_SECURE`: Require HTTPS for cookies (set to True in production)

### Configuration Classes

The application uses different configurations for different environments:

- **DevelopmentConfig**: Debug enabled, relaxed security
- **ProductionConfig**: Debug disabled, enhanced security, HTTPS required
- **TestingConfig**: For running tests

Edit `config.py` to customize settings like:
- Temp file cleanup interval (default: 24 hours)
- Maximum upload size (default: 16MB)
- Session cookie settings

## 📝 Using the Application

### Creating a Document

1. **Select Template**: On the home page, click on the document type (e.g., "Writ Petition")

2. **Fill Details**:
   - Enter date and district
   - Use rich text editors for Main Prayer and Interim Prayer
   - Add petitioners with names and addresses
   - Add respondents with names and addresses

3. **Format Text**: Use the toolbar to:
   - Change font (Arial, Times New Roman, Calibri, etc.)
   - Adjust font size (12px, 14px, 16px, 18px)
   - Apply bold, italic, underline
   - Create ordered or bulleted lists
   - Change text alignment

4. **Generate**: Click "Generate Document" to download the .docx file

### Adding New Document Templates

1. **Create a Word Template**:
   - Use placeholders like `{{date}}`, `{{petitioner}}`, `{{respondents}}`
   - Save as `.docx` in the `doc_templates/` folder

2. **Register in app.py**:
   ```python
   DOC_TEMPLATES = {
       "WP": {
           "name": "Writ Petition",
           "fields": ["date", "petitioner", "respondents", "main_prayer", "interim_prayer", "district"]
       },
       "NEW_TYPE": {
           "name": "Your New Template",
           "fields": ["field1", "field2", "field3"]
       }
   }
   ```

3. **Create/Update Form Template**: Modify `templates/form.html` if custom fields are needed

## 🔒 Security Features

- **CSRF Protection**: All forms protected against Cross-Site Request Forgery
- **Input Validation**: Server-side validation for all inputs
- **Secure Sessions**: HTTPOnly and SameSite cookie attributes
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Logging**: All errors logged for security auditing
- **File Cleanup**: Automatic removal of old temporary files

## 🧹 Maintenance

### Cleaning Temporary Files

The application automatically cleans up temporary files older than 24 hours when the home page is visited. To manually trigger cleanup or change the cleanup schedule, modify the `cleanup_old_files()` function in `app.py`.

### Viewing Logs

Application logs are stored in `app.log`. Monitor this file for:
- Error tracking
- Usage patterns
- Security events

```bash
# View recent logs
tail -f app.log

# On Windows (PowerShell)
Get-Content app.log -Wait -Tail 50
```

## 🚀 Production Deployment

### Important Security Steps

1. **Set a Strong Secret Key**:
   ```bash
   export SECRET_KEY=$(python -c 'import os; print(os.urandom(32).hex())')
   ```

2. **Disable Debug Mode**:
   ```bash
   export FLASK_ENV=production
   export FLASK_DEBUG=False
   ```

3. **Enable HTTPS**:
   - Use a reverse proxy (nginx, Apache)
   - Set `SESSION_COOKIE_SECURE=True`

4. **Use Production Server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

### Deployment Checklist

- [ ] Change `SECRET_KEY` to a random value
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Enable HTTPS
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Configure proper logging (file rotation)
- [ ] Set up firewall rules
- [ ] Configure backup strategy for templates
- [ ] Monitor disk space for temp folder

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Template not found" error
- **Solution**: Ensure the .docx template file exists in `doc_templates/` folder

**Issue**: CSRF token missing
- **Solution**: Clear browser cookies and reload the page

**Issue**: Temp folder fills up
- **Solution**: Check cleanup settings in `config.py` or manually delete old files

**Issue**: Import errors
- **Solution**: Ensure virtual environment is activated and run `pip install -r requirements.txt`

## 📦 Dependencies

- **Flask 3.1.0**: Web framework
- **Flask-WTF 1.2.2**: Form handling and CSRF protection
- **docxtpl 0.20.1**: Word template processing
- **python-docx 1.2.0**: Word document manipulation
- **beautifulsoup4 4.14.2**: HTML parsing
- **lxml 6.0.2**: XML processing
- **WTForms 3.2.1**: Form validation
- **python-dotenv 1.0.1**: Environment variable management

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contributing guidelines here]

## 📧 Support

For issues or questions, please [add contact information or issue tracker URL].

## 🎯 Roadmap

- [ ] Add more document templates
- [ ] Support for document preview before download
- [ ] User authentication and document history
- [ ] Batch document generation
- [ ] Custom template builder UI
- [ ] Export to PDF functionality
- [ ] Email integration for document delivery

---

