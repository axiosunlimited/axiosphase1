import React, { useEffect, useMemo, useState } from 'react'
import {
  Alert,
  Button,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Switch,
  Table,
  Typography,
  message,
} from 'antd'
import { CopyOutlined, PlusOutlined, ReloadOutlined, SendOutlined } from '@ant-design/icons'
import { createInvite, listInvites, resendInvite, type InviteListItem, type InviteStatus } from '../../api/auth'

const roleOptions = [
  { value: 'SYSTEM_ADMIN', label: 'SYSTEM_ADMIN' },
  { value: 'HR_MANAGER', label: 'HR_MANAGER' },
  { value: 'HR_OFFICER', label: 'HR_OFFICER' },
  { value: 'LINE_MANAGER', label: 'LINE_MANAGER' },
  { value: 'FINANCE_OFFICER', label: 'FINANCE_OFFICER' },
  { value: 'EMPLOYEE', label: 'EMPLOYEE' },
]

function formatDateTime(val?: string | null) {
  if (!val) return ''
  const d = new Date(val)
  if (Number.isNaN(d.getTime())) return String(val)
  return d.toLocaleString()
}

function StatusPill({ status }: { status: InviteStatus }) {
  const cls =
    status === 'pending'
      ? 'badge-success'
      : status === 'used'
      ? 'badge-neutral'
      : 'badge-warning'
  return <span className={`badge-pill ${cls}`}>{status}</span>
}

async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    message.success('Copied')
  } catch {
    message.error('Copy failed')
  }
}

