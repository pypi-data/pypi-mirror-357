import argparse
import sys
from browser_launcher.profile_manager import BrowserProfileManager, LaunchOptions
from browser_launcher.alternative_browser_manager import AlternativeBrowserManager

ALL_BROWSERS = [
    "chrome", "firefox", "edge", "opera", "brave", "maxthon", "midori", "midori_new", "netsurf", "min"
]
PROFILE_BROWSERS = ["chrome", "firefox"]

def main():
    parser = argparse.ArgumentParser(description="Browser Launcher CLI")
    subparsers = parser.add_subparsers(dest="command")

    # List profiles
    list_profiles = subparsers.add_parser("list-profiles", help="List browser profiles")
    list_profiles.add_argument("--browser", required=True, choices=["chrome", "firefox"], help="Browser type")

    # List browsers (including alternatives)
    list_browsers = subparsers.add_parser("list-browsers", help="List all available browsers (including alternatives)")

    # Launch browser
    launch = subparsers.add_parser("launch", help="Launch a browser with a specific profile and URL")
    launch.add_argument("--browser", required=True, choices=ALL_BROWSERS, help="Browser type")
    launch.add_argument("--profile", help="Profile name or path (required for chrome/firefox)")
    launch.add_argument("--url", required=True, help="URL to open")
    launch.add_argument("--incognito", action="store_true", help="Incognito/private mode")

    args = parser.parse_args()

    if args.command == "list-profiles":
        mgr = BrowserProfileManager()
        if args.browser == "chrome":
            profiles = mgr.list_chrome_profiles()
        else:
            profiles = mgr.list_firefox_profiles()
        if not profiles:
            print(f"No profiles found for {args.browser}.")
        else:
            for p in profiles:
                print(f"Name: {p.name} | Path: {p.path} | Email: {getattr(p, 'email', None)}")

    elif args.command == "list-browsers":
        mgr = AlternativeBrowserManager()
        browsers = mgr.browser_paths.keys()
        print("Available browsers:")
        for b in browsers:
            print(f"- {b}")

    elif args.command == "launch":
        if args.browser in PROFILE_BROWSERS:
            if not args.profile:
                print(f"Error: --profile is required for {args.browser}.")
                sys.exit(1)
            mgr = BrowserProfileManager()
            options = LaunchOptions(incognito=args.incognito)
            print(f"Launching {args.browser} with profile '{args.profile}' and URL '{args.url}'" + (" in incognito mode" if args.incognito else ""))
            mgr.launch_browser(
                browser_type=args.browser,
                profile=args.profile,
                url=args.url,
                options=options
            )
        else:
            mgr = AlternativeBrowserManager()
            print(f"Launching {args.browser} with URL '{args.url}'" + (" in incognito/private mode" if args.incognito else ""))
            mgr.launch_browser(
                browser_type=args.browser,
                url=args.url,
                private_mode=args.incognito
            )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
