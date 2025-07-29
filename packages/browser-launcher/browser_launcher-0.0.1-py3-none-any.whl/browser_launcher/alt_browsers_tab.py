"""
Alternative browsers tab for the Browser Launcher.

This module provides a tab for displaying and launching alternative browsers.
"""

import logging
from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGridLayout, QLabel
)

from .components import BrowserButton

# Initialize logger
logger = logging.getLogger(__name__)

class AltBrowsersTab(QWidget):
    """Tab for displaying and launching alternative browsers."""

    def __init__(self, alt_browser_manager, parent=None):
        """
        Initialize the alternative browsers tab.

        Args:
            alt_browser_manager: Alternative browser manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.alt_browser_manager = alt_browser_manager
        self.parent_launcher = parent

        # Set up UI
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins

        # Create a scrollable area for browsers
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        self.grid_layout.setSpacing(5)  # Reduce spacing between buttons

        # Get alternative browsers - only those that are actually available
        try:
            browsers = self.alt_browser_manager.list_available_browsers()
            logger.info(f"Found {len(browsers)} available alternative browsers")

            if browsers:
                # Create a button for each browser
                row, col = 0, 0
                max_cols = 4  # Increase number of columns in the grid

                for browser in browsers:
                    # Get the browser path for logging
                    browser_path = self.alt_browser_manager.get_browser_path(browser)

                    # Log browser details for debugging
                    logger.debug(f"Alternative browser: {browser} at {browser_path}")

                    # Create browser button
                    browser_button = BrowserButton(browser_name=browser)

                    # Use a helper function to create a proper closure
                    self._connect_browser_button(browser_button, browser)

                    # Add to grid
                    self.grid_layout.addWidget(browser_button, row, col)

                    # Update grid position
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
            else:
                # No browsers found
                logger.warning("No alternative browsers found")
                no_browsers_label = QLabel("No alternative browsers found. Install other browsers to see them here.")
                no_browsers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.grid_layout.addWidget(no_browsers_label, 0, 0)

        except Exception as e:
            # Handle errors
            logger.error(f"Error loading alternative browsers: {e}", exc_info=True)
            error_label = QLabel(f"Error loading browsers: {str(e)}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(error_label, 0, 0)

        # Finish setting up the scroll area
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

    def _connect_browser_button(self, button, browser_name):
        """
        Helper method to connect button click to handler with correct browser name.

        Args:
            button: Browser button to connect
            browser_name: Name of the browser for this button
        """
        button.clicked.connect(lambda checked, name=browser_name:
                              self.parent_launcher.on_alt_browser_button_clicked(name))

    def update_theme(self, theme_name):
        """
        Update the theme of the tab.

        Args:
            theme_name: Name of the theme ("light" or "dark")
        """
        # Update style based on theme
        # Currently handled by parent
        pass
