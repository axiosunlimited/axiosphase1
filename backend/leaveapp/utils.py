from datetime import timedelta

def business_days(start_date, end_date, holiday_dates=set()):
    if end_date < start_date:
        return 0
    days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5 and current not in holiday_dates:
            days += 1
        current += timedelta(days=1)
    return days
