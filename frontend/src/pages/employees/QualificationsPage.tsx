import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function QualificationsPage() {
  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)

  return (
    <CrudPage
      title="Qualifications"
      endpoint="qualifications"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Employee', render: (_: any, r: any) => `${r.employee?.employee_number ?? ''} ${r.employee?.full_name ?? r.employee?.email ?? ''}`.trim() },
        { title: 'Name', dataIndex: 'name' },
        { title: 'Institution', dataIndex: 'institution' },
        { title: 'Year', dataIndex: 'year_obtained' },
      ]}
      fields={[
        { name: 'employee_id', label: 'Employee', type: 'select', required: true, options: employeeOptions },
        { name: 'name', label: 'Qualification', type: 'text', required: true },
        { name: 'institution', label: 'Institution', type: 'text' },
        { name: 'year_obtained', label: 'Year Obtained', type: 'number' },
      ]}
    />
  )
}
