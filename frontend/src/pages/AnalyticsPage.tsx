import React, { useEffect, useState } from 'react'
import {
  AlertOutlined,
  BarChartOutlined,
  CalendarOutlined,
  FileTextOutlined,
  LineChartOutlined,
  LoadingOutlined,
  TeamOutlined,
  UserOutlined,
  WalletOutlined,
} from '@ant-design/icons'
import { Card, Col, Row, Select, Space, Spin, Statistic, Table, Tag, Typography, Tabs, Empty, Button, Tooltip } from 'antd'
import { http } from '../api/client'

interface AnalyticsDashboard {
  dashboard_type: string
  metrics: Record<string, any>
  charts: Record<string, any>
  error?: string
}

const DASHBOARD_COLORS = {
  blue: '#1890ff',
  green: '#52c41a',
  orange: '#fa8c16',
  red: '#f5222d',
  purple: '#722ed1',
  cyan: '#13c2c2',
}

function StatCard({
  icon,
  label,
  value,
  suffix,
  color,
  tooltip,
}: {
  icon: React.ReactNode
  label: string
  value: string | number
  suffix?: string
  color?: string
  tooltip?: string
}) {
  return (
    <Tooltip title={tooltip}>
      <div
        style={{
          padding: '16px',
          background: 'var(--bg-panel)',
          borderRadius: '8px',
          border: '1px solid var(--border)',
          textAlign: 'center',
          cursor: tooltip ? 'help' : 'default',
        }}
      >
        <div style={{ fontSize: '24px', color: color || '#1890ff', marginBottom: '8px' }}>{icon}</div>
        <div style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '4px' }}>{label}</div>
        <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text)' }}>
          {value}
          {suffix && <span style={{ fontSize: '14px', marginLeft: '4px' }}>{suffix}</span>}
        </div>
      </div>
    </Tooltip>
  )
}

function SimpleBarChart({ data, title }: { data: any[]; title: string }) {
  if (!data || data.length === 0) return <Empty />

  const maxValue = Math.max(...data.map((d) => d.count || 0), 1)

  return (
    <Card title={title} size="small">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {data.map((item, idx) => {
          const name = item.name || item.leave_type__name || item.title || Object.values(item)[0]
          const count = item.count || item.total || 0
          const percent = (count / maxValue) * 100
          return (
            <div key={idx}>
              <div style={{ fontSize: '12px', marginBottom: '4px', display: 'flex', justifyContent: 'space-between' }}>
                <span>{name}</span>
                <span style={{ fontWeight: 700 }}>{count}</span>
              </div>
              <div
                style={{
                  height: '8px',
                  background: 'var(--bg-secondary)',
                  borderRadius: '4px',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    height: '100%',
                    width: `${percent}%`,
                    background: Object.values(DASHBOARD_COLORS)[idx % Object.keys(DASHBOARD_COLORS).length],
                    transition: 'width 0.3s ease',
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </Card>
  )
}

function SimpleTable({ data, title, columns }: { data: any[]; title: string; columns?: string[] }) {
  if (!data || data.length === 0) return <Empty />

  const cols = columns || (data.length > 0 ? Object.keys(data[0]) : [])

  const tableColumns = cols.map((col) => ({
    title: col.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').toUpperCase(),
    dataIndex: col,
    key: col,
    render: (text: any) => {
      if (typeof text === 'number') return text.toFixed(2)
      return text
    },
  }))

  return (
    <Card title={title} size="small">
      <Table
        dataSource={data.slice(0, 10)}
        columns={tableColumns}
        pagination={false}
        size="small"
        rowKey={(_, idx) => idx ?? 0}
      />
    </Card>
  )
}

function SystemAdminDashboard({ data }: { data: AnalyticsDashboard }) {
  const metrics = data.metrics || {}
  const charts = data.charts || {}

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <Row gutter={16}>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<TeamOutlined />}
            label="Total Employees"
            value={metrics.total_employees || 0}
            color={DASHBOARD_COLORS.blue}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<UserOutlined />}
            label="Active Employees"
            value={metrics.active_employees || 0}
            color={DASHBOARD_COLORS.green}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<FileTextOutlined />}
            label="Contracts Expiring"
            value={metrics.contracts_expiring_soon || 0}
            color={DASHBOARD_COLORS.orange}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<AlertOutlined />}
            label="System Alerts"
            value={metrics.active_system_alerts || 0}
            color={DASHBOARD_COLORS.red}
          />
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<FileTextOutlined />}
            label="Open Vacancies"
            value={metrics.active_vacancies || 0}
            color={DASHBOARD_COLORS.purple}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<TeamOutlined />}
            label="Pending Applicants"
            value={metrics.pending_applicants || 0}
            color={DASHBOARD_COLORS.cyan}
          />
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} md={12}>
          <SimpleBarChart data={charts.employees_by_department || []} title="Employees by Department" />
        </Col>
        <Col xs={24} md={12}>
          <SimpleBarChart data={charts.users_by_role || []} title="Users by Role" />
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24}>
          <SimpleBarChart data={charts.leave_by_status || []} title="Leave Requests by Status" />
        </Col>
      </Row>
    </div>
  )
}

