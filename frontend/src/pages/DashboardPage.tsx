import React, { useEffect, useMemo, useState } from 'react'
import {
  AlertOutlined,
  BarChartOutlined,
  BellOutlined,
  BookOutlined,
  CalendarOutlined,
  FileTextOutlined,
  GiftOutlined,
  ImportOutlined,
  PlusOutlined,
  SafetyCertificateOutlined,
  SolutionOutlined,
  TeamOutlined,
  UserOutlined,
  WarningOutlined,
} from '@ant-design/icons'
import { Badge, Spin, Table, Tabs, Tag, Typography } from 'antd'
import { Link } from 'react-router-dom'
import { fetchDashboard } from '../api/auth'
import { useAuth, userDisplayName } from '../context/AuthContext'

const HR_ROLES = ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER']
const MANAGER_ROLES = [...HR_ROLES, 'LINE_MANAGER', 'PVC', 'ADMIN_OFFICER', 'FINANCE_OFFICER']

function StatCard({ label, value, meta, accent }: { label: string; value: React.ReactNode; meta?: React.ReactNode; accent?: boolean }) {
  return (
    <div className={`stat-card ${accent ? 'stat-card--accent' : ''}`}>
      <div className="stat-card__label">{label}</div>
      <div className="stat-card__value">
        {value}
        {meta ? <span className="stat-card__meta">{meta}</span> : null}
      </div>
    </div>
  )
}

function AlertTable({ title, data, columns }: { title: string; data: any[]; columns: any[] }) {
  if (!data?.length) return null
  return (
    <div style={{ marginBottom: 20 }}>
      <h3 style={{ margin: '0 0 8px', fontSize: 14, fontWeight: 700, color: 'var(--text)' }}>
        <WarningOutlined style={{ marginRight: 6, color: '#f59e0b' }} />
        {title} <Tag color="orange">{data.length}</Tag>
      </h3>
      <Table
        dataSource={data}
        columns={columns}
        size="small"
        pagination={false}
        rowKey={(r, i) => `${r.employee_number || ''}-${i}`}
        style={{ borderRadius: 8, overflow: 'hidden' }}
      />
    </div>
  )
}

function NotificationList({ items }: { items: any[] }) {
  if (!items?.length) return <Typography.Text type="secondary">No recent notifications.</Typography.Text>
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {items.map((n: any) => (
        <div key={n.id} style={{
          padding: '10px 14px', borderRadius: 8, background: 'var(--bg-panel)',
          border: '1px solid var(--border)', opacity: n.is_read ? 0.7 : 1,
        }}>
          <div style={{ fontWeight: 600, fontSize: 13 }}>
            {!n.is_read && <Badge dot style={{ marginRight: 6 }} />}
            {n.title}
          </div>
          <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>{n.message}</div>
          <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>
            {n.created_at ? new Date(n.created_at).toLocaleString() : ''}
          </div>
        </div>
      ))}
    </div>
  )
}

