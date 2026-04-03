import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function SystemSettingsPage() {
  return (
    <CrudPage
      title="System Settings"
      endpoint="system-settings"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Key', dataIndex: 'key' },
        { title: 'Value', dataIndex: 'value', render: (_: any, r: any) => JSON.stringify(r.value ?? null) },
        { title: 'Updated', dataIndex: 'updated_at' },
      ]}
      fields={[
        { name: 'key', label: 'Key', type: 'text', required: true },
        { name: 'value', label: 'Value (JSON)', type: 'json' },
      ]}
    />
  )
}
