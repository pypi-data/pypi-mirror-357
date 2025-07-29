import json
from typing import Any


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
