import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function PoliciesPage() {
  return (
    <CrudPage
      title="Policies"
      endpoint="policies"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Title', dataIndex: 'title' },
        { title: 'Version', dataIndex: 'version' },
        { title: 'Effective Date', dataIndex: 'effective_date' },
        { title: 'Active', dataIndex: 'is_active', render: (_: any, r: any) => (r.is_active ? 'Yes' : 'No') },
        { title: 'Created', dataIndex: 'created_at' },
      ]}
      fields={[
        { name: 'title', label: 'Title', type: 'text', required: true },
        { name: 'description', label: 'Description', type: 'textarea' },
        { name: 'document', label: 'Policy Document', type: 'file' },
        { name: 'version', label: 'Version', type: 'text' },
        { name: 'effective_date', label: 'Effective Date', type: 'date' },
        { name: 'is_active', label: 'Active', type: 'boolean' },
      ]}
    />
  )
}
