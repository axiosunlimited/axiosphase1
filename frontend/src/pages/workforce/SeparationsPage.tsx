import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function SeparationsPage() {
  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)

  const typeOptions = [
    { value: 'RESIGNATION', label: 'Resignation' },
    { value: 'RETIREMENT', label: 'Retirement' },
    { value: 'TERMINATION', label: 'Termination' },
    { value: 'CONTRACT_END', label: 'Contract End' },
    { value: 'OTHER', label: 'Other' },
  ]

  return (
    <CrudPage
      title="Separations"
      endpoint="separations"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Employee', render: (_: any, r: any) => `${r.employee?.employee_number ?? ''} ${r.employee?.full_name ?? r.employee?.email ?? ''}`.trim() },
        { title: 'Date', dataIndex: 'separation_date' },
        { title: 'Type', dataIndex: 'separation_type' },
        { title: 'Reason', dataIndex: 'reason' },
      ]}
      fields={[
        { name: 'employee_id', label: 'Employee', type: 'select', required: true, options: employeeOptions },
        { name: 'separation_date', label: 'Separation Date', type: 'date', required: true },
        { name: 'separation_type', label: 'Separation Type', type: 'select', required: true, options: typeOptions },
        { name: 'reason', label: 'Reason', type: 'textarea' },
      ]}
    />
  )
}
