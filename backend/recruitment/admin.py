from django.contrib import admin
from .models import Vacancy, Applicant, Interview, Appointment

admin.site.register(Vacancy)
admin.site.register(Applicant)
admin.site.register(Interview)
admin.site.register(Appointment)
