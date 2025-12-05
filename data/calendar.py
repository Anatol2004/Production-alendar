from datetime import datetime, timedelta
import calendar as cal



class ProductionCalendar:
    @staticmethod

    def get_two_week_period(start_date=None):
        if not start_date:
            today = datetime.now().date()
            start_date = today - timedelta(days=today.weekday())
        
        dates = []
        current_date = start_date
        work_days_added = 0
        
        while work_days_added < 10:
            if current_date.weekday() < 5:
                dates.append(current_date)
                work_days_added += 1
            current_date += timedelta(days=1)
        
        return dates
    


    @staticmethod
    def get_month_calendar(year=None, month=None):
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
        
        month_calendar = []
        num_days = cal.monthrange(year, month)[1]
        
        for day in range(1, num_days + 1):
            date = datetime(year, month, day).date()
            is_weekend = date.weekday() >= 5  
            month_calendar.append({
                'date': date,
                'day_of_week': date.strftime('%A'),
                'is_weekend': is_weekend
            })
        
        return month_calendar