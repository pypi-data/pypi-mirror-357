"""
Main browser launcher tab for ZTray Modular.

This module provides the main tab for the Browser Launcher functionality.
"""

import os
import sys
import logging
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit,
    QPushButton, QCheckBox, QScrollArea, QGridLayout, QGroupBox, QMessageBox,
    QSizePolicy, QComboBox
)
from PyQt6.QtGui import QIcon

# Initialize logger
logger = logging.getLogger(__name__)

# Import our implementation for browsers
from .alternative_browser_manager import AlternativeBrowserManager, LaunchOptions
# Import new profile manager implementation
from .profile_manager import BrowserProfileManager, BrowserProfile

from .chrome_tab import ChromeProfilesTab
from .firefox_tab import FirefoxProfilesTab
from .alt_browsers_tab import AltBrowsersTab
from .components import UrlPresetButton, update_component_styles


class BrowserLauncherTab(QWidget):
    """Main tab for the Browser Launcher within ZTray Modular."""

    def __init__(self, parent=None):
        """
        Initialize the Browser Launcher tab.

        Args:
            parent: Parent widget
        """
        # Get the QWidget window if parent is MainWindow
        if parent and hasattr(parent, 'window'):
            parent_widget = parent.window
        else:
            parent_widget = parent

        super().__init__(parent_widget)

        # Initialize managers
        try:
            logger.info("Initializing BrowserProfileManager")
            self.profile_manager = BrowserProfileManager()

            # Use our internal AlternativeBrowserManager implementation
            self.alt_browser_manager = AlternativeBrowserManager()

            # Log profile counts for debugging
            chrome_profiles = self.profile_manager.list_chrome_profiles()
            firefox_profiles = self.profile_manager.list_firefox_profiles()
            logger.info(f"Found {len(chrome_profiles)} Chrome profiles and {len(firefox_profiles)} Firefox profiles")

            # Log alternative browser counts
            alt_browsers = self.alt_browser_manager.list_available_browsers()
            logger.info(f"Found {len(alt_browsers)} alternative browsers: {', '.join(alt_browsers)}")

            if not chrome_profiles and not firefox_profiles:
                logger.warning("No browser profiles detected!")
        except Exception as e:
            logger.error(f"Error initializing browser managers: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize browser managers: {e}")

        # Store the MainWindow parent for reference
        self.main_window = parent

        # Set up UI
        self.setup_ui()

        # Set default theme
        self.update_theme("light")

    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)  # Reduce outer margins
        main_layout.setSpacing(5)  # Reduce spacing between sections

        # URL input area
        url_group = QGroupBox("URL")
        url_group.setMaximumHeight(120)  # Limit the height of the URL section
        url_layout = QVBoxLayout(url_group)
        url_layout.setContentsMargins(5, 5, 5, 5)  # Reduce inner margins
        url_layout.setSpacing(3)  # Reduce spacing

        # URL input field with label
        url_input_layout = QHBoxLayout()
        url_input_layout.setSpacing(3)  # Reduce spacing
        self.url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL or select a preset (e.g., google.com)")
        url_input_layout.addWidget(self.url_label)
        url_input_layout.addWidget(self.url_input)

        # Private mode checkbox
        self.private_mode_checkbox = QCheckBox("🕵️‍♂️")
        self.private_mode_checkbox.setToolTip("Private/Incognito mode")
        url_input_layout.addWidget(self.private_mode_checkbox)

        url_layout.addLayout(url_input_layout)

        # URL presets
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(3)  # Reduce spacing
        preset_label = QLabel("Presets:")
        preset_layout.addWidget(preset_label)

        # Add preset combobox instead of buttons
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(150)  # Set a minimum width for readability
        self.preset_combo.addItem("Select a preset URL...", "")
        self.preset_combo.currentIndexChanged.connect(self.on_preset_selected)

        try:
            # Load bookmarks from user profile directory
            user_profile = os.environ.get("USERPROFILE" if os.name == "nt" else "HOME", "")
            bookmarks_path = Path(user_profile) / "bookmarks.json"

            if bookmarks_path.exists():
                with open(bookmarks_path, 'r', encoding='utf-8') as f:
                    url_mappings = json.load(f)
                    # Add each bookmark to the combobox with name as display text and URL as data
                    for name, url in url_mappings.items():
                        display_text = f"{name} ({url})"
                        self.preset_combo.addItem(display_text, url)

                    # Log URL mappings
                    logger.debug(f"URL mappings from {bookmarks_path}: {url_mappings}")
            else:
                logger.warning(f"Bookmarks file not found at {bookmarks_path}")
                # Add a disabled item to indicate no bookmarks
                self.preset_combo.addItem("No bookmarks found")
                self.preset_combo.setEnabled(False)
        except Exception as e:
            logger.error(f"Error creating URL presets: {e}")
            # Add a disabled item to indicate error
            self.preset_combo.addItem("URL presets not available")
            self.preset_combo.setEnabled(False)

        preset_layout.addWidget(self.preset_combo)
        preset_layout.addStretch()
        url_layout.addLayout(preset_layout)

        main_layout.addWidget(url_group)

        # Browser tabs
        self.browser_tabs = QTabWidget()

        # Add browser type tabs
        self.chrome_tab = ChromeProfilesTab(self.profile_manager, self)
        self.firefox_tab = FirefoxProfilesTab(self.profile_manager, self)
        self.alt_browsers_tab = AltBrowsersTab(self.alt_browser_manager, self)

        self.browser_tabs.addTab(self.chrome_tab, "Chrome")
        self.browser_tabs.addTab(self.firefox_tab, "Firefox")
        self.browser_tabs.addTab(self.alt_browsers_tab, "Other Browsers")

        main_layout.addWidget(self.browser_tabs)

    def on_preset_selected(self, index=None):
        """Handle preset selection from the combobox."""
        if index == 0:  # Skip the "Select a preset URL..." option
            return

        # Get the URL data directly from the combobox's itemData role
        selected_url = self.preset_combo.currentData()
        if selected_url:
            self.url_input.setText(selected_url)

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

    def on_profile_button_clicked(self, browser_type: str, profile_name: str):
        """
        Handle profile button click for Chrome and Firefox.

        Args:
            browser_type: Type of browser ("chrome" or "firefox")
            profile_name: Name of the profile to launch
        """
        url = self.url_input.text().strip()
        private_mode = self.private_mode_checkbox.isChecked()

        if not url:
            # If URL is empty, show a message
            QMessageBox.warning(
                self,
                "Missing URL",
                "Please enter a URL or select a preset before launching a browser."
            )
            return

        try:
            # Launch browser with profile
            options = LaunchOptions(incognito=private_mode)

            logger.info(f"Launching {browser_type} with profile '{profile_name}'" +
                  (f" in private mode" if private_mode else "") +
                  f" at URL: {url}")

            # Resolve URL shortcuts
            resolved_url = self.resolve_url(url)

            self.profile_manager.launch_browser(
                browser_type=browser_type,
                profile=profile_name,
                url=resolved_url,
                options=options
            )

            if hasattr(self.window(), 'statusBar'):
                self.window().statusBar().showMessage(
                    f"Launched {browser_type} with profile '{profile_name}'", 3000
                )

        except Exception as e:
            logger.error(f"Error launching browser: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Launch Error",
                f"Error launching {browser_type} with profile '{profile_name}':\n\n{str(e)}"
            )

    def on_alt_browser_button_clicked(self, browser_type: str):
        """
        Handle button click for alternative browsers.

        Args:
            browser_type: Type of browser to launch
        """
        url = self.url_input.text().strip()
        private_mode = self.private_mode_checkbox.isChecked()

        if not url:
            # If URL is empty, show a message
            QMessageBox.warning(
                self,
                "Missing URL",
                "Please enter a URL or select a preset before launching a browser."
            )
            return

        try:
            # Launch alternative browser
            logger.info(f"Launching {browser_type}" +
                  (f" in private mode" if private_mode else "") +
                  f" at URL: {url}")

            # Resolve URL shortcuts
            resolved_url = self.resolve_url(url)

            # Use our internal implementation
            self.alt_browser_manager.launch_browser(
                browser_type=browser_type,
                url=resolved_url,
                private_mode=private_mode
            )

            if hasattr(self.window(), 'statusBar'):
                self.window().statusBar().showMessage(f"Launched {browser_type}", 3000)

        except Exception as e:
            logger.error(f"Error launching browser: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Launch Error",
                f"Error launching {browser_type}:\n\n{str(e)}"
            )

    def update_theme(self, theme_name):
        """
        Update the theme of all components.

        Args:
            theme_name: Name of the theme ("light" or "dark")
        """
        # Update the styles of all components
        update_component_styles(self, theme_name)
