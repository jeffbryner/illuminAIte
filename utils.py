import logging
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# tools
def day_of_week() -> str:
    """Get the current day of the week.
    Example:
        {{time.dayOfWeek}} => Sunday
    """
    now = datetime.datetime.now()
    return now.strftime("%A")
