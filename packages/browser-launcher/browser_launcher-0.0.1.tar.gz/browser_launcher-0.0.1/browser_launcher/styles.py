"""
Styles for the Browser Launcher components.

This module provides the CSS styles for the Browser Launcher UI components.
"""

# Profile button styles
PROFILE_BUTTON_STYLE_DARK = """
QPushButton.profile-button {
    background-color: #2D3748;
    color: #FFC107;
    border: 1px solid #FFC107;
    border-radius: 4px;
    padding: 4px 8px;
    text-align: center;
    font-size: 12px;
    font-weight: bold;
}
QPushButton.profile-button:hover {
    background-color: #4A5568;
    color: #FFC107;
    border: 1px solid #FFD54F;
}
QPushButton.profile-button:pressed {
    background-color: #FFD600;
    color: #102040;
    border: 1px solid #FFD600;
}
"""

PROFILE_BUTTON_STYLE_LIGHT = """
QPushButton.profile-button {
    background-color: #E2E8F0;
    color: #2C5282;
    border: 1px solid #2C5282;
    border-radius: 4px;
    padding: 4px 8px;
    text-align: center;
    font-size: 12px;
    font-weight: bold;
}
QPushButton.profile-button:hover {
    background-color: #CBD5E0;
    color: #2C5282;
    border: 1px solid #4299E1;
}
QPushButton.profile-button:pressed {
    background-color: #4299E1;
    color: #FFFFFF;
    border: 1px solid #2C5282;
}
"""

# Browser button styles
BROWSER_BUTTON_STYLE_DARK = """
QPushButton.browser-button {
    background-color: #2D3748;
    color: #38B2AC;
    border: 1px solid #38B2AC;
    border-radius: 4px;
    padding: 4px 8px;
    text-align: center;
    font-size: 12px;
    font-weight: bold;
}
QPushButton.browser-button:hover {
    background-color: #4A5568;
    color: #38B2AC;
    border: 1px solid #4FD1C5;
}
QPushButton.browser-button:pressed {
    background-color: #38B2AC;
    color: #FFFFFF;
    border: 1px solid #38B2AC;
}
"""

BROWSER_BUTTON_STYLE_LIGHT = """
QPushButton.browser-button {
    background-color: #E2E8F0;
    color: #2B6CB0;
    border: 1px solid #2B6CB0;
    border-radius: 4px;
    padding: 4px 8px;
    text-align: center;
    font-size: 12px;
    font-weight: bold;
}
QPushButton.browser-button:hover {
    background-color: #CBD5E0;
    color: #2B6CB0;
    border: 1px solid #3182CE;
}
QPushButton.browser-button:pressed {
    background-color: #3182CE;
    color: #FFFFFF;
    border: 1px solid #2B6CB0;
}
"""

# URL preset button styles
URL_PRESET_BUTTON_STYLE_DARK = """
QPushButton.preset-button {
    background-color: #2D3748;
    color: #FFC107;
    border: 1px solid #FFC107;
    border-radius: 3px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: bold;
}
QPushButton.preset-button:hover {
    background-color: #4A5568;
    color: #FFC107;
    border: 1px solid #FFD54F;
}
QPushButton.preset-button:pressed {
    background-color: #FFD600;
    color: #102040;
    border: 1px solid #FFD600;
}
"""

URL_PRESET_BUTTON_STYLE_LIGHT = """
QPushButton.preset-button {
    background-color: #E2E8F0;
    color: #2C5282;
    border: 1px solid #2C5282;
    border-radius: 3px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: bold;
}
QPushButton.preset-button:hover {
    background-color: #CBD5E0;
    color: #2C5282;
    border: 1px solid #4299E1;
}
QPushButton.preset-button:pressed {
    background-color: #4299E1;
    color: #FFFFFF;
    border: 1px solid #2C5282;
}
"""

def get_styles(theme_name):
    """
    Get the appropriate styles for the given theme.

    Args:
        theme_name: The name of the theme ("light" or "dark")

    Returns:
        Dictionary containing style strings for different components
    """
    if theme_name == "dark":
        return {
            "profile_button": PROFILE_BUTTON_STYLE_DARK,
            "url_preset_button": URL_PRESET_BUTTON_STYLE_DARK,
            "browser_button": BROWSER_BUTTON_STYLE_DARK
        }
    else:  # light theme
        return {
            "profile_button": PROFILE_BUTTON_STYLE_LIGHT,
            "url_preset_button": URL_PRESET_BUTTON_STYLE_LIGHT,
            "browser_button": BROWSER_BUTTON_STYLE_LIGHT
        }
