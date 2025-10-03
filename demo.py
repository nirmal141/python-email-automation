
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
import os
import time
from datetime import datetime
import logging

class EmailAutomation:
    def __init__(self, sender_email, sender_password, sender_name="Nirmal Boghara"):
    
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.sender_name = sender_name
        self.smtp_server = None
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for tracking email sends"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('email_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def connect_to_smtp(self, smtp_server="smtp.gmail.com", smtp_port=587):

        try:
            self.smtp_server = smtplib.SMTP(smtp_server, smtp_port)
            self.smtp_server.starttls()
            self.smtp_server.login(self.sender_email, self.sender_password)
            self.logger.info("Successfully connected to SMTP server")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to SMTP server: {str(e)}")
            return False

    def disconnect_from_smtp(self):
        """Disconnect from SMTP server"""
        if self.smtp_server:
            self.smtp_server.quit()
            self.logger.info("Disconnected from SMTP server")

    def extract_recruiter_name(self, email):

        # Extract name part before @ and format it
        name_part = email.split('@')[0]

        # Handle different name formats
        if '.' in name_part:
            # firstname.lastname format
            parts = name_part.split('.')
            name = ' '.join([part.capitalize() for part in parts])
        elif '_' in name_part:
            # firstname_lastname format
            parts = name_part.split('_')
            name = ' '.join([part.capitalize() for part in parts])
        else:
            # single name
            name = name_part.capitalize()

        return name

    def create_personalized_email(self, company_name, role, recruiter_email, recruiter_first_name=None, resume_path=None):

        recruiter_name = recruiter_first_name if recruiter_first_name else self.extract_recruiter_name(recruiter_email)

        # Subject line
        subject = f"Excited for {role} Position at {company_name}"

        # HTML email body (same text, tighter spacing via inline styles)
        html_body = f"""
        <html>
        <body style="margin:0;padding:0;">
          <div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.35;color:#111;">
            <p style="margin:0 0 8px;">Hi {recruiter_name},</p>

            <p style="margin:0 0 8px;">Pleasure to e-meet you! I hope you're doing great! I am Nirmal Boghara, studying my second year MS in Computer Science at New York University, writing this mail to express my interest in {role} opportunity at {company_name} for Spring 2026! I won't make this very long for you, but thanks for your time. Here's everything about me:</p>

            <ul style="margin:0 0 8px;padding-left:20px;">
              <li style="margin:2px 0;">Studying CS at NYU</li>
              <li style="margin:2px 0;">Did my undergrad at University of Mumbai in Computer Engineering</li>
              <li style="margin:2px 0;">Interned at Chewy last summer as an AI Innovator Intern II in Boston, MA.</li>
              <li style="margin:2px 0;">Currently Technical Ambassador at Qualcomm, mentored 200+ students at their Edge AI Hackathons across USA.</li>
              <li style="margin:2px 0;">Got featured in the <a href="https://urldefense.proofpoint.com/v2/url?u=https-3A__www.qualcomm.com_developer_blog_2025_07_from-2Dold-2Dto-2Delite-2Dhow-2Dnyu-2Dhack-2Dwinners-2Dembraced-2Dsnapdragon&d=DwMGaQ&c=slrrB7dE8n7gBJbeO0g-IQ&r=pyihzPbGwz9yNqAmgJS8KQ&m=Mt7rte2SLZlLU0YFz-V87h2Uf18WGdp4pOt9bFuKr38KoVG17ByPIE43oI6gKQMx&s=lIqTWjfnEeqY5g2h5Y9lsZqbQ4qEhWgffXRV8tGanSs&e=">Qualcomm developer Blog</a>.</li>
              <li style="margin:2px 0;">Won 5 hackathons, attended 20+</li>
              <li style="margin:2px 0;">Deep technical knowledge in SWE, AI, ML models with multiple academic and professional projects.</li>
              <li style="margin:2px 0;">Previously interned at 3 consultancies & tech companies as SDE, AI, and Fullstack roles.</li>
              <li style="margin:2px 0;">AI Business Fellow at Perplexity</li>
              <li style="margin:2px 0;">I always build for social causes (<a href="https://github.com/nirmal141/TUTORAI">TutorAI</a>, <a href="https://github.com/nirmal141/PyroguardAI">PyroguardAI</a>, <a href="https://github.com/nirmal141/Fitfarm-main">Fitfarm</a>, <a href="https://github.com/nirmal141/Fittify">Fittify</a>) and more.</li>
              <li style="margin:2px 0;">I solve rubik's cube in under 30 seconds (helps me stay sharp!)</li>
            </ul>

            <p style="margin:0 0 8px;">I learn and adapt things very quickly and am highly interested in working at {company_name} as a {role}. Looking forward to chatting with you on how my skills align with the org.</p>
            <p style="margin:0 0 8px;">Attaching all the relevant links for your reference and my resume. Thank you for your time. Have a great day.</p>
            

            <p style="margin:0 0 8px;">
            <a href="https://github.com/nirmal141">Github</a> | 
            <a href="https://nirmal-aiswe.vercel.app">Portfolio</a> | 
            <a href="https://linkedin.com/in/nirmal-boghara">Linkedin</a>
            </p>

            <p style="margin:0 0 8px;">Best regards,<br>
            <strong>Nirmal Boghara</strong><br>
            MS in Computer Science, New York University<br>
            📧 {self.sender_email}<br>
            
            </p>
          </div>
        </body>
        </html>
        """

        # Plain text version (verbatim text as provided)
        text_body = f"""
Hi {recruiter_name}, 

Pleasure to e-meet you! I hope you're doing great! I am Nirmal Boghara, studying my second year MS in Computer Science at New York University, writing this mail to express my interest in {role} opportunity at {company_name} for Spring 2026! I won't make this very long for you, but thanks for your time. Here's everything about me:

Studying CS at NYU 
Did my undergrad at University of Mumbai in Computer Engineering
Interned at Chewy last summer as an AI Innovator Intern II in Boston, MA.
Currently Technical Ambassador at Qualcomm, mentored 200+ students at their Edge AI Hackathons across USA.
Got featured in the Qualcomm developer Blog.
Won 5 hackathons, attended 20+
Deep technical knowledge in SWE, AI, ML models with multiple academic and professional projects.
Previously interned at 3 consultancies & tech companies as SDE, AI, and Fullstack roles.
AI Business Fellow at Perplexity
I always build for social causes (TutorAI, PyroguardAI, Fitfarm, Fittify) and more.
⁠⁠I solve rubik's cube in under 30 seconds (helps me stay sharp!)

I learn and adapt things very quickly and am highly interested in working at {company_name} as a {role}. Looking forward to chatting with you on how my skills align with the org.
Attaching all the relevant links for your reference and my resume. Thank you for your time. Have a great day.

Best regards,
Nirmal Boghara
MS in Computer Science, New York University
Email: {self.sender_email}
Github | Portfolio | Linkedin
        """

        return subject, html_body, text_body

    def send_email(self, to_email, subject, html_body, text_body, resume_path=None):

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr((self.sender_name, self.sender_email))
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add text and HTML parts
            text_part = MIMEText(text_body, 'plain')
            html_part = MIMEText(html_body, 'html')

            msg.attach(text_part)
            msg.attach(html_part)

            # Attach resume if provided
            if resume_path and os.path.exists(resume_path):
                with open(resume_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(resume_path)}'
                    )
                    msg.attach(part)

            # Send email
            self.smtp_server.send_message(msg)
            self.logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_bulk_emails(self, csv_file_path, resume_path=None, delay_seconds=2, test_mode=True):

        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)

            # Validate required columns
            required_columns = ['company_name', 'role', 'recruiter_email']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"CSV must contain columns: {required_columns}")
            
            # Check for optional recruiter_first_name column
            has_recruiter_name = 'recruiter_first_name' in df.columns

            # Initialize statistics
            stats = {
                'total_emails': len(df),
                'sent_successfully': 0,
                'failed_to_send': 0,
                'start_time': datetime.now(),
                'failed_emails': []
            }

            self.logger.info(f"Starting bulk email campaign for {stats['total_emails']} recipients")

            if not test_mode:
                # Connect to SMTP server
                if not self.connect_to_smtp():
                    return stats

            # Process each row
            for index, row in df.iterrows():
                company_name = row['company_name']
                role = row['role']
                recruiter_email = row['recruiter_email']
                recruiter_first_name = row.get('recruiter_first_name') if has_recruiter_name else None

                # Create personalized email
                subject, html_body, text_body = self.create_personalized_email(
                    company_name, role, recruiter_email, recruiter_first_name, resume_path
                )

                if test_mode:
                    # Test mode: just log what would be sent
                    self.logger.info(f"TEST MODE - Would send to {recruiter_email} ({company_name} - {role})")
                    self.logger.info(f"Subject: {subject}")
                    stats['sent_successfully'] += 1
                else:
                    # Actually send email
                    if self.send_email(recruiter_email, subject, html_body, text_body, resume_path):
                        stats['sent_successfully'] += 1
                    else:
                        stats['failed_to_send'] += 1
                        stats['failed_emails'].append(recruiter_email)

                    # Add delay to avoid spam detection
                    time.sleep(delay_seconds)

                # Progress update
                if (index + 1) % 10 == 0:
                    self.logger.info(f"Progress: {index + 1}/{stats['total_emails']} emails processed")

            if not test_mode:
                self.disconnect_from_smtp()

            # Final statistics
            stats['end_time'] = datetime.now()
            stats['duration'] = stats['end_time'] - stats['start_time']

            self.logger.info(f"Campaign completed!")
            self.logger.info(f"Total emails: {stats['total_emails']}")
            self.logger.info(f"Successfully sent: {stats['sent_successfully']}")
            self.logger.info(f"Failed to send: {stats['failed_to_send']}")
            self.logger.info(f"Duration: {stats['duration']}")

            return stats

        except Exception as e:
            self.logger.error(f"Error in bulk email campaign: {str(e)}")
            return stats


