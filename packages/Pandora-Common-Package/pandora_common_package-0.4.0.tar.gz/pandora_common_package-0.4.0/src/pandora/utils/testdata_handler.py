import json
import os
import re
from typing import Dict, List, Union

import jmespath
from deepdiff import DeepDiff

from pandora.utils.settings_loader import ConfigLoader


class TestDataHandler:

    @staticmethod
    def load_test_data(file_path, testcases) -> Union[Dict, List]:
        """
        Load test cases from a YAML file and format environment variables

        Args:
            file_path: Path to the YAML file
            testcases: Key in the YAML file where test cases are located

        Returns:
            Dictionary or list containing test cases with environment variables replaced

        Raises:
            KeyError: If the specified test cases key is not found
        """
        try:
            data = ConfigLoader.load_config(file_path)
        except Exception as e:
            raise f"YAML format error in {file_path}: {str(e)}"

        if testcases in data:
            test_cases = data[testcases]
            return TestDataHandler().map_testdata_variables(test_cases)
        else:
            available_keys = list(data.keys()) if isinstance(data, dict) else []
            raise KeyError(f"Key '{testcases}' not found in file {file_path}. Available keys: {available_keys}")


    def map_testdata_variables(self, test_cases):
        """
        Recursively replace environment variable placeholders in test case data.

        This method processes test case data to substitute placeholders
        in the format ${VARIABLE} with their corresponding environment variable values.
        If an environment variable is not set, the placeholder is left unchanged.

        Args:
            test_cases: Test case data in various types (str, dict, list, etc.)

        Returns:
            Processed test case data with environment variables substituted
        """

        def replace_match(match):
            """
            Callback function for re.sub() to replace environment variable placeholders.

            Args:
                match: Match object from regular expression pattern

            Returns:
                Substituted value from environment variable or original placeholder
            """
            var_name = match.group(1)  # Extract variable name from match
            # Use environment variable value if exists, otherwise keep original placeholder
            value = os.getenv(var_name, f"${{{var_name}}}")
            return value

        # Traverse the input data and replace variables
        if isinstance(test_cases, str):
            # Replace placeholders in strings (e.g., "${API_KEY}" -> "abc123")
            pattern = re.compile(r"\$\{(\w+)\}")  # Matches ${VARIABLE} format
            return pattern.sub(replace_match, test_cases)

        elif isinstance(test_cases, dict):
            # Recursively process dictionary values
            return {
                key: self.map_testdata_variables(value)
                for key, value in test_cases.items()
            }

        elif isinstance(test_cases, list):
            # Recursively process list items
            return [self.map_testdata_variables(item) for item in test_cases]

        else:
            # Return other types (int, float, None, etc.) unchanged
            return test_cases

