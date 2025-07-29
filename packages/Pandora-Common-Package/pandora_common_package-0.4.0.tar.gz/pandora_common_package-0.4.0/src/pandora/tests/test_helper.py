from pandora.utils import helper
from pandora.utils.email import mailinator_email
from pandora.utils.helper import get_value_from_jwt_token_payload


def test_extract_param_from_url():
    url = "https://example.com/path?param1=value1&param2=value2"
    param_name = "param1"
    expected_value = "value1"
    actual_value = helper.extract_param_from_url(url, param_name)
    assert (
            actual_value == expected_value
    ), f"Expected {expected_value}, but got {actual_value}"


def example_get_email_content():
    inbox = "abc@hp.com"
    inbox = inbox.split('@')[0]
    emails = mailinator_email.get_email_list(inbox, 6, 5)
    mail_id = mailinator_email.get_email_id(emails, "New authentication request")
    mail_details = mailinator_email.get_email_details(mail_id)
    pat = r':#0076AD;">(.*?)</div>'
    mfa = mailinator_email.get_content_from_email_withpattern(mail_details, pat)
    print("mfa:", mfa.strip())


def test_get_value_from_jwt_token():
    test_jwt_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidGVzdF91c2VyIiwiaWQiOiJ0ZXN0XzEyMyJ9."
    expect_jwt_payload_value = "test_user"
    expect_jwt_header_value = "JWT"

    actual_jwt_payload_value = get_value_from_jwt_token_payload(test_jwt_token, "user")
    actual_jwt_header_value = get_value_from_jwt_token_payload(test_jwt_token, "typ", parse_header=True)

    assert expect_jwt_payload_value == actual_jwt_payload_value, f"Expected payload {expect_jwt_payload_value}, but got {actual_jwt_payload_value}"
    assert expect_jwt_header_value == actual_jwt_header_value, f"Expected header {expect_jwt_header_value}, but got {actual_jwt_header_value}"