function HRManagerDashboard({ data }: { data: AnalyticsDashboard }) {
  const metrics = data.metrics || {}
  const charts = data.charts || {}

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <Row gutter={16}>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<TeamOutlined />}
            label="Total Employees"
            value={metrics.total_employees || 0}
            color={DASHBOARD_COLORS.blue}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<UserOutlined />}
            label="Active Employees"
            value={metrics.active_employees || 0}
            color={DASHBOARD_COLORS.green}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<AlertOutlined />}
            label="Leave Pending"
            value={metrics.leave_pending_approval || 0}
            color={DASHBOARD_COLORS.orange}
            tooltip="Waiting for approval"
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<FileTextOutlined />}
            label="Contracts Expiring"
            value={metrics.contracts_expiring_soon || 0}
            color={DASHBOARD_COLORS.red}
            tooltip="Within 90 days"
          />
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<CalendarOutlined />}
            label="Probation Ending"
            value={metrics.probation_ending_soon || 0}
            color={DASHBOARD_COLORS.purple}
            tooltip="Within 30 days"
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<TeamOutlined />}
            label="Retiring This Year"
            value={metrics.retiring_this_year || 0}
            color={DASHBOARD_COLORS.cyan}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<FileTextOutlined />}
            label="Missing Documents"
            value={metrics.missing_required_documents || 0}
            color={DASHBOARD_COLORS.orange}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<WalletOutlined />}
            label="Claims Pending"
            value={metrics.education_claims_pending || 0}
            color={DASHBOARD_COLORS.blue}
          />
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Card title="Leave Summary" size="small">
            <Row gutter={12}>
              {(charts.leave_summary || []).map((item: any, idx: number) => (
                <Col xs={8} key={idx}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '18px', fontWeight: 700, color: DASHBOARD_COLORS.blue }}>
                      {item.count}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--muted)' }}>{item.status}</div>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <SimpleBarChart data={charts.interviews_pending_by_vacancy || []} title="Interviews Pending by Vacancy" />
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} md={12}>
          <SimpleBarChart data={charts.leave_by_type || []} title="Leave Requests by Type" />
        </Col>
      </Row>
    </div>
  )
}

function LineManagerDashboard({ data }: { data: AnalyticsDashboard }) {
  const metrics = data.metrics || {}
  const charts = data.charts || {}

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <Row gutter={16}>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<TeamOutlined />}
            label="Team Size"
            value={metrics.team_size || 0}
            color={DASHBOARD_COLORS.blue}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<CalendarOutlined />}
            label="On Leave Today"
            value={metrics.on_leave_today || 0}
            color={DASHBOARD_COLORS.orange}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<AlertOutlined />}
            label="Pending Requests"
            value={metrics.pending_leave_requests || 0}
            color={DASHBOARD_COLORS.red}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<FileTextOutlined />}
            label="Contracts Expiring"
            value={metrics.team_contracts_expiring || 0}
            color={DASHBOARD_COLORS.purple}
          />
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} md={12}>
          <SimpleBarChart data={charts.team_leave_by_type || []} title="Team Leave by Type" />
        </Col>
        <Col xs={24} md={12}>
          <SimpleBarChart data={charts.team_by_department || []} title="Team by Department" />
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24}>
          <SimpleTable data={charts.team_leave_balances || []} title="Team Leave Balances" />
        </Col>
      </Row>
    </div>
  )
}

function FinanceOfficerDashboard({ data }: { data: AnalyticsDashboard }) {
  const metrics = data.metrics || {}
  const charts = data.charts || {}

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <Row gutter={16}>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<WalletOutlined />}
            label="Total Claims"
            value={metrics.total_claims || 0}
            color={DASHBOARD_COLORS.blue}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<FileTextOutlined />}
            label="Claims Paid"
            value={metrics.claims_paid || 0}
            color={DASHBOARD_COLORS.green}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<AlertOutlined />}
            label="Pending Finance"
            value={metrics.claims_pending_finance || 0}
            color={DASHBOARD_COLORS.orange}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<AlertOutlined />}
            label="Needs Info"
            value={metrics.claims_needing_info || 0}
            color={DASHBOARD_COLORS.red}
          />
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<WalletOutlined />}
            label="Amount Claimed"
            value={`ZWL ${(metrics.total_amount_claimed_this_year || 0).toLocaleString()}`}
            color={DASHBOARD_COLORS.blue}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<WalletOutlined />}
            label="Amount Paid"
            value={`ZWL ${(metrics.total_amount_paid_this_year || 0).toLocaleString()}`}
            color={DASHBOARD_COLORS.green}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <StatCard
            icon={<WalletOutlined />}
            label="Amount Pending"
            value={`ZWL ${(metrics.total_amount_pending_this_year || 0).toLocaleString()}`}
            color={DASHBOARD_COLORS.orange}
          />
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} md={12}>
          <SimpleBarChart data={charts.claims_by_status || []} title="Claims by Status" />
        </Col>
        <Col xs={24} md={12}>
          <SimpleBarChart data={charts.claims_by_department || []} title="Claims by Department" />
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24}>
          <SimpleTable data={charts.top_claimants || []} title="Top Claimants" />
        </Col>
      </Row>
    </div>
  )
}

