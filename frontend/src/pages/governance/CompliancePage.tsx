import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function CompliancePage() {
  return (
    <CrudPage
      title="Compliance Items"
      endpoint="compliance-items"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Title', dataIndex: 'title' },
        { title: 'Category', dataIndex: 'category' },
        { title: 'Due Date', dataIndex: 'due_date' },
        { title: 'Status', dataIndex: 'status' },
        { title: 'Created', dataIndex: 'created_at' },
      ]}
      fields={[
        { name: 'title', label: 'Title', type: 'text', required: true },
        { name: 'description', label: 'Description', type: 'textarea' },
        { name: 'category', label: 'Category', type: 'text' },
        { name: 'due_date', label: 'Due Date', type: 'date' },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          options: [
            { label: 'Pending', value: 'PENDING' },
            { label: 'Compliant', value: 'COMPLIANT' },
            { label: 'Non-Compliant', value: 'NON_COMPLIANT' },
          ],
        },
        { name: 'notes', label: 'Notes', type: 'textarea' },
      ]}
    />
  )
}
