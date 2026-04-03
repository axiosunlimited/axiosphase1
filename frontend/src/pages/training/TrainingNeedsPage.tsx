import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function TrainingNeedsPage() {
  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)
  const { options: deptOptions } = useOptions('departments', (d) => d.name)
  const { options: competencyOptions } = useOptions('competencies', (c) => `${c.name}${c.category ? ` (${c.category})` : ''}`)

  const priorityOptions = [
    { value: 'LOW', label: 'Low' },
    { value: 'MEDIUM', label: 'Medium' },
    { value: 'HIGH', label: 'High' },
  ]

  return (
    <CrudPage
      title="Training Needs"
      endpoint="training-needs"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Employee', render: (_: any, r: any) => r.employee ? `${r.employee.employee_number} ${r.employee.full_name || r.employee.email}`.trim() : '' },
        { title: 'Department', render: (_: any, r: any) => r.department?.name },
        { title: 'Competency', render: (_: any, r: any) => r.competency?.name },
        { title: 'Priority', dataIndex: 'priority' },
        { title: 'Identified By', dataIndex: 'identified_by_email' },
        { title: 'Identified At', dataIndex: 'identified_at' },
        { title: 'Description', dataIndex: 'description' },
      ]}
      fields={[
        { name: 'employee_id', label: 'Employee (optional)', type: 'select', options: employeeOptions },
        { name: 'department_id', label: 'Department (optional)', type: 'select', options: deptOptions },
        { name: 'competency_id', label: 'Competency (optional)', type: 'select', options: competencyOptions },
        { name: 'priority', label: 'Priority', type: 'select', required: true, options: priorityOptions },
        { name: 'description', label: 'Description', type: 'textarea' },
      ]}
    />
  )
}
