from database import Database
from services.email_service import EmailService
import random
import json
import os

class SupplierCommunication:
    def __init__(self):
        self.db = Database()
        self.email_service = EmailService()
        # Force registration of logging capability
        if not hasattr(self, 'log_communication'):
            print("CRITICAL: Communication model initialized without LOGGING function!")

    def log_communication(self, supplier_id, sender_type, admin_email_fallback, recipient_email, subject, message, status, attachments=None):
        """Standardized method to log any message (sent or received) into the local database"""
        settings = self.email_service.get_settings()
        admin_email = settings['admin_email'] if settings else admin_email_fallback
        
        # Convert attachments list to JSON string for storage
        attachments_json = json.dumps(attachments) if attachments else None
        
        log_query = """
            INSERT INTO supplier_communications (supplier_id, sender_type, sender_email, recipient_email, subject, message, status, attachments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute_query(log_query, (supplier_id, sender_type, admin_email, recipient_email, subject, message, status, attachments_json))

    def send_admin_email(self, supplier_id, subject, message):
        """Sends an actual email via the service AND logs it in the database"""
        query = "SELECT email FROM suppliers WHERE supplier_id = ?"
        supplier = self.db.execute_query(query, (supplier_id,))
        if not supplier:
            return False, "Supplier not found"
        
        recipient_email = supplier[0][0]
        
        # Dispatch email
        success, info = self.email_service.send_email(recipient_email, subject, message)
        
        # Log to DB using the new standalone method
        self.log_communication(
            supplier_id, "Admin", admin_email_fallback='admin@system.com',
            recipient_email=recipient_email, subject=subject, message=message, 
            status="Sent" if success else "Failed"
        )
        
        return success, info

    def get_communication_history(self, supplier_id):
        """Fetch all messages exchanged with this supplier including attachments"""
        query = """
            SELECT sender_type, subject, message, timestamp, status, attachments 
            FROM supplier_communications 
            WHERE supplier_id = ? 
            ORDER BY timestamp ASC
        """
        return self.db.execute_query(query, (supplier_id,))

    def simulate_supplier_reply(self, supplier_id):
        """Simulates an incoming email from the supplier for 'Exchange' demonstration"""
        query = "SELECT email, name FROM suppliers WHERE supplier_id = ?"
        supplier = self.db.execute_query(query, (supplier_id,))
        if not supplier: return
        
        supp_email, supp_name = supplier[0]
        settings = self.email_service.get_settings()
        admin_email = settings['admin_email'] if settings else 'admin@system.com'
        
        replies = [
            f"Hello, we have received your order request. We'll process it soon.",
            f"The prices for the items you requested have been updated. Please see our new catalog.",
            f"We are sorry to inform you that some items are out of stock.",
            f"Your order has been shipped and is expected to arrive tomorrow.",
            f"Thank you for the message. We are looking forward to our next business together."
        ]
        
        reply_msg = random.choice(replies)
        
        log_query = """
            INSERT INTO supplier_communications (supplier_id, sender_type, sender_email, recipient_email, subject, message, status, is_read)
            VALUES (?, 'Supplier', ?, ?, 'RE: Supply Order Inquiry', ?, 'Received', 0)
        """
        self.db.execute_query(log_query, (supplier_id, supp_email, admin_email, reply_msg))

    def sync_incoming_emails(self, target_supplier_id=None):
        """Fetches real incoming emails and saves them to the database history"""
        # If we have a target supplier, search specifically for their email
        target_email = None
        if target_supplier_id:
            res = self.db.execute_query("SELECT email FROM suppliers WHERE supplier_id = ?", (target_supplier_id,))
            if res: target_email = res[0][0]

        new_messages = self.email_service.fetch_incoming_messages(sender_email=target_email)
        if not new_messages:
            return 0

        # Get map of emails to supplier_ids
        suppliers = self.db.execute_query("SELECT supplier_id, email FROM suppliers")
        email_map = {s[1]: s[0] for s in suppliers if s[1]}
        
        count = 0
        for m in new_messages:
            # Extract email from "Name <email@domain.com>"
            import re
            sender_raw = m['sender']
            sender_email = re.search(r'[\w\.-]+@[\w\.-]+', sender_raw)
            if not sender_email: continue
            sender_email = sender_email.group(0)

            if sender_email in email_map:
                sid = email_map[sender_email]
                if target_supplier_id and sid != target_supplier_id:
                    continue
                
                # Check if already exists by UID
                exists = self.db.execute_query(
                    "SELECT 1 FROM supplier_communications WHERE uid = ?", 
                    (m['uid'],)
                )
                if not exists:
                    # Clean the body to remove quotes
                    clean_body = self._clean_message_body(m['body'])
                    
                    # Fetch admin email from settings
                    admin_settings = self.db.execute_query("SELECT admin_email FROM admin_settings LIMIT 1")
                    admin_email = admin_settings[0][0] if admin_settings else 'admin@system.com'

                    self.db.execute_query(
                        """
                        INSERT INTO supplier_communications 
                        (supplier_id, sender_type, sender_email, recipient_email, subject, message, status, uid, is_read)
                        VALUES (?, 'Supplier', ?, ?, ?, ?, 'Received', ?, 0)
                        """,
                        (sid, sender_email, admin_email, m['subject'], clean_body, m['uid'])
                    )
                    count += 1
        return count

    def _clean_message_body(self, raw_body):
        """Removes email quotes and reply headers to keep the chat clean"""
        if not raw_body: return ""
        
        lines = raw_body.splitlines()
        clean_lines = []
        
        # Split markers for standard email replies
        split_markers = [
            "On ", "From: ", "--- Original Message ---", 
            "________________________________", "Sent from my"
        ]
        
        for line in lines:
            trimmed = line.strip()
            # If we hit a standard reply splitter, stop taking more lines
            if any(trimmed.startswith(marker) for marker in split_markers) and ("wrote:" in trimmed or ":" in trimmed):
                break
            
            # Skip quoted lines starting with >
            if trimmed.startswith(">"):
                continue
                
            clean_lines.append(line)
            
        return "\n".join(clean_lines).strip()

    def get_total_unread_count(self):
        """Returns the total number of unread supplier messages across all suppliers"""
        query = "SELECT COUNT(*) FROM supplier_communications WHERE sender_type = 'Supplier' AND is_read = 0"
        res = self.db.execute_query(query)
        return res[0][0] if res else 0

    def mark_as_read(self, supplier_id):
        """Marks all messages for a specific supplier as read"""
        query = "UPDATE supplier_communications SET is_read = 1 WHERE supplier_id = ?"
        self.db.execute_query(query, (supplier_id,))

    def get_unread_summary(self):
        """Returns a summarized list of suppliers with unread messages"""
        query = """
            SELECT s.supplier_id, s.name, s.email, COUNT(c.comm_id) as unread_count
            FROM suppliers s
            JOIN supplier_communications c ON s.supplier_id = c.supplier_id
            WHERE c.sender_type = 'Supplier' AND c.is_read = 0
            GROUP BY s.supplier_id
        """
        results = self.db.execute_query(query)
        summary = []
        for row in results:
            summary.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'count': row[3]
            })
        return summary

    def update_admin_email_settings(self, **kwargs):
        """Updates the admin email settings in the database"""
        if not kwargs: return
        
        # We only have one settings record, so we just update the first one
        query = "SELECT * FROM admin_settings LIMIT 1"
        if not self.db.execute_query(query):
            # Insert first record if empty
            self.db.execute_query("INSERT INTO admin_settings (admin_email) VALUES ('admin@system.com')")
            
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)
            
        query = f"UPDATE admin_settings SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE setting_id = 1"
        self.db.execute_query(query, tuple(values))
        return True
