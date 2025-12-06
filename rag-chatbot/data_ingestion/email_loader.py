import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Any
import os
from datetime import datetime
from .base_loader import BaseLoader

class EmailLoader(BaseLoader):
    """Load emails from IMAP server"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.email_config = config.get('email', {})
        self.max_emails = self.email_config.get('max_emails', 100)
    
    def load(self) -> List[Dict[str, Any]]:
        if not self.is_enabled():
            return []
        
        email_user = os.getenv('EMAIL_USER')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        if not email_user or not email_password:
            print("⚠️  Email credentials not found in .env file")
            return []
        
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(
                self.email_config.get('imap_server', 'imap.gmail.com'),
                self.email_config.get('imap_port', 993)
            )
            mail.login(email_user, email_password)
            mail.select('inbox')
            
            # Search for emails
            status, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            
            documents = []
            count = 0
            
            # Process emails (most recent first)
            for email_id in reversed(email_ids[:self.max_emails]):
                if count >= self.max_emails:
                    break
                
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue
                
                email_body = msg_data[0][1]
                msg = email.message_from_bytes(email_body)
                
                # Decode subject
                subject = self._decode_header(msg['Subject'])
                sender = self._decode_header(msg['From'])
                date = msg['Date']
                
                # Get email body
                body = self._get_email_body(msg)
                
                if body:
                    content = f"Subject: {subject}\nFrom: {sender}\nDate: {date}\n\n{body}"
                    documents.append({
                        'content': content,
                        'metadata': {
                            'source': 'email',
                            'subject': subject,
                            'sender': sender,
                            'date': date,
                            'email_id': email_id.decode()
                        }
                    })
                    count += 1
            
            mail.close()
            mail.logout()
            print(f"✅ Loaded {len(documents)} emails")
            return documents
            
        except Exception as e:
            print(f"❌ Error loading emails: {str(e)}")
            return []
    
    def _decode_header(self, header):
        """Decode email header"""
        if header is None:
            return ""
        decoded = decode_header(header)
        return ''.join([text.decode(encoding or 'utf-8', errors='ignore') 
                       if isinstance(text, bytes) else text 
                       for text, encoding in decoded])
    
    def _get_email_body(self, msg):
        """Extract email body text"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                pass
        return body

