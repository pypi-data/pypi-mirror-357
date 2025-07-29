import asyncore
import threading
import pytest
from utils.email import EmailSender, DummySMTPServer
import uuid
import os
import subprocess
import time
import smtplib
import socket
from pytest import MonkeyPatch
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


class TestSendEmail:
    @pytest.fixture(scope="module")
    def smtp_server(self):
        """
        Pytest fixture: Starts a local DummySMTPServer for use by send_email_with_auth during tests.
        It listens by default on 127.0.0.1:8025. After tests are done, the server is shut down and resources released.
        """
        host = '127.0.0.1'
        port = 8025
        server = DummySMTPServer((host, port), None)

        # asyncore.loop() must run in a separate thread to avoid blocking the main thread
        thread = threading.Thread(target=asyncore.loop, kwargs={'timeout': 1})
        thread.daemon = True
        thread.start()

        # Wait a short while for the thread to start and the port to begin listening
        timeout = 5.0
        start = time.time()
        while True:
            try:
                # Try connecting to local port 8025 until successful or timeout occurs
                s = socket.create_connection((host, port), timeout=1)
                s.close()
                break
            except Exception:
                if time.time() - start > timeout:
                    pytest.skip("Unable to start DummySMTPServer, skipping email tests")
                time.sleep(0.1)

        yield server

        # Teardown: Close the server and exit asyncore.loop
        server.close()  # Close the listening socket
        time.sleep(0.1)  # Wait for socket to close
        # Pump asyncore.loop once more to clean up the thread
        asyncore.loop(timeout=1, count=1)
        # The thread will exit due to socket closure; no need to join (daemon=True)

    @pytest.fixture(autouse=True)
    def patch_smtp_ssl(self, monkeypatch: MonkeyPatch):
        """
        Pytest fixture：handle with mock SSL/TLS auth.
        """
        monkeypatch.setattr(smtplib, "SMTP_SSL", smtplib.SMTP)
        monkeypatch.setattr(smtplib.SMTP, "starttls", lambda self: None)
        yield

    @classmethod
    def send_email_succeeded_with_assertions(cls, param_dict, smtp_server):
        """
        Common actions and assertions for send email succeeded check.
        """
        # Call the function, note using auth_type="ssl" (monkeypatch has replaced SMTP_SSL with SMTP)
        send_result = EmailSender.send_email_with_auth(
            email_content=param_dict["email_content"],
            from_addr=param_dict["from_addr"],
            to_addr=param_dict["to_addr"],
            cc_addr=param_dict["cc_addr"],
            subject=param_dict["subject"],
            smtp_server=param_dict["smtp_server"],
            auth_type=param_dict["auth_type"],
            smtp_port=param_dict["smtp_port"],
            username=param_dict["username"],
            password=param_dict["password"],
            attachment_paths=param_dict["attachment_paths"],
            timeout=param_dict["timeout"]
        )

        # Handle assertion for send result
        assert send_result, "Send email failed."

        # Retrieve the received email from DummySMTPServer.messages
        try:
            assert len(smtp_server.messages) == 1, "The server should have received exactly one email"
            peer, mailfrom, rcpttos, data = smtp_server.messages[0]
        finally:
            # Clear messages for following assertions
            smtp_server.messages.clear()

        # Validate mailfrom and rcpttos received by smtp_server
        assert mailfrom == param_dict["from_addr"]

        # rcpttos should contain to_addr and cc_addr; order may not match, but contents must be the same
        expected_recipients = set(param_dict["to_addr"] + param_dict["cc_addr"])
        assert set(rcpttos) == expected_recipients

        # Parse data to extract actual subject, from, to, and html content
        parsed = DummySMTPServer.extract_parts_from_message(data)

        assert parsed['subject'] == param_dict["subject"]
        assert parsed['from'] == param_dict["from_addr"]
        # For to_addr, order may differ, but contents must match
        if param_dict["to_addr"]:
            assert set([ele.strip() for ele in parsed['to'][0].split(',')]) == set(param_dict["to_addr"])
        if param_dict["cc_addr"]:
            assert set([ele.strip() for ele in parsed['cc'][0].split(',')]) == set(param_dict["cc_addr"])
        # Assertion for attachments
        assert len(parsed['attachments']) == len(param_dict["attachment_paths"])
        if param_dict["attachment_paths"]:
            attachment_paths_str = str(param_dict["attachment_paths"])
            for element in parsed['attachments']:
                filename = element['filename']
                assert filename in attachment_paths_str, "Failed to find filename in attachment_paths"
        else:
            # The HTML body must exactly match the html string
            assert parsed['html_content'].strip() == param_dict["email_content"]

    @classmethod
    def send_email_failed_with_assertions(cls, param_dict, smtp_server, part_of_error_msg: str):
        """
        Common actions and assertions for send email failed check.
        """
        send_result: bool = False
        try:
            send_result = EmailSender.send_email_with_auth(
                email_content=param_dict["email_content"],
                from_addr=param_dict["from_addr"],
                to_addr=param_dict["to_addr"],
                cc_addr=param_dict["cc_addr"],
                subject=param_dict["subject"],
                smtp_server=param_dict["smtp_server"],
                auth_type=param_dict["auth_type"],
                smtp_port=param_dict["smtp_port"],
                username=param_dict["username"],
                password=param_dict["password"],
                attachment_paths=param_dict["attachment_paths"],
                timeout=param_dict["timeout"]
            )
        except Exception as e:
            # Accept for part of error msg and raise AssertionError if not match
            if part_of_error_msg not in str(e):
                # Clear messages for following assertions
                smtp_server.messages.clear()
                raise AssertionError(f"Expect {part_of_error_msg} in error msg, but actual is {str(e)}")

        try:
            # Handle assertion for send result
            assert not send_result, "Expect send email failed, but actually send email succeeded."

            # Retrieve the received email from DummySMTPServer.messages
            assert len(smtp_server.messages) == 0, \
                f"The server should not received any email, but actually received {len(smtp_server.messages)}"
        finally:
            # Clear messages for following assertions
            smtp_server.messages.clear()

    def test_send_email_basic(self, monkeypatch, smtp_server):
        # Prepare test data
        current_uuid: str = str(uuid.uuid4())
        logger.info(f"current_uuid={current_uuid}")
        param_dict: dict = {
            "email_content": f"<h1>Test Content {current_uuid}</h1><p>This is a test email {current_uuid}.</p>",
            "from_addr": "pandora_test01@example.com",
            "to_addr": ["pandora_test02@example.com", "pandora_test03@example.com"],
            "cc_addr": [],
            "subject": f"Pandora send email test {current_uuid}",
            "smtp_server": "127.0.0.1",
            "auth_type": "ssl",
            "smtp_port": 8025,
            "username": None,
            "password": None,
            "attachment_paths": [],
            "timeout": 60000.0
        }

        # Send email with assertions
        self.send_email_succeeded_with_assertions(param_dict, smtp_server)

    def test_send_email_with_cc_addr(self, monkeypatch, smtp_server):
        # Prepare test data
        current_uuid: str = str(uuid.uuid4())
        logger.info(f"current_uuid={current_uuid}")
        param_dict: dict = {
            "email_content": f"<h1>Test Content {current_uuid}</h1><p>This is a test email {current_uuid}.</p>",
            "from_addr": "pandora_test01@example.com",
            "to_addr": ["pandora_test02@example.com"],
            "cc_addr": ["pandora_test04@example.com", "pandora_test05@example.com"],
            "subject": f"Pandora send email test {current_uuid}",
            "smtp_server": "127.0.0.1",
            "auth_type": "ssl",
            "smtp_port": 8025,
            "username": None,
            "password": None,
            "attachment_paths": [],
            "timeout": 60000.0
        }

        # Send email with assertions
        self.send_email_succeeded_with_assertions(param_dict, smtp_server)

    def test_send_email_with_attachment(self, monkeypatch, smtp_server):
        # Zip current file as part of attachment
        current_file_abspath = os.path.abspath(__file__)
        result = subprocess.run(f"python -m zipfile -c {current_file_abspath}.zip {current_file_abspath}",
                                check=True, text=True, capture_output=True)
        if result.stderr:
            pytest.fail(reason="Test failed due to create zip attachment files failed")

        # Prepare test data
        current_uuid: str = str(uuid.uuid4())
        logger.info(f"current_uuid={current_uuid}")
        param_dict: dict = {
            "email_content": f"<h1>Test Content {current_uuid}</h1><p>This is a test email {current_uuid}.</p>",
            "from_addr": "pandora_test01@example.com",
            "to_addr": ["pandora_test02@example.com"],
            "cc_addr": [],
            "subject": f"Pandora send email test {current_uuid}",
            "smtp_server": "127.0.0.1",
            "auth_type": "ssl",
            "smtp_port": 8025,
            "username": None,
            "password": None,
            "attachment_paths": [current_file_abspath, f"{current_file_abspath}.zip"],
            "timeout": 60000.0
        }

        # Send email with assertions
        self.send_email_succeeded_with_assertions(param_dict, smtp_server)

    def test_send_email_with_attachment_not_exists(self, monkeypatch, smtp_server):
        # Zip current file as part of attachment
        current_file_abspath = os.path.abspath(__file__)
        result = subprocess.run(f"python -m zipfile -c {current_file_abspath}.zip {current_file_abspath}",
                                check=True, text=True, capture_output=True)
        if result.stderr:
            pytest.fail(reason="Test failed due to create zip attachment files failed")

        # Prepare test data
        current_uuid: str = str(uuid.uuid4())
        logger.info(f"current_uuid={current_uuid}")
        param_dict: dict = {
            "email_content": f"<h1>Test Content {current_uuid}</h1><p>This is a test email {current_uuid}.</p>",
            "from_addr": "pandora_test01@example.com",
            "to_addr": ["pandora_test02@example.com"],
            "cc_addr": [],
            "subject": f"Pandora send email test {current_uuid}",
            "smtp_server": "127.0.0.1",
            "auth_type": "ssl",
            "smtp_port": 8025,
            "username": None,
            "password": None,
            "attachment_paths": [current_file_abspath, f"{current_file_abspath}{current_uuid}.zip"],
            "timeout": 60000.0
        }

        # Send email with assertions
        self.send_email_failed_with_assertions(param_dict, smtp_server, 'File path not found')

    def test_send_email_with_tls(self, monkeypatch, smtp_server):
        # Prepare test data
        current_uuid: str = str(uuid.uuid4())
        logger.info(f"current_uuid={current_uuid}")
        param_dict: dict = {
            "email_content": f"<h1>Test Content {current_uuid}</h1><p>This is a test email {current_uuid}.</p>",
            "from_addr": "pandora_test01@example.com",
            "to_addr": ["pandora_test02@example.com"],
            "cc_addr": [],
            "subject": f"Pandora send email test {current_uuid}",
            "smtp_server": "127.0.0.1",
            "auth_type": "tls",
            "smtp_port": 8025,
            "username": None,
            "password": None,
            "attachment_paths": [],
            "timeout": 60000.0
        }

        # Send email with assertions
        self.send_email_succeeded_with_assertions(param_dict, smtp_server)

    def test_send_email_with_time_out_limit(self, monkeypatch, smtp_server):
        # Prepare test data
        current_uuid: str = str(uuid.uuid4())
        param_dict: dict = {
            "email_content": f"<h1>Test Content {current_uuid}</h1><p>This is a test email {current_uuid}.</p>",
            "from_addr": "pandora_test01@example.com",
            "to_addr": ["pandora_test02@example.com"],
            "cc_addr": [],
            "subject": f"Pandora send email test {current_uuid}",
            "smtp_server": "127.0.0.1",
            "auth_type": "tls",
            "smtp_port": 9025,
            "username": None,
            "password": None,
            "attachment_paths": [],
            "timeout": 0.1
        }

        # Send email with assertions
        self.send_email_failed_with_assertions(param_dict, smtp_server, 'timed out')
