import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function DisciplinaryCasesPage() {
  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)

  return (
    <CrudPage
      title="Disciplinary Cases"
      endpoint="disciplinary-cases"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        {
          title: 'Employee',
          render: (_: any, r: any) =>
            `${r.employee?.employee_number ?? ''} ${r.employee?.full_name ?? r.employee?.email ?? ''}`.trim(),
        },
        { title: 'Description', dataIndex: 'case_description' },
        { title: 'Date', dataIndex: 'date' },
        { title: 'Outcome', dataIndex: 'outcome' },
        { title: 'Created', dataIndex: 'created_at' },
      ]}
      fields={[
        { name: 'employee_id', label: 'Employee', type: 'select', required: true, options: employeeOptions },
        { name: 'case_description', label: 'Case Description', type: 'textarea', required: true },
        { name: 'date', label: 'Date', type: 'date', required: true },
        { name: 'outcome', label: 'Outcome', type: 'textarea' },
        { name: 'supporting_document', label: 'Supporting Document', type: 'file' },
      ]}
    />
  )
}
