from rest_framework.routers import DefaultRouter

from employees.views import (
    DepartmentViewSet,
    PositionViewSet,
    EmployeeViewSet,
    EmployeeDocumentViewSet,
    QualificationViewSet,
    EmploymentHistoryViewSet,
)
from recruitment.views import VacancyViewSet, ApplicantViewSet, InterviewViewSet, AppointmentViewSet
from leaveapp.views import LeaveTypeViewSet, LeaveBalanceViewSet, LeaveRequestViewSet, PublicHolidayViewSet
from performance.views import AppraisalTemplateViewSet, AppraisalViewSet, GoalViewSet
from notifications.views import NotificationViewSet, FeedbackViewSet
from notifications.views import NotificationSettingViewSet, EmailTemplateViewSet, SystemAlertViewSet

from contracts.views import ContractViewSet
from benefits.views import (
    EducationAssistancePolicyViewSet,
    DependantViewSet,
    DependantDocumentViewSet,
    EducationClaimViewSet,
    EducationClaimDocumentViewSet,
)
from imports.views import ImportJobViewSet
from system.views import SystemSettingViewSet, BackupArtifactViewSet

from training.views import (
    CompetencyViewSet,
    EmployeeCompetencyViewSet,
    TrainingProgramViewSet,
    TrainingNeedViewSet,
    EmployeeTrainingViewSet,
)
from workforce.views import EstablishmentItemViewSet, SeparationViewSet
from governance.views import (
    ApprovalProcessConfigViewSet,
    PolicyViewSet,
    PolicyAcknowledgementViewSet,
    DisciplinaryCaseViewSet,
    GrievanceViewSet,
    ComplianceItemViewSet,
)
from reports.views import ReportDefinitionViewSet, PredefinedReportViewSet, AnalyticsDashboardViewSet
from audit.views import AuditLogViewSet
from accounts.admin_views import UserViewSet, GroupViewSet, PermissionViewSet
from accounts.token_blacklist_api import OutstandingTokenViewSet, BlacklistedTokenViewSet

router = DefaultRouter()

# Core HR
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"positions", PositionViewSet, basename="position")
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"employee-documents", EmployeeDocumentViewSet, basename="employee-document")
router.register(r"qualifications", QualificationViewSet, basename="qualification")
router.register(r"employment-history", EmploymentHistoryViewSet, basename="employment-history")

# Recruitment
router.register(r"vacancies", VacancyViewSet, basename="vacancy")
router.register(r"applicants", ApplicantViewSet, basename="applicant")
router.register(r"interviews", InterviewViewSet, basename="interview")
router.register(r"appointments", AppointmentViewSet, basename="appointment")

# Leave
router.register(r"leave-types", LeaveTypeViewSet, basename="leave-type")
router.register(r"leave-balances", LeaveBalanceViewSet, basename="leave-balance")
router.register(r"leave-requests", LeaveRequestViewSet, basename="leave-request")
router.register(r"public-holidays", PublicHolidayViewSet, basename="public-holiday")

# Performance
router.register(r"appraisal-templates", AppraisalTemplateViewSet, basename="appraisal-template")
router.register(r"appraisals", AppraisalViewSet, basename="appraisal")
router.register(r"goals", GoalViewSet, basename="goal")

# Notifications / feedback
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"feedback", FeedbackViewSet, basename="feedback")
router.register(r"notification-settings", NotificationSettingViewSet, basename="notification-setting")
router.register(r"email-templates", EmailTemplateViewSet, basename="email-template")
router.register(r"system-alerts", SystemAlertViewSet, basename="system-alert")

# Contracts (employee lifecycle)
router.register(r"contracts", ContractViewSet, basename="contract")

# Education Assistance / Benefits
router.register(r"education-assistance-policies", EducationAssistancePolicyViewSet, basename="education-policy")
router.register(r"dependants", DependantViewSet, basename="dependant")
router.register(r"dependant-documents", DependantDocumentViewSet, basename="dependant-document")
router.register(r"education-claims", EducationClaimViewSet, basename="education-claim")
router.register(r"education-claim-documents", EducationClaimDocumentViewSet, basename="education-claim-document")

# Imports
router.register(r"import-jobs", ImportJobViewSet, basename="import-job")

# System settings / backups
router.register(r"system-settings", SystemSettingViewSet, basename="system-setting")
router.register(r"backups", BackupArtifactViewSet, basename="backup")

# Phase 2: Training & Development
router.register(r"competencies", CompetencyViewSet, basename="competency")
router.register(r"employee-competencies", EmployeeCompetencyViewSet, basename="employee-competency")
router.register(r"training-programs", TrainingProgramViewSet, basename="training-program")
router.register(r"training-needs", TrainingNeedViewSet, basename="training-need")
router.register(r"training-records", EmployeeTrainingViewSet, basename="training-record")

# Phase 2: Workforce Planning
router.register(r"establishment", EstablishmentItemViewSet, basename="establishment")
router.register(r"separations", SeparationViewSet, basename="separation")

# Reporting & Analytics
router.register(r"report-definitions", ReportDefinitionViewSet, basename="report-definition")
router.register(r"predefined-reports", PredefinedReportViewSet, basename="predefined-report")
router.register(r"analytics", AnalyticsDashboardViewSet, basename="analytics")

# Governance / workflows
router.register(r"approval-process-configs", ApprovalProcessConfigViewSet, basename="approval-process-config")
router.register(r"policies", PolicyViewSet, basename="policy")
router.register(r"policy-acknowledgements", PolicyAcknowledgementViewSet, basename="policy-acknowledgement")
router.register(r"disciplinary-cases", DisciplinaryCaseViewSet, basename="disciplinary-case")
router.register(r"grievances", GrievanceViewSet, basename="grievance")
router.register(r"compliance-items", ComplianceItemViewSet, basename="compliance-item")

# Admin / governance
router.register(r"users", UserViewSet, basename="user")
router.register(r"groups", GroupViewSet, basename="group")
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"audit-logs", AuditLogViewSet, basename="audit-log")

# Token blacklist
router.register(r"outstanding-tokens", OutstandingTokenViewSet, basename="outstanding-token")
router.register(r"blacklisted-tokens", BlacklistedTokenViewSet, basename="blacklisted-token")
