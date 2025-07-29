"""
Browser profile management for ZTray Modular.

This module provides functionality for detecting, listing, and managing browser profiles,
particularly focusing on Chrome and Firefox.
"""

import os
import sys
import platform
import logging
import subprocess
import re
import json
import configparser
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set, Union
import shutil
from dataclasses import dataclass

# Initialize logger
logger = logging.getLogger(__name__)

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

# Default directories
PROGRAM_FILES = os.environ.get("ProgramFiles", "C:\\Program Files")
PROGRAM_FILES_X86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
LOCAL_APP_DATA = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
APP_DATA = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))

# Browser user data directories
BROWSER_USER_DATA_DIRS = {
    "CHROME": {
        "Windows": os.path.join(LOCAL_APP_DATA, "Google", "Chrome", "User Data"),
        "Darwin": os.path.expanduser("~/Library/Application Support/Google/Chrome"),
        "Linux": os.path.expanduser("~/.config/google-chrome")
    },
    "FIREFOX": {
        "Windows": os.path.join(APP_DATA, "Mozilla", "Firefox"),
        "Darwin": os.path.expanduser("~/Library/Application Support/Firefox"),
        "Linux": os.path.expanduser("~/.mozilla/firefox")
    },
}

# Email mappings
CHROME_PROFILE_TO_EMAIL = {
    "Default": "primary@email.com",
    "Profile 1": "work@email.com",
    "Profile 2": "personal@email.com",
}


class BrowserProfile:
    """
    Represents a browser profile.

    Attributes:
        name: The name of the profile
        path: The path to the profile directory
        browser_type: The type of browser this profile belongs to
        display_name: Human-readable display name for the profile
        email: Email address associated with the profile, if any
        last_used: Timestamp when the profile was last used, if known
    """

    def __init__(self, name: str, path: str, browser_type: str,
                display_name: Optional[str] = None,
                email: Optional[str] = None,
                last_used: Optional[str] = None):
        """
        Initialize a browser profile.

        Args:
            name: The name of the profile
            path: The path to the profile directory
            browser_type: The type of browser this profile belongs to
            display_name: Human-readable display name (defaults to name)
            email: Email address associated with the profile
            last_used: Timestamp when the profile was last used
        """
        self.name = name
        self.path = path
        self.browser_type = browser_type
        self.display_name = display_name or name
        self.email = email
        self.last_used = last_used

    def to_dict(self) -> Dict[str, str]:
        """
        Convert the profile to a dictionary.

        Returns:
            Dictionary representation of the profile
        """
        return {
            "name": self.name,
            "path": self.path,
            "browser_type": self.browser_type,
            "display_name": self.display_name,
            "email": self.email,
            "last_used": self.last_used
        }


class LaunchOptions:
    """
    Launch options for a browser.

    Attributes:
        headless (bool): Whether to run in headless mode
        incognito (bool): Whether to run in incognito/private mode
        args (List[str]): Additional command-line arguments
    """

    def __init__(self,
                headless: bool = False,
                incognito: bool = False,
                private_mode: bool = False,
                args: Optional[List[str]] = None):
        """
        Initialize launch options.

        Args:
            headless: Whether to run in headless mode
            incognito: Whether to run in incognito/private mode
            private_mode: Alias for incognito (for backward compatibility)
            args: Additional command-line arguments
        """
        self.headless = headless
        self.incognito = incognito or private_mode
        self.args = args or []


