"""
Wakanda Protocol - African Sovereignty Blueprint

A comprehensive full-stack platform uniting:
- Financial Technology Hub
- Semiconductor & Minerals Supply Chain
- AI-Driven Skills & Disability Support
- Public Sector Digitalization
- Civic Infrastructure & Disaster Response
- Data Governance & Security
"""

__version__ = "0.1.0"
__author__ = "Wakanda Protocol Team"

from .core.config import settings
from .core.security import SecurityManager
from .api.main import create_app

__all__ = ["settings", "SecurityManager", "create_app"]