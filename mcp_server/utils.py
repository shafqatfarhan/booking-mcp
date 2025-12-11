"""
Utility functions for the booking-mcp application.
"""

import os
import sys
from logging.config import dictConfig


def setup_logging() -> None:
    """
    Set up logging configuration.
    """
    log_level = os.getenv("FASTMCP_LOG_LEVEL", "INFO")
    handlers = ['console']
    standard_format = (
        '%(asctime)s %(levelname)s %(process)d '
        '[%(name)s] %(filename)s:%(lineno)d - %(message)s'
    )
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': standard_format,
            },
            'raw': {'format': '%(message)s'},
        },
        'handlers': {
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': sys.stdout,
            },
        },
        'loggers': {
            "uvicorn.access": {
                "level": "WARNING",
                "handlers": handlers,
                "propagate": False
            },
            "uvicorn.error": {
                "level": log_level,
                "handlers": handlers,
                "propagate": True
            },
            "fastmcp": {
                "level": log_level,
                "handlers": handlers,
                "propagate": False,
            },
            "mcp.server": {
                "level": log_level,
                "handlers": handlers,
                "propagate": True,
            },
            '': {
                'handlers': handlers,
                'level': log_level,
                'propagate': False
            },
        }
    })
