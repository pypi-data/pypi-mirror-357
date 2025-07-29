# browser_launcher

A utility for launching browsers (Chrome, Firefox, and alternatives) with specific profiles, URLs, and incognito/private mode from Python or the command line.

## Features
- Launch Chrome or Firefox with a specific user profile and URL
- Support for incognito/private mode
- List available browser profiles
- List available browsers (including alternatives like Edge, Opera, Brave, etc.)
- Simple command-line interface (CLI)
- Usable as a Python library

## Installation

```bash
pip install browser_launcher
```

Or install from source:

```bash
git clone https://github.com/mexyusef/browser_launcher.git
cd browser_launcher
pip install .
```

## Usage

### Command Line

List Chrome profiles:
```bash
browser-launcher list-profiles --browser chrome
```

List Firefox profiles:
```bash
browser-launcher list-profiles --browser firefox
```

List all available browsers:
```bash
browser-launcher list-browsers
```

Launch Firefox with a specific profile and URL (incognito):
```bash
browser-launcher launch --browser firefox --profile myprofile --url https://gmail.com --incognito
```

Launch Chrome with a specific profile and URL:
```bash
browser-launcher launch --browser chrome --profile "Profile 1" --url https://example.com
```

### Python Library

```python
from browser_launcher.profile_manager import BrowserProfileManager, LaunchOptions

mgr = BrowserProfileManager()
options = LaunchOptions(incognito=True)
mgr.launch_browser(
    browser_type="firefox",
    profile="myprofile",
    url="https://gmail.com",
    options=options
)
```

## License

MIT License. See LICENSE file for details.