/* ═══════════════════════════════════════════════════ HR / ADMIN DASHBOARD */
function HRDashboard({ data, firstName }: { data: any; firstName: string }) {
  const stats = data?.stats || {}
  const alerts = data?.alerts || {}

  return (
    <div>
      <div className="dash-hero">
        <div>
          <h1>Welcome back, {firstName}</h1>
          <p>Here's what's happening with your organization today.</p>
        </div>
      </div>

      <div className="stat-row">
        <StatCard label="Total Employees" value={stats.total_employees ?? '—'} accent />
        <StatCard label="Open Vacancies" value={stats.open_vacancies ?? '—'} meta="Active" />
        <StatCard
          label="On Leave Today"
          value={stats.on_leave_today ?? '—'}
          meta={stats.pending_leave != null ? `${stats.pending_leave} pending` : undefined}
        />
        <StatCard label="Pending Claims" value={stats.pending_claims ?? '—'} meta="School Fees" />
      </div>

      {/* Alerts Panel */}
      <Tabs
        defaultActiveKey="alerts"
        items={[
          {
            key: 'alerts',
            label: <span><AlertOutlined /> Lifecycle Alerts</span>,
            children: (
              <div>
                <AlertTable
                  title="Contracts Expiring"
                  data={alerts.contracts_expiring || []}
                  columns={[
                    { title: 'Employee #', dataIndex: 'employee_number', width: 120 },
                    { title: 'Name', dataIndex: 'name' },
                    { title: 'End Date', dataIndex: 'end_date', width: 120 },
                    { title: 'Days Left', dataIndex: 'days_remaining', width: 90, render: (d: number) => <Tag color={d <= 30 ? 'red' : d <= 60 ? 'orange' : 'blue'}>{d}</Tag> },
                  ]}
                />
                <AlertTable
                  title="Probation Ending"
                  data={alerts.probation_ending || []}
                  columns={[
                    { title: 'Employee #', dataIndex: 'employee_number', width: 120 },
                    { title: 'Name', dataIndex: 'name' },
                    { title: 'Probation End', dataIndex: 'probation_end_date', width: 120 },
                    { title: 'Days Left', dataIndex: 'days_remaining', width: 90, render: (d: number) => <Tag color={d <= 7 ? 'red' : 'orange'}>{d}</Tag> },
                  ]}
                />
                <AlertTable
                  title="Upcoming Retirements"
                  data={alerts.retirements || []}
                  columns={[
                    { title: 'Employee #', dataIndex: 'employee_number', width: 120 },
                    { title: 'Name', dataIndex: 'name' },
                    { title: 'Retirement Date', dataIndex: 'retirement_date', width: 120 },
                    { title: 'Days Left', dataIndex: 'days_remaining', width: 90, render: (d: number) => <Tag color={d <= 90 ? 'red' : 'blue'}>{d}</Tag> },
                  ]}
                />
                <AlertTable
                  title="Missing Documents"
                  data={alerts.missing_documents || []}
                  columns={[
                    { title: 'Employee #', dataIndex: 'employee_number', width: 120 },
                    { title: 'Name', dataIndex: 'name' },
                    { title: 'Missing', dataIndex: 'missing', render: (v: string[]) => v?.map((m) => <Tag key={m} color="red" style={{ marginBottom: 2 }}>{m.replace(/_/g, ' ')}</Tag>) },
                  ]}
                />
                {!alerts.contracts_expiring?.length && !alerts.probation_ending?.length && !alerts.retirements?.length && !alerts.missing_documents?.length && (
                  <Typography.Text type="secondary">No active alerts.</Typography.Text>
                )}
              </div>
            ),
          },
          {
            key: 'birthdays',
            label: <span><GiftOutlined /> Upcoming Birthdays</span>,
            children: alerts.upcoming_birthdays?.length ? (
              <Table
                dataSource={alerts.upcoming_birthdays}
                columns={[
                  { title: 'Employee #', dataIndex: 'employee_number', width: 120 },
                  { title: 'Name', dataIndex: 'name' },
                  { title: 'Date', dataIndex: 'date', width: 120 },
                  { title: '', dataIndex: 'days_until', width: 100, render: (d: number) => d === 0 ? <Tag color="green">Today!</Tag> : <Tag>{d} day(s)</Tag> },
                ]}
                size="small"
                pagination={false}
                rowKey={(r: any, i) => `${r.employee_number}-${i}`}
              />
            ) : <Typography.Text type="secondary">No upcoming birthdays this week.</Typography.Text>,
          },
          {
            key: 'notifications',
            label: <span><BellOutlined /> Notifications</span>,
            children: <NotificationList items={data?.recent_notifications || []} />,
          },
        ]}
      />

      {/* Quick Navigation */}
      <section className="quick-nav" style={{ marginTop: 24 }}>
        <h2 className="quick-nav__title">Quick Actions</h2>
        <div className="quick-grid">
          <Link to="/employees/employees" className="nav-card">
            <div className="nav-card__icon" style={{ background: 'rgba(14, 165, 233, 0.12)' }}><TeamOutlined style={{ fontSize: 18 }} /></div>
            <h3>Employees</h3>
            <p>Manage employee records, personal details, and digital documents.</p>
            <div className="nav-card__link">View Records →</div>
          </Link>
          <Link to="/leave/requests" className="nav-card">
            <div className="nav-card__icon" style={{ background: 'rgba(245, 158, 11, 0.15)' }}><CalendarOutlined style={{ fontSize: 18 }} /></div>
            <h3>Leave Management</h3>
            <p>Review leave requests, check balances, and manage time-off policies.</p>
            <div className="nav-card__link">Manage Requests →</div>
          </Link>
          <Link to="/benefits/claims" className="nav-card">
            <div className="nav-card__icon" style={{ background: 'rgba(34, 197, 94, 0.14)' }}><BookOutlined style={{ fontSize: 18 }} /></div>
            <h3>School Fees Claims</h3>
            <p>Review and approve education assistance claims and reimbursements.</p>
            <div className="nav-card__link">Review Claims →</div>
          </Link>
          <Link to="/admin/imports" className="nav-card">
            <div className="nav-card__icon" style={{ background: 'rgba(168, 85, 247, 0.12)' }}><ImportOutlined style={{ fontSize: 18 }} /></div>
            <h3>Data Import</h3>
            <p>Bulk import employees, leave balances, and contracts from CSV/XLSX.</p>
            <div className="nav-card__link">Import Data →</div>
          </Link>
          <Link to="/reports/predefined" className="nav-card">
            <div className="nav-card__icon" style={{ background: 'rgba(239, 68, 68, 0.10)' }}><BarChartOutlined style={{ fontSize: 18 }} /></div>
            <h3>Reports</h3>
            <p>Generate council summaries, HR committee reports, and workforce analytics.</p>
            <div className="nav-card__link">Generate Reports →</div>
          </Link>
          <Link to="/security" className="nav-card">
            <div className="nav-card__icon" style={{ background: 'rgba(100, 116, 139, 0.12)' }}><SafetyCertificateOutlined style={{ fontSize: 18 }} /></div>
            <h3>Security</h3>
            <p>System-wide 2FA setup, access logs, and granular permission management.</p>
            <div className="nav-card__link">Admin Settings →</div>
          </Link>
        </div>
      </section>

      <div className="dash-footer">
        <div>© {new Date().getFullYear()} HRIS Portal. All rights reserved.</div>
        <div style={{ display: 'flex', gap: 16 }}>
          <a href="#" onClick={(e) => e.preventDefault()}>Privacy Policy</a>
          <a href="#" onClick={(e) => e.preventDefault()}>Terms of Service</a>
          <a href="#" onClick={(e) => e.preventDefault()}>Support</a>
        </div>
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════ MANAGER DASHBOARD */
function ManagerDashboard({ data, firstName }: { data: any; firstName: string }) {
  const stats = data?.stats || {}

  return (
    <div>
      <div className="dash-hero">
        <div>
          <h1>Welcome back, {firstName}</h1>
          <p>Your team overview at a glance.</p>
        </div>
      </div>

      <div className="stat-row">
        <StatCard label="Team Size" value={stats.team_count ?? '—'} accent />
        <StatCard label="Team On Leave" value={stats.team_on_leave ?? '—'} />
        <StatCard label="Pending Approvals" value={stats.pending_approvals ?? '—'} meta="Leave" />
      </div>

      <section style={{ marginBottom: 24 }}>
        <h2 className="quick-nav__title"><BellOutlined style={{ marginRight: 6 }} />Recent Notifications</h2>
        <NotificationList items={data?.recent_notifications || []} />
      </section>

      <section className="quick-nav">
        <h2 className="quick-nav__title">Quick Actions</h2>
        <div className="quick-grid">
          <Link to="/leave/requests" className="nav-card">
            <div className="nav-card__icon" style={{ background: 'rgba(245, 158, 11, 0.15)' }}><CalendarOutlined style={{ fontSize: 18 }} /></div>
            <h3>Leave Approvals</h3>
            <p>Review and approve pending leave requests from your team.</p>
            <div className="nav-card__link">Manage Leave →</div>
          </Link>
          <Link to="/employees/employees" className="nav-card">
            <div className="nav-card__icon" style={{ background: 'rgba(14, 165, 233, 0.12)' }}><TeamOutlined style={{ fontSize: 18 }} /></div>
            <h3>Team Members</h3>
            <p>View your team's employee records and information.</p>
            <div className="nav-card__link">View Team →</div>
          </Link>
          <Link to="/performance/appraisals" className="nav-card">
            <div className="nav-card__icon" style={{ background: 'rgba(168, 85, 247, 0.12)' }}><BarChartOutlined style={{ fontSize: 18 }} /></div>
            <h3>Performance</h3>
            <p>Manage appraisals and performance reviews for your team.</p>
            <div className="nav-card__link">Performance Hub →</div>
          </Link>
        </div>
      </section>

      <div className="dash-footer">
        <div>© {new Date().getFullYear()} HRIS Portal. All rights reserved.</div>
        <div style={{ display: 'flex', gap: 16 }}>
          <a href="#" onClick={(e) => e.preventDefault()}>Privacy Policy</a>
          <a href="#" onClick={(e) => e.preventDefault()}>Terms of Service</a>
          <a href="#" onClick={(e) => e.preventDefault()}>Support</a>
        </div>
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════ EMPLOYEE SELF-SERVICE */
function EmployeeDashboard({ data, firstName }: { data: any; firstName: string }) {
  const profile = data?.profile || {}
  const leaveBalances = data?.leave_balances || []
  const leaveRequests = data?.leave_requests || []
  const claims = data?.education_claims || []
  const documents = data?.documents || []
  const dependants = data?.dependants || []
  const missingDocs: string[] = data?.missing_documents || []

  const statusColor = (s: string) => {
    if (s?.includes('APPROVED') || s === 'PAID') return 'green'
    if (s?.includes('REJECTED')) return 'red'
    if (s?.includes('PENDING') || s === 'SUBMITTED' || s === 'NEEDS_INFO' || s === 'FINANCE_PENDING') return 'orange'
    return 'default'
  }

  return (
    <div>
      <div className="dash-hero">
        <div>
          <h1>Welcome, {firstName}</h1>
          <p>Your personal HR self-service portal.</p>
        </div>
      </div>

      {/* Missing Documents Alert */}
      {missingDocs.length > 0 && (
        <div style={{
          background: '#fff7ed', border: '1px solid #fed7aa',
          borderRadius: 'var(--radius-lg)', padding: '14px 20px', marginBottom: 20,
          display: 'flex', alignItems: 'flex-start', gap: 12,
        }}>
          <WarningOutlined style={{ color: '#f59e0b', fontSize: 18, marginTop: 2, flexShrink: 0 }} />
          <div>
            <div style={{ fontWeight: 700, color: '#92400e', marginBottom: 6 }}>
              Action Required: Missing Documents ({missingDocs.length})
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {missingDocs.map((cat) => (
                <Tag key={cat} color="orange" style={{ marginBottom: 0 }}>
                  {cat.replace(/_/g, ' ')}
                </Tag>
              ))}
            </div>
            <div style={{ marginTop: 8, fontSize: 12, color: '#92400e' }}>
              Please upload the missing documents via <Link to="/employees/documents" style={{ color: '#d97706', fontWeight: 600 }}>My Documents</Link>.
            </div>
          </div>
        </div>
      )}

      {/* Profile Summary */}
      {profile.employee_number && (
        <div style={{
          background: 'var(--bg-panel)', border: '1px solid var(--border)',
          borderRadius: 'var(--radius-lg)', padding: '16px 20px', marginBottom: 20,
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12,
        }}>
          <div><span style={{ color: 'var(--muted)', fontSize: 12, fontWeight: 600 }}>EMPLOYEE #</span><div style={{ fontWeight: 700 }}>{profile.employee_number}</div></div>
          <div><span style={{ color: 'var(--muted)', fontSize: 12, fontWeight: 600 }}>DEPARTMENT</span><div style={{ fontWeight: 700 }}>{profile.department}</div></div>
          <div><span style={{ color: 'var(--muted)', fontSize: 12, fontWeight: 600 }}>POSITION</span><div style={{ fontWeight: 700 }}>{profile.position}</div></div>
          <div><span style={{ color: 'var(--muted)', fontSize: 12, fontWeight: 600 }}>STATUS</span><div style={{ fontWeight: 700 }}>{profile.employment_status}</div></div>
          <div><span style={{ color: 'var(--muted)', fontSize: 12, fontWeight: 600 }}>CONTRACT</span><div style={{ fontWeight: 700 }}>{profile.contract_type}</div></div>
          <div><span style={{ color: 'var(--muted)', fontSize: 12, fontWeight: 600 }}>DATE OF BIRTH</span><div style={{ fontWeight: 700 }}>{profile.date_of_birth || <span style={{ color: 'var(--muted)' }}>Not set — <Link to="/employees/employees" style={{ color: '#d97706' }}>update profile</Link></span>}</div></div>
          <div><span style={{ color: 'var(--muted)', fontSize: 12, fontWeight: 600 }}>LINE MANAGER</span><div style={{ fontWeight: 700 }}>{profile.line_manager || '—'}</div></div>
        </div>
      )}

      {/* Leave Balances */}
      <div className="stat-row" style={{ gridTemplateColumns: `repeat(${Math.min(leaveBalances.length || 1, 4)}, minmax(0, 1fr))` }}>
        {leaveBalances.length > 0 ? leaveBalances.map((lb: any, i: number) => (
          <StatCard
            key={i}
            label={lb.leave_type}
            value={lb.days_remaining}
            meta={`of ${lb.days_entitled} days`}
            accent={i === 0}
          />
        )) : (
          <StatCard label="Leave Balance" value="—" meta="No balances found" />
        )}
      </div>

      <Tabs
        defaultActiveKey="leave"
        items={[
          {
            key: 'leave',
            label: <span><CalendarOutlined /> Leave History</span>,
            children: leaveRequests.length ? (
              <Table
                dataSource={leaveRequests}
                columns={[
                  { title: 'Type', dataIndex: 'leave_type' },
                  { title: 'Start', dataIndex: 'start_date' },
                  { title: 'End', dataIndex: 'end_date' },
                  { title: 'Days', dataIndex: 'days_requested', width: 60 },
                  { title: 'Status', dataIndex: 'status', render: (s: string) => <Tag color={statusColor(s)}>{s}</Tag> },
                ]}
                size="small"
                pagination={false}
                rowKey="id"
              />
            ) : <Typography.Text type="secondary">No leave requests yet.</Typography.Text>,
          },
          {
            key: 'claims',
            label: <span><BookOutlined /> School Fees Claims</span>,
            children: claims.length ? (
              <Table
                dataSource={claims}
                columns={[
                  { title: 'Dependant', dataIndex: 'dependant_name' },
                  { title: 'Year', dataIndex: 'academic_year', width: 70 },
                  { title: 'Claimed', dataIndex: 'amount_claimed', render: (v: number) => v?.toLocaleString() },
                  { title: 'Approved', dataIndex: 'amount_approved', render: (v: number | null) => v != null ? v.toLocaleString() : '—' },
                  { title: 'Status', dataIndex: 'status', render: (s: string) => <Tag color={statusColor(s)}>{s}</Tag> },
                ]}
                size="small"
                pagination={false}
                rowKey="id"
              />
            ) : <Typography.Text type="secondary">No education claims yet.</Typography.Text>,
          },
          {
            key: 'documents',
            label: <span><FileTextOutlined /> My Documents</span>,
            children: documents.length ? (
              <Table
                dataSource={documents}
                columns={[
                  { title: 'Category', dataIndex: 'category', render: (c: string) => c?.replace(/_/g, ' ') },
                  { title: 'File Name', dataIndex: 'original_name' },
                  { title: 'Uploaded', dataIndex: 'uploaded_at', render: (v: string) => v ? new Date(v).toLocaleDateString() : '' },
                ]}
                size="small"
                pagination={false}
                rowKey="id"
              />
            ) : <Typography.Text type="secondary">No documents uploaded yet.</Typography.Text>,
          },
          {
            key: 'dependants',
            label: <span><UserOutlined /> Dependants</span>,
            children: dependants.length ? (
              <Table
                dataSource={dependants}
                columns={[
                  { title: 'Name', dataIndex: 'name' },
                  { title: 'Relationship', dataIndex: 'relationship' },
                  { title: 'Education Level', dataIndex: 'education_level' },
                  { title: 'Institution', dataIndex: 'institution_name' },
                  { title: 'Eligible', dataIndex: 'benefit_eligible', render: (v: boolean) => v ? <Tag color="green">Yes</Tag> : <Tag color="red">No</Tag> },
                ]}
                size="small"
                pagination={false}
                rowKey="id"
              />
            ) : <Typography.Text type="secondary">No dependants registered.</Typography.Text>,
          },
          {
            key: 'notifications',
            label: <span><BellOutlined /> Notifications</span>,
            children: <NotificationList items={data?.recent_notifications || []} />,
          },
        ]}
      />

      {/* Quick Actions */}
      <section className="quick-nav" style={{ marginTop: 24 }}>
        <h2 className="quick-nav__title">Quick Actions</h2>
        <div className="quick-grid">
          <Link to="/leave/requests" className="nav-card">
            <div className="nav-card__icon" style={{ background: 'rgba(245, 158, 11, 0.15)' }}><CalendarOutlined style={{ fontSize: 18 }} /></div>
            <h3>Apply for Leave</h3>
            <p>Submit a new leave request for approval.</p>
            <div className="nav-card__link">Apply Now →</div>
          </Link>
          <Link to="/benefits/claims" className="nav-card">
            <div className="nav-card__icon" style={{ background: 'rgba(34, 197, 94, 0.14)' }}><BookOutlined style={{ fontSize: 18 }} /></div>
            <h3>School Fees Claim</h3>
            <p>Submit an education assistance claim for your dependants.</p>
            <div className="nav-card__link">Submit Claim →</div>
          </Link>
          <Link to="/employees/documents" className="nav-card">
            <div className="nav-card__icon" style={{ background: 'rgba(14, 165, 233, 0.12)' }}><FileTextOutlined style={{ fontSize: 18 }} /></div>
            <h3>Upload Documents</h3>
            <p>Upload or update your personal and professional documents.</p>
            <div className="nav-card__link">Manage Documents →</div>
          </Link>
          <Link to="/benefits/dependants" className="nav-card">
            <div className="nav-card__icon" style={{ background: 'rgba(168, 85, 247, 0.12)' }}><UserOutlined style={{ fontSize: 18 }} /></div>
            <h3>My Dependants</h3>
            <p>Register dependants to qualify for school fees and education claims.</p>
            <div className="nav-card__link">Manage Dependants →</div>
          </Link>
        </div>
      </section>

      <div className="dash-footer">
        <div>© {new Date().getFullYear()} HRIS Portal. All rights reserved.</div>
        <div style={{ display: 'flex', gap: 16 }}>
          <a href="#" onClick={(e) => e.preventDefault()}>Privacy Policy</a>
          <a href="#" onClick={(e) => e.preventDefault()}>Terms of Service</a>
          <a href="#" onClick={(e) => e.preventDefault()}>Support</a>
        </div>
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════ MAIN PAGE */
export default function DashboardPage() {
  const { user } = useAuth()
  const firstName = useMemo(() => {
    const full = userDisplayName(user) || ''
    const parts = full.trim().split(/\s+/).filter(Boolean)
    return parts[0] || full
  }, [user])

  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    let mounted = true
      ; (async () => {
        setLoading(true)
        try {
          const result = await fetchDashboard()
          if (mounted) setData(result)
        } catch {
          // fallback - API might not be available yet
          if (mounted) setData(null)
        } finally {
          if (mounted) setLoading(false)
        }
      })()
    return () => { mounted = false }
  }, [])

  if (loading) {
    return (
      <div style={{ padding: '64px 0', textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    )
  }

  const role = user?.role || data?.role || ''

  if (HR_ROLES.includes(role)) {
    return <HRDashboard data={data} firstName={firstName} />
  }
  if (MANAGER_ROLES.includes(role)) {
    return <ManagerDashboard data={data} firstName={firstName} />
  }
  return <EmployeeDashboard data={data} firstName={firstName} />
}