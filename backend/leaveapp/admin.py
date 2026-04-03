from django.contrib import admin
from .models import LeaveType, LeaveBalance, LeaveRequest, PublicHoliday

admin.site.register(LeaveType)
admin.site.register(LeaveBalance)
admin.site.register(LeaveRequest)
admin.site.register(PublicHoliday)