def assert_all_assertions(test_case, actual_api_response) -> tuple[bool, list[str]]:
    """
    Validate all assertions in a YAML test case against an actual API response.

    Args:
        test_case: YAML test case data containing expectations
        actual_api_response: Actual response object from the API call

    Returns:
        Tuple (is_passed, messages):
        - is_passed: True if all assertions passed, False otherwise
        - messages: List of validation results and error messages
    Note: - This function use jmespath to extract values from JSON
            here's the sample usage: https://github.com/jmespath/jmespath.py
          - Use "Except_Body" to specify the expected response body in the test case
          - use "Verification" to specify the verification rules
          - Use "Status_Code" to specify the expected HTTP status code
    """
    messages = []
    is_passed = True

    # Validate HTTP status code
    expected_status_code = test_case.get('Status_Code')
    actual_status_code = actual_api_response.status_code

    if expected_status_code is not None:
        if actual_status_code != expected_status_code:
            messages.append(f"Status code mismatch! Expected: {expected_status_code}, Actual: {actual_status_code}")
            is_passed = False
            return is_passed, messages

    # Parse actual response body as JSON
    try:
        actual_body = actual_api_response.json()
    except json.JSONDecodeError:
        messages.append("Failed to parse actual API response body as JSON.")
        is_passed = False
        return is_passed, messages

    # Parse expected response body
    expect_body = test_case.get('Expect_Body', '')

    if not expect_body:
        messages.append("No expected body provided in the test case.")
        return True, messages  # Success if no expectations

    # Convert string JSON to object if necessary
    if isinstance(expect_body, str):
        try:
            expect_body = json.loads(expect_body.strip())
        except json.JSONDecodeError:
            messages.append("Expected body is not valid JSON.")
            is_passed = False
            return is_passed, messages

    # Extract verification rules
    verifications = test_case.get('Verification', [])

    # Supported Operators:
    # ----------------------
    # - Equal: Value equality check
    # - NotEqual: Value inequality check
    # - Contains: Check if actual value contains expected value
    # - NotContain: Check if actual value does not contain expected value
    # - StructureCompare: Deep structure comparison (ignore order)
    # - StructureCompare with order: Deep structure comparison (consider order)

    # Process each verification rule
    for rule in verifications:
        parts = rule.split('-', 1)
        if len(parts) != 2:
            messages.append(f"Invalid verification rule: {rule}")
            is_passed = False
            return is_passed, messages

        operator, path = parts

        # Extract values from JSON using JMESPath
        try:
            expect_value = jmespath.search(path, expect_body)
            actual_value = jmespath.search(path, actual_body)
        except Exception as e:
            messages.append(f"Invalid Jmespath expression: {path}, Error: {str(e)}")
            is_passed = False
            return is_passed, messages

        # Perform validation based on operator type
        if operator == 'Equal':
            if actual_value != expect_value:
                messages.append(
                    f"Equality check failed - Path: {path}, Expected: {expect_value}, Actual: {actual_value}")
                is_passed = False
                return is_passed, messages

        elif operator == 'NotEqual':
            if actual_value == expect_value:
                messages.append(
                    f"Inequality check failed - Path: {path}, Expected not equal to: {expect_value}, Actual: {actual_value}")
                is_passed = False
                return is_passed, messages

        elif operator == 'Contains':
            if actual_value is None:
                messages.append(f"Actual value is None - Path: {path}")
                is_passed = False
                return is_passed, messages

            if not isinstance(actual_value, (str, list, dict)):
                messages.append("Actual value is not a string, list, or dict.")
                is_passed = False
                return is_passed, messages

            if isinstance(expect_value, list):
                if not is_sublist(expect_value, actual_value):
                    messages.append(
                        f"Sublist check failed - Path: {path}, Expected to contain: {expect_value}, Actual: {actual_value}")
                    is_passed = False
                    return is_passed, messages
            elif expect_value not in actual_value:
                messages.append(
                    f"Contains check failed - Path: {path}, Expected to contain: {expect_value}, Actual: {actual_value}")
                is_passed = False
                return is_passed, messages

        elif operator == 'NotContain':
            if actual_value is None:
                continue  # Skip check if actual value is None

            if not isinstance(actual_value, (str, list, dict)):
                messages.append("Actual value is not a string, list, or dict.")
                is_passed = False
                return is_passed, messages

            if isinstance(expect_value, list):
                if is_sublist(expect_value, actual_value):
                    messages.append(
                        f"Does not contain check failed - Path: {path}, Expected not to contain: {expect_value}, Actual: {actual_value}")
                    is_passed = False
                    return is_passed, messages
            elif expect_value in actual_value:
                messages.append(
                    f"Does not contain check failed - Path: {path}, Expected not to contain: {expect_value}, Actual: {actual_value}")
                is_passed = False
                return is_passed, messages

        elif operator == 'StructureCompare':
            if expect_value is None or actual_value is None:
                messages.append(f"Structure comparison failed - Path: {path}, Null value found")
                is_passed = False
                return is_passed, messages

            # Compare structures ignoring order
            diff = DeepDiff(expect_value, actual_value, ignore_order=True)
            if diff:
                messages.append(f"Structure comparison failed - Path: {path}, Differences: {diff}")
                is_passed = False
                return is_passed, messages

        elif operator == 'StructureCompareWithOrder':
            if expect_value is None or actual_value is None:
                messages.append(f"Structure comparison failed - Path: {path}, Null value found")
                is_passed = False
                return is_passed, messages

            # Compare structures considering order
            diff = DeepDiff(expect_value, actual_value, ignore_order=False)
            if diff:
                messages.append(f"Structure comparison failed - Path: {path}, Differences: {diff}")
                is_passed = False
                return is_passed, messages

        else:
            messages.append(f"Unsupported operator: {operator}")
            is_passed = False
            return is_passed, messages

    # All assertions passed
    messages.append("All assertions passed successfully")
    return is_passed, messages


def is_sublist(sublist, main_list) -> bool:
    """
    Check if sublist is a contiguous subsequence of main_list

    Args:
        sublist: List to check for
        main_list: List to check within

    Returns:
        True if sublist is found in main_list in the same order
    """
    if main_list is None:
        return False

    n, m = len(sublist), len(main_list)

    # Check all possible starting positions
    for i in range(m - n + 1):
        if main_list[i:i + n] == sublist:
            return True

    return False