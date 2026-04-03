import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import RequireAuth from './components/RequireAuth'
import AppShell from './components/AppShell'

import LoginPage from './pages/LoginPage'
import AcceptInvitePage from './pages/AcceptInvitePage'
import DashboardPage from './pages/DashboardPage'
import SecurityPage from './pages/SecurityPage'

// Employees
import EmployeesPage from './pages/employees/EmployeesPage'
import DepartmentsPage from './pages/employees/DepartmentsPage'
import PositionsPage from './pages/employees/PositionsPage'
import QualificationsPage from './pages/employees/QualificationsPage'
import EmployeeDocumentsPage from './pages/employees/EmployeeDocumentsPage'
import EmploymentHistoryPage from './pages/employees/EmploymentHistoryPage'
import ContractsPage from './pages/employees/ContractsPage'
import EmployeeProfilePage from './pages/employees/EmployeeProfilePage'
import DraftContractPage from './pages/employees/DraftContractPage'

// Leave
import LeaveRequestsPage from './pages/leave/LeaveRequestsPage'
import LeaveBalancesPage from './pages/leave/LeaveBalancesPage'
import LeaveTypesPage from './pages/leave/LeaveTypesPage'
import PublicHolidaysPage from './pages/leave/PublicHolidaysPage'

// ── PHASE 2+ MODULES (temporarily disabled for Phase 1 rollout) ──────────────

// Recruitment
// import VacanciesPage from './pages/recruitment/VacanciesPage'
// import ApplicantsPage from './pages/recruitment/ApplicantsPage'
// import InterviewsPage from './pages/recruitment/InterviewsPage'
// import AppointmentsPage from './pages/recruitment/AppointmentsPage'

// Performance
// import AppraisalTemplatesPage from './pages/performance/AppraisalTemplatesPage'
// import AppraisalsPage from './pages/performance/AppraisalsPage'
// import GoalsPage from './pages/performance/GoalsPage'

// Notifications (in-app)
// import NotificationsPage from './pages/notifications/NotificationsPage'
// import FeedbackPage from './pages/notifications/FeedbackPage'

// Admin
import UsersAdminPage from './pages/admin/UsersAdminPage'
import UserInvitesPage from './pages/admin/UserInvitesPage'
import GroupsAdminPage from './pages/admin/GroupsAdminPage'
import PermissionsPage from './pages/admin/PermissionsPage'
import AuditLogsPage from './pages/admin/AuditLogsPage'

// Token Blacklist
// import OutstandingTokensPage from './pages/tokens/OutstandingTokensPage'
// import BlacklistedTokensPage from './pages/tokens/BlacklistedTokensPage'

// Reports
import PredefinedReportsPage from './pages/reports/PredefinedReportsPage'
import ReportDefinitionsPage from './pages/reports/ReportDefinitionsPage'
import AnalyticsPage from './pages/AnalyticsPage'

// Training & Development
// import CompetenciesPage from './pages/training/CompetenciesPage'
// import EmployeeCompetenciesPage from './pages/training/EmployeeCompetenciesPage'
// import TrainingProgramsPage from './pages/training/TrainingProgramsPage'
// import TrainingNeedsPage from './pages/training/TrainingNeedsPage'
// import TrainingRecordsPage from './pages/training/TrainingRecordsPage'

// Workforce Planning
// import EstablishmentPage from './pages/workforce/EstablishmentPage'
// import SeparationsPage from './pages/workforce/SeparationsPage'

// Governance / Evaluation
// import ApprovalConfigsPage from './pages/admin/ApprovalConfigsPage'

// Governance Module
// import PoliciesPage from './pages/governance/PoliciesPage'
// import PolicyAcknowledgementsPage from './pages/governance/PolicyAcknowledgementsPage'
// import DisciplinaryCasesPage from './pages/governance/DisciplinaryCasesPage'
// import GrievancesPage from './pages/governance/GrievancesPage'
// import CompliancePage from './pages/governance/CompliancePage'

// Benefits
// import DependantsPage from './pages/benefits/DependantsPage'
// import DependantDocumentsPage from './pages/benefits/DependantDocumentsPage'
// import EducationClaimsPage from './pages/benefits/EducationClaimsPage'
// import EducationClaimDocumentsPage from './pages/benefits/EducationClaimDocumentsPage'
// import EducationPoliciesPage from './pages/benefits/EducationPoliciesPage'

// ─────────────────────────────────────────────────────────────────────────────

