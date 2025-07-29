import requests
import os
from dotenv import load_dotenv
import loguru
import base64
import json
from src.pandora.config.config import c_config


def get_variable_group(group_ids: list, project: str = None):
    """
    Fetch variables from specified Azure DevOps variable group IDs.

    Args:
    group_ids (list): A list of variable group IDs.
    project (str): The Azure DevOps project name. If not provided, uses the one from configuration.
﻿
    Notes:
    Reads environment variables ADO_ORG, ADO_PROJECT, and ADO_PAT from .env file. If debugging is done locally, put the .env in the config folder.
    """
    org = c_config.ado_org
    token = c_config.ado_token
    project = project
    if not all([org, project, token]):
        raise ValueError("Missing required environment variables: org, project, or token")

    basic_auth = base64.b64encode(f":{token}".encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/json"
    }

    all_variables = {}
    for group_id in group_ids:
        group_id = group_id.strip()
        if not group_id:
            continue
        api_url = c_config.ado_api_url.format(
            org=org,
            project=project,
            group_id=group_id,
        )
        response = requests.get(api_url, headers=headers)

        if response.status_code != 200:
            try:
                error_detail = response.json()
            except Exception:
                error_detail = response.text
            logger.error(f"Failed to get variable group {group_id}: {response.status_code}, {error_detail}")
            continue
        try:
            data = response.json()
        except Exception as e:
            logger.error(f"Failed to parse JSON for group {group_id}: {e}")
            continue
        variables = data.get("variables", {})
        all_variables.update(variables)

    return all_variables


def export_value_to_env(project: str = None):
    """
    Export Azure DevOps variable group values to environment variables.

    Notes:
        - Reads ADO_GROUP_IDS from environment variable and fetches variables via Azure DevOps API.
        - Skips setting environment variables that already exist in os.environ.
    """
    group_ids = os.getenv("ADO_GROUP_IDS", "").split(",")

    variables = get_variable_group(c_config.group_ids, project=project)
    for key, value in variables.items():
        actual_value = value.get("value")
        if actual_value and key not in os.environ:
            os.environ[key] = actual_value
            logger.info(f"Set env var: {key} = ***hidden***")
        else:
            logger.info(f"Skipped existing env var: {key}")
    return variables


if __name__ == "__main__":
    # Used for external pipeline calls
    from loguru import logger

    test_project = "initium"
    export_value_to_env(project=test_project)