class BrowserProfileManager:
    """
    Manager for browser profiles across different browsers.

    This class provides functionality to detect, list, and launch browsers with
    specific profiles. It supports Chrome, Firefox, and other browsers depending
    on the platform.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the browser profile manager.

        Args:
            config: Optional configuration dictionary.
        """
        # Initialize with default configuration
        self.config = config or {}

        # Set up paths and mappings with fallbacks to constants
        user_data_dirs = self.config.get('user_data_dirs', {})
        self.chrome_profiles_path = user_data_dirs.get('chrome', BROWSER_USER_DATA_DIRS.get('CHROME', {}).get('Windows' if IS_WINDOWS else 'Darwin' if IS_MAC else 'Linux', ''))
        self.firefox_profiles_path = user_data_dirs.get('firefox', BROWSER_USER_DATA_DIRS.get('FIREFOX', {}).get('Windows' if IS_WINDOWS else 'Darwin' if IS_MAC else 'Linux', ''))
        self.profile_to_email = self.config.get('email_mappings', CHROME_PROFILE_TO_EMAIL)

        # Log what we're using
        if self.chrome_profiles_path:
            logger.debug(f"Using Chrome profiles path: {self.chrome_profiles_path}")
        else:
            logger.warning("Chrome profiles path is not set")

        if self.firefox_profiles_path:
            logger.debug(f"Using Firefox profiles path: {self.firefox_profiles_path}")
        else:
            logger.warning("Firefox profiles path is not set")

        # Firefox profiles mapping from name to path
        self.firefox_profiles: Dict[str, str] = {}

        # Chrome profiles
        self.chrome_profiles: List[BrowserProfile] = []

        # Initialize
        self._load_firefox_profiles()
        self._load_chrome_profiles()

        logger.debug("BrowserProfileManager initialized")

    def _load_firefox_profiles(self) -> None:
        """
        Load Firefox profiles from profiles.ini file.

        This method parses the Firefox profiles.ini file to find all available profiles.
        """
        if not self.firefox_profiles_path or not os.path.exists(self.firefox_profiles_path):
            logger.warning(f"Firefox profiles path not found: {self.firefox_profiles_path}")
            return

        profiles_ini_path = Path(self.firefox_profiles_path)
        if profiles_ini_path.name != 'profiles.ini':
            profiles_ini_path = profiles_ini_path / 'profiles.ini'

        if not profiles_ini_path.exists():
            logger.warning(f"Firefox profiles.ini not found: {profiles_ini_path}")
            return

        try:
            logger.debug(f"Loading Firefox profiles from: {profiles_ini_path}")
            # Use configparser to read the ini file
            config = configparser.ConfigParser()
            config.read(profiles_ini_path)

            # Log the sections found in the ini file
            logger.debug(f"Found {len(config.sections())} sections in profiles.ini: {', '.join(config.sections())}")

            # Clear existing profiles
            self.firefox_profiles = {}

            # Loop through sections to find profiles
            for section in config.sections():
                if section.startswith('Profile'):
                    if 'Name' in config[section] and 'Path' in config[section]:
                        name = config[section]['Name']
                        path_value = config[section]['Path']

                        # Handle relative vs absolute paths
                        if 'IsRelative' in config[section] and config[section].getboolean('IsRelative'):
                            # Relative path - join with parent directory of profiles.ini
                            path = str(profiles_ini_path.parent / path_value)
                        else:
                            # Absolute path
                            path = path_value

                        self.firefox_profiles[name] = path
                        logger.debug(f"Found Firefox profile: '{name}' at {path}")

            logger.info(f"Loaded {len(self.firefox_profiles)} Firefox profiles: {', '.join(self.firefox_profiles.keys())}")

        except Exception as e:
            logger.error(f"Error loading Firefox profiles: {e}", exc_info=True)
            self.firefox_profiles = {}

    def _load_chrome_profiles(self) -> None:
        """
        Load Chrome profiles from the User Data directory.

        This method scans the Chrome User Data directory to find profiles.
        """
        self.chrome_profiles = []

        if not self.chrome_profiles_path or not os.path.exists(self.chrome_profiles_path):
            logger.warning(f"Chrome profiles path not found: {self.chrome_profiles_path}")
            return

        try:
            user_data_dir = Path(self.chrome_profiles_path)

            # Find all directories that are profiles (either Default or Profile X)
            profile_paths = [
                d for d in user_data_dir.iterdir()
                if d.is_dir() and (d.name == 'Default' or d.name.startswith('Profile '))
            ]

            for profile_path in profile_paths:
                # Parse profile name
                profile_name = profile_path.name

                # Try to get email from preferences file
                email = self._get_chrome_profile_email(profile_path)

                # If not found, try to get from mapping
                if not email and profile_name in self.profile_to_email:
                    email = self.profile_to_email[profile_name]

                # Create BrowserProfile object with the correct format
                profile = BrowserProfile(
                    name=profile_name,
                    path=str(profile_path),
                    browser_type='chrome',
                    display_name=profile_name,
                    email=email
                )

                self.chrome_profiles.append(profile)
                logger.debug(f"Found Chrome profile: {profile_name} at {profile_path}")

            logger.info(f"Loaded {len(self.chrome_profiles)} Chrome profiles")

        except Exception as e:
            logger.error(f"Error loading Chrome profiles: {e}")
            self.chrome_profiles = []

    def _get_chrome_profile_email(self, profile_path: Path) -> Optional[str]:
        """
        Extract the email associated with a Chrome profile.

        Args:
            profile_path: Path to the Chrome profile directory

        Returns:
            The email address if found, or None
        """
        try:
            preferences_path = profile_path / 'Preferences'
            if not preferences_path.exists():
                return None

            with open(preferences_path, 'r', encoding='utf-8') as f:
                preferences = json.load(f)

            # Try to get the email from account info
            if 'account_info' in preferences:
                for account in preferences['account_info']:
                    if 'email' in account:
                        return account['email']

            # Try to get from profile info
            if 'profile' in preferences and 'name' in preferences['profile']:
                name = preferences['profile']['name']
                # If name looks like an email
                if '@' in name and '.' in name.split('@')[1]:
                    return name

            return None

        except Exception as e:
            logger.debug(f"Error getting Chrome profile email: {e}")
            return None

    def list_chrome_profiles(self) -> List[BrowserProfile]:
        """
        List all Chrome profiles.

        Returns:
            List of Chrome profiles
        """
        try:
            # Simply return our already loaded profiles
            return self.chrome_profiles
        except Exception as e:
            logger.error(f"Error listing Chrome profiles: {e}")
            return []

    def list_firefox_profiles(self) -> List[BrowserProfile]:
        """
        List all Firefox profiles.

        Returns:
            List of Firefox profiles
        """
        try:
            result = []
            for name, path in self.firefox_profiles.items():
                profile = BrowserProfile(
                    name=name,
                    path=path,
                    browser_type="firefox",
                    display_name=name
                )
                result.append(profile)
            return result
        except Exception as e:
            logger.error(f"Error listing Firefox profiles: {e}")
            return []

    def resolve_url(self, url: str) -> str:
        """
        Resolve a URL or shorthand to a full URL.

        Args:
            url: URL or shorthand to resolve

        Returns:
            Full URL with protocol
        """
        # Load bookmarks from user profile directory
        try:
            user_profile = os.environ.get("USERPROFILE" if os.name == "nt" else "HOME", "")
            bookmarks_path = Path(user_profile) / "bookmarks.json"

            if bookmarks_path.exists():
                with open(bookmarks_path, 'r', encoding='utf-8') as f:
                    url_mappings = json.load(f)
                    # If it's a shorthand, resolve it
                    if url in url_mappings:
                        return url_mappings[url]
        except Exception as e:
            logger.error(f"Error resolving URL from bookmarks: {e}")

        # If not in bookmarks or bookmarks not available, ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url

    def launch_browser(self,
                      browser_type: str,
                      profile: Optional[str] = None,
                      url: Optional[str] = None,
                      options: Optional[LaunchOptions] = None) -> None:
        """
        Launch a browser with the specified profile and URL.

        Args:
            browser_type: Type of browser to launch
            profile: Profile name or path
            url: URL to open
            options: Launch options
        """
        if options is None:
            options = LaunchOptions()

        # Get browser executable
        browser_path = self._get_browser_executable(browser_type)
        if not browser_path:
            raise ValueError(f"Browser executable not found for {browser_type}")

        # Build command based on browser type
        if browser_type.lower() in ["chrome", "chromium", "edge", "brave"]:
            cmd = self._build_chrome_like_command(
                browser_type=browser_type,
                browser_path=browser_path,
                profile=profile,
                url=url,
                options=options
            )
        elif browser_type.lower() == "firefox":
            cmd = self._build_firefox_command(
                browser_path=browser_path,
                profile=profile,
                url=url,
                options=options
            )
        else:
            # Simple launch with URL
            cmd = [browser_path]
            if url:
                cmd.append(url)

        # Log the command
        logger.info(f"Launching browser with command: {' '.join(cmd)}")

        # Execute
        try:
            subprocess.Popen(cmd, shell=False)
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
            raise RuntimeError(f"Failed to launch browser: {e}")

    def _get_browser_executable(self, browser_type: str) -> Optional[str]:
        """
        Get the path to the browser executable.

        Args:
            browser_type: Type of browser

        Returns:
            Path to the browser executable, or None if not found
        """
        # Default paths based on platform and browser type
        browser_paths = {
            "chrome": {
                "Windows": os.path.join(PROGRAM_FILES, "Google", "Chrome", "Application", "chrome.exe"),
                "Darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "Linux": "/usr/bin/google-chrome"
            },
            "firefox": {
                "Windows": os.path.join(PROGRAM_FILES, "Mozilla Firefox", "firefox.exe"),
                "Darwin": "/Applications/Firefox.app/Contents/MacOS/firefox",
                "Linux": "/usr/bin/firefox"
            },
            "edge": {
                "Windows": os.path.join(PROGRAM_FILES_X86, "Microsoft", "Edge", "Application", "msedge.exe"),
                "Darwin": "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                "Linux": "/usr/bin/microsoft-edge"
            }
        }

        # Try to get from config
        browser_key = browser_type.lower()
        platform_key = "Windows" if IS_WINDOWS else "Darwin" if IS_MAC else "Linux"

        # Try to get from default paths
        if browser_key in browser_paths and platform_key in browser_paths[browser_key]:
            path = browser_paths[browser_key][platform_key]
            if os.path.exists(path):
                return path

        # Try to find in PATH
        try:
            if IS_WINDOWS:
                # On Windows, append .exe if needed
                exe_name = f"{browser_key}.exe"
                for path in os.environ.get("PATH", "").split(os.pathsep):
                    exe_path = os.path.join(path, exe_name)
                    if os.path.exists(exe_path):
                        return exe_path
            else:
                # On Unix-like systems, check if executable exists in PATH
                if shutil.which(browser_key):
                    return browser_key
        except Exception as e:
            logger.debug(f"Error finding browser in PATH: {e}")

        return None

    def _build_chrome_like_command(self,
                             browser_type: str,
                             browser_path: str,
                             profile: Optional[str],
                             url: Optional[str],
                             options: LaunchOptions) -> List[str]:
        """
        Build command for Chrome-like browsers.

        Args:
            browser_type: Type of browser
            browser_path: Path to browser executable
            profile: Profile name or path
            url: URL to open
            options: Launch options

        Returns:
            Command as a list of strings
        """
        cmd = [browser_path]

        # Add profile path if specified
        if profile:
            # Check if it's a profile name or path
            if os.path.isdir(profile):
                # It's a path
                cmd.extend(["--user-data-dir=" + profile])
            else:
                # It's a name, find the profile
                for chrome_profile in self.chrome_profiles:
                    if chrome_profile.name == profile:
                        # Found the profile, use its path
                        cmd.extend(["--user-data-dir=" + os.path.dirname(chrome_profile.path)])
                        cmd.extend(["--profile-directory=" + os.path.basename(chrome_profile.path)])
                        break
                else:
                    # Profile not found, use default User Data dir with profile name
                    cmd.extend(["--user-data-dir=" + self.chrome_profiles_path])
                    cmd.extend(["--profile-directory=" + profile])

        # Add incognito mode if specified
        if options.incognito:
            cmd.append("--incognito")

        # Add headless mode if specified
        if options.headless:
            cmd.append("--headless")

        # Add additional arguments
        if options.args:
            cmd.extend(options.args)

        # Add URL if specified
        if url:
            cmd.append(url)

        return cmd

    def _build_firefox_command(self,
                         browser_path: str,
                         profile: Optional[str],
                         url: Optional[str],
                         options: LaunchOptions) -> List[str]:
        """
        Build command for Firefox.

        Args:
            browser_path: Path to browser executable
            profile: Profile name or path
            url: URL to open
            options: Launch options

        Returns:
            Command as a list of strings
        """
        cmd = [browser_path]

        # Add profile if specified
        if profile:
            # Check if it's a profile name or path
            if os.path.isdir(profile):
                # It's a path
                cmd.extend(["-P", os.path.basename(profile)])
            else:
                # It's a name
                cmd.extend(["-P", profile])

        # Add private mode if specified
        if options.incognito:
            cmd.append("--private-window")

        # Add headless mode if specified
        if options.headless:
            cmd.append("--headless")

        # Add additional arguments
        if options.args:
            cmd.extend(options.args)

        # Add URL if specified
        if url:
            cmd.append(url)

        return cmd

    def get_profile(self, browser_type: str, profile_name: str) -> Optional[BrowserProfile]:
        """
        Get a profile by browser type and name.

        Args:
            browser_type: Type of browser
            profile_name: Name of the profile

        Returns:
            BrowserProfile object if found, None otherwise
        """
        if browser_type.lower() == "chrome":
            for profile in self.chrome_profiles:
                if profile.name == profile_name:
                    return profile
        elif browser_type.lower() == "firefox":
            if profile_name in self.firefox_profiles:
                return BrowserProfile(
                    name=profile_name,
                    path=self.firefox_profiles[profile_name],
                    browser_type="firefox",
                    display_name=profile_name
                )
        return None
