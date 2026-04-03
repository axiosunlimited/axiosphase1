from django.contrib import admin
from .models import (
    ApprovalProcessConfig,
    Policy,
    PolicyAcknowledgement,
    DisciplinaryCase,
    Grievance,
    ComplianceItem,
)

admin.site.register(ApprovalProcessConfig)
admin.site.register(Policy)
admin.site.register(PolicyAcknowledgement)
admin.site.register(DisciplinaryCase)
admin.site.register(Grievance)
admin.site.register(ComplianceItem)
