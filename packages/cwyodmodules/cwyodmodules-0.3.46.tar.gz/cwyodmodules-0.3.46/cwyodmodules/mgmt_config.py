"""
Azure Project Management Configuration Template

This template provides standardized configuration for Azure logging and identity
management across projects. It creates singleton instances of AzureLogger and
AzureIdentity that can be imported and used throughout your application.

Usage:
    from mgmt_config import logger, identity
    
    logger.info("Application started")
    credential = identity.get_credential()
"""

import os
from typing import Optional, Dict, Any
from azpaddypy.mgmt.logging import create_app_logger, create_function_logger
from azpaddypy.mgmt.identity import create_azure_identity

# =============================================================================
# SERVICE CONFIGURATION
# =============================================================================

# Service identity - customize these for your project
SERVICE_NAME = os.getenv("SERVICE_NAME", "cwyodmodules-pacakge")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Enable console output (useful for local development)
LOGGER_ENABLE_CONSOLE = os.getenv("LOGGER_ENABLE_CONSOLE", "true").lower() == "true"

# Application Insights connection string (optional, will use environment variable if not set)
LOGGER_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

# Configure which Azure SDK components to instrument
LOGGER_INSTRUMENTATION_OPTIONS = {
    "azure_sdk": {"enabled": True},
    "django": {"enabled": False},
    "fastapi": {"enabled": False},
    "flask": {"enabled": True},
    "psycopg2": {"enabled": True},
    "requests": {"enabled": True},
    "urllib": {"enabled": True},
    "urllib3": {"enabled": True},
}

# =============================================================================
# IDENTITY CONFIGURATION
# =============================================================================

# Token caching settings
IDENTITY_ENABLE_TOKEN_CACHE = os.getenv("IDENTITY_ENABLE_TOKEN_CACHE", "true").lower() == "true"
IDENTITY_ALLOW_UNENCRYPTED_STORAGE = os.getenv("IDENTITY_ALLOW_UNENCRYPTED_STORAGE", "true").lower() == "true"

# Custom credential options (None means use defaults)
IDENTITY_CUSTOM_CREDENTIAL_OPTIONS: Optional[Dict[str, Any]] = None

# Connection string for identity logging (uses same as logger by default)
IDENTITY_CONNECTION_STRING = LOGGER_CONNECTION_STRING

# =============================================================================
# INITIALIZE SERVICES
# =============================================================================
# Create logger instance
if "functionapp" in os.getenv("REFLECTION_KIND", "app"):
    logger = create_function_logger(
        function_app_name=os.getenv("REFLECTION_NAME", "app"),
        function_name="backend",
        service_version=SERVICE_VERSION,
        connection_string=LOGGER_CONNECTION_STRING,
        instrumentation_options=LOGGER_INSTRUMENTATION_OPTIONS,
    )
    logger.info("Function logger initialized")
else:
    logger = create_app_logger(
        service_name=SERVICE_NAME,
        service_version=SERVICE_VERSION,
        connection_string=LOGGER_CONNECTION_STRING,
        enable_console_logging=LOGGER_ENABLE_CONSOLE,
        instrumentation_options=LOGGER_INSTRUMENTATION_OPTIONS,
    )
    logger.info("App logger initialized")

# Create identity instance with shared logger
identity = create_azure_identity(
    service_name=SERVICE_NAME,
    service_version=SERVICE_VERSION,
    enable_token_cache=IDENTITY_ENABLE_TOKEN_CACHE,
    allow_unencrypted_storage=IDENTITY_ALLOW_UNENCRYPTED_STORAGE,
    custom_credential_options=IDENTITY_CUSTOM_CREDENTIAL_OPTIONS,
    connection_string=IDENTITY_CONNECTION_STRING,
    logger=logger,
)

# =============================================================================
# VALIDATION & STARTUP
# =============================================================================

# Validate critical configuration
if SERVICE_NAME == __name__:
    logger.warning(
        "SERVICE_NAME is not configured. Please set SERVICE_NAME environment variable or update this template.",
        extra={"configuration_issue": "service_name_not_set"}
    )

if not LOGGER_CONNECTION_STRING:
    logger.info(
        "No Application Insights connection string configured. Telemetry will be disabled.",
        extra={"telemetry_status": "disabled"}
    )

# Log successful initialization
logger.info(
    f"Management configuration initialized for service '{SERVICE_NAME}' v{SERVICE_VERSION}",
    extra={
        "service_name": SERVICE_NAME,
        "service_version": SERVICE_VERSION,
        "console_logging": LOGGER_ENABLE_CONSOLE,
        "token_cache_enabled": IDENTITY_ENABLE_TOKEN_CACHE,
        "telemetry_enabled": bool(LOGGER_CONNECTION_STRING),
    }
)

# =============================================================================
# EXPORTS
# =============================================================================

# Export both logger and identity for use in applications
__all__ = ["logger", "identity"]
