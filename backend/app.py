from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
import mimetypes

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            static_folder='../frontend',
            static_url_path='')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", SENDER_EMAIL)

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
RESUME_DIR = os.path.join(FRONTEND_DIR, 'Resume')
IMAGES_DIR = os.path.join(FRONTEND_DIR, 'images')

# ============================================
# SERVE FRONTEND FILES
# ============================================

@app.route('/')
def serve_index():
    """Serve the main index.html file"""
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    """Serve all frontend files (CSS, JS, images, etc.)"""
    # Try to serve the requested file
    file_path = os.path.join(FRONTEND_DIR, path)
    
    # If file exists in frontend, serve it
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, path)
    
    # Check if it's in images folder
    images_path = os.path.join(IMAGES_DIR, path)
    if os.path.exists(images_path) and os.path.isfile(images_path):
        return send_from_directory(IMAGES_DIR, path)
    
    # If it's a CSS/JS file with wrong path, try to serve from frontend root
    if path.endswith('.css') or path.endswith('.js'):
        filename = os.path.basename(path)
        return send_from_directory(FRONTEND_DIR, filename)
    
    # Otherwise, serve index.html (for SPA routing)
    return send_from_directory(FRONTEND_DIR, 'index.html')

# ============================================
# DOWNLOAD CV ENDPOINT
# ============================================

@app.route('/download-cv')
def download_cv():
    """Download CV endpoint"""
    try:
        cv_filename = 'Arulmani S_TCS_NQT.pdf.pdf'
        cv_path = os.path.join(RESUME_DIR, cv_filename)
        
        # Alternative filenames to try
        alternative_filenames = [
            'Arulmani_S_Resume.pdf',
            'Arulmani_S_CV.pdf',
            'resume.pdf',
            'cv.pdf'
        ]
        
        # Check if file exists
        if not os.path.exists(cv_path):
            # Try alternative filenames
            for alt_filename in alternative_filenames:
                alt_path = os.path.join(RESUME_DIR, alt_filename)
                if os.path.exists(alt_path):
                    cv_path = alt_path
                    cv_filename = alt_filename
                    break
            else:
                logger.error(f"CV file not found in {RESUME_DIR}")
                return jsonify({'error': 'CV file not found'}), 404
        
        # Log download (optional)
        logger.info(f"CV downloaded at: {datetime.now()}")
        
        # Send file for download
        return send_file(
            cv_path,
            as_attachment=True,
            download_name='Arulmani_S_Resume.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error downloading CV: {str(e)}")
        return jsonify({'error': 'Failed to download CV'}), 500

# ============================================
# CONTACT FORM ENDPOINT
# ============================================

@app.route('/api/contact', methods=['POST'])
def contact_form():
    """Handle contact form submission"""
    try:
        # Get form data
        data = request.json
        
        # Extract fields
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')
        
        # Validate required fields
        if not all([name, email, subject, message]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'message': 'Please enter a valid email address'
            }), 400
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = f"Portfolio Contact: {subject}"
        
        # Email body (HTML format)
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #22C1F1; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .field {{ margin-bottom: 20px; }}
                .label {{ font-weight: bold; color: #666; margin-bottom: 5px; }}
                .value {{ background: white; padding: 10px; border-radius: 5px; border-left: 4px solid #22C1F1; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📬 New Message from Portfolio</h2>
                </div>
                <div class="content">
                    <div class="field">
                        <div class="label">👤 Name:</div>
                        <div class="value">{name}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">📧 Email:</div>
                        <div class="value"><a href="mailto:{email}">{email}</a></div>
                    </div>
                    
                    <div class="field">
                        <div class="label">📋 Subject:</div>
                        <div class="value">{subject}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">💬 Message:</div>
                        <div class="value" style="white-space: pre-wrap;">{message}</div>
                    </div>
                    
                    <div class="field">
                        <div class="label">⏰ Time:</div>
                        <div class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>
                    
                    <div class="footer">
                        <a href="mailto:{email}?subject=Re:%20{subject}" 
                           style="background: #22C1F1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                           Reply to {name}
                        </a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        # Send auto-reply to user (optional)
        send_auto_reply(name, email)
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully! I will get back to you soon.'
        }), 200
        
    except Exception as e:
        logger.error(f"Contact form error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to send message. Please try again later.'
        }), 500

def send_auto_reply(name, user_email):
    """Send auto-reply to the user"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = user_email
        msg['Subject'] = "Thank you for contacting Arulmani"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #22C1F1;">Thank You for Reaching Out! 🙏</h2>
            <p>Dear {name},</p>
            <p>Thank you for contacting me. I have received your message and will get back to you within 24 hours.</p>
            <p>In the meantime, feel free to:</p>
            <ul>
                <li>Check out my <a href="https://www.linkedin.com/in/arulmani-s/">LinkedIn</a></li>
                <li>Browse my <a href="#">GitHub</a></li>
            </ul>
            <p>Best regards,<br>
            <strong>Arulmani S</strong><br>
            Web Developer</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
    except Exception as e:
        logger.error(f"Auto-reply failed: {str(e)}")

# ============================================
# HIRE ME ENDPOINT
# ============================================

@app.route('/api/hire-me', methods=['POST'])
def hire_me():
    """Handle Hire Me button click"""
    try:
        data = request.json
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = "🎯 Hiring Interest - Arulmani S"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #22C1F1;">🎯 Someone wants to hire you!</h2>
            
            <div style="background: #f5f5f5; padding: 20px; border-radius: 10px;">
                <p><strong>From:</strong> {data.get('name', 'Anonymous')}</p>
                <p><strong>Email:</strong> {data.get('email', 'Not provided')}</p>
                <p><strong>Message:</strong> {data.get('message', 'Interested in hiring')}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <p><a href="mailto:{data.get('email')}" 
                  style="background: #22C1F1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                  Reply to Candidate
            </a></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"Hire me error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# HEALTH CHECK ENDPOINT
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if server is running"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'email_configured': bool(SENDER_EMAIL and SENDER_PASSWORD)
    })

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == '__main__':
    # Check if email is configured
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        logger.warning("⚠️  Email not configured. Contact form will not work.")
        logger.warning("   Set SENDER_EMAIL and SENDER_PASSWORD in .env file")
    
    # Check if CV exists
    cv_path = os.path.join(RESUME_DIR, 'Arulmani S_TCS_NQT.pdf.pdf')
    if not os.path.exists(cv_path):
        logger.warning(f"⚠️  CV file not found at: {cv_path}")
        logger.warning("   Download CV feature may not work")
    
    print("\n" + "="*50)
    print("🚀 Portfolio Server Starting...")
    print("="*50)
    print(f"📁 Frontend: {FRONTEND_DIR}")
    print(f"📄 CV Path: {RESUME_DIR}")
    print(f"📧 Email: {'✅ Configured' if SENDER_EMAIL else '❌ Not configured'}")
    print("="*50)
    print("🌐 Access your portfolio at:")
    print("   http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)