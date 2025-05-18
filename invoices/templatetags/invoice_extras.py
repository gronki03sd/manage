from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtracts the arg from the value."""
    # Handle None values
    if value is None:
        value = 0
    if arg is None:
        arg = 0
    
    try:
        # Convert to float to avoid decimal/None type errors
        return float(value) - float(arg)
    except (ValueError, TypeError):
        try:
            # Try to handle Decimal objects
            if isinstance(value, Decimal):
                value = float(value)
            if isinstance(arg, Decimal):
                arg = float(arg)
            return value - arg
        except (ValueError, TypeError):
            return 0