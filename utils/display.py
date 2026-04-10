"""
Display utilities for Kenya Wealth Agent CLI.

This module provides functions for printing formatted output
to the terminal with colors and styling.
"""

# Try to import colorama for colored output
try:
    from colorama import init, Fore, Back, Style

    init()  # Initialize colorama
    COLORAMA_AVAILABLE = True
except ImportError:
    # Fallback if colorama is not available
    COLORAMA_AVAILABLE = False

    # Define dummy color constants
    class DummyColor:
        def __getattr__(self, name):
            return ""

    Fore = Back = Style = DummyColor()


def print_header() -> None:
    """Print a beautiful header banner for the application."""
    print()
    print(f"{Fore.CYAN}{'╔' + '═' * 58 + '╝'}{Style.RESET_ALL}")
    print(
        f"{Fore.CYAN}║{Style.RESET_ALL}{' ' * 20}{Fore.YELLOW}🇰🇪 KENYA WEALTH{Style.RESET_ALL}{' ' * 19}{Fore.CYAN}║{Style.RESET_ALL}"
    )
    print(
        f"{Fore.CYAN}║{Style.RESET_ALL}{' ' * 18}{Fore.YELLOW}& FINANCE AGENT{Style.RESET_ALL}{' ' * 21}{Fore.CYAN}║{Style.RESET_ALL}"
    )
    print(
        f"{Fore.CYAN}║{Style.RESET_ALL}{' ' * 10}{Fore.GREEN}Your Personal Financial Advisor{Style.RESET_ALL}{' ' * 12}{Fore.CYAN}║{Style.RESET_ALL}"
    )
    print(
        f"{Fore.CYAN}║{Style.RESET_ALL}{' ' * 8}{Fore.WHITE}for the Kenyan Market Context{Style.RESET_ALL}{' ' * 13}{Fore.CYAN}║{Style.RESET_ALL}"
    )
    print(f"{Fore.CYAN}{'╚' + '═' * 58 + '╝'}{Style.RESET_ALL}")
    print()


def print_section_header(title: str, icon: str = "") -> None:
    """Print a formatted section header.

    Args:
        title: The title text to display
        icon: Optional emoji icon to prefix the title
    """
    prefix = f"{icon} " if icon else ""
    print(f"\n{Fore.BLUE}┌{'─' * 56}┐{Style.RESET_ALL}")
    print(
        f"{Fore.BLUE}│{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{prefix}{title}{Style.RESET_ALL}"
        f"{' ' * (55 - len(prefix) - len(title))}{Fore.BLUE}│{Style.RESET_ALL}"
    )
    print(f"{Fore.BLUE}└{'─' * 56}┘{Style.RESET_ALL}")


def print_menu_item(key: str, description: str, color=None) -> None:
    """Print a formatted menu item.

    Args:
        key: The menu key/shortcut
        description: Description of what the menu item does
        color: Color to use for the bullet point (default: green)
    """
    if color is None:
        color = Fore.GREEN
    print(
        f"  {color}▸{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{key:<12}{Style.RESET_ALL} "
        f"{Fore.WHITE}→{Style.RESET_ALL} {description}"
    )


def print_success(message: str) -> None:
    """Print a success message.

    Args:
        message: The success message to display
    """
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str) -> None:
    """Print an error message.

    Args:
        message: The error message to display
    """
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_info(message: str) -> None:
    """Print an info message.

    Args:
        message: The info message to display
    """
    print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")


def print_divider(char: str = "─", width: int = 60) -> None:
    """Print a horizontal divider.

    Args:
        char: Character to use for the divider (default: ─)
        width: Width of the divider (default: 60)
    """
    print(f"{Fore.BLUE}{char * width}{Style.RESET_ALL}")