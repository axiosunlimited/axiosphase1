import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'
import { useAuth } from '../../context/AuthContext'

export default function ContractsPage() {
  const { user } = useAuth()
  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)

  const role = user?.role || ''
  const readOnly = !['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER'].includes(role)
  const isEmployee = role === 'EMPLOYEE'

  return (
    <CrudPage
      title="Contracts"
      endpoint="contracts"
      readOnly={readOnly}
      columns={[
        { title: 'ID', dataIndex: 'id' },
        {
          title: 'Employee',
          render: (_: any, r: any) =>
            `${r.employee?.employee_number ?? ''} ${r.employee?.full_name ?? r.employee?.email ?? ''}`.trim(),
        },
        { title: 'Start', dataIndex: 'start_date' },
        { title: 'End', dataIndex: 'end_date' },
        { title: 'Probation End', dataIndex: 'probation_end_date' },
        { title: 'Type', dataIndex: 'contract_type' },
        { title: 'Active', dataIndex: 'is_active', render: (_: any, r: any) => (r.is_active ? 'Yes' : 'No') },
        { title: 'Created', dataIndex: 'created_at' },
      ]}
      fields={[
        { name: 'employee_id', label: 'Employee', type: 'select', required: true, options: employeeOptions, hidden: () => isEmployee },
        { name: 'start_date', label: 'Start Date', type: 'date', required: true },
        { name: 'end_date', label: 'End Date', type: 'date' },
        { name: 'probation_end_date', label: 'Probation End Date', type: 'date' },
        {
          name: 'contract_type',
          label: 'Contract Type',
          type: 'select',
          required: true,
          options: [
            { label: 'Permanent', value: 'PERMANENT' },
            { label: 'Fixed Term', value: 'FIXED_TERM' },
            { label: 'Part time', value: 'PART_TIME' },
            { label: 'Casual', value: 'CASUAL' },
            { label: 'Consultancy', value: 'CONSULTANCY' },
          ],
        },
      ]}
    />
  )
}
