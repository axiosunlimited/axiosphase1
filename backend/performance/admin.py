from django.contrib import admin
from .models import AppraisalTemplate, Appraisal, Goal

admin.site.register(AppraisalTemplate)
admin.site.register(Appraisal)
admin.site.register(Goal)
