import React, { useEffect, useMemo, useState, useCallback } from 'react'
import { Badge, Button, Input, Tooltip } from 'antd'
import {
  AppstoreOutlined,
  BarChartOutlined,
  BellOutlined,
  CalendarOutlined,
  CloseOutlined,
  DownOutlined,
  FileTextOutlined,
  KeyOutlined,
  LogoutOutlined,
  MenuOutlined,
  MoonOutlined,
  ProjectOutlined,
  ReadOutlined,
  SafetyCertificateOutlined,
  SearchOutlined,
  SettingOutlined,
  SolutionOutlined,
  SunOutlined,
  TeamOutlined,
} from '@ant-design/icons'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth, userDisplayName } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

function initials(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean)
  const a = parts[0]?.[0] ?? ''
  const b = parts.length > 1 ? parts[parts.length - 1]?.[0] ?? '' : ''
  return (a + b).toUpperCase() || 'U'
}

function formatRole(role: string) {
  return role.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

type NavChild = { label: string; to: string; roles?: string[] }

type NavSection = {
  key: string
  label: string
  icon: React.ReactNode
  to?: string
  children?: NavChild[]
  roles?: string[]
  permissionPrefixes?: string[]
  active: (pathname: string) => boolean
}

export default function AppShell() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout, reload } = useAuth()
  const { mode, toggle } = useTheme()

  const pathname = location.pathname
  const [mobileOpen, setMobileOpen] = useState(false)

  const closeMobile = useCallback(() => setMobileOpen(false), [])

  // Close mobile sidebar on route change
  useEffect(() => { closeMobile() }, [pathname, closeMobile])

  // Periodic user data refresh to pick up role/permission changes
  useEffect(() => {
    const interval = setInterval(() => {
      reload().catch(() => { }) // silenced
    }, 5000)
    return () => clearInterval(interval)
  }, [reload])

  const sections: NavSection[] = useMemo(() => {
    const allSections: NavSection[] = [
      {
        key: 'dashboard',
        label: 'Dashboard',
        to: '/',
        icon: <AppstoreOutlined />,
        active: (p) => p === '/',
      },
      {
        key: 'employees',
        label: 'Employees',
        icon: <TeamOutlined />,
        roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER', 'EMPLOYEE'],
        permissionPrefixes: ['employees.'],
        children: [
          { label: 'My Profile', to: '/employees/employees', roles: ['EMPLOYEE'] },
          { label: 'My Documents', to: '/employees/documents', roles: ['EMPLOYEE'] },
          { label: 'Employees', to: '/employees/employees', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'] },
          { label: 'Departments', to: '/employees/departments', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'] },
          { label: 'Positions', to: '/employees/positions', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'] },
          { label: 'Qualifications', to: '/employees/qualifications', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'] },
          { label: 'Employee Documents', to: '/employees/documents', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'] },
          { label: 'Employment History', to: '/employees/history', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'] },
          { label: 'Contracts', to: '/employees/contracts', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'] },
          { label: 'Draft Contract', to: '/employees/draft-contract', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'] },
        ],
        active: (p) => p.startsWith('/employees'),
      },
      // ── PHASE 2+ NAV SECTIONS (disabled for Phase 1 rollout) ──────────────

      // Benefits -- Phase 2
      // {
      //   key: 'benefits',
      //   label: 'Benefits',
      //   icon: <FileTextOutlined />,
      //   roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER', 'FINANCE_OFFICER', 'EMPLOYEE'],
      //   permissionPrefixes: ['benefits.'],
      //   children: [
      //     { label: 'My Dependants', to: '/benefits/dependants', roles: ['EMPLOYEE'] },
      //     { label: 'My School Fees Claims', to: '/benefits/claims', roles: ['EMPLOYEE'] },
      //     { label: 'Dependants', to: '/benefits/dependants', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER', 'FINANCE_OFFICER'] },
      //     { label: 'Dependant Documents', to: '/benefits/dependant-documents', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER', 'FINANCE_OFFICER'] },
      //     { label: 'Education Claims', to: '/benefits/claims', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER', 'FINANCE_OFFICER'] },
      //     { label: 'Claim Documents', to: '/benefits/claim-documents', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER', 'FINANCE_OFFICER'] },
      //     { label: 'Education Policy', to: '/benefits/policies', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'] },
      //   ],
      //   active: (p) => p.startsWith('/benefits'),
      // },
      {
        key: 'reports',
        label: 'Reports & Analytics',
        icon: <FileTextOutlined />,
        roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER', 'LINE_MANAGER', 'FINANCE_OFFICER'],
        permissionPrefixes: ['reports.'],
        children: [
          { label: 'Analytics Dashboard', to: '/analytics' },
          { label: 'Predefined Reports', to: '/reports/predefined', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'] },
          { label: 'Custom Reports', to: '/reports/custom', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'] },
        ],
        active: (p) => p.startsWith('/reports') || p.startsWith('/analytics'),
      },
      // Recruitment -- Phase 2
      // {
      //   key: 'recruitment',
      //   label: 'Recruitment',
      //   icon: <SolutionOutlined />,
      //   roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'],
      //   permissionPrefixes: ['recruitment.'],
      //   children: [
      //     { label: 'Vacancies', to: '/recruitment/vacancies' },
      //     { label: 'Applicants', to: '/recruitment/applicants' },
      //     { label: 'Interviews', to: '/recruitment/interviews' },
      //     { label: 'Appointments', to: '/recruitment/appointments' },
      //   ],
      //   active: (p) => p.startsWith('/recruitment'),
      // },
      {
        key: 'leave',
        label: 'Leave',
        icon: <CalendarOutlined />,
        children: [
          { label: 'Leave Requests', to: '/leave/requests' },
          { label: 'Leave Balances', to: '/leave/balances' },
          { label: 'Leave Types', to: '/leave/types', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'] },
          { label: 'Public Holidays', to: '/leave/holidays', roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'] },
        ],
        active: (p) => p.startsWith('/leave'),
      },
      // Performance -- Phase 2
      // {
      //   key: 'performance',
      //   label: 'Performance',
      //   icon: <BarChartOutlined />,
      //   roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'LINE_MANAGER'],
      //   permissionPrefixes: ['performance.', 'evaluation.'],
      //   children: [
      //     { label: 'Appraisal Templates', to: '/performance/templates' },
      //     { label: 'Appraisals', to: '/performance/appraisals' },
      //     { label: 'Goals', to: '/performance/goals' },
      //   ],
      //   active: (p) => p.startsWith('/performance'),
      // },

      // Training -- Phase 2
      // {
      //   key: 'training',
      //   label: 'Training',
      //   icon: <ReadOutlined />,
      //   roles: ['SYSTEM_ADMIN', 'HR_MANAGER'],
      //   permissionPrefixes: ['training.'],
      //   children: [
      //     { label: 'Training Programs', to: '/training/programs' },
      //     { label: 'Training Records', to: '/training/records' },
      //     { label: 'Training Needs', to: '/training/needs' },
      //     { label: 'Competencies', to: '/training/competencies' },
      //     { label: 'Employee Competencies', to: '/training/employee-competencies' },
      //   ],
      //   active: (p) => p.startsWith('/training'),
      // },

      // Workforce Planning -- Phase 2
      // {
      //   key: 'workforce',
      //   label: 'Workforce Planning',
      //   icon: <ProjectOutlined />,
      //   roles: ['SYSTEM_ADMIN', 'HR_MANAGER'],
      //   permissionPrefixes: ['workforce.'],
      //   children: [
      //     { label: 'Staff Establishment', to: '/workforce/establishment' },
      //     { label: 'Separations', to: '/workforce/separations' },
      //   ],
      //   active: (p) => p.startsWith('/workforce'),
      // },

      // Governance -- Phase 2
      // {
      //   key: 'governance',
      //   label: 'Governance',
      //   icon: <SafetyCertificateOutlined />,
      //   roles: ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'],
      //   permissionPrefixes: ['governance.'],
      //   children: [
      //     { label: 'Policies', to: '/governance/policies' },
      //     { label: 'Acknowledgements', to: '/governance/acknowledgements' },
      //     { label: 'Disciplinary Cases', to: '/governance/disciplinary' },
      //     { label: 'Grievances', to: '/governance/grievances' },
      //     { label: 'Compliance', to: '/governance/compliance' },
      //   ],
      //   active: (p) => p.startsWith('/governance'),
      // },
      {
        key: 'security',
        label: 'Security',
        to: '/security',
        icon: <SafetyCertificateOutlined />,
        active: (p) => p.startsWith('/security'),
      },
      // Notifications (in-app) -- Phase 2
      // {
      //   key: 'notifications',
      //   label: 'Notifications',
      //   icon: <BellOutlined />,
      //   children: [
      //     { label: 'Notifications', to: '/notifications/notifications' },
      //     { label: 'Feedback', to: '/notifications/feedback' },
      //   ],
      //   active: (p) => p.startsWith('/notifications'),
      // },
      {
        key: 'admin',
        label: 'Admin',
        icon: <SettingOutlined />,
        roles: ['SYSTEM_ADMIN', 'HR_MANAGER'],
        permissionPrefixes: ['accounts.', 'auth.', 'governance.'],
        children: [
          // Visible to both SYSTEM_ADMIN and HR_MANAGER
          { label: 'Users', to: '/admin/users', roles: ['SYSTEM_ADMIN', 'HR_MANAGER'] },
          { label: 'Invites', to: '/admin/invites', roles: ['SYSTEM_ADMIN', 'HR_MANAGER'] },
          { label: 'Audit Logs', to: '/admin/audit-logs', roles: ['SYSTEM_ADMIN', 'HR_MANAGER'] },
          // Restricted to SYSTEM_ADMIN only
          { label: 'Groups', to: '/admin/groups', roles: ['SYSTEM_ADMIN'] },
          { label: 'Permissions', to: '/admin/permissions', roles: ['SYSTEM_ADMIN'] },
          { label: 'Approval Workflows', to: '/admin/approval-workflows', roles: ['SYSTEM_ADMIN'] },
          { label: 'Imports', to: '/admin/imports', roles: ['SYSTEM_ADMIN'] },
          { label: 'Notification Settings', to: '/admin/notification-settings', roles: ['SYSTEM_ADMIN'] },
          { label: 'Email Templates', to: '/admin/email-templates', roles: ['SYSTEM_ADMIN'] },
          { label: 'System Settings', to: '/admin/system-settings', roles: ['SYSTEM_ADMIN'] },
          { label: 'Backups', to: '/admin/backups', roles: ['SYSTEM_ADMIN'] },
        ],
        active: (p) => p.startsWith('/admin'),
      },
      // Token Blacklist -- Phase 2
      // {
      //   key: 'tokens',
      //   label: 'Token Blacklist',
      //   icon: <KeyOutlined />,
      //   roles: ['SYSTEM_ADMIN'],
      //   permissionPrefixes: ['token_blacklist.'],
      //   children: [
      //     { label: 'Outstanding Tokens', to: '/tokens/outstanding' },
      //     { label: 'Blacklisted Tokens', to: '/tokens/blacklisted' },
      //   ],
      //   active: (p) => p.startsWith('/tokens'),
      // },

      // ── END PHASE 2+ NAV SECTIONS ───────────────────────────────────────────
    ]

    const perms = user?.permissions ?? []
    const hasAnyPerm = (prefixes?: string[]) =>
      !!prefixes && perms.some((p) => prefixes.some((pfx) => p.startsWith(pfx)))

    return allSections
      .filter((s) => !s.roles || (user?.role && s.roles.includes(user.role)) || hasAnyPerm(s.permissionPrefixes))
      .map((s) => {
        if (!s.children) return s
        return {
          ...s,
          children: s.children.filter((c) => !c.roles || (user?.role && c.roles.includes(user.role))),
        }
      })
  }, [user?.role, user?.permissions])

  const [open, setOpen] = useState<Record<string, boolean>>(() => {
    const initial: Record<string, boolean> = {}
    for (const s of sections) {
      if (s.children) initial[s.key] = false
    }
    return initial
  })

  useEffect(() => {
    setOpen((prev) => {
      const next = { ...prev }
      for (const s of sections) {
        if (s.children && s.active(pathname)) next[s.key] = true
      }
      return next
    })
  }, [pathname, sections])

  function toggleGroup(key: string) {
    setOpen((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const displayName = userDisplayName(user) || 'User'
  const userRole = user?.role ? formatRole(user.role) : ''

  return (
    <div className="app-shell">
      {/* Mobile overlay */}
      <div
        className={`sidebar-overlay ${mobileOpen ? 'sidebar-overlay--visible' : ''}`}
        onClick={closeMobile}
      />

      <aside className={`sidebar ${mobileOpen ? 'sidebar--open' : ''}`}>
        <Link to="/" className="sidebar__brand">
          <div className="brand__icon" aria-hidden>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="7" height="7" rx="1" />
              <rect x="14" y="3" width="7" height="7" rx="1" />
              <rect x="3" y="14" width="7" height="7" rx="1" />
              <rect x="14" y="14" width="7" height="7" rx="1" />
            </svg>
          </div>
          <span>HRIS Portal</span>
        </Link>

        <nav className="sidebar__nav" aria-label="Primary navigation">
          {sections.map((section) => {
            const isActive = section.active(pathname)

            if (!section.children) {
              return (
                <Link
                  key={section.key}
                  to={section.to || '/'}
                  className={`nav-item ${isActive ? 'nav-item--active' : ''}`}
                >
                  {section.icon}
                  <span>{section.label}</span>
                </Link>
              )
            }

            const isOpen = !!open[section.key]
            return (
              <div key={section.key} className="nav-group">
                <button
                  type="button"
                  className={`nav-item nav-item--group ${isActive ? 'nav-item--active' : ''}`}
                  onClick={() => toggleGroup(section.key)}
                  aria-expanded={isOpen}
                >
                  {section.icon}
                  <span>{section.label}</span>
                  <DownOutlined
                    className={`nav-item__chev ${isOpen ? 'nav-item__chev--open' : ''}`}
                    aria-hidden
                  />
                </button>

                {isOpen && (
                  <div className="nav-sub" role="group" aria-label={section.label}>
                    {section.children.map((child) => {
                      const childActive = pathname === child.to
                      return (
                        <Link
                          key={child.to}
                          to={child.to}
                          className={`nav-subitem ${childActive ? 'nav-subitem--active' : ''}`}
                        >
                          <span>{child.label}</span>
                        </Link>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })}
        </nav>

        <div className="sidebar__bottom">
          <Button
            type="text"
            className="nav-item"
            onClick={toggle}
            icon={mode === 'dark' ? <SunOutlined /> : <MoonOutlined />}
          >
            <span>Appearance</span>
          </Button>
          <Button
            type="text"
            className="nav-item"
            onClick={() => {
              logout()
              navigate('/login')
            }}
            icon={<LogoutOutlined />}
          >
            <span>Logout</span>
          </Button>
        </div>

        {/* User profile at bottom */}
        <div className="sidebar__user">
          <div className="sidebar__user-avatar">{initials(displayName)}</div>
          <div className="sidebar__user-info">
            <div className="sidebar__user-name">{displayName}</div>
            {userRole && <div className="sidebar__user-role">{userRole}</div>}
          </div>
        </div>
      </aside>

      <div className="shell-main">
        <header className="topbar">
          <button
            className="mobile-menu-btn"
            onClick={() => setMobileOpen((v) => !v)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <CloseOutlined /> : <MenuOutlined />}
          </button>

          <Input
            className="topbar__search"
            allowClear
            placeholder="Search..."
            prefix={<SearchOutlined style={{ color: 'var(--muted)' }} />}
          />

          <Tooltip title="Notifications">
            <Badge dot>
              <Button type="text" shape="circle" icon={<BellOutlined />} />
            </Badge>
          </Tooltip>
        </header>

        <div className="content">
          <div className="page">
            <Outlet />
          </div>
        </div>
      </div>
    </div>
  )
}