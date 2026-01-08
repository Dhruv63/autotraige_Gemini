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

    def send_critical_alert(self, ticket_data):
        """Sends an email alert to the boss for Critical tickets."""
        if not self.sender_email or not self.sender_password or not self.boss_email:
            logging.warning("SMTP credentials not set. Skipping email alert.")
            return

        try:
            subject = f"🚨 CRITICAL TICKET: {ticket_data.get('ticket_id', 'Unknown')}"
            
            body = f"""
            CRITICAL ISSUE REPORTED
            -----------------------
            Ticket ID: {ticket_data.get('ticket_id')}
            Priority: {ticket_data.get('priority_level')}
            Team: {ticket_data.get('assigned_team')}
            
            Issue Summary:
            {ticket_data.get('extracted_issue')}
            
            Full Summary:
            {ticket_data.get('summary')}
            
            Action Required Immediately.
            """

            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.boss_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, self.boss_email, text)
            server.quit()
            
            logging.info(f"Critical alert email sent to {self.boss_email}")
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")