// Admin extras
import ImportsPage from './pages/admin/ImportsPage'
import SystemSettingsPage from './pages/admin/SystemSettingsPage'
import BackupsPage from './pages/admin/BackupsPage'
import NotificationSettingsPage from './pages/admin/NotificationSettingsPage'
import EmailTemplatesPage from './pages/admin/EmailTemplatesPage'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/accept-invite" element={<AcceptInvitePage />} />

      <Route element={<RequireAuth />}>
        <Route element={<AppShell />}>
          <Route index element={<DashboardPage />} />

          <Route path="employees">
            <Route index element={<Navigate to="/employees/employees" replace />} />
            <Route path="employees" element={<EmployeesPage />} />
            <Route path="departments" element={<DepartmentsPage />} />
            <Route path="positions" element={<PositionsPage />} />
            <Route path="qualifications" element={<QualificationsPage />} />
            <Route path="documents" element={<EmployeeDocumentsPage />} />
            <Route path="history" element={<EmploymentHistoryPage />} />
            <Route path="contracts" element={<ContractsPage />} />
            <Route path="draft-contract" element={<DraftContractPage />} />
          </Route>

          {/* ── PHASE 2+ ROUTES (disabled for Phase 1 rollout) ───────────────────── */}

          {/* Benefits -- Phase 2
          <Route path="benefits">
            <Route index element={<Navigate to="/benefits/dependants" replace />} />
            <Route path="dependants" element={<DependantsPage />} />
            <Route path="dependant-documents" element={<DependantDocumentsPage />} />
            <Route path="claims" element={<EducationClaimsPage />} />
            <Route path="claim-documents" element={<EducationClaimDocumentsPage />} />
            <Route path="policies" element={<EducationPoliciesPage />} />
          </Route>
          */}

          <Route path="leave">
            <Route index element={<Navigate to="/leave/requests" replace />} />
            <Route path="requests" element={<LeaveRequestsPage />} />
            <Route path="balances" element={<LeaveBalancesPage />} />
            <Route path="types" element={<LeaveTypesPage />} />
            <Route path="holidays" element={<PublicHolidaysPage />} />
          </Route>

          {/* Recruitment -- Phase 2
          <Route path="recruitment">
            <Route index element={<Navigate to="/recruitment/vacancies" replace />} />
            <Route path="vacancies" element={<VacanciesPage />} />
            <Route path="applicants" element={<ApplicantsPage />} />
            <Route path="interviews" element={<InterviewsPage />} />
            <Route path="appointments" element={<AppointmentsPage />} />
          </Route>
          */}

          {/* Performance -- Phase 2
          <Route path="performance">
            <Route index element={<Navigate to="/performance/appraisals" replace />} />
            <Route path="templates" element={<AppraisalTemplatesPage />} />
            <Route path="appraisals" element={<AppraisalsPage />} />
            <Route path="goals" element={<GoalsPage />} />
          </Route>
          */}

          {/* Notifications -- Phase 2
          <Route path="notifications">
            <Route index element={<Navigate to="/notifications/notifications" replace />} />
            <Route path="notifications" element={<NotificationsPage />} />
            <Route path="feedback" element={<FeedbackPage />} />
          </Route>
          */}

          <Route path="admin">
            <Route index element={<Navigate to="/admin/users" replace />} />
            <Route path="users" element={<UsersAdminPage />} />
            <Route path="invites" element={<UserInvitesPage />} />
            <Route path="groups" element={<GroupsAdminPage />} />
            <Route path="permissions" element={<PermissionsPage />} />
            <Route path="audit-logs" element={<AuditLogsPage />} />
            {/* Approval Workflows -- Phase 2
            <Route path="approval-workflows" element={<ApprovalConfigsPage />} />
            */}
            <Route path="imports" element={<ImportsPage />} />
            <Route path="system-settings" element={<SystemSettingsPage />} />
            <Route path="backups" element={<BackupsPage />} />
            <Route path="notification-settings" element={<NotificationSettingsPage />} />
            <Route path="email-templates" element={<EmailTemplatesPage />} />
          </Route>

          {/* Token Blacklist -- Phase 2
          <Route path="tokens">
            <Route index element={<Navigate to="/tokens/outstanding" replace />} />
            <Route path="outstanding" element={<OutstandingTokensPage />} />
            <Route path="blacklisted" element={<BlacklistedTokensPage />} />
          </Route>
          */}

          <Route path="reports">
            <Route index element={<Navigate to="/reports/predefined" replace />} />
            <Route path="predefined" element={<PredefinedReportsPage />} />
            <Route path="custom" element={<ReportDefinitionsPage />} />
          </Route>

          <Route path="analytics" element={<AnalyticsPage />} />

          {/* Training -- Phase 2
          <Route path="training">
            <Route index element={<Navigate to="/training/programs" replace />} />
            <Route path="competencies" element={<CompetenciesPage />} />
            <Route path="employee-competencies" element={<EmployeeCompetenciesPage />} />
            <Route path="programs" element={<TrainingProgramsPage />} />
            <Route path="needs" element={<TrainingNeedsPage />} />
            <Route path="records" element={<TrainingRecordsPage />} />
          </Route>
          */}

          {/* Workforce Planning -- Phase 2
          <Route path="workforce">
            <Route index element={<Navigate to="/workforce/establishment" replace />} />
            <Route path="establishment" element={<EstablishmentPage />} />
            <Route path="separations" element={<SeparationsPage />} />
          </Route>
          */}

          {/* Governance -- Phase 2
          <Route path="governance">
            <Route index element={<Navigate to="/governance/policies" replace />} />
            <Route path="policies" element={<PoliciesPage />} />
            <Route path="acknowledgements" element={<PolicyAcknowledgementsPage />} />
            <Route path="disciplinary" element={<DisciplinaryCasesPage />} />
            <Route path="grievances" element={<GrievancesPage />} />
            <Route path="compliance" element={<CompliancePage />} />
          </Route>
          */}

          {/* ─────────────────────────────────────────────────────────────────── */}

          <Route path="security" element={<SecurityPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
