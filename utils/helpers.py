from tabulate import tabulate
from colorama import init, Fore, Style
from datetime import datetime

# Initialize colorama
init()

def format_currency(amount):
    """Format number as currency"""
    return f"${amount:,.2f}"

def format_date(date_str):
    """Format date string"""
    if isinstance(date_str, str):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    else:
        date_obj = date_str
    return date_obj.strftime("%Y-%m-%d %H:%M:%S")

def print_table(headers, data, title=None):
    """Print data in a formatted table"""
    if title:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{title}{Style.RESET_ALL}")
    
    if not data:
        print(f"{Fore.YELLOW}No data available{Style.RESET_ALL}")
        return

    print(tabulate(data, headers=headers, tablefmt="grid"))

def print_success(message):
    """Print success message in green"""
    print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")

def print_error(message):
    """Print error message in red"""
    print(f"{Fore.RED}{message}{Style.RESET_ALL}")

def print_warning(message):
    """Print warning message in yellow"""
    print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")

def validate_date(date_str):
    """Validate date string format"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_positive_number(value):
    """Validate if value is a positive number"""
    try:
        num = float(value)
        return num > 0
    except ValueError:
        return False

def get_user_input(prompt, validator=None, error_message=None):
    """Get user input with validation"""
    while True:
        value = input(prompt).strip()
        if validator is None or validator(value):
            return value
        if error_message:
            print_error(error_message)
        else:
            print_error("Invalid input. Please try again.") 