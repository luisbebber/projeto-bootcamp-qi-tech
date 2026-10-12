from datetime import datetime, timedelta, timezone

BRASILIA = timezone(timedelta(hours=-3))


def month_label(months_ago: int = 0) -> str:
    now = datetime.now(BRASILIA)
    total_months = now.year * 12 + (now.month - 1) - months_ago
    year, month_index = divmod(total_months, 12)

    return f"{year:04d}-{month_index + 1:02d}"
