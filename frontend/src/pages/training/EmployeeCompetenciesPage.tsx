import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function EmployeeCompetenciesPage() {
  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)
  const { options: competencyOptions } = useOptions('competencies', (c) => `${c.name}${c.category ? ` (${c.category})` : ''}`)

  return (
    <CrudPage
      title="Employee Competencies"
      endpoint="employee-competencies"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Employee', render: (_: any, r: any) => `${r.employee?.employee_number ?? ''} ${r.employee?.full_name ?? r.employee?.email ?? ''}`.trim() },
        { title: 'Competency', render: (_: any, r: any) => r.competency?.name },
        { title: 'Category', render: (_: any, r: any) => r.competency?.category },
        { title: 'Level', dataIndex: 'level' },
        { title: 'Last Assessed', dataIndex: 'last_assessed' },
        { title: 'Notes', dataIndex: 'notes' },
      ]}
      fields={[
        { name: 'employee_id', label: 'Employee', type: 'select', required: true, options: employeeOptions },
        { name: 'competency_id', label: 'Competency', type: 'select', required: true, options: competencyOptions },
        { name: 'level', label: 'Level (1–5)', type: 'number', required: true },
        { name: 'last_assessed', label: 'Last Assessed', type: 'date' },
        { name: 'notes', label: 'Notes', type: 'textarea' },
      ]}
    />
  )
}
