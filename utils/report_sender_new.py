import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Tuple

class ReportGenerator:
    def __init__(self, smtp_settings: Dict[str, Any]):
        """Initialize the ReportGenerator with SMTP settings"""
        self.smtp_settings = smtp_settings.copy()
        
        # Ensure port is an integer
        if isinstance(self.smtp_settings.get('port'), str):
            self.smtp_settings['port'] = int(self.smtp_settings['port'])
        
        self.email_template = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .header { background: #f8f9fa; padding: 20px; margin-bottom: 20px; }
                .metric { background: #ffffff; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }
                .issue { background: #fff3cd; padding: 15px; margin: 10px 0; border-radius: 4px; }
                .summary { background: #f8f9fa; padding: 15px; margin: 10px 0; }
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """

    def generate_ticket_report(self, ticket_data: Dict[str, Any]) -> str:
        """Generate HTML report from ticket data"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""
        <div class="header">
            <h2>Incident Report - {ticket_data.get('ticket_id', 'N/A')}</h2>
            <p>Generated on: {timestamp}</p>
        </div>

        <div class="metrics">
            <div class="metric">
                <strong>Priority Level:</strong> {ticket_data.get('priority', 'N/A')}
            </div>
            <div class="metric">
                <strong>Confidence Score:</strong> {ticket_data.get('confidence', 0.0):.2f}
            </div>
            <div class="metric">
                <strong>Assigned Team:</strong> {ticket_data.get('team', 'N/A')}
            </div>
            <div class="metric">
                <strong>Sentiment:</strong> {ticket_data.get('sentiment', 'N/A').title()}
            </div>
        </div>

        <h3>Issue Summary</h3>
        <div class="summary">
            {ticket_data.get('summary', 'Not available.')}
        </div>

        <h3>Extracted Issue</h3>
        <div class="issue">
            {ticket_data.get('issue', 'Not available.')}
        </div>

        <h3>Recommended Actions</h3>
        <div class="summary">
            {ticket_data.get('suggested_solution', 'No recommendations available.')}
        </div>
        
        {f'<h3>Additional Comments</h3><div class="summary">{ticket_data["admin_comments"]}</div>' if ticket_data.get('admin_comments') else ''}
        """
        
        return self.email_template.format(content=content)

    def send_report(self, recipient: str, subject: str, ticket_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Send the report via email"""
        server = None
        try:
            # Validate SMTP settings
            required_settings = ['server', 'port', 'username', 'password']
            if not all(key in self.smtp_settings for key in required_settings):
                missing = [key for key in required_settings if key not in self.smtp_settings]
                error_msg = f"Missing SMTP settings: {', '.join(missing)}"
                print(f"Debug - {error_msg}")
                return False, error_msg

            # Prepare email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_settings['username']
            msg['To'] = recipient
            
            # Generate and attach HTML report
            html_content = self.generate_ticket_report(ticket_data)
            msg.attach(MIMEText(html_content, 'html'))

            # Connect to SMTP server
            print(f"Debug - Connecting to SMTP server {self.smtp_settings['server']}:{self.smtp_settings['port']}...")
            server = smtplib.SMTP(self.smtp_settings['server'], self.smtp_settings['port'])
            server.set_debuglevel(1)  # Enable SMTP debug output
            
            # Initial EHLO
            server.ehlo()
            print("Debug - Initial EHLO completed")
            
            # Start TLS encryption
            print("Debug - Starting TLS...")
            server.starttls()
            
            # Re-run EHLO after TLS
            server.ehlo()
            print("Debug - TLS encryption established")
            
            # Login with credentials
            print(f"Debug - Attempting login for {self.smtp_settings['username']}...")
            server.login(
                self.smtp_settings['username'],
                self.smtp_settings['password'].strip()
            )
            print("Debug - Login successful")
            
            # Send email
            print("Debug - Sending message...")
            server.send_message(msg)
            print("Debug - Message sent successfully")
            
            # Clean up
            if server:
                server.quit()
            return True, "Email sent successfully"
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = "Authentication failed. Please verify your Gmail App Password. "
            error_msg += "Make sure you have:\n"
            error_msg += "1. Enabled 2-Step Verification in your Google Account\n"
            error_msg += "2. Generated an App Password specifically for this application\n"
            error_msg += "3. Copied the 16-character password correctly without spaces"
            print(f"Debug - Authentication Error: {str(e)}")
            return False, error_msg
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error occurred: {str(e)}"
            print(f"Debug - SMTP Error: {str(e)}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"Debug - Unexpected Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, error_msg
            
        finally:
            # Always try to clean up the connection
            if server:
                try:
                    server.quit()
                except Exception:
                    pass