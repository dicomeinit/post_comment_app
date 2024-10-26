from datetime import date, datetime

from ninja.errors import HttpError

from .ai_model import get_model


def check_for_profanity(content: str) -> bool:
    """
    Checks if the provided content contains offensive or inappropriate language.
    """
    response = get_model().generate_content(
        f"Check if the following text contains offensive or inappropriate language: {content}"
    )
    return "yes" in response.text.lower()


def validate_and_parse_date(date_str: str) -> date:
    """
    Helper function to validate and parse date strings in the format YYYY-MM-DD
    using Django's DateField.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HttpError(400, f"Invalid date: {date_str}")
