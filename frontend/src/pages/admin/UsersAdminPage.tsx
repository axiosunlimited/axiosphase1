import React, { useMemo, useState } from 'react'
import { Button, Form, Input, Modal, Space, message } from 'antd'
import CrudPage from '../../components/CrudPage'
import { resource } from '../../api/resources'
import { useOptions } from '../../hooks/useOptions'

const roleOptions = [
  { value: 'SYSTEM_ADMIN', label: 'SYSTEM_ADMIN' },
  { value: 'HR_MANAGER', label: 'HR_MANAGER' },
  { value: 'HR_OFFICER', label: 'HR_OFFICER' },
  { value: 'LINE_MANAGER', label: 'LINE_MANAGER' },
  { value: 'FINANCE_OFFICER', label: 'FINANCE_OFFICER' },
  { value: 'EMPLOYEE', label: 'EMPLOYEE' },
]

export default function UsersAdminPage() {
  const api = useMemo(() => resource('users'), [])
  const { options: groupOptions } = useOptions('groups', (g) => g.name)
  const { options: permOptions } = useOptions('permissions', (p) => `${p.content_type?.app_label}.${p.content_type?.model}: ${p.codename}`)

  const [pwOpen, setPwOpen] = useState(false)
  const [pwId, setPwId] = useState<number | null>(null)
  const [pwReload, setPwReload] = useState<(() => void) | null>(null)
  const [form] = Form.useForm()

  const openPw = (id: number, reload: () => void) => {
    setPwId(id)
    setPwReload(() => reload)
    form.resetFields()
    setPwOpen(true)
  }

  const submitPw = async () => {
    const vals = await form.validateFields()
    if (!pwId) return
    try {
      await api.action(pwId, 'set_password', { password: vals.password })
      message.success('Password updated')
      setPwOpen(false)
      const fn = pwReload
      setPwReload(null)
      setPwId(null)
      fn?.()
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to set password')
    }
  }

  return (
    <>
      <CrudPage
        title="Users"
        endpoint="users"
        columns={[
          { title: 'ID', dataIndex: 'id' },
          { title: 'Email', dataIndex: 'email' },
          { title: 'First Name', dataIndex: 'first_name' },
          { title: 'Last Name', dataIndex: 'last_name' },
          { title: 'Role', dataIndex: 'role' },
          {
            title: 'Active',
            render: (_: any, r: any) => (
              <span className={`badge-pill ${r.is_active ? 'badge-success' : 'badge-neutral'}`}>
                {r.is_active ? 'Active' : 'Inactive'}
              </span>
            )
          },
          {
            title: 'Staff',
            render: (_: any, r: any) => (
              r.is_staff && <span className="badge-pill badge-success">Staff</span>
            )
          },
          {
            title: 'Superuser',
            render: (_: any, r: any) => (
              r.is_superuser && <span className="badge-pill badge-success">Superuser</span>
            )
          },
          {
            title: '2FA',
            render: (_: any, r: any) => (
              <span className={`badge-pill ${r.twofa_enabled ? 'badge-success' : 'badge-neutral'}`}>
                {r.twofa_enabled ? 'Enabled' : 'Disabled'}
              </span>
            )
          },
          { title: 'Failed Logins', dataIndex: 'failed_login_attempts' },
          { title: 'Locked Until', dataIndex: 'locked_until' },
          { title: 'Joined', dataIndex: 'date_joined' },
        ]}
        fields={[
          { name: 'email', label: 'Email', type: 'text', required: true },
          { name: 'first_name', label: 'First Name', type: 'text' },
          { name: 'last_name', label: 'Last Name', type: 'text' },
          { name: 'role', label: 'Role', type: 'select', required: true, options: roleOptions },
          { name: 'is_active', label: 'Is Active', type: 'boolean' },
          { name: 'is_staff', label: 'Is Staff', type: 'boolean' },
          { name: 'is_superuser', label: 'Is Superuser', type: 'boolean' },
          { name: 'groups', label: 'Groups', type: 'multiselect', options: groupOptions },
          { name: 'user_permissions', label: 'User Permissions', type: 'multiselect', options: permOptions },
        ]}
        rowActions={(r, helpers) => (
          <Space wrap>
            <Button size="small" onClick={() => openPw(r.id, helpers.reload)}>
              Set Password
            </Button>
          </Space>
        )}
      />

      <Modal
        open={pwOpen}
        title="Set User Password"
        onCancel={() => setPwOpen(false)}
        onOk={submitPw}
        okText="Update"
        destroyOnClose
      >
        <Form layout="vertical" form={form}>
          <Form.Item
            name="password"
            label="New Password"
            rules={[
              { required: true, message: 'Password is required' },
              { min: 8, message: 'Must be at least 8 characters' },
            ]}
          >
            <Input.Password />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
