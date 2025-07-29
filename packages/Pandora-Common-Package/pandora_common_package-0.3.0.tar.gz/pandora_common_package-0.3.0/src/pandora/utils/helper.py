import base64
import json
from urllib.parse import urlparse, parse_qs

import jwt
from jwt.exceptions import InvalidTokenError, DecodeError


def extract_param_from_url(url, param_name):
    """
    Extracts a single query parameter from a URL.

    Args:
        url: The full URL containing the query string.
        param_name: The name of the parameter to extract.

    Returns:
        - The parameter value as a string if present.
        - An empty string "" if the parameter exists but has no value (e.g., "?param=").
        - None if the parameter is not present in the URL.

    """
    try:
        # Parse the URL into components and extract the query string
        parsed_url = urlparse(url)
        # Parse the query string into a dictionary of lists
        query_params = parse_qs(parsed_url.query)

        # Safely retrieve the first value of the parameter, defaulting to None
        # Returns None if parameter is missing, empty string if present but valueless
        return query_params.get(param_name, [None])[0]

    except ValueError as ve:
        # Handle invalid URL format
        raise ValueError(f"Invalid URL format: {url}") from ve
    except Exception as e:
        # Handle unexpected parsing errors
        raise ValueError(f"Error parsing URL: {str(e)}") from e


def parse_jwt_token(token, parse_header=False, secret_key=None, algorithms=None):
    """
    Parse a JWT token and return its payload or header

    Args:
        token (str): JWT token to be parsed
        parse_header (bool, optional): If True, return header instead of payload. Default: False
        secret_key (str, optional): Secret key for signature verification. Default: None
        algorithms (list, optional): Allowed signing algorithms. Default: ['HS256']

    Returns:
        dict: Payload or Header data contained in the token

    Raises:
        InvalidTokenError: Raised when the token is invalid, expired, or signature verification fails
        DecodeError: Raised when the token format is incorrect or cannot be parsed
    """
    if algorithms is None:
        algorithms = ['HS256']

    try:
        if parse_header:
            parts = token.split('.')
            if len(parts) < 2:
                raise ValueError("Invalid JWT format")

            header_encoded = parts[0]
            missing_padding = len(header_encoded) % 4
            if missing_padding:
                header_encoded += '=' * (4 - missing_padding)

            header_bytes = base64.urlsafe_b64decode(header_encoded)
            return json.loads(header_bytes.decode('utf-8'))

        else:
            if secret_key:
                payload = jwt.decode(token, secret_key, algorithms=algorithms)
            else:
                payload = jwt.decode(token, options={"verify_signature": False})
            return payload

    except (InvalidTokenError, DecodeError, ValueError) as e:
        print(f"JWT parsing failed: {str(e)}")


def get_value_from_jwt_token_payload(token, key, parse_header=False,  secret_key=None, algorithms=None):
    """
    Retrieve a specific value from the JWT token's payload

    Args:
        token (str): JWT token to be parsed
        key (str): Key name to retrieve from the payload
        parse_header (bool, optional): If True, return header instead of payload. Default: False
        secret_key (str, optional): Secret key for signature verification. Default: None
        algorithms (list, optional): Allowed signing algorithms. Default: ['HS256']

    Returns:
        Any: Value corresponding to the key, or None if key does not exist

    Raises:
        InvalidTokenError: Raised when the token is invalid, expired, or signature verification fails
        DecodeError: Raised when the token format is incorrect or cannot be parsed
    """
    try:
        # Get payload by calling parse method
        data = parse_jwt_token(token, parse_header, secret_key, algorithms)
        return data.get(key)

    except Exception as e:
        print(f"Failed to retrieve value from JWT payload: {str(e)}")
