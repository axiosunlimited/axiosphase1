import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'
import { useAuth } from '../../context/AuthContext'

export default function LeaveBalancesPage() {
  const { user } = useAuth()
  const isEmployee = user?.role === 'EMPLOYEE'
  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)
  const { options: leaveTypeOptions } = useOptions('leave-types', (lt) => lt.name)

  return (
    <CrudPage
      title="Leave Balances"
      endpoint="leave-balances"
      readOnly={isEmployee}
      columns={[
        { title: 'Employee', render: (_: any, r: any) => `${r.employee?.employee_number ?? ''} ${r.employee?.full_name ?? r.employee?.email ?? ''}`.trim() },
        { title: 'Leave Type', render: (_: any, r: any) => r.leave_type?.name },
        { title: 'Year', dataIndex: 'year' },
        { title: 'Entitled', dataIndex: 'days_entitled' },
        { title: 'Used', dataIndex: 'days_used' },
        { title: 'Remaining', dataIndex: 'days_remaining' },
      ]}
      fields={[
        { name: 'employee_id', label: 'Employee', type: 'select', required: true, options: employeeOptions },
        { name: 'leave_type_id', label: 'Leave Type', type: 'select', required: true, options: leaveTypeOptions },
        { name: 'year', label: 'Year', type: 'number', required: true },
        { name: 'days_entitled', label: 'Days Entitled', type: 'number', required: true },
        { name: 'days_used', label: 'Days Used', type: 'number', required: true },
      ]}
    />
  )
}
