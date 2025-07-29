import json
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


def create_error_response(error_msg: str) -> str:
    """Create a standardized error response.

    Args:
        error_msg: Error message to include

    Returns:
        str: JSON error response
    """
    return json.dumps({"success": False, "error": error_msg})


def create_success_response(data: Any) -> str:
    """Create a standardized success response.

    Args:
        data: Data to include in response

    Returns:
        str: JSON success response
    """
    return json.dumps({"success": True, "data": data})


def parse_request(event) -> Dict[str, Any]:
    """Parse the request data from the event.

    Args:
        event: The OpenFaaS event object

    Returns:
        dict: Parsed request data with at least an 'action' key
    """
    default_response = {"action": ""}

    if not hasattr(event, "body") or not event.body:
        logger.warning("No body found in event")
        return default_response

    try:
        parsed_data = json.loads(event.body)
        if not isinstance(parsed_data, dict):
            logger.warning("Request body is not a JSON object")
            return default_response
        return parsed_data
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default_response
