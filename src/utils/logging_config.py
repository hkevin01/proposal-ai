"""
Centralized logging configuration for Proposal AI.
"""
import logging
import sys

def setup_logging():
    """Set up logging for Proposal AI (console and file)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/proposal_ai.log", encoding="utf-8")
        ]
    )
