import re
import time
import requests
from src.pandora.config.config import c_config
from email.message import EmailMessage
from pathlib import Path
import mimetypes
import smtplib
import smtpd
import email
from email import policy
from email.parser import BytesParser
import os
import zipfile
from typing import Union
import logging

# Configure module-level logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class EmailUtils:
    def __init__(self):
        pass

    def get_email_list(self, inbox_name, max_retries=6, retry_interval=5):
        """
            get email list（have retry）
            Args:
                inbox_name: inbox name
                max_retries: maxium retry times
                retry_interval: interval for retry（s）
            Returns:
                when success, it will return email data dict，if fail, it will return null
            """
        url = f"{c_config.mailinator_base_url}/domains/{c_config.mailinator_domain}/inboxes/{inbox_name}"
        headers = {
            "Authorization": f"Bearer {c_config.mailinator_token}",
            "Content-Type": "application/json"
        }
        json_data = ""
        for i in range(max_retries):
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                json_data = response.json()
                if json_data["msgs"]:
                    if json_data["msgs"][0]["seconds_ago"] < 15:
                        print("get the latest email")
                        break
                    else:
                        time.sleep(retry_interval)
        return json_data

    def get_email_id(self, json_data, subject: str):
        """
           get email id from with specific subject from email list
           Args:
             json_data: the dict include email list
             subject: the email subject to search for
          Raises:
             return empty if json_data wrong
        """
        email_id: str  # New authentication request
        if json_data["msgs"]:
            for email in json_data["msgs"]:
                print("email subject:", email["subject"])
                if email["subject"] == subject:
                    print("email id:", email["id"])
                    email_id = email["id"]
                    break
        return email_id

    def get_email_details(self, inbox_id):
        """
        get email details info from specific email
        Raises:
           return email datails info
        """
        url = f"{c_config.mailinator_base_url}/domains/{c_config.mailinator_domain}/messages/{inbox_id}"
        headers = {
            "Authorization": f"Bearer {c_config.mailinator_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_content_from_email_withpattern(self, json_data, pattern):
        """
          get specific pattern from email
          Raises:
              return email content if success, otherwise return None
        """
        for part in json_data.get("parts", []):
            body = part.get("body", "")
            match = re.search(pattern, body)
            if match:
                return match.group(1).strip()
        return None


class EmailSender:
    @classmethod
    def _normalize_addrs(cls, addrs: Union[str, list]) -> Union[list, None]:
        """
        Protected method expected to use only inner class.
        Normalize address input:
          - If 'addrs' is a list, it's assumed to be already split and is returned directly.
          - If 'addrs' is a string, it is split using ',' or ';' as delimiters,
            whitespace is stripped from each part, and empty strings are ignored.

        Args:
            addrs: The addresses to process, as a string or list of strings.

        Returns:
            list: A list of cleaned and split addresses.
            None: If addrs is None.
        """
        # Return directly for None type
        if addrs is None:
            return addrs

        # Return a shallow copy if input is already a list
        if isinstance(addrs, list):
            return addrs.copy()

        # Raise an error for unsupported input types
        if not isinstance(addrs, str):
            raise TypeError(f"Expected str or list[str], got {type(addrs).__name__}")

        # Split on commas or semicolons, optionally followed by whitespace
        parts = re.split(r'[,;]\s*', addrs)

        # Strip each part and exclude empty entries
        result = [addr.strip() for addr in parts if addr.strip()]

        return result

    @classmethod
    def _compress_path(cls, source_path: str, destination_zip: str = "") -> bool:
        """
        Protected method expected to use only inner class.
        Compress a directory (including its root) into a .zip file,
        skip compression if source is a file.

        Args:
            source_path: Path to a directory or file.
            destination_zip: Optional path to output .zip. If empty, defaults to '<source_path>.zip'.

        Returns:
            True if a directory was compressed; False if input was a file.
        """
        # Normalize and check existence
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Error: Path '{source_path}' does not exist.")

        # Determine default destination if needed
        if not destination_zip:
            normalized = source_path.rstrip(os.sep)
            destination_zip = f"{normalized}.zip"

        logger.info(f"Target ZIP file: '{destination_zip}'")

        # If source is a directory, compress it (including root folder)
        if os.path.isdir(source_path):
            # Remove existing zip if present
            if os.path.isfile(destination_zip):
                os.remove(destination_zip)

            root_folder = os.path.basename(source_path.rstrip(os.sep))
            with zipfile.ZipFile(destination_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                for dirpath, dirnames, filenames in os.walk(source_path):
                    # compute archive-relative path
                    os.path.relpath(dirpath, os.path.dirname(source_path))
                    for fname in filenames:
                        full_path = os.path.join(dirpath, fname)
                        arcname = os.path.join(root_folder, os.path.relpath(full_path, source_path))
                        zf.write(full_path, arcname)
            logger.info(f"Directory '{source_path}' (including root) has been compressed to '{destination_zip}'.")
            return True

        # If source is a file, skip compression
        elif os.path.isfile(source_path):
            logger.info(f"Input path '{source_path}' is a file. No compression needed.")
            return False

        else:
            # Shouldn't happen, but for completeness
            raise RuntimeError(f"Unknown path type: '{source_path}'.")

    @classmethod
    def send_email_with_auth(cls,
                             email_content: str,
                             from_addr: str,
                             to_addr: Union[str, list[str]],
                             subject: str,
                             smtp_server: str,
                             cc_addr: Union[str, list[str]] = None,
                             auth_type: str = 'ssl',
                             smtp_port: int = 25,
                             username: str = None,
                             password: str = None,
                             attachment_paths: Union[str, list[str]] = None,
                             timeout: float = 60000.0) -> bool:
        """
        Send an email via SMTP with optional SSL/TLS authentication, HTML body support, CC and attachments.

        Args:
            email_content : str
                The HTML-formatted content of the email body.
            from_addr : str
                The sender's email address (e.g. "alice@example.com").
            to_addr : Union[str, list[str]]
                A list of recipient email addresses.
            subject : str
                Subject line of the email.
            smtp_server : str
                Hostname or IP address of the SMTP server (e.g. "smtp.example.com").
            cc_addr : Union[str, list[str]], optional
                A list of CC (carbon copy) recipient addresses. Default is None.
            auth_type : str, optional
                Authentication/encryption method: "ssl" for SMTPS or "tls" for STARTTLS. Defaults to "ssl".
            smtp_port : int, optional
                Port number of the SMTP service. Defaults to 25.
            username : str, optional
                Username for SMTP authentication. If omitted, no login is performed (anonymous).
            password : str, optional
                Password for SMTP authentication. Must be provided if `username` is set.
            attachment_paths : Union[str, list[str]], optional
                List of filesystem paths to files to attach. Default is None.
            timeout : float, optional
                Timeout in milliseconds for SMTP connection. Default is 60000.0.

        Returns:
            True if the email was sent successfully, raise exceptions otherwise.
        """
        # Handle multiple addresses
        timeout_seconds = timeout / 1000.0
        to_addr = cls._normalize_addrs(to_addr)
        cc_addr = cls._normalize_addrs(cc_addr)
        attachment_paths = cls._normalize_addrs(attachment_paths)
        logger.info("Preparing to send email: subject='%s', from='%s', to=%s, cc=%s", subject, from_addr, to_addr,
                    cc_addr)

        # Build the email message
        msg = EmailMessage()
        msg['From'] = from_addr
        msg['To'] = ', '.join(to_addr)
        if cc_addr:
            msg['Cc'] = ', '.join(cc_addr)
        msg['Subject'] = subject
        msg.set_content("Please use an HTML-supported email client to view this report.")
        msg.add_alternative(email_content, subtype='html')
        logger.debug("Email headers set and HTML content added.")

        # Handle attachments
        attachment_paths = attachment_paths or []
        for file_path in attachment_paths:
            path = Path(file_path)
            if path.is_dir():
                cls._compress_path(source_path=file_path)
                normalized = file_path.rstrip(os.sep)
                path = Path(f"{normalized}.zip")
            if not path.is_file():
                logger.error("Attachment not found: %s", file_path)
                raise FileNotFoundError(f"File path not found: {file_path}")
            data = path.read_bytes()
            ctype, encoding = mimetypes.guess_type(file_path)
            if ctype is None or encoding is not None:
                maintype, subtype = 'application', 'octet-stream'
            else:
                maintype, subtype = ctype.split('/', 1)
            msg.add_attachment(
                data,
                maintype=maintype,
                subtype=subtype,
                filename=path.name
            )
            logger.info("Attached file '%s' (type: %s/%s)", path.name, maintype, subtype)

        # Send email via SMTP
        auth_type = auth_type.lower()
        try:
            if auth_type == 'ssl':
                logger.info("Connecting to SMTP server %s:%d using SSL", smtp_server, smtp_port)
                with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=timeout_seconds) as smtp:
                    smtp.ehlo()
                    smtp.ehlo()  # Call function twice to support servers double-check.
                    if username and password:
                        logger.info("Logging in as user '%s'", username)
                        smtp.login(username, password)
                    smtp.send_message(msg)
            elif auth_type == 'tls':
                logger.info("Connecting to SMTP server %s:%d using TLS", smtp_server, smtp_port)
                with smtplib.SMTP(smtp_server, smtp_port, timeout=timeout_seconds) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()  # Call function twice to support servers double-check.
                    if username and password:
                        logger.info("Logging in as user '%s'", username)
                        smtp.login(username, password)
                    smtp.send_message(msg)
            else:
                logger.error("Unsupported auth_type: %s", auth_type)
                raise ValueError(f"Auth type must be 'ssl' or 'tls': {auth_type}")
        except Exception as e:
            logger.exception("Failed to send email: %s", e)
            raise
        else:
            logger.info("Email sent successfully to %s", to_addr)
            return True


class DummySMTPServer(smtpd.SMTPServer):
    """
    A "dummy" SMTP server: stores all emails received by process_message into the self.messages list.
    """

    def __init__(self, localaddr, remoteaddr):
        super().__init__(localaddr, remoteaddr)
        # Store received emails: [(peer, mailfrom, rcpttos, data), ...]
        self.messages = []

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        """
        This method is called whenever a client submits an email via the SMTP DATA command.
        Parameters:
          - peer: a tuple of (ip, port) for the client
          - mailfrom: sender's email address
          - rcpttos: all recipient addresses (includes To + Cc)
          - data: the raw email content (RFC822 format), usually bytes or str type
        """
        # Do not perform any "forwarding" here, just store the info in self.messages
        self.messages.append((peer, mailfrom, rcpttos, data))
        # Returning None means 250 OK
        return

    @classmethod
    def extract_parts_from_message(cls, raw_data) -> dict:
        """
        Parse the raw email data received by DummySMTPServer into an EmailMessage object, and extract key information:
          - mailfrom and rcpttos are additionally passed in by the server, and can be accessed from the fixture
          - subject, from, to, cc, HTML body, list of attachments
        Returns a dictionary, for example: {
            'subject': ...,
            'from': ...,
            'to': [...],
            'cc': [...],     # Empty list if no CC
            'html_content': ...,   # HTML string
            'attachments': [ {'filename':..., 'content': b'...'} , ... ]
        }
        """
        # If raw_data is a str, convert it to bytes first
        if isinstance(raw_data, str):
            raw_data = raw_data.encode('utf-8')

        msg: email.message.EmailMessage = BytesParser(policy=policy.default).parsebytes(raw_data)
        result = {
            'subject': msg['Subject'],
            'from': msg['From'],
            'to': [addr.strip() for addr in msg.get_all('To', [])],
            'cc': [addr.strip() for addr in msg.get_all('Cc', [])],
            'html_content': None,
            'attachments': []
        }

        # Iterate through all parts to find the HTML part and attachments
        if msg.is_multipart():
            for part in msg.iter_parts():
                content_type = part.get_content_type()
                disposition = part.get_content_disposition()

                # If it's HTML (typically Content-Type: text/html)
                if content_type == 'text/html' and disposition is None:
                    result['html_content'] = part.get_content()  # Directly get as str
                # If it's an attachment
                elif disposition == 'attachment':
                    filename = part.get_filename()
                    payload_bytes = part.get_content()  # bytes
                    result['attachments'].append({
                        'filename': filename,
                        'content': payload_bytes
                    })
        else:
            # If the whole email is a single part (very rare, as our construction typically uses multipart/alternative)
            content_type = msg.get_content_type()
            if content_type == 'text/html':
                result['html_content'] = msg.get_content()

        return result


mailinator_email = EmailUtils()
