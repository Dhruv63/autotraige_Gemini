import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

class EmailService:
    def __init__(self):
        self.smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", 587))
        self.sender_email = os.environ.get("SMTP_EMAIL")
        self.sender_password = os.environ.get("SMTP_PASSWORD")
        self.boss_email = os.environ.get("BOSS_EMAIL")

    def _get_html_template(self, title, ticket_data, note=None, is_critical=False):
        """Generates an HTML email body."""
        color = "#e53e3e" if is_critical else "#3182ce"
        bg_color = "#fff5f5" if is_critical else "#ebf8ff"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
                .header {{ background-color: {color}; color: white; padding: 15px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 20px; background-color: #ffffff; }}
                .card {{ background-color: {bg_color}; padding: 15px; border-left: 4px solid {color}; margin-bottom: 20px; border-radius: 4px; }}
                .field {{ margin-bottom: 10px; }}
                .label {{ font-weight: bold; color: #555; }}
                .footer {{ margin-top: 20px; text-align: center; font-size: 12px; color: #777; border-top: 1px solid #eee; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{title}</h2>
                </div>
                <div class="content">
                    <div class="card">
                        <div class="field"><span class="label">Ticket ID:</span> {ticket_data.get('ticket_id', 'Unknown')}</div>
                        <div class="field"><span class="label">Priority:</span> <strong>{ticket_data.get('priority_level', 'N/A')}</strong></div>
                        <div class="field"><span class="label">Team:</span> {ticket_data.get('assigned_team', 'N/A')}</div>
                    </div>

                    <h3>⚠️ Issue Reported</h3>
                    <p>{ticket_data.get('extracted_issue', 'No issue extracted.')}</p>
        """

        if note:
            html += f"""
                    <div style="background-color: #f0fff4; padding: 15px; border: 1px solid #c6f6d5; border-radius: 4px; margin-top: 20px;">
                        <h4 style="margin-top: 0; color: #2f855a;">📝 Admin Note</h4>
                        <p style="margin-bottom: 0;">{note}</p>
                    </div>
            """

        html += f"""
                    <h3>📄 Full Summary</h3>
                    <p>{ticket_data.get('summary', 'No summary available.')}</p>
                    
                    <div class="footer">
                        <p>AutoTriage.AI Notification System</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def send_critical_alert(self, ticket_data):
        """Sends an email alert to the boss for Critical tickets."""
        if not self.sender_email or not self.sender_password or not self.boss_email:
            logging.warning("SMTP credentials not set. Skipping email alert.")
            return

        try:
            subject = f"🚨 CRITICAL TICKET: {ticket_data.get('ticket_id', 'Unknown')}"
            html_body = self._get_html_template("CRITICAL ISSUE REPORTED", ticket_data, is_critical=True)

            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.boss_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, self.boss_email, msg.as_string())
            server.quit()
            
            logging.info(f"Critical alert email sent to {self.boss_email}")
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")

    def send_email(self, ticket_data, note=None, recipient=None):
        """Sends a manual email for a ticket."""
        if not self.sender_email or not self.sender_password:
             logging.warning("SMTP credentials not set. Cannot send email.")
             return False, "SMTP credentials not configured."
        
        target_email = recipient if recipient else self.boss_email
        if not target_email:
            return False, "No recipient email provided."

        try:
            subject = f"Ticket Update: {ticket_data.get('ticket_id', 'Unknown')}"
            html_body = self._get_html_template("Ticket Update Notification", ticket_data, note=note, is_critical=False)

            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = target_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, target_email, msg.as_string())
            server.quit()
            
            return True, f"Email sent to {target_email}"
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False, f"Failed to send email: {e}"
