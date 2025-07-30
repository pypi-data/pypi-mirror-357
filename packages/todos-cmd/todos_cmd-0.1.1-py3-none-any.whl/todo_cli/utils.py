from datetime import datetime
from colorama import Fore, Style
from typing import Optional


def format_due_date(due_str: Optional[str]) -> str:
    if not due_str:
        return ""

    try:
        due = datetime.strptime(due_str, "%Y-%m-%d")
        now = datetime.now()

        if due.date() < now.date():
            return f"{Fore.RED}(Overdue: {due_str}){Style.RESET_ALL}"
        elif due.date() == now.date():
            return f"{Fore.YELLOW}(Due Today){Style.RESET_ALL}"
        else:
            return f"(Due: {due_str})"
    except ValueError:
        return f"{Fore.RED}(Invalid due date){Style.RESET_ALL}"



def colored_status(is_done: bool) -> str:
    """Returns ✓ or ✗ with color."""
    return f"{Fore.GREEN}✓{Style.RESET_ALL}" if is_done else f"{Fore.RED}✗{Style.RESET_ALL}"


def colored_priority(priority: str) -> str:
    """Returns colored priority tag."""
    priority = priority.lower()
    if priority == "high":
        return f"{Fore.RED}HIGH{Style.RESET_ALL}"
    elif priority == "medium":
        return f"{Fore.YELLOW}MEDIUM{Style.RESET_ALL}"
    else:
        return f"{Fore.CYAN}LOW{Style.RESET_ALL}"


def validate_priority(priority: str) -> bool:
    return priority.lower() in {"low", "medium", "high"}
