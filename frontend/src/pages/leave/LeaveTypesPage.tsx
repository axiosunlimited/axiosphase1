import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useAuth } from '../../context/AuthContext'

export default function LeaveTypesPage() {
  const { user } = useAuth()
  const isEmployee = user?.role === 'EMPLOYEE'

  return (
    <CrudPage
      title="Leave Types"
      endpoint="leave-types"
      readOnly={isEmployee}
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Name', dataIndex: 'name' },
        { title: 'Default Days/Year', dataIndex: 'default_days_per_year' },
        { title: 'Requires Approval', render: (_: any, r: any) => String(!!r.requires_approval) },
      ]}
      fields={[
        { name: 'name', label: 'Name', type: 'text', required: true },
        { name: 'default_days_per_year', label: 'Default Days Per Year', type: 'number', required: true },
        { name: 'requires_approval', label: 'Requires Approval', type: 'boolean' },
      ]}
    />
  )
}
