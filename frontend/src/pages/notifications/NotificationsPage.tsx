import React, { useMemo } from 'react'
import { Button, Space, message } from 'antd'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'
import { resource } from '../../api/resources'
import { useAuth } from '../../context/AuthContext'

export default function NotificationsPage() {
  const { user } = useAuth()
  const isAdmin = ['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'].includes(user?.role || '')

  const { options: userOptions } = useOptions('users', (u) => `${u.email} (${u.role})`)
  const api = useMemo(() => resource('notifications'), [])

  return (
    <CrudPage
      title="Notifications"
      endpoint="notifications"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'User', render: (_: any, r: any) => r.user_email || r.user },
        { title: 'Title', dataIndex: 'title' },
        { title: 'Message', dataIndex: 'message' },
        { title: 'Read', render: (_: any, r: any) => String(!!r.is_read) },
        { title: 'Created', dataIndex: 'created_at' },
      ]}
      fields={[
        {
          name: 'user_id',
          label: 'Recipient (optional)',
          type: 'select',
          options: userOptions,
          hidden: () => !isAdmin,
        },
        { name: 'title', label: 'Title', type: 'text', required: true },
        { name: 'message', label: 'Message', type: 'textarea', required: true },
        { name: 'is_read', label: 'Is Read', type: 'boolean' },
      ]}
      rowActions={(r, helpers) => (
        <Space wrap>
          {!r.is_read && (
            <Button
              size="small"
              onClick={async () => {
                try {
                  await api.action(r.id, 'mark_read')
                  message.success('Marked as read')
                  helpers.reload()
                } catch (e: any) {
                  message.error(e?.response?.data?.detail || 'Action failed')
                }
              }}
            >
              Mark Read
            </Button>
          )}
        </Space>
      )}
    />
  )
}
