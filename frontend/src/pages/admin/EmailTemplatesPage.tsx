import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function EmailTemplatesPage() {
  return (
    <CrudPage
      title="Email Templates"
      endpoint="email-templates"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Key', dataIndex: 'key' },
        { title: 'Enabled', dataIndex: 'enabled', render: (_: any, r: any) => (r.enabled ? 'Yes' : 'No') },
        { title: 'Subject', dataIndex: 'subject_template' },
        { title: 'Updated', dataIndex: 'updated_at' },
      ]}
      fields={[
        { name: 'key', label: 'Key', type: 'text', required: true },
        { name: 'enabled', label: 'Enabled', type: 'boolean' },
        { name: 'subject_template', label: 'Subject Template', type: 'text', required: true },
        { name: 'body_template', label: 'Body Template', type: 'textarea', required: true },
      ]}
    />
  )
}
