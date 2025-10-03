from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
import os
import pandas as pd
from datetime import datetime
import json
from demo import EmailAutomation
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Global variables for email automation
email_automation = None
campaign_status = {
    'running': False,
    'progress': 0,
    'total': 0,
    'sent': 0,
    'failed': 0,
    'current_email': '',
    'start_time': None,
    'end_time': None,
    'results': None
}

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/onboarding')
def onboarding():
    """Onboarding page for new users"""
    return render_template('onboarding.html')

@app.route('/configure', methods=['GET', 'POST'])
def configure():
    """Email configuration page"""
    if request.method == 'POST':
        global email_automation
        
        sender_email = request.form.get('sender_email')
        sender_password = request.form.get('sender_password')
        sender_name = request.form.get('sender_name', 'Nirmal Boghara')
        
        if not sender_email or not sender_password:
            flash('Please provide both email and password', 'error')
            return render_template('configure.html')
        
        try:
            email_automation = EmailAutomation(sender_email, sender_password, sender_name)
            flash('Email configuration saved successfully!', 'success')
            return redirect(url_for('upload'))
        except Exception as e:
            flash(f'Error configuring email: {str(e)}', 'error')
    
    return render_template('configure.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """CSV file upload page"""
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No file selected', 'error')
            return render_template('upload.html')
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return render_template('upload.html')
        
        if file and file.filename.endswith('.csv'):
            # Save uploaded file
            filename = f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(filepath)
            
            # Validate CSV structure
            try:
                df = pd.read_csv(filepath)
                required_columns = ['company_name', 'role', 'recruiter_email']
                if not all(col in df.columns for col in required_columns):
                    flash(f'CSV must contain columns: {required_columns}', 'error')
                    os.remove(filepath)
                    return render_template('upload.html')
                
                # Store file info in session or global variable
                app.config['current_csv'] = filepath
                flash(f'File uploaded successfully! Found {len(df)} contacts.', 'success')
                return redirect(url_for('preview'))
                
            except Exception as e:
                flash(f'Error reading CSV file: {str(e)}', 'error')
                if os.path.exists(filepath):
                    os.remove(filepath)
        else:
            flash('Please upload a CSV file', 'error')
    
    return render_template('upload.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    """Upload resume file"""
    if 'resume_file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['resume_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file type
    allowed_extensions = {'.pdf', '.doc', '.docx'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({'error': 'Please upload a PDF, DOC, or DOCX file'}), 400
    
    # Check file size (max 10MB)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > 10 * 1024 * 1024:  # 10MB
        return jsonify({'error': 'File size too large. Maximum 10MB allowed.'}), 400
    
    try:
        # Save resume file
        filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)
        
        # Store resume path in app config
        app.config['current_resume'] = filepath
        
        return jsonify({
            'message': 'Resume uploaded successfully!',
            'filename': filename,
            'filepath': filepath
        })
        
    except Exception as e:
        return jsonify({'error': f'Error uploading resume: {str(e)}'}), 500

@app.route('/get_resume_list')
def get_resume_list():
    """Get list of available resume files"""
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        return jsonify([])
    
    resume_files = []
    for filename in os.listdir(uploads_dir):
        if filename.startswith('resume_') and filename.endswith(('.pdf', '.doc', '.docx')):
            filepath = os.path.join(uploads_dir, filename)
            file_size = os.path.getsize(filepath)
            resume_files.append({
                'filename': filename,
                'filepath': filepath,
                'size': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2)
            })
    
    return jsonify(resume_files)

@app.route('/preview')
def preview():
    """Preview CSV data before sending"""
    csv_file = app.config.get('current_csv')
    if not csv_file or not os.path.exists(csv_file):
        flash('No CSV file found. Please upload a file first.', 'error')
        return redirect(url_for('upload'))
    
    try:
        df = pd.read_csv(csv_file)
        # Show first 10 rows for preview
        preview_data = df.head(10).to_dict('records')
        total_rows = len(df)
        return render_template('preview.html', 
                             preview_data=preview_data, 
                             total_rows=total_rows,
                             columns=df.columns.tolist())
    except Exception as e:
        flash(f'Error reading CSV file: {str(e)}', 'error')
        return redirect(url_for('upload'))

@app.route('/campaign')
def campaign():
    """Campaign management page"""
    return render_template('campaign.html', status=campaign_status)

@app.route('/start_campaign', methods=['POST'])
def start_campaign():
    """Start email campaign"""
    global campaign_status, email_automation
    
    if email_automation is None:
        return jsonify({'error': 'Please configure email settings first'}), 400
    
    csv_file = app.config.get('current_csv')
    if not csv_file or not os.path.exists(csv_file):
        return jsonify({'error': 'No CSV file found. Please upload a file first.'}), 400
    
    if campaign_status['running']:
        return jsonify({'error': 'Campaign is already running'}), 400
    
    # Get campaign parameters
    test_mode = request.json.get('test_mode', True)
    delay_seconds = request.json.get('delay_seconds', 2)
    resume_path = request.json.get('resume_path', app.config.get('current_resume', 'Nirmal_Boghara_FTE_Resume.pdf'))
    
    # Check if resume exists
    if resume_path and not os.path.exists(resume_path):
        resume_path = None
    
    # Reset campaign status
    campaign_status.update({
        'running': True,
        'progress': 0,
        'sent': 0,
        'failed': 0,
        'current_email': '',
        'start_time': datetime.now().isoformat(),
        'end_time': None,
        'results': None
    })
    
    # Start campaign in background thread
    def run_campaign():
        global campaign_status
        try:
            # Read CSV to get total count
            df = pd.read_csv(csv_file)
            total_emails = len(df)
            campaign_status['total'] = total_emails
            
            # Create a custom email automation that updates progress
            class ProgressEmailAutomation(EmailAutomation):
                def send_bulk_emails(self, csv_file_path, resume_path=None, delay_seconds=2, test_mode=True):
                    global campaign_status
                    try:
                        df = pd.read_csv(csv_file_path)
                        required_columns = ['company_name', 'role', 'recruiter_email']
                        if not all(col in df.columns for col in required_columns):
                            raise ValueError(f"CSV must contain columns: {required_columns}")
                        
                        has_recruiter_name = 'recruiter_first_name' in df.columns
                        stats = {
                            'total_emails': len(df),
                            'sent_successfully': 0,
                            'failed_to_send': 0,
                            'start_time': datetime.now(),
                            'failed_emails': []
                        }
                        
                        if not test_mode:
                            if not self.connect_to_smtp():
                                return stats
                        
                        for index, row in df.iterrows():
                            company_name = row['company_name']
                            role = row['role']
                            recruiter_email = row['recruiter_email']
                            recruiter_first_name = row.get('recruiter_first_name') if has_recruiter_name else None
                            
                            # Update progress
                            campaign_status['current_email'] = recruiter_email
                            campaign_status['progress'] = index + 1
                            campaign_status['sent'] = stats['sent_successfully']
                            campaign_status['failed'] = stats['failed_to_send']
                            
                            # Debug logging
                            print(f"Progress: {index + 1}/{len(df)} - {recruiter_email}")
                            
                            subject, html_body, text_body = self.create_personalized_email(
                                company_name, role, recruiter_email, recruiter_first_name, resume_path
                            )
                            
                            if test_mode:
                                self.logger.info(f"TEST MODE - Would send to {recruiter_email} ({company_name} - {role})")
                                stats['sent_successfully'] += 1
                            else:
                                if self.send_email(recruiter_email, subject, html_body, text_body, resume_path):
                                    stats['sent_successfully'] += 1
                                else:
                                    stats['failed_to_send'] += 1
                                    stats['failed_emails'].append(recruiter_email)
                                
                                time.sleep(delay_seconds)
                            
                            # Update final counts
                            campaign_status['sent'] = stats['sent_successfully']
                            campaign_status['failed'] = stats['failed_to_send']
                        
                        if not test_mode:
                            self.disconnect_from_smtp()
                        
                        stats['end_time'] = datetime.now()
                        stats['duration_seconds'] = int((stats['end_time'] - stats['start_time']).total_seconds())
                        return stats
                        
                    except Exception as e:
                        self.logger.error(f"Error in bulk email campaign: {str(e)}")
                        return stats
            
            # Use the progress-aware email automation
            progress_automation = ProgressEmailAutomation(
                email_automation.sender_email,
                email_automation.sender_password,
                email_automation.sender_name
            )
            
            results = progress_automation.send_bulk_emails(
                csv_file_path=csv_file,
                resume_path=resume_path,
                delay_seconds=delay_seconds,
                test_mode=test_mode
            )
            
            campaign_status.update({
                'running': False,
                'end_time': datetime.now().isoformat(),
                'results': results,
                'sent': results['sent_successfully'],
                'failed': results['failed_to_send'],
                'total': results['total_emails']
            })
        except Exception as e:
            campaign_status.update({
                'running': False,
                'end_time': datetime.now().isoformat(),
                'error': str(e)
            })
    
    thread = threading.Thread(target=run_campaign)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Campaign started successfully'})

@app.route('/stop_campaign', methods=['POST'])
def stop_campaign():
    """Stop email campaign"""
    global campaign_status
    campaign_status['running'] = False
    return jsonify({'message': 'Campaign stopped'})

@app.route('/campaign_status')
def get_campaign_status():
    """Get current campaign status"""
    # Create a JSON-safe copy of campaign status
    status_copy = {
        'running': campaign_status.get('running', False),
        'progress': campaign_status.get('progress', 0),
        'total': campaign_status.get('total', 0),
        'sent': campaign_status.get('sent', 0),
        'failed': campaign_status.get('failed', 0),
        'current_email': campaign_status.get('current_email', ''),
        'start_time': campaign_status.get('start_time'),
        'end_time': campaign_status.get('end_time'),
        'results': campaign_status.get('results')
    }
    
    # Convert duration to seconds if it exists
    if 'duration' in campaign_status and campaign_status['duration']:
        if hasattr(campaign_status['duration'], 'total_seconds'):
            status_copy['duration'] = int(campaign_status['duration'].total_seconds())
        else:
            status_copy['duration'] = str(campaign_status['duration'])
    
    # Handle results duration if it exists
    if status_copy.get('results') and 'duration' in status_copy['results']:
        if hasattr(status_copy['results']['duration'], 'total_seconds'):
            status_copy['results']['duration'] = int(status_copy['results']['duration'].total_seconds())
        elif 'duration_seconds' in status_copy['results']:
            status_copy['results']['duration'] = status_copy['results']['duration_seconds']
    
    return jsonify(status_copy)

@app.route('/test_connection', methods=['POST'])
def test_connection():
    """Test email connection"""
    global email_automation
    
    # Get email credentials from request
    data = request.get_json()
    if not data or not data.get('sender_email') or not data.get('sender_password'):
        return jsonify({'error': 'Email credentials required'}), 400
    
    try:
        # Create temporary email automation instance for testing
        temp_automation = EmailAutomation(
            data['sender_email'], 
            data['sender_password'], 
            data.get('sender_name', 'Nirmal Boghara')
        )
        
        if temp_automation.connect_to_smtp():
            temp_automation.disconnect_from_smtp()
            return jsonify({'message': 'Connection successful!'})
        else:
            return jsonify({'error': 'Connection failed'}), 400
    except Exception as e:
        return jsonify({'error': f'Connection error: {str(e)}'}), 400

@app.route('/send_test_email', methods=['POST'])
def send_test_email():
    """Send a test email"""
    global email_automation
    
    if email_automation is None:
        return jsonify({'error': 'Please configure email settings first'}), 400
    
    test_email = request.json.get('test_email')
    if not test_email:
        return jsonify({'error': 'Test email address required'}), 400
    
    try:
        if not email_automation.connect_to_smtp():
            return jsonify({'error': 'Failed to connect to SMTP server'}), 400
        
        # Create test email
        subject, html_body, text_body = email_automation.create_personalized_email(
            "Test Company", "Test Role", test_email, "Test Recruiter"
        )
        
        success = email_automation.send_email(test_email, subject, html_body, text_body)
        email_automation.disconnect_from_smtp()
        
        if success:
            return jsonify({'message': 'Test email sent successfully!'})
        else:
            return jsonify({'error': 'Failed to send test email'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error sending test email: {str(e)}'}), 400

@app.route('/email_template')
def email_template():
    """Email template customization page"""
    return render_template('email_template.html')


@app.route('/save_email_template', methods=['POST'])
def save_email_template():
    """Save custom email template"""
    data = request.get_json()
    
    # Store email template in app config
    app.config['email_template'] = {
        'subject_template': data.get('subject_template', 'Excited for {role} Position at {company_name}'),
        'html_template': data.get('html_template', ''),
        'text_template': data.get('text_template', ''),
        'sender_name': data.get('sender_name', 'Nirmal Boghara'),
        'sender_email': data.get('sender_email', ''),
        'signature': data.get('signature', '')
    }
    
    return jsonify({'message': 'Email template saved successfully!'})

@app.route('/get_email_template')
def get_email_template():
    """Get current email template"""
    template = app.config.get('email_template', {})
    return jsonify(template)

@app.route('/preview_email', methods=['POST'])
def preview_email():
    """Preview email with sample data"""
    data = request.get_json()
    
    # Sample data for preview
    sample_data = {
        'company_name': data.get('company_name', 'Sample Company'),
        'role': data.get('role', 'Software Engineer Intern'),
        'recruiter_email': data.get('recruiter_email', 'recruiter@company.com'),
        'recruiter_first_name': data.get('recruiter_first_name', 'John')
    }
    
    # Get template
    template = app.config.get('email_template', {})
    
    # Create preview email
    if email_automation:
        subject, html_body, text_body = email_automation.create_personalized_email(
            sample_data['company_name'],
            sample_data['role'],
            sample_data['recruiter_email'],
            sample_data['recruiter_first_name']
        )
        
        return jsonify({
            'subject': subject,
            'html_body': html_body,
            'text_body': text_body
        })
    else:
        return jsonify({'error': 'Email automation not configured'}), 400

# Create necessary directories (only in local development)
if not os.environ.get('VERCEL'):
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

# For Vercel deployment
handler = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)

