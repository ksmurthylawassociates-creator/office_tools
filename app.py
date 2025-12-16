"""
Advanced Document Generator - Flask Application
A web application for generating legal documents from templates.
"""
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, Response, session, abort
from flask_wtf.csrf import CSRFProtect
from docxtpl import DocxTemplate
from bs4 import BeautifulSoup
import os
import uuid
import logging
from datetime import datetime, timedelta
from config import config
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore

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

# Initialize Firebase
try:
    if not firebase_admin._apps:
        firebase_cred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'firebase-key.json')
        if os.path.exists(firebase_cred_path):
            cred = credentials.Certificate(firebase_cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            logger.info("Firebase initialized successfully")
        else:
            db = None
            logger.warning("Firebase credentials not found. Invoice generator will not work.")
    else:
        db = firestore.client()
except Exception as e:
    logger.error(f"Error initializing Firebase: {e}")
    db = None

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


def invoice_password_required(f):
    """Decorator to require password for invoice generator routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('invoice_authenticated'):
            return redirect(url_for('invoice_password'))
        return f(*args, **kwargs)
    return decorated_function


# ---- Invoice Generator Helper Functions ----
def generate_invoice_id():
    """Generate unique invoice ID."""
    if not db:
        raise Exception("Firebase not initialized")
    counters_ref = db.collection("meta").document("counters")

    @firestore.transactional
    def txn(transaction):
        snap = counters_ref.get(transaction=transaction)
        data = snap.to_dict() or {}
        next_num = int(data.get("invoice_next", 1))
        transaction.set(counters_ref, {"invoice_next": next_num + 1}, merge=True)
        return f"inv{next_num:04d}"

    return txn(db.transaction())


def generate_ref_no(issue_date: str):
    """Generate Ref No in format: Bill/{Month}/{Year}/{SequentialNumber}"""
    if not db or not issue_date:
        return None
    
    try:
        if "/" in issue_date:
            parts = issue_date.split("/")
            if len(parts) == 3:
                day, month, year = parts
                month_num = int(month)
            else:
                return None
        else:
            parts = issue_date.split("-")
            if len(parts) == 3:
                year, month_num, day = parts
                month_num = int(month_num)
            else:
                return None
        
        months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        if month_num < 1 or month_num > 12:
            return None
        
        month_abbr = months[month_num]
        month_key = f"{year}_{month_num:02d}"
        counters_ref = db.collection("meta").document("counters")

        @firestore.transactional
        def txn(transaction):
            snap = counters_ref.get(transaction=transaction)
            data = snap.to_dict() or {}
            monthly_counters = data.get("monthly_ref_counters", {})
            current_count = int(monthly_counters.get(month_key, 0)) + 1
            monthly_counters[month_key] = current_count
            transaction.set(counters_ref, {"monthly_ref_counters": monthly_counters}, merge=True)
            return f"Bill/{month_abbr}/{year}/{current_count:02d}"

        return txn(db.transaction())
        
    except Exception as e:
        logger.error(f"Error generating ref_no: {e}")
        return None


def doc_or_404(invoice_id: str):
    """Get invoice document or return 404."""
    if not db:
        abort(404)
    snap = db.collection("invoices").document(invoice_id).get()
    if not snap.exists:
        abort(404)
    return snap.to_dict()


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


# ---- Invoice Generator Routes ----
@app.route("/invoice/password", methods=["GET", "POST"])
def invoice_password():
    """Password verification for invoice generator."""
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == app.config.get('INVOICE_GENERATOR_PASSWORD'):
            session['invoice_authenticated'] = True
            flash("Access granted!", "success")
            return redirect(url_for('invoice_list'))
        else:
            flash("Incorrect password. Please try again.", "error")
    
    return render_template("invoice_password.html")


@app.route("/invoice/logout")
def invoice_logout():
    """Logout from invoice generator."""
    session.pop('invoice_authenticated', None)
    flash("Logged out from invoice generator.", "info")
    return redirect(url_for('home'))


@app.route("/invoices")
@invoice_password_required
@error_handler
def invoice_list():
    """List all invoices."""
    if not db:
        flash("Firebase not initialized. Invoice generator is unavailable.", "error")
        return redirect(url_for('home'))
    
    snaps = db.collection("invoices").order_by(
        "created_at", direction=firestore.Query.DESCENDING
    ).stream()
    invoices = [s.to_dict() for s in snaps]
    return render_template("invoice_list.html", invoices=invoices)


@app.route("/invoices/new", methods=["GET"])
@invoice_password_required
@error_handler
def new_invoice():
    """Show form to create new invoice."""
    if not db:
        flash("Firebase not initialized. Invoice generator is unavailable.", "error")
        return redirect(url_for('home'))
    return render_template("invoice_form.html")


@app.route("/invoices", methods=["POST"])
@invoice_password_required
@error_handler
def create_invoice():
    """Create a new invoice."""
    if not db:
        flash("Firebase not initialized. Invoice generator is unavailable.", "error")
        return redirect(url_for('home'))
    
    invoice_id = generate_invoice_id()
    
    items, idx = [], 0
    while True:
        desc = request.form.get(f"items-{idx}-description")
        if not desc:
            break
        rate = float(request.form.get(f"items-{idx}-rate", 0) or 0)
        items.append({"description": desc, "qty": 1, "rate": rate})
        idx += 1

    issue_date = request.form.get("issue_date", "")
    firm_type = request.form.get("firm_type", "individual")
    
    if firm_type == "associates":
        firm_name = "K. S. Murthy Associates"
        firm_role = ""
    else:
        firm_name = "K. Srinivas Murthy"
        firm_role = "Senior Advocate"

    ref_no = generate_ref_no(issue_date)

    doc = {
        "invoice_id": invoice_id,
        "issue_date": issue_date,
        "ref_no": ref_no,
        "case_ref": request.form.get("case_ref", ""),
        "recipient_name": request.form.get("recipient_name", ""),
        "recipient_address": request.form.get("recipient_address", ""),
        "subject_continuation": request.form.get("subject_continuation", ""),
        "bank_option": request.form.get("bank_option", "option1"),
        "firm_type": firm_type,
        "firm_name": firm_name,
        "firm_role": firm_role,
        "items": items,
        "created_at": datetime.utcnow(),
        "firm": {
            "firm_name": firm_name,
            "address": "D.No. 23-1-2, Ground Floor, Sri Sai Viswanatha Towers, Satyaranayana Puram,\nVijayawada – 520003",
            "phone": "",
            "gstin": None,
        },
    }
    db.collection("invoices").document(invoice_id).set(doc)
    flash(f'Invoice {invoice_id} created successfully!', 'success')
    return redirect(url_for("invoice_detail", invoice_id=invoice_id))


@app.route("/invoices/<invoice_id>")
@invoice_password_required
@error_handler
def invoice_detail(invoice_id):
    """View invoice details."""
    if not db:
        flash("Firebase not initialized. Invoice generator is unavailable.", "error")
        return redirect(url_for('home'))
    
    inv = doc_or_404(invoice_id)
    firm = inv.get("firm") or {"firm_name": "", "address": "", "phone": "", "gstin": None}
    auto = request.args.get("auto") == "1"
    return render_template("invoice_print.html", invoice=inv, firm=firm, auto_print=auto)


@app.route("/invoices/<invoice_id>/edit", methods=["GET"])
@invoice_password_required
@error_handler
def invoice_edit_form(invoice_id):
    """Show form to edit invoice."""
    if not db:
        flash("Firebase not initialized. Invoice generator is unavailable.", "error")
        return redirect(url_for('home'))
    
    inv = doc_or_404(invoice_id)
    return render_template("invoice_edit.html", invoice=inv)


@app.route("/invoices/<invoice_id>/edit", methods=["POST"])
@invoice_password_required
@error_handler
def invoice_edit(invoice_id):
    """Update invoice."""
    if not db:
        flash("Firebase not initialized. Invoice generator is unavailable.", "error")
        return redirect(url_for('home'))
    
    _ = doc_or_404(invoice_id)

    items, idx = [], 0
    while True:
        desc = request.form.get(f"items-{idx}-description")
        if not desc:
            break
        rate = float(request.form.get(f"items-{idx}-rate", 0) or 0)
        items.append({"description": desc, "qty": 1, "rate": rate})
        idx += 1

    firm_type = request.form.get("firm_type", "individual")
    
    if firm_type == "associates":
        firm_name = "K. S. Murthy Associates"
        firm_role = ""
    else:
        firm_name = "K. Srinivas Murthy"
        firm_role = "Senior Advocate"

    updates = {
        "issue_date": request.form.get("issue_date", ""),
        "case_ref": request.form.get("case_ref", ""),
        "recipient_name": request.form.get("recipient_name", ""),
        "recipient_address": request.form.get("recipient_address", ""),
        "subject_continuation": request.form.get("subject_continuation", ""),
        "bank_option": request.form.get("bank_option", "option1"),
        "firm_type": firm_type,
        "firm_name": firm_name,
        "firm_role": firm_role,
        "items": items,
        "updated_at": datetime.utcnow(),
    }
    db.collection("invoices").document(invoice_id).set(updates, merge=True)
    flash(f'Invoice {invoice_id} updated successfully!', 'success')
    return redirect(url_for("invoice_detail", invoice_id=invoice_id))


@app.route("/invoices/<invoice_id>/delete", methods=["POST"])
@invoice_password_required
@error_handler
def invoice_delete(invoice_id):
    """Delete invoice."""
    if not db:
        flash("Firebase not initialized. Invoice generator is unavailable.", "error")
        return redirect(url_for('home'))
    
    db.collection("invoices").document(invoice_id).delete()
    flash(f'Invoice {invoice_id} deleted successfully!', 'success')
    return redirect(url_for('invoice_list'))


# ---- Invoice Template Filters ----
@app.template_filter("ddmmyyyy")
def ddmmyyyy(value):
    """Format date to dd/mm/yyyy."""
    if not value:
        return value
    try:
        if "/" in value:
            parts = value.split("/")
            if len(parts) == 3 and len(parts[2]) == 4:
                return value
        y, m, d = value.split("-")
        return f"{d}/{m}/{y}"
    except Exception:
        return value


def _format_inr(amount: float) -> str:
    """Format amount in Indian Rupee format."""
    neg = amount < 0
    amount = abs(float(amount))
    s = f"{amount:.2f}"
    whole, frac = s.split(".")
    if len(whole) <= 3:
        grouped = whole
    else:
        last3 = whole[-3:]
        head = whole[:-3]
        parts = []
        while head:
            parts.append(head[-2:])
            head = head[:-2]
        grouped = ",".join(reversed(parts)) + "," + last3
    return ("-" if neg else "") + grouped + "." + frac


@app.template_filter("inr")
def inr(value):
    """Format value as INR currency."""
    try:
        return _format_inr(float(value))
    except Exception:
        return value


@app.template_filter("number_to_words")
def number_to_words(value):
    """Convert number to words in Indian format."""
    try:
        num = int(float(value))
        if num == 0:
            return "Zero Rupees Only"
        
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", 
                "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", 
                "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        def convert_hundreds(n):
            result = ""
            if n >= 100:
                result += ones[n // 100] + " Hundred"
                n %= 100
                if n > 0:
                    result += " "
            if n >= 20:
                result += tens[n // 10]
                n %= 10
                if n > 0:
                    result += " " + ones[n]
            elif n > 0:
                result += ones[n]
            return result.strip()
        
        result_parts = []
        
        if num >= 10000000:
            crores = num // 10000000
            result_parts.append(convert_hundreds(crores) + " Crore")
            num %= 10000000
        
        if num >= 100000:
            lakhs = num // 100000
            result_parts.append(convert_hundreds(lakhs) + " Lakh")
            num %= 100000
        
        if num >= 1000:
            thousands = num // 1000
            result_parts.append(convert_hundreds(thousands) + " Thousand")
            num %= 1000
        
        if num > 0:
            result_parts.append(convert_hundreds(num))
        
        words = " ".join(result_parts) + " Rupees Only"
        return words
    except Exception:
        return value


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