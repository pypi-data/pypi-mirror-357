# =============================================================================
# THE XPECTRANET PROTOCOL™ — Symbolic Cognition SDK
#
# Copyright (c) 2025 Xpectra Data Technologies Ltd.
# SPDX-License-Identifier: BSL-1.1-XD
#
# Module: __init__.py
#
# Overview:
# ---------
# Public API Entry Point for the XpectraNet Mesh Cognition Protocol.
# This SDK enables protocol-grade symbolic memory and cognitive alignment
# for agents, LLMs, and mesh workflows. Exposes all stable, production-level
# functions:
#   - Mint symbolic memory blocks (CMBs)
#   - Reconstruct protocol-level cognitive state (diffusion)
#   - Resolve contradiction (collapse)
#   - Clarify ambiguity or drift (clarifier)
#   - Remix cognitive trails (remix)
#   - Canonize symbolic states (audit, mesh reference)
#
# Protocol Law:
#   - All mesh cognition, remix, and canonicalization MUST use these interfaces.
#   - Unauthorized symbolic forking, remix, or canonization outside protocol bounds
#     is a violation of protocol law.
#   - XpectraNet®, XpectraData™, and all marks are registered trademarks.
#
# Product Usage:
#   - This entrypoint is the only supported way to interface with protocol memory
#     for all apps, agents, and Circle mesh validators.
#   - See https://xpectranet.com/sdk/docs for full reference and compliance details.
# =============================================================================

from .sdk.mint import mint_insight              # Epistemic declaration — mint symbolic memory blocks (CMBs)
from .sdk.diffuse import diffuse_state          # Contextual reconstruction — diffuse prior trail into live cognitive state
from .sdk.collapse import collapse_inputs       # Contradiction resolution — collapse divergent beliefs into a protocol-compliant state
from .sdk.remix import remix_from_state         # Lineage-traceable divergence — create structured forks/remixes of cognition trails
from .sdk.canon import canonize_state           # Epistemic commitment — canonize symbolic state for audit, reference, and mesh reuse
from .sdk.clarifier import clarifier_reroute    # Reflexive protocol repair — reroute or clarify on drift, rupture, or ambiguity

__all__ = [
    "mint_insight",         # Symbolic minting of mesh input as CognitiveMemoryBlock
    "diffuse_state",        # Mesh anchor fusion and live context reconstruction
    "collapse_inputs",      # Collapse of contradictions and epistemic divergence
    "remix_from_state",     # Structured, auditable cognition forking
    "canonize_state",       # Commitment and sealing of mesh memory for replay and cross-agent audit
    "clarifier_reroute",    # Protocol-driven drift/ambiguity repair and clarifier reflex
]