# Example usage and configuration
def main():

    # Configuration - UPDATE THESE VALUES
    SENDER_EMAIL = "nb3964@nyu.edu"  # Replace with your email
    SENDER_PASSWORD = "qvgd fvkv dccr hpxx"
    # Replace with your app-specific password
    SENDER_NAME = "Nirmal Boghara"                  # Your name

    # File paths
    CSV_FILE_PATH = "sample_contacts.csv"  # Path to your CSV file
    RESUME_PATH = "Nirmal_Boghara_FTE_Resume.pdf"              # Path to your resume (optional)

    # Email settings
    DELAY_BETWEEN_EMAILS = 1  # Seconds to wait between emails
    TEST_MODE = False          # Set to False when ready to send actual emails

    # Create email automation instance
    email_bot = EmailAutomation(SENDER_EMAIL, SENDER_PASSWORD, SENDER_NAME)

    # Run the email campaign
    results = email_bot.send_bulk_emails(
        csv_file_path=CSV_FILE_PATH,
        resume_path=RESUME_PATH,
        delay_seconds=DELAY_BETWEEN_EMAILS,
        test_mode=TEST_MODE
    )

    print("\nEmail Campaign Results:")
    print(f"Total emails: {results['total_emails']}")
    print(f"Successfully sent: {results['sent_successfully']}")
    print(f"Failed to send: {results['failed_to_send']}")

    if results['failed_emails']:
        print(f"Failed emails: {results['failed_emails']}")


if __name__ == "__main__":
    main()
