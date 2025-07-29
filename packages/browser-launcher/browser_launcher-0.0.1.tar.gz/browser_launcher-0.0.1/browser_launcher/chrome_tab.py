"""
Chrome profiles tab for the Browser Launcher.

This module provides a tab for displaying and launching Chrome profiles.
"""

import logging
from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGridLayout, QLabel
)

from .components import BrowserProfileButton

# Initialize logger
logger = logging.getLogger(__name__)

class ChromeProfilesTab(QWidget):
    """Tab for displaying and launching Chrome profiles."""

    def __init__(self, profile_manager, parent=None):
        """
        Initialize the Chrome profiles tab.

        Args:
            profile_manager: Browser profile manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.parent_launcher = parent

        # Set up UI
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins

        # Create a scrollable area for profiles
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        self.grid_layout.setSpacing(5)  # Reduce spacing between buttons

        # Get Chrome profiles
        try:
            chrome_profiles = self.profile_manager.list_chrome_profiles()
            logger.info(f"Found {len(chrome_profiles)} Chrome profiles")

            if chrome_profiles:
                # Create a button for each profile
                row, col = 0, 0
                max_cols = 4  # Increase number of columns in the grid

                for profile in chrome_profiles:
                    # Log profile details for debugging
                    logger.debug(f"Chrome profile: {profile.name} ({profile.display_name}), email: {profile.email}")

                    # Create profile button
                    profile_button = BrowserProfileButton(
                        profile_name=profile.name,
                        display_name=profile.display_name,
                        email=profile.email
                    )

                    # Use a helper function to create a proper closure
                    self._connect_profile_button(profile_button, profile.name)

                    # Add to grid
                    self.grid_layout.addWidget(profile_button, row, col)

                    # Update grid position
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
            else:
                # No profiles found
                logger.warning("No Chrome profiles found")
                no_profiles_label = QLabel("No profiles found. Make sure Chrome is installed and has profiles set up.")
                no_profiles_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.grid_layout.addWidget(no_profiles_label, 0, 0)

        except Exception as e:
            # Handle errors
            logger.error(f"Error loading Chrome profiles: {e}", exc_info=True)
            error_label = QLabel(f"Error loading profiles: {str(e)}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(error_label, 0, 0)

        # Finish setting up the scroll area
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

    def _connect_profile_button(self, button, profile_name):
        """
        Helper method to connect button click to handler with correct profile name.

        Args:
            button: Profile button to connect
            profile_name: Name of the profile for this button
        """
        button.clicked.connect(lambda checked, name=profile_name:
                              self.parent_launcher.on_profile_button_clicked("chrome", name))

    def update_theme(self, theme_name):
        """
        Update the theme of the tab.

        Args:
            theme_name: Name of the theme ("light" or "dark")
        """
        # Update style based on theme
        # Currently handled by parent
        pass
