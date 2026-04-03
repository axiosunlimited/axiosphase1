import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function NotificationSettingsPage() {
  return (
    <CrudPage
      title="Notification Settings"
      endpoint="notification-settings"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Key', dataIndex: 'key' },
        { title: 'Enabled', dataIndex: 'enabled', render: (_: any, r: any) => (r.enabled ? 'Yes' : 'No') },
        { title: 'Config', dataIndex: 'config', render: (_: any, r: any) => JSON.stringify(r.config || {}) },
        { title: 'Updated', dataIndex: 'updated_at' },
      ]}
      fields={[
        { name: 'key', label: 'Key', type: 'text', required: true },
        { name: 'enabled', label: 'Enabled', type: 'boolean' },
        { name: 'config', label: 'Config (JSON)', type: 'json' },
      ]}
    />
  )
}
