from django.contrib import admin
from .models import Competency, EmployeeCompetency, TrainingProgram, TrainingNeed, EmployeeTraining

admin.site.register(Competency)
admin.site.register(EmployeeCompetency)
admin.site.register(TrainingProgram)
admin.site.register(TrainingNeed)
admin.site.register(EmployeeTraining)
