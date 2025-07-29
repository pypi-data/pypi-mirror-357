"""
Browser Launcher module for ZTray Modular.

This module provides functionality for launching browsers with different profiles.
"""

from .browser_tab import BrowserLauncherTab
from .alternative_browser_manager import AlternativeBrowserManager, LaunchOptions

__all__ = [
    "BrowserLauncherTab",
    "AlternativeBrowserManager",
    "LaunchOptions"
]
