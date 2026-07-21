"""
trustcalc.config.defaults
=========================

Default configuration values for the Trust Calculus framework.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------

PROJECT_NAME = "Trust Calculus"
VERSION = "1.0.0"

# ---------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------

DEFAULT_MAX_WORKERS = 4
DEFAULT_TIMEOUT = 30.0
DEFAULT_ENABLE_ASYNC = True
DEFAULT_VERBOSE = False

# ---------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------

DEFAULT_TRUST_THRESHOLD = 0.80
DEFAULT_MAX_LEAKAGE = 0.0

DEFAULT_POLICY_ENGINE = True
DEFAULT_SIDECHANNEL_DETECTION = True
DEFAULT_ALLOW_PRIVILEGE_ESCALATION = False

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_ENABLED = True
DEFAULT_LOG_TO_FILE = True
DEFAULT_LOG_FILE = "trustcalc.log"

# ---------------------------------------------------------------------
# Output Directories
# ---------------------------------------------------------------------

DEFAULT_OUTPUT_DIR = Path("output")
DEFAULT_REPORT_DIR = DEFAULT_OUTPUT_DIR / "reports"
DEFAULT_PLOT_DIR = DEFAULT_OUTPUT_DIR / "plots"
DEFAULT_LOG_DIR = DEFAULT_OUTPUT_DIR / "logs"
DEFAULT_EXPORT_DIR = DEFAULT_OUTPUT_DIR / "exports"

# ---------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------

DEFAULT_NUM_EXPERIMENTS = 100
DEFAULT_RANDOM_SEED = 42

# ---------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------

DEFAULT_FIGURE_FORMAT = "png"
DEFAULT_FIGURE_DPI = 300

# ---------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------

DEFAULT_REPORT_FORMAT = "markdown"

SUPPORTED_REPORT_FORMATS = (
    "markdown",
    "json",
    "text",
)

# ---------------------------------------------------------------------
# File Formats
# ---------------------------------------------------------------------

SUPPORTED_CONFIG_FORMATS = (
    ".json",
    ".yaml",
    ".yml",
)

SUPPORTED_PLOT_FORMATS = (
    "png",
    "pdf",
    "svg",
)