function EmployeeDashboard({ data }: { data: AnalyticsDashboard }) {
  const charts = data.charts || {}

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <Row gutter={16}>
        <Col xs={24}>
          <Card title="My Leave Balances" size="small">
            <Row gutter={16}>
              {(charts.leave_balances || []).map((balance: any, idx: number) => (
                <Col xs={12} sm={8} key={idx}>
                  <div style={{ padding: '12px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '4px' }}>
                      {balance.leave_type__name}
                    </div>
                    <div style={{ fontSize: '18px', fontWeight: 700, marginBottom: '4px' }}>
                      {balance.days_remaining || 0}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--muted)' }}>
                      Used: {balance.days_used} / {balance.days_entitled}
                    </div>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>

      {charts.contract_expiry_date && (
        <Row gutter={16}>
          <Col xs={24}>
            <Card
              title="Contract Information"
              size="small"
              style={{
                borderLeft: '4px solid var(--primary)',
              }}
            >
              <Space direction="vertical">
                <div>
                  <span style={{ color: 'var(--muted)', marginRight: '8px' }}>Contract Expiry:</span>
                  <span style={{ fontWeight: 700 }}>{charts.contract_expiry_date || 'N/A'}</span>
                </div>
              </Space>
            </Card>
          </Col>
        </Row>
      )}

      {charts.recent_leave_requests && charts.recent_leave_requests.length > 0 && (
        <Row gutter={16}>
          <Col xs={24}>
            <SimpleTable data={charts.recent_leave_requests} title="Recent Leave Requests" />
          </Col>
        </Row>
      )}

      {charts.upcoming_approved_leaves && charts.upcoming_approved_leaves.length > 0 && (
        <Row gutter={16}>
          <Col xs={24}>
            <SimpleTable data={charts.upcoming_approved_leaves} title="Upcoming Approved Leave" />
          </Col>
        </Row>
      )}

      {charts.my_education_claims && charts.my_education_claims.length > 0 && (
        <Row gutter={16}>
          <Col xs={24}>
            <SimpleTable data={charts.my_education_claims} title="My Education Claims" />
          </Col>
        </Row>
      )}
    </div>
  )
}

export default function AnalyticsPage() {
  const [dashboard, setDashboard] = useState<AnalyticsDashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [year, setYear] = useState<number>(new Date().getFullYear())

  const loadDashboard = async () => {
    setLoading(true)
    try {
      const res = await http.get('/analytics/my_dashboard/', { params: { year } })
      setDashboard(res.data)
    } catch (error: any) {
      console.error('Failed to load analytics:', error)
      setDashboard({
        dashboard_type: 'error',
        metrics: {},
        charts: {},
        error: error?.response?.data?.detail || 'Failed to load analytics',
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadDashboard()
  }, [year])

  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i)

  const renderDashboard = () => {
    if (!dashboard) return <Empty />

    switch (dashboard.dashboard_type) {
      case 'system_admin':
        return <SystemAdminDashboard data={dashboard} />
      case 'hr_manager':
        return <HRManagerDashboard data={dashboard} />
      case 'line_manager':
        return <LineManagerDashboard data={dashboard} />
      case 'finance_officer':
        return <FinanceOfficerDashboard data={dashboard} />
      case 'employee':
        return <EmployeeDashboard data={dashboard} />
      case 'error':
        return <Empty description={dashboard.error} />
      default:
        return <Empty description="Unknown dashboard type" />
    }
  }

  return (
    <div className="panel">
      <div className="page-header">
        <div>
          <h1>Analytics Dashboard</h1>
          <p>Role-based insights and metrics</p>
        </div>
        <Space>
          <Select
            value={year}
            onChange={setYear}
            style={{ width: 120 }}
            options={years.map((y) => ({ label: y.toString(), value: y }))}
          />
          <Button onClick={() => void loadDashboard()} loading={loading}>
            Refresh
          </Button>
        </Space>
      </div>

      {dashboard?.error && (
        <div style={{ marginBottom: '20px' }}>
          <Tag color="error">{dashboard.error}</Tag>
        </div>
      )}

      <Spin spinning={loading} indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />}>
        {renderDashboard()}
      </Spin>
    </div>
  )
}