"""
Alternative browser management for ZTray Browser Launcher.

This module provides functionality for detecting and launching alternative browsers
that don't have the concept of user profiles, like Edge, Opera, Maxthon, etc.
"""

import os
import sys
import platform
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

# Initialize logger
logger = logging.getLogger(__name__)

# Determine operating system
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

# Common paths by platform
if IS_WINDOWS:
    LOCAL_APPDATA = os.environ.get("LOCALAPPDATA", os.path.join(os.environ.get("USERPROFILE", "C:\\"), "AppData", "Local"))
    PROGRAM_FILES = os.environ.get("PROGRAMFILES", "C:\\Program Files")
    PROGRAM_FILES_X86 = os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")

    # Browser executable paths - following legacy code
    BROWSER_PATHS = {
        "EDGE": os.path.join(PROGRAM_FILES_X86, "Microsoft", "Edge", "Application", "msedge.exe"),
    }
elif IS_MAC:
    # Browser executable paths for macOS
    BROWSER_PATHS = {
        "EDGE": "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    }
else:  # Linux
    # Browser executable paths for Linux
    BROWSER_PATHS = {
        "EDGE": "/usr/bin/microsoft-edge",
    }


class LaunchOptions:
    """Options for launching a browser."""

    def __init__(self, headless: bool = False, incognito: bool = False,
                private_mode: bool = False, args: Optional[List[str]] = None):
        """
        Initialize browser launch options.

        Args:
            headless: Whether to launch in headless mode
            incognito: Whether to launch in incognito mode (Chrome/Edge)
            private_mode: Whether to launch in private mode (Firefox/other browsers)
            args: Additional command-line arguments for the browser
        """
        self.headless = headless
        self.incognito = incognito
        self.private_mode = private_mode or incognito  # Alias for compatibility
        self.args = args or []


class AlternativeBrowserManager:
    """
    Manager for alternative browsers that don't have profile support.

    This class provides functionality to detect and launch browsers like
    Edge, Opera, Maxthon, etc., which don't have the same profile system
    as Chrome or Firefox.
    """

    def __init__(self, custom_paths: Optional[Dict[str, str]] = None):
        """
        Initialize the alternative browser manager.

        Args:
            custom_paths: Optional dictionary mapping browser names to custom paths
        """
        # Initialize browser paths dictionary
        self.browser_paths = {}

        # Initialize with empty values - exactly like legacy code
        for browser in ["edge", "opera", "brave", "maxthon", "midori", "midori_new", "netsurf", "min"]:
            self.browser_paths[browser] = ""

        # Update with defaults - following legacy code structure
        if IS_WINDOWS:
            defaults = {
                "edge": BROWSER_PATHS.get("EDGE", ""),
                "opera": os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera', 'launcher.exe'),
                "brave": os.path.join(LOCAL_APPDATA, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
                "maxthon": os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Maxthon', 'Maxthon.exe'),
                "midori": 'C:\\Program Files\\Midori Browser\\midori.exe',
                "midori_new": 'C:\\Program Files\\Midori Browser\\midori.exe',
                "netsurf": 'C:\\Program Files (x86)\\NetSurf\\NetSurf\\NetSurf.exe',
                "min": os.path.join(os.environ.get('LOCALAPPDATA', ''), 'min', 'min.exe')
            }
        elif IS_MAC:
            defaults = {
                "edge": BROWSER_PATHS.get("EDGE", ""),
                "opera": '/Applications/Opera.app/Contents/MacOS/Opera',
                "brave": '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
                "min": '/Applications/Min.app/Contents/MacOS/Min'
            }
        else:  # Linux
            defaults = {
                "edge": BROWSER_PATHS.get("EDGE", ""),
                "opera": '/usr/bin/opera',
                "brave": '/usr/bin/brave-browser',
                "midori": '/usr/bin/midori',
                "min": '/usr/bin/min'
            }

        # Update paths with defaults that exist
        for browser, path in defaults.items():
            if path and os.path.exists(path):
                self.browser_paths[browser] = path

        # Special case for user-specified paths - directly from legacy code
        if IS_WINDOWS:
            custom_paths = {
                "midori": "C:\\Users\\usef\\Desktop\\midori\\midori.exe",
                "opera": "C:\\Users\\usef\\AppData\\Local\\Programs\\Opera\\opera.exe"
            }

            # Only update if the paths exist
            for browser, path in custom_paths.items():
                if path and os.path.exists(path):
                    self.browser_paths[browser] = path
                    logger.info(f"Using custom path for {browser}: {path}")

        # Update with any additional custom paths
        if custom_paths:
            for browser, path in custom_paths.items():
                if path and os.path.exists(path):
                    self.browser_paths[browser] = path
                    logger.info(f"Using custom path for {browser}: {path}")

        # List of alternative browsers - exactly as in legacy code
        self.alt_browsers = [
            "edge", "opera", "brave", "maxthon", "midori", "midori_new",
            "netsurf", "min"
        ]

        logger.debug(f"Initialized AlternativeBrowserManager with paths: {self.browser_paths}")

    def list_available_browsers(self) -> List[str]:
        """
        List all available alternative browsers.

        Returns:
            List of available browser names
        """
        # Following legacy code
        available = []
        for browser in self.alt_browsers:
            path = self.browser_paths.get(browser)
            if path and os.path.exists(path):
                available.append(browser)
                logger.debug(f"Found available browser: {browser} at {path}")
            else:
                logger.debug(f"Browser not found: {browser}")

        return available

    def is_browser_available(self, browser_type: str) -> bool:
        """
        Check if a specific browser is available.

        Args:
            browser_type: Type of browser to check

        Returns:
            True if the browser is available, False otherwise
        """
        browser_type = browser_type.lower()
        path = self.browser_paths.get(browser_type)
        if not path:
            return False

        return os.path.exists(path)

    def get_browser_path(self, browser_type: str) -> Optional[str]:
        """
        Get the path to a browser executable.

        Args:
            browser_type: Name of the browser

        Returns:
            Path to the browser executable, or None if not found
        """
        return self.browser_paths.get(browser_type.lower())

    def launch_browser(self,
                      browser_type: str,
                      url: Optional[str] = None,
                      private_mode: bool = False,
                      headless: bool = False,
                      options: Optional[LaunchOptions] = None) -> None:
        """
        Launch an alternative browser.

        Args:
            browser_type: Type of browser to launch
            url: URL to open (optional)
            private_mode: Whether to launch in private/incognito mode
            headless: Whether to launch in headless mode
            options: Launch options (optional)

        Raises:
            FileNotFoundError: If the browser executable is not found
            ValueError: If the browser is not supported
        """
        browser_type = browser_type.lower()
        if not self.is_browser_available(browser_type):
            raise FileNotFoundError(f"Browser executable not found for {browser_type}")

        # Get browser path
        browser_path = self.browser_paths[browser_type]

        # Build command
        cmd = [browser_path]

        # Add private mode flag if requested
        if private_mode:
            if browser_type == 'edge':
                cmd.append('--inprivate')
            elif browser_type == 'opera':
                cmd.append('--private')
            elif browser_type == 'brave':
                cmd.append('--incognito')
            elif browser_type == 'maxthon':
                cmd.append('--private')
            elif browser_type == 'min':
                cmd.append('--private')

        # Add headless mode flag if requested
        if headless:
            if browser_type in ['edge', 'opera', 'brave']:
                cmd.append('--headless')

        # Add URL
        if url:
            # Make sure URL includes protocol
            if not url.startswith(('http://', 'https://', 'ftp://', 'file://')):
                url = f"https://{url}"
            cmd.append(url)

        # Launch browser
        logger.info(f"Launching {browser_type} with command: {' '.join(cmd)}")
        try:
            # Use subprocess.Popen to not block and return control immediately
            process = subprocess.Popen(cmd, start_new_session=True)
            logger.debug(f"Browser process started with PID: {process.pid}")
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
            raise
