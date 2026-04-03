import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  Alert,
  Button,
  Descriptions,
  Spin,
  Table,
  Tabs,
  Tag,
  Typography,
  Space,
  message,
} from 'antd'
import {
  ArrowLeftOutlined,
  CalendarOutlined,
  FileTextOutlined,
  IdcardOutlined,
  HistoryOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons'
import { http } from '../../api/client'
import { downloadBlob } from '../../api/resources'

function downloadAsFile(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export default function EmployeeProfilePage() {
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(true)
  const [employee, setEmployee] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  // Related data
  const [leaveRequests, setLeaveRequests] = useState<any[]>([])
  const [leaveBalances, setLeaveBalances] = useState<any[]>([])
  const [documents, setDocuments] = useState<any[]>([])
  const [contracts, setContracts] = useState<any[]>([])
  const [history, setHistory] = useState<any[]>([])
  const [qualifications, setQualifications] = useState<any[]>([])
  const [downloadingId, setDownloadingId] = useState<number | null>(null)

  useEffect(() => {
    if (!id) return
    let mounted = true
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const [empRes, leaveRes, balRes, docRes, contractRes, histRes] = await Promise.all([
          http.get(`/employees/${id}/`).catch(() => null),
          http.get('/leave-requests/', { params: { employee_id: id } }).catch(() => ({ data: [] })),
          http.get('/leave-balances/', { params: { employee_id: id } }).catch(() => ({ data: [] })),
          http.get('/employee-documents/', { params: { employee_id: id } }).catch(() => ({ data: [] })),
          http.get('/contracts/', { params: { employee_id: id } }).catch(() => ({ data: [] })),
          http.get('/employment-history/', { params: { employee_id: id } }).catch(() => ({ data: [] })),
        ])

        if (!mounted) return

        if (!empRes?.data) {
          setError('Employee not found')
          setLoading(false)
          return
        }

        setEmployee(empRes.data)
        setQualifications(empRes.data?.qualifications || [])
        setLeaveRequests(Array.isArray(leaveRes?.data) ? leaveRes.data : [])
        setLeaveBalances(Array.isArray(balRes?.data) ? balRes.data : [])
        setDocuments(Array.isArray(docRes?.data) ? docRes.data : [])
        setContracts(Array.isArray(contractRes?.data) ? contractRes.data : [])
        setHistory(Array.isArray(histRes?.data) ? histRes.data : [])
      } catch (e: any) {
        if (mounted) setError(e?.response?.data?.detail || 'Failed to load employee')
      } finally {
        if (mounted) setLoading(false)
      }
    })()
    return () => { mounted = false }
  }, [id])

  const statusColor = (s: string) => {
    if (!s) return 'default'
    const u = s.toUpperCase()
    if (u.includes('APPROVED') || u === 'ACTIVE' || u === 'PAID') return 'green'
    if (u.includes('REJECTED') || u === 'CANCELLED') return 'red'
    if (u.includes('PENDING') || u.includes('SUBMITTED')) return 'orange'
    return 'default'
  }

  if (loading) {
    return <div style={{ padding: '64px 0', textAlign: 'center' }}><Spin size="large" /></div>
  }

  if (error || !employee) {
    return (
      <div>
        <Link to="/employees/employees"><Button icon={<ArrowLeftOutlined />}>Back to Employees</Button></Link>
        <Alert type="error" message={error || 'Employee not found'} showIcon style={{ marginTop: 16 }} />
      </div>
    )
  }

  const emp = employee
  const user = emp.user || {}

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        <Link to="/employees/employees"><Button icon={<ArrowLeftOutlined />} type="text" /></Link>
        <div>
          <Typography.Title level={2} style={{ margin: 0, fontSize: 24, fontWeight: 800 }}>
            {user.full_name || user.first_name ? `${user.first_name} ${user.last_name}`.trim() : user.email}
          </Typography.Title>
          <Typography.Text type="secondary">{emp.employee_number} · {emp.department?.name} · {emp.position?.title}</Typography.Text>
        </div>
        <Tag color={statusColor(emp.employment_status)} style={{ marginLeft: 'auto', fontSize: 13, padding: '2px 12px' }}>
          {emp.employment_status}
        </Tag>
      </div>

      <Tabs
        defaultActiveKey="personal"
        items={[
          {
            key: 'personal',
            label: <span><IdcardOutlined /> Personal Info</span>,
            children: (
              <Descriptions bordered column={{ xs: 1, sm: 2, md: 3 }} size="small">
                <Descriptions.Item label="Title">{emp.title || '—'}</Descriptions.Item>
                <Descriptions.Item label="Gender">{emp.gender || '—'}</Descriptions.Item>
                <Descriptions.Item label="Employee Number">{emp.employee_number}</Descriptions.Item>
                <Descriptions.Item label="Email">{user.email}</Descriptions.Item>
                <Descriptions.Item label="Phone">{emp.phone || '—'}</Descriptions.Item>
                <Descriptions.Item label="Date of Birth">{emp.date_of_birth || '—'}</Descriptions.Item>
                <Descriptions.Item label="National ID">{emp.national_id || '—'}</Descriptions.Item>
                <Descriptions.Item label="Address">{emp.address || '—'}</Descriptions.Item>
                <Descriptions.Item label="Department">{emp.department?.name || '—'}</Descriptions.Item>
                <Descriptions.Item label="Position">{emp.position?.title || '—'}</Descriptions.Item>
                <Descriptions.Item label="Academic">{emp.position?.is_academic ? 'Yes' : 'No'}</Descriptions.Item>
                <Descriptions.Item label="Contract Type">{emp.contract_type || '—'}</Descriptions.Item>
                <Descriptions.Item label="Hire Date">{emp.hire_date || '—'}</Descriptions.Item>
                <Descriptions.Item label="Contract End Date">{emp.end_date || '—'}</Descriptions.Item>
                <Descriptions.Item label="Grade">{emp.grade || '—'}</Descriptions.Item>
                <Descriptions.Item label="School">{emp.school || '—'}</Descriptions.Item>
                <Descriptions.Item label="Line Manager">
                  {emp.line_manager ? `${emp.line_manager.first_name || ''} ${emp.line_manager.last_name || ''}`.trim() || emp.line_manager.email : '—'}
                </Descriptions.Item>
                <Descriptions.Item label="Role">{user.role}</Descriptions.Item>
                <Descriptions.Item label="2FA Enabled">{user.twofa_enabled ? <Tag color="green">Yes</Tag> : <Tag>No</Tag>}</Descriptions.Item>
              </Descriptions>
            ),
          },
          {
            key: 'qualifications',
            label: <span><SafetyCertificateOutlined /> Qualifications</span>,
            children: qualifications.length ? (
              <Table
                dataSource={qualifications}
                columns={[
                  { title: 'Qualification', dataIndex: 'name' },
                  { title: 'Institution', dataIndex: 'institution' },
                  { title: 'Year', dataIndex: 'year_obtained', width: 80 },
                ]}
                size="small"
                pagination={false}
                rowKey="id"
              />
            ) : <Typography.Text type="secondary">No qualifications recorded.</Typography.Text>,
          },
          {
            key: 'leave',
            label: <span><CalendarOutlined /> Leave Records</span>,
            children: (
              <div>
                {leaveBalances.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <Typography.Text strong style={{ display: 'block', marginBottom: 8 }}>Current Balances</Typography.Text>
                    <Table
                      dataSource={leaveBalances}
                      columns={[
                        { title: 'Leave Type', render: (_: any, r: any) => r.leave_type?.name || r.leave_type_name || '—' },
                        { title: 'Year', dataIndex: 'year', width: 70 },
                        { title: 'Entitled', dataIndex: 'days_entitled', width: 80 },
                        { title: 'Used', dataIndex: 'days_used', width: 80 },
                        { title: 'Remaining', dataIndex: 'days_remaining', width: 90, render: (v: number) => <Tag color={v > 0 ? 'green' : 'red'}>{v}</Tag> },
                      ]}
                      size="small"
                      pagination={false}
                      rowKey="id"
                    />
                  </div>
                )}
                <Typography.Text strong style={{ display: 'block', marginBottom: 8 }}>Leave Requests</Typography.Text>
                {leaveRequests.length ? (
                  <Table
                    dataSource={leaveRequests}
                    columns={[
                      { title: 'Type', render: (_: any, r: any) => r.leave_type?.name || r.leave_type_name || '—' },
                      { title: 'Start', dataIndex: 'start_date' },
                      { title: 'End', dataIndex: 'end_date' },
                      { title: 'Days', dataIndex: 'days_requested', width: 60 },
                      { title: 'Status', dataIndex: 'status', render: (s: string) => <Tag color={statusColor(s)}>{s}</Tag> },
                      { title: 'Created', dataIndex: 'created_at', render: (v: string) => v ? new Date(v).toLocaleDateString() : '' },
                    ]}
                    size="small"
                    pagination={{ pageSize: 10 }}
                    rowKey="id"
                  />
                ) : <Typography.Text type="secondary">No leave requests found.</Typography.Text>}
              </div>
            ),
          },
          {
            key: 'documents',
            label: <span><FileTextOutlined /> Documents</span>,
            children: documents.length ? (
              <Table
                dataSource={documents}
                columns={[
                  { title: 'Category', dataIndex: 'category', render: (c: string) => c?.replace(/_/g, ' ') },
                  { title: 'File', dataIndex: 'original_name' },
                  { title: 'Version', dataIndex: 'version', width: 70 },
                  { title: 'Latest', dataIndex: 'is_latest', width: 70, render: (v: boolean) => v ? <Tag color="green">Yes</Tag> : <Tag>No</Tag> },
                  { title: 'Size', dataIndex: 'size_bytes', width: 90, render: (v: number) => v ? `${(v / 1024).toFixed(1)} KB` : '—' },
                  { title: 'Uploaded', dataIndex: 'uploaded_at', render: (v: string) => v ? new Date(v).toLocaleDateString() : '' },
                  {
                    title: 'Actions',
                    width: 100,
                    render: (_: any, r: any) => (
                      <Button
                        size="small"
                        loading={downloadingId === r.id}
                        onClick={async () => {
                          try {
                            setDownloadingId(r.id)
                            const blob = await downloadBlob(`/employee-documents/${r.id}/download/`)
                            downloadAsFile(blob, r.original_name || `document_${r.id}`)
                          } catch (e: any) {
                            message.error(e?.response?.data?.detail || 'Download failed')
                          } finally {
                            setDownloadingId(null)
                          }
                        }}
                      >
                        Download
                      </Button>
                    ),
                  },
                ]}
                size="small"
                pagination={{ pageSize: 10 }}
                rowKey="id"
              />
            ) : <Typography.Text type="secondary">No documents uploaded.</Typography.Text>,
          },
          {
            key: 'contracts',
            label: <span><FileTextOutlined /> Contracts</span>,
            children: contracts.length ? (
              <Table
                dataSource={contracts}
                columns={[
                  { title: 'Start Date', dataIndex: 'start_date' },
                  { title: 'End Date', dataIndex: 'end_date', render: (v: string) => v || 'Open-ended' },
                  { title: 'Probation End', dataIndex: 'probation_end_date', render: (v: string) => v || '—' },
                  { title: 'Active', dataIndex: 'is_active', render: (v: boolean) => v ? <Tag color="green">Yes</Tag> : <Tag>No</Tag> },
                ]}
                size="small"
                pagination={false}
                rowKey="id"
              />
            ) : <Typography.Text type="secondary">No contracts found.</Typography.Text>,
          },
          {
            key: 'history',
            label: <span><HistoryOutlined /> Employment History</span>,
            children: history.length ? (
              <Table
                dataSource={history}
                columns={[
                  { title: 'Department', render: (_: any, r: any) => r.department?.name || '—' },
                  { title: 'Position', render: (_: any, r: any) => r.position?.title || '—' },
                  { title: 'Status', dataIndex: 'employment_status' },
                  { title: 'Contract', dataIndex: 'contract_type' },
                  { title: 'Start', dataIndex: 'start_date' },
                  { title: 'End', dataIndex: 'end_date', render: (v: string) => v || 'Current' },
                  { title: 'Note', dataIndex: 'note' },
                ]}
                size="small"
                pagination={false}
                rowKey="id"
              />
            ) : <Typography.Text type="secondary">No employment history recorded.</Typography.Text>,
          },
        ]}
      />
    </div>
  )
}
