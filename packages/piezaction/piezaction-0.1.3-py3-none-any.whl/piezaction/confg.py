import os
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""

    pass


@dataclass
class ConfigValue:
    """Container for configuration values with metadata."""

    value: Any
    source: str
    required: bool = True
    default: Any = None


class ConfigTools:
    """Tools class for easily getting configuration from environment variables."""

    def __init__(self, prefix: str = ""):
        """Initialize ConfigTools with optional prefix for environment variables.

        Args:
            prefix: Optional prefix to prepend to all environment variable names
        """
        self.prefix = prefix.upper()

    def _get_env_name(self, key: str) -> str:
        """Get the full environment variable name with prefix."""
        if self.prefix:
            return f"{self.prefix}_{key.upper()}"
        return key.upper()

    def get(self, key: str, default: Any = None, required: bool = False) -> Any:
        """Get a configuration value from environment variables.

        Args:
            key: The configuration key (will be converted to uppercase)
            default: Default value if not found in environment
            required: If True, raises ConfigurationError when missing

        Returns:
            The configuration value

        Raises:
            ConfigurationError: If required configuration is missing
        """
        env_name = self._get_env_name(key)
        value = os.environ.get(env_name, default)

        if required and value is None:
            raise ConfigurationError(f"Missing required configuration: {env_name}")

        return value

    def get_str(self, key: str, default: str = None, required: bool = False) -> str:
        """Get a string configuration value."""
        value = self.get(key, default, required)
        return str(value) if value is not None else None

    def get_int(self, key: str, default: int = None, required: bool = False) -> int:
        """Get an integer configuration value."""
        value = self.get(key, default, required)
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ConfigurationError(f"Invalid integer value for {key}: {value}")

    def get_float(
        self, key: str, default: float = None, required: bool = False
    ) -> float:
        """Get a float configuration value."""
        value = self.get(key, default, required)
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ConfigurationError(f"Invalid float value for {key}: {value}")

    def get_bool(self, key: str, default: bool = None, required: bool = False) -> bool:
        """Get a boolean configuration value."""
        value = self.get(key, default, required)
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)

    def get_list(
        self,
        key: str,
        separator: str = ",",
        default: List = None,
        required: bool = False,
    ) -> List[str]:
        """Get a list configuration value from comma-separated string."""
        value = self.get(key, default, required)
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(separator) if item.strip()]
        return [str(value)]

    def validate_required(self, keys: List[str]) -> None:
        """Validate that all required configuration keys are present.

        Args:
            keys: List of required configuration keys

        Raises:
            ConfigurationError: If any required configuration is missing
        """
        missing = []
        for key in keys:
            env_name = self._get_env_name(key)
            if not os.environ.get(env_name):
                missing.append(env_name)

        if missing:
            raise ConfigurationError(
                f"Missing required configuration: {', '.join(missing)}"
            )

    def get_all(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple configuration values at once.

        Args:
            keys: List of configuration keys to retrieve

        Returns:
            Dictionary with key-value pairs
        """
        result = {}
        for key in keys:
            result[key] = self.get(key)
        return result

    def get_typed(
        self, key: str, value_type: type, default: Any = None, required: bool = False
    ) -> Any:
        """Get a configuration value with type conversion.

        Args:
            key: The configuration key
            value_type: The type to convert the value to
            default: Default value if not found
            required: If True, raises ConfigurationError when missing

        Returns:
            The configuration value converted to the specified type
        """
        value = self.get(key, default, required)
        if value is None:
            return None

        try:
            return value_type(value)
        except (ValueError, TypeError):
            raise ConfigurationError(
                f"Invalid {value_type.__name__} value for {key}: {value}"
            )


# Example usage and additional convenience methods
# class DatabaseConfig:
#     """Example configuration class for database settings."""

#     def __init__(self, prefix: str = "DB"):
#         self.config = ConfigTools(prefix)

#     def get_connection_string(self) -> str:
#         """Get database connection string from environment variables."""
#         self.config.validate_required(["HOST", "PORT", "NAME", "USER", "PASSWORD"])

#         host = self.config.get_str("HOST", required=True)
#         port = self.config.get_int("PORT", default=5432)
#         name = self.config.get_str("NAME", required=True)
#         user = self.config.get_str("USER", required=True)
#         password = self.config.get_str("PASSWORD", required=True)

#         return f"postgresql://{user}:{password}@{host}:{port}/{name}"

#     def get_pool_settings(self) -> Dict[str, Any]:
#         """Get database connection pool settings."""
#         return {
#             "min_size": self.config.get_int("POOL_MIN_SIZE", default=1),
#             "max_size": self.config.get_int("POOL_MAX_SIZE", default=10),
#             "max_queries": self.config.get_int("POOL_MAX_QUERIES", default=50000),
#             "max_inactive_connection_lifetime": self.config.get_float("POOL_MAX_INACTIVE_LIFETIME", default=300.0),
#         }
