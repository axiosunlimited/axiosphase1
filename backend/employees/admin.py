from django.contrib import admin
from .models import Department, Position, Employee, Qualification, EmployeeDocument

admin.site.register(Department)
admin.site.register(Position)
admin.site.register(Employee)
admin.site.register(Qualification)
admin.site.register(EmployeeDocument)
