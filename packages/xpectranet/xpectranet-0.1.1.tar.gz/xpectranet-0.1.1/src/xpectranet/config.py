# =============================================================================
# THE XPECTRANET PROTOCOL™ — Symbolic Cognition SDK
#
# Copyright (c) 2025 Xpectra Data Technologies Ltd.
# SPDX-License-Identifier: BSL-1.1-XD
#
# Module: config.py
#
# Overview:
# ---------
# Central configuration for the XpectraNet Protocol SDK.
# Defines protocol versions, symbolic cognition parameters,
# and tunable thresholds for mesh memory operations.
#
# Protocol Law:
#   - Configuration MUST be set only via this module or explicit environment variables.
#   - Any override or fork outside protocol boundaries is prohibited.
#   - Version and threshold fields power drift detection, protocol compliance,
#     and mesh validator enforcement.
#
# Product Usage:
#   - Used throughout the SDK for protocol versioning, drift management,
#     and symbolic mesh configuration. All mesh agents reference this file for
#     protocol alignment.
# =============================================================================

import os

# Current active symbolic protocol version
PROTOCOL_VERSION = "v1.0"

# Supported symbolic protocol versions (future-proofed)
SUPPORTED_VERSIONS = ["v1.0"]

# Load drift threshold from environment, fallback to 0.7 if unset
DRIFT_THRESHOLD = float(os.getenv("XPECTRANET_DRIFT_THRESHOLD", "0.7"))
