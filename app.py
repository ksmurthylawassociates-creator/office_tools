"""
Advanced Document Generator - Flask Application
A web application for generating legal documents from templates.
"""
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, Response
from flask_wtf.csrf import CSRFProtect
from docxtpl import DocxTemplate
from bs4 import BeautifulSoup
import os
import uuid
import logging
from datetime import datetime, timedelta
from config import config
from functools import wraps

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not app.config['DEBUG'] else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define available templates and their fields
DOC_TEMPLATES = {
    "WP": {
        "name": "Writ Petition",
        "fields": ["date", "petitioner", "respondents", "main_prayer", "interim_prayer", "district"]
}
}


def extract_plain(html):
    """
    Extract plain text from HTML content.
    
    Args:
        html: HTML string to parse
        
    Returns:
        Plain text with line breaks preserved
    """
    if not html:
        return ""
    try:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n").strip()
    except Exception as e:
        logger.error(f"Error extracting plain text: {e}")
        return html


def cleanup_old_files():
    """
    Remove temporary files older than TEMP_FILE_MAX_AGE.
    """
    try:
        temp_folder = app.config['TEMP_FOLDER']
        if not os.path.exists(temp_folder):
            return
        
        max_age = app.config['TEMP_FILE_MAX_AGE']
        now = datetime.now()
        removed_count = 0
        
        for filename in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, filename)
            if os.path.isfile(file_path):
                file_age = datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_age > max_age:
                    os.remove(file_path)
                    removed_count += 1
                    logger.info(f"Removed old temp file: {filename}")
        
        if removed_count > 0:
            logger.info(f"Cleanup complete: {removed_count} file(s) removed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


def validate_input(value, field_name, max_length=1000, required=True):
    """
    Validate form input.
    
    Args:
        value: Input value to validate
        field_name: Name of the field for error messages
        max_length: Maximum allowed length
        required: Whether the field is required
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if required and not value:
        return False, f"{field_name} is required"
    
    if value and len(value) > max_length:
        return False, f"{field_name} exceeds maximum length of {max_length}"
    
    return True, None


def error_handler(f):
    """Decorator for handling errors in routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            flash("An error occurred while processing your request. Please try again.", "error")
            return redirect(url_for('home'))
    return decorated_function


@app.route("/")
def home():
    """Render home page with available templates."""
    cleanup_old_files()  # Clean up old files on home page visit
    return render_template("home.html", templates=DOC_TEMPLATES)


@app.route("/form/<doc_type>", methods=["GET"])
@error_handler
def form(doc_type):
    """
    Render form for a specific document type.
    
    Args:
        doc_type: Type of document to generate
    """
    template_info = DOC_TEMPLATES.get(doc_type)
    if not template_info:
        flash("Invalid document type selected.", "error")
        return redirect(url_for('home'))
    
    logger.info(f"Rendering form for document type: {doc_type}")
    return render_template("form.html", doc_type=doc_type, template_info=template_info)


@app.route("/generate", methods=["POST"])
@error_handler
def generate():
    """
    Generate document from form data.
    """
    doc_type = request.form.get("doc_type")
    template_info = DOC_TEMPLATES.get(doc_type)

    if not template_info:
        flash("Invalid document type.", "error")
        return redirect(url_for('home'))

    # Validate required fields
    date = request.form.get("date", "").strip()
    district = request.form.get("district", "").strip()
    
    is_valid, error = validate_input(date, "Date", max_length=20)
    if not is_valid:
        flash(error, "error")
        return redirect(url_for('form', doc_type=doc_type))
    
    is_valid, error = validate_input(district, "District", max_length=100)
    if not is_valid:
        flash(error, "error")
        return redirect(url_for('form', doc_type=doc_type))

    # Combine multiple petitioners
    petitioner_names = request.form.getlist("petitioner_names")
    petitioner_addresses = request.form.getlist("petitioner_addresses")
    
    if not petitioner_names or not any(petitioner_names):
        flash("At least one petitioner is required.", "error")
        return redirect(url_for('form', doc_type=doc_type))

    # Create list of petitioners for Word template looping
    petitioner_list = []
    for name, addr in zip(petitioner_names, petitioner_addresses):
        name_clean = extract_plain(name)
        addr_clean = extract_plain(addr)
        if name_clean:  # Only add if name is not empty
            # Preserve line breaks in address - split by newlines and join with proper formatting
            address_lines = [line.strip() for line in addr_clean.split('\n') if line.strip()]
            petitioner_list.append({
                'name': name_clean,
                'address': '\n'.join(address_lines)  # Keep line breaks for Word template
            })

    # Combine multiple respondents
    respondent_names = request.form.getlist("respondent_names")
    respondent_addresses = request.form.getlist("respondent_addresses")
    
    if not respondent_names or not any(respondent_names):
        flash("At least one respondent is required.", "error")
        return redirect(url_for('form', doc_type=doc_type))

    # Create list of respondents for Word template looping
    respondent_list = []
    for name, addr in zip(respondent_names, respondent_addresses):
        name_clean = extract_plain(name)
        addr_clean = extract_plain(addr)
        if name_clean:  # Only add if name is not empty
            # Preserve line breaks in address - split by newlines and join with proper formatting
            address_lines = [line.strip() for line in addr_clean.split('\n') if line.strip()]
            respondent_list.append({
                'name': name_clean,
                'address': '\n'.join(address_lines)  # Keep line breaks for Word template
            })

    # Prepare context with multiple access patterns for flexibility
    context = {
        "date": date,
        "district": district,
        
        # FULL LISTS - For looping through all petitioners/respondents
        "petitioner_list": petitioner_list,
        "respondent_list": respondent_list,
        
        # FIRST PETITIONER/RESPONDENT - Quick access to primary party
        "first_petitioner": petitioner_list[0] if petitioner_list else {'name': '', 'address': ''},
        "first_respondent": respondent_list[0] if respondent_list else {'name': '', 'address': ''},
        
        # LEGACY FORMAT - Combined text for backward compatibility
        "petitioner": "\n\n".join([f"{p['name']}\n{p['address']}" for p in petitioner_list]),
        "respondents": "\n\n".join([f"{r['name']}\n{r['address']}" for r in respondent_list]),
        
        # NAMES ONLY - Comma-separated list of names
        "petitioner_names": ", ".join([p['name'] for p in petitioner_list]),
        "respondent_names": ", ".join([r['name'] for r in respondent_list]),
        
        # ADDRESSES ONLY - Separate list of addresses
        "petitioner_addresses": petitioner_list,  # Can loop through for addresses
        "respondent_addresses": respondent_list,  # Can loop through for addresses
        
        # COUNT - How many petitioners/respondents
        "petitioner_count": len(petitioner_list),
        "respondent_count": len(respondent_list),
        
        "main_prayer": extract_plain(request.form.get("main_prayer", "")),
        "interim_prayer": extract_plain(request.form.get("interim_prayer", ""))
    }

    # Template loading
    template_path = os.path.join(app.config['TEMPLATE_FOLDER'], f"{doc_type}.docx")
    if not os.path.exists(template_path):
        logger.error(f"Template not found: {template_path}")
        flash("Document template not found. Please contact administrator.", "error")
        return redirect(url_for('home'))

    # Generate document
    try:
        doc = DocxTemplate(template_path)
        doc.render(context)

        output_filename = f"output_{uuid.uuid4().hex}.docx"
        output_path = os.path.join(app.config['TEMP_FOLDER'], output_filename)
        os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
        doc.save(output_path)

        logger.info(f"Document generated successfully: {output_filename}")
        download_filename = f"{doc_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        
        # Ensure "Save As" dialog appears by setting proper headers
        response = send_file(
            output_path, 
            as_attachment=True, 
            download_name=download_filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        # Explicitly set Content-Disposition to force "Save As" dialog
        response.headers['Content-Disposition'] = f'attachment; filename="{download_filename}"'
        
        return response
    except Exception as e:
        logger.error(f"Error generating document: {e}", exc_info=True)
        flash("Error generating document. Please check your input and try again.", "error")
        return redirect(url_for('form', doc_type=doc_type))


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.url}")
    flash("Page not found.", "error")
    return redirect(url_for('home'))


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"500 error: {error}", exc_info=True)
    flash("An internal error occurred. Please try again later.", "error")
    return redirect(url_for('home'))


if __name__ == "__main__":
    # Ensure temp directory exists
    os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])