export default function UserInvitesPage() {
  const [rows, setRows] = useState<InviteListItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [status, setStatus] = useState<InviteStatus | 'all'>('all')
  const [email, setEmail] = useState('')

  const [open, setOpen] = useState(false)
  const [form] = Form.useForm()

  const reload = async () => {
    setError(null)
    setLoading(true)
    try {
      const data = await listInvites({
        status: status === 'all' ? undefined : status,
        email: email.trim() ? email.trim() : undefined,
      })
      setRows(Array.isArray(data) ? data : [])
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load invites')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void reload()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const openCreate = () => {
    form.resetFields()
    form.setFieldsValue({ role: 'EMPLOYEE', auto_activate: false })
    setOpen(true)
  }

  const submitCreate = async () => {
    const vals = await form.validateFields()
    try {
      const res = await createInvite({
        email: vals.email,
        first_name: vals.first_name,
        last_name: vals.last_name,
        role: vals.role,
        auto_activate: !!vals.auto_activate,
        expires_in_days: vals.expires_in_days ? Number(vals.expires_in_days) : undefined,
      })
      setOpen(false)
      await reload()

      Modal.info({
        title: 'Invite created',
        content: (
          <div>
            <div style={{ marginBottom: 8 }}>
              <strong>{res.email}</strong>
            </div>
            <div style={{ marginBottom: 8 }}>
              Expires: {formatDateTime(res.expires_at)}
            </div>
            <div style={{ marginBottom: 8 }}>
              Email sent: <strong>{res.email_sent ? 'Yes' : 'No'}</strong>
              {!res.email_sent && res.email_error ? (
                <span style={{ marginLeft: 8, color: '#b45309' }}>({res.email_error})</span>
              ) : null}
            </div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
              <Input value={res.activation_link} readOnly />
              <Button icon={<CopyOutlined />} onClick={() => copyToClipboard(res.activation_link)}>
                Copy link
              </Button>
            </div>
          </div>
        ),
        okText: 'Close',
      })
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to create invite')
    }
  }

  const onResend = async (inviteId: number) => {
    try {
      const res = await resendInvite(inviteId)
      await reload()
      Modal.info({
        title: 'Invite resent',
        content: (
          <div>
            <div style={{ marginBottom: 8 }}>
              Expires: {formatDateTime(res.expires_at)}
            </div>
            <div style={{ marginBottom: 8 }}>
              Email sent: <strong>{res.email_sent ? 'Yes' : 'No'}</strong>
              {!res.email_sent && res.email_error ? (
                <span style={{ marginLeft: 8, color: '#b45309' }}>({res.email_error})</span>
              ) : null}
            </div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
              <Input value={res.activation_link} readOnly />
              <Button icon={<CopyOutlined />} onClick={() => copyToClipboard(res.activation_link)}>
                Copy link
              </Button>
            </div>
          </div>
        ),
        okText: 'Close',
      })
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to resend invite')
    }
  }

  const columns = useMemo(
    () => [
      { title: 'ID', dataIndex: 'id', width: 60 },
      {
        title: 'Email',
        dataIndex: 'email',
        width: 230,
        ellipsis: true,
      },
      { title: 'Role', dataIndex: 'role', width: 140, ellipsis: true },
      {
        title: 'Auto Activate',
        width: 110,
        align: 'center' as const,
        render: (_: any, r: InviteListItem) => (r.auto_activate ? 'Yes' : 'No'),
      },
      {
        title: 'Status',
        width: 100,
        align: 'center' as const,
        render: (_: any, r: InviteListItem) => <StatusPill status={r.status} />,
      },
      {
        title: 'Expires',
        dataIndex: 'expires_at',
        width: 170,
        render: (v: string) => formatDateTime(v),
      },
      {
        title: 'Used',
        dataIndex: 'used_at',
        width: 170,
        render: (v: string | null) => (v ? formatDateTime(v) : '—'),
      },
      {
        title: 'Created By',
        dataIndex: 'created_by_email',
        width: 200,
        ellipsis: true,
      },
      {
        title: 'Created',
        dataIndex: 'created_at',
        width: 170,
        render: (v: string) => formatDateTime(v),
      },
      {
        title: 'Actions',
        key: 'actions',
        fixed: 'right' as const,
        width: 120,
        render: (_: any, r: InviteListItem) => (
          <Button
            size="small"
            icon={<SendOutlined />}
            disabled={r.status !== 'pending'}
            onClick={() => onResend(r.id)}
          >
            Resend
          </Button>
        ),
      },
    ],
    [status, email]
  )

  return (
    <div className="panel">
      <div className="page-header">
        <Typography.Title level={2} style={{ margin: 0, fontSize: 26, fontWeight: 800, letterSpacing: '-0.3px' }}>
          User Invites
        </Typography.Title>

        <Space wrap style={{ flex: 1, justifyContent: 'flex-end' }}>
          <Select
            value={status}
            onChange={setStatus}
            style={{ width: 150 }}
            options={[
              { value: 'all', label: 'All statuses' },
              { value: 'pending', label: 'Pending' },
              { value: 'used', label: 'Used' },
              { value: 'expired', label: 'Expired' },
            ]}
          />
          <Input
            placeholder="Filter by email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ width: 220 }}
            allowClear
          />
          <Button className="btn-refresh" icon={<ReloadOutlined />} onClick={reload}>
            Refresh
          </Button>
          <Button type="primary" className="btn-new" icon={<PlusOutlined />} onClick={openCreate}>
            New Invite
          </Button>
        </Space>
      </div>

      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16, borderRadius: 10 }} />}

      <Table
        rowKey="id"
        loading={loading}
        dataSource={rows}
        columns={columns as any}
        scroll={{ x: 1500 }}
        pagination={{ pageSize: 8, showSizeChanger: false, position: ['bottomCenter'] }}
      />

      <Modal
        open={open}
        title="Create Invite"
        onCancel={() => setOpen(false)}
        onOk={submitCreate}
        okText="Create"
        destroyOnClose
      >
        <Form layout="vertical" form={form} requiredMark={false}>
          <Form.Item
            name="email"
            label="Email"
            rules={[{ required: true, type: 'email', message: 'Valid email is required' }]}
          >
            <Input placeholder="new.user@example.com" />
          </Form.Item>

          <div style={{ display: 'flex', gap: 12 }}>
            <Form.Item name="first_name" label="First Name" style={{ flex: 1 }}>
              <Input placeholder="First name" />
            </Form.Item>
            <Form.Item name="last_name" label="Last Name" style={{ flex: 1 }}>
              <Input placeholder="Last name" />
            </Form.Item>
          </div>

          <Form.Item name="role" label="Role" rules={[{ required: true, message: 'Role is required' }]}>
            <Select options={roleOptions} />
          </Form.Item>

          <Form.Item name="auto_activate" label="Auto activate on acceptance" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item
            name="expires_in_days"
            label="Expires in days (optional)"
            tooltip="If omitted, backend uses INVITE_EXPIRE_DAYS"
          >
            <Input type="number" min={1} max={90} placeholder="e.g. 7" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
