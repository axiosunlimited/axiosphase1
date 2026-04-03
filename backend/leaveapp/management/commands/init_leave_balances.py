from django.core.management.base import BaseCommand
from django.utils import timezone
from employees.models import Employee
from leaveapp.models import LeaveType, LeaveBalance

class Command(BaseCommand):
    help = "Initialize leave balances for all employees for the current year."

    def handle(self, *args, **options):
        year = timezone.now().year
        leave_types = LeaveType.objects.all()
        created = 0
        for emp in Employee.objects.all():
            for lt in leave_types:
                obj, was_created = LeaveBalance.objects.get_or_create(
                    employee=emp, leave_type=lt, year=year,
                    defaults={"days_entitled": lt.default_days_per_year, "days_used": 0}
                )
                if was_created:
                    created += 1
        self.stdout.write(self.style.SUCCESS(f"Created {created} leave balance records for year {year}."))
