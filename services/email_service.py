import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
import imaplib
import email
from email.header import decode_header
from email.mime.base import MIMEBase
from email import encoders
import os
from database import Database

class EmailService:
    def __init__(self):
        self.db = Database()

    def get_settings(self):
        """Fetch the current mail configuration from admin_settings"""
        query = """
            SELECT admin_email, mail_mode, smtp_host, smtp_port, 
                   smtp_user, smtp_pass, api_endpoint, api_sid, api_key,
                   imap_host, imap_port 
            FROM admin_settings 
            ORDER BY updated_at DESC LIMIT 1
        """
        result = self.db.execute_query(query)
        if result:
            r = result[0]
            return {
                'admin_email': r[0],
                'mail_mode': r[1],
                'smtp_host': r[2],
                'smtp_port': r[3],
                'smtp_user': r[4],
                'smtp_pass': r[5],
                'api_endpoint': r[6],
                'api_sid': r[7],
                'api_key': r[8],
                'imap_host': r[9] if len(r) > 9 else 'imap.gmail.com',
                'imap_port': r[10] if len(r) > 10 else 993
            }
        return None

    def send_email(self, recipient_email, subject, body, attachments=None):
        """Dispatches email based on the configured mode (Simulation, SMTP, or API) with optional attachments"""
        settings = self.get_settings()
        if not settings:
            return False, "No settings configured"

        mode = settings['mail_mode']
        
        if mode == 'Simulation':
            # Just pretend it worked
            return True, "Simulation Successful (Internal Log Only)"

        elif mode == 'SMTP':
            try:
                msg = MIMEMultipart()
                msg['From'] = settings['admin_email']
                msg['To'] = recipient_email
                msg['Subject'] = subject
                
                html_content = self._get_branded_template(body)
                msg.attach(MIMEText(html_content, 'html'))

                # Handle Attachments
                if attachments:
                    for file_path in attachments:
                        if not os.path.exists(file_path):
                            continue
                        
                        try:
                            filename = os.path.basename(file_path)
                            with open(file_path, "rb") as f:
                                part = MIMEBase("application", "octet-stream")
                                part.set_payload(f.read())
                            
                            encoders.encode_base64(part)
                            part.add_header(
                                "Content-Disposition",
                                f"attachment; filename= {filename}",
                            )
                            msg.attach(part)
                        except Exception as e:
                            print(f"Failed to attach {file_path}: {e}")

                server = smtplib.SMTP(settings['smtp_host'], settings['smtp_port'], timeout=10)
                server.starttls()
                server.login(settings['smtp_user'], settings['smtp_pass'])
                server.send_message(msg)
                server.quit()
                return True, "Email sent via SMTP"
            except Exception as e:
                return False, f"SMTP Error: {str(e)}"

        elif mode == 'API':
            try:
                # This is a generic implementation using requests
                # The user provides the API Endpoint and API Key
                payload = {
                    "from": settings['admin_email'],
                    "to": recipient_email,
                    "subject": subject,
                    "html": self._get_branded_template(body),
                    "text": body
                }
                headers = {"Content-Type": "application/json"}
                auth = None
                
                if settings.get('api_sid') and settings.get('api_key'):
                    # Basic Auth (SID:Secret)
                    from requests.auth import HTTPBasicAuth
                    auth = HTTPBasicAuth(settings['api_sid'], settings['api_key'])
                elif settings.get('api_key'):
                    # Bearer Token
                    headers["Authorization"] = f"Bearer {settings['api_key']}"

                response = requests.post(
                    settings['api_endpoint'], 
                    data=json.dumps(payload), 
                    headers=headers, 
                    auth=auth,
                    timeout=10
                )
                
                if response.status_code in [200, 201, 202]:
                    return True, "Email sent via API"
                else:
                    return False, f"API Error ({response.status_code}): {response.text}"
            except Exception as e:
                return False, f"Request Error: {str(e)}"
        elif mode == 'Mailgun':
            try:
                # Mailgun uses multipart/form-data instead of JSON
                payload = {
                    "from": settings['admin_email'],
                    "to": recipient_email,
                    "subject": subject,
                    "html": self._get_branded_template(body),
                    "text": body
                }
                # Mailgun auth is 'api:API_KEY'
                from requests.auth import HTTPBasicAuth
                auth = HTTPBasicAuth('api', settings['api_key'])
                
                response = requests.post(
                    settings['api_endpoint'], 
                    data=payload, 
                    auth=auth,
                    timeout=10
                )
                
                if response.status_code in [200, 201, 202]:
                    return True, "Email sent via Mailgun"
                else:
                    return False, f"Mailgun Error ({response.status_code}): {response.text}"
            except Exception as e:
                return False, f"Request Error: {str(e)}"

        return False, "Invalid mail mode"

    def _get_branded_template(self, body):
        """Wraps the plain text body in a professional HTML template"""
        # Convert newlines to <br> for HTML
        html_body = body.replace("\n", "<br>")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #202124; line-height: 1.8; margin: 0; padding: 0; background-color: #f4f6f8; }}
                .container {{ width: 100%; max-width: 650px; margin: 20px auto; border: 1px solid #e0e0e0; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                .header {{ background-color: #1a2a3a; padding: 40px 20px; text-align: center; }}
                .logo-text {{ color: #ffcc00; font-size: 36px; font-weight: bold; letter-spacing: 3px; text-transform: uppercase; }}
                .star {{ color: #ffcc00; font-size: 28px; }}
                .content {{ padding: 50px 40px; min-height: 150px; font-size: 16px; color: #3c4043; }}
                .footer {{ background-color: #fafbfb; padding: 30px; text-align: center; font-size: 13px; color: #5f6368; border-top: 1px solid #f1f3f4; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo-text">5 ST<span class="star">★</span>R</div>
                    <div style="color: #bdc3c7; font-size: 12px; margin-top: 5px;">INVENTORY MANAGEMENT SYSTEM</div>
                </div>
                <div class="content">
                    {html_body}
                </div>
                <div class="footer">
                    This is an automated message from the 5 STAR Inventory System.<br>
                    © 2026 Admin Management Hub. All rights reserved.
                </div>
            </div>
        </body>
        </html>
        """

    def fetch_incoming_messages(self, sender_email=None):
        """Fetches new emails from the configured IMAP server, optionally filtered by sender"""
        settings = self.get_settings()
        if not settings or settings['mail_mode'] == 'Simulation':
            return []

        messages = []
        try:
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(settings['imap_host'], settings['imap_port'])
            mail.login(settings['smtp_user'], settings['smtp_pass'])
            mail.select("INBOX")

            # Search logic: If sender is provided, search specifically for them
            if sender_email:
                status, response = mail.search(None, f'FROM "{sender_email}"')
            else:
                status, response = mail.search(None, "ALL")
                
            if status != 'OK': return []

            msg_ids = response[0].split()
            # Fetch last 50 messages (increased from 20)
            limit = 50 if sender_email else 20
            for i in range(len(msg_ids)-1, max(-1, len(msg_ids) - (limit + 1)), -1):
                res, msg_data = mail.fetch(msg_ids[i], "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        
                        sender = msg.get("From")
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode()

                        messages.append({
                            'uid': msg_ids[i].decode(),
                            'sender': sender,
                            'subject': subject,
                            'body': body,
                            'timestamp': msg.get("Date")
                        })
            mail.logout()
        except Exception as e:
            print(f"IMAP Error: {e}")
            
        return messages
