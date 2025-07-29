"""
Custom UI components for the Browser Launcher.

This module provides custom PyQt6 widgets for the Browser Launcher.
"""

from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6.QtCore import Qt

from .styles import get_styles


class BrowserProfileButton(QPushButton):
    """Custom button for browser profiles with theming support."""

    def __init__(self, profile_name, display_name=None, email=None, parent=None):
        """
        Initialize the button with profile information.

        Args:
            profile_name: Internal profile name
            display_name: Display name to show on the button (optional)
            email: Email associated with the profile (optional)
            parent: Parent widget
        """
        super().__init__(parent)
        self.profile_name = profile_name
        self.setProperty("class", "profile-button")  # For stylesheet targeting

        # Set display text
        if display_name and display_name != profile_name:
            display_text = display_name
        else:
            display_text = profile_name

        # Add email if available, but keep it shorter
        if email:
            email_short = email
            if len(email) > 20:
                # Truncate long email addresses
                email_parts = email.split('@')
                if len(email_parts) == 2:
                    username, domain = email_parts
                    if len(username) > 12:
                        username = username[:10] + '...'
                    email_short = f"{username}@{domain}"
            display_text = f"{display_text}\n({email_short})"

        self.setText(display_text)
        # Reduce button height
        self.setMinimumHeight(40)
        self.setMaximumHeight(50)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


class BrowserButton(QPushButton):
    """Custom button for alternative browsers with theming support."""

    def __init__(self, browser_name, parent=None):
        """
        Initialize the button with browser information.

        Args:
            browser_name: Name of the browser
            parent: Parent widget
        """
        super().__init__(parent)
        self.browser_name = browser_name
        self.setProperty("class", "browser-button")  # For stylesheet targeting

        # Format browser name for display (capitalize)
        display_name = browser_name.capitalize()

        self.setText(display_name)
        # Reduce button height
        self.setMinimumHeight(40)
        self.setMaximumHeight(50)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


class UrlPresetButton(QPushButton):
    """Custom button for URL presets with theming support."""

    def __init__(self, name, url, parent=None):
        """
        Initialize the button with URL information.

        Args:
            name: Name of the URL preset
            url: URL to load when clicked
            parent: Parent widget
        """
        super().__init__(parent)
        self.name = name
        self.url = url
        self.setProperty("class", "preset-button")  # For stylesheet targeting

        self.setText(name)
        self.setMinimumWidth(70)
        self.setMaximumWidth(100)
        # Reduce preset button height
        self.setMinimumHeight(30)
        self.setMaximumHeight(35)


def update_component_styles(widget, theme_name):
    """
    Update the styles of components in a widget based on the theme.

    Args:
        widget: Widget containing components to update
        theme_name: Theme name ("light" or "dark")
    """
    styles = get_styles(theme_name)

    # Apply styles to all custom components
    widget.setStyleSheet(
        styles["profile_button"] +
        styles["url_preset_button"] +
        styles["browser_button"]
    )
