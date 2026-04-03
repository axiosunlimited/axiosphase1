import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function GrievancesPage() {
  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)

  return (
    <CrudPage
      title="Grievances"
      endpoint="grievances"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        {
          title: 'Employee',
          render: (_: any, r: any) =>
            `${r.employee?.employee_number ?? ''} ${r.employee?.full_name ?? r.employee?.email ?? ''}`.trim(),
        },
        { title: 'Subject', dataIndex: 'subject' },
        { title: 'Date Filed', dataIndex: 'date_filed' },
        { title: 'Status', dataIndex: 'status' },
        { title: 'Resolution', dataIndex: 'resolution' },
        { title: 'Created', dataIndex: 'created_at' },
      ]}
      fields={[
        { name: 'employee_id', label: 'Employee', type: 'select', required: true, options: employeeOptions },
        { name: 'subject', label: 'Subject', type: 'text', required: true },
        { name: 'description', label: 'Description', type: 'textarea', required: true },
        { name: 'date_filed', label: 'Date Filed', type: 'date', required: true },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          options: [
            { label: 'Open', value: 'OPEN' },
            { label: 'Under Review', value: 'UNDER_REVIEW' },
            { label: 'Resolved', value: 'RESOLVED' },
            { label: 'Closed', value: 'CLOSED' },
          ],
        },
        { name: 'resolution', label: 'Resolution', type: 'textarea' },
      ]}
    />
  )
}
