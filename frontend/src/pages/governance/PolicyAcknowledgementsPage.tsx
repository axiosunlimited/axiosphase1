import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function PolicyAcknowledgementsPage() {
  const { options: policyOptions } = useOptions('policies', (p) => p.title)
  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)

  return (
    <CrudPage
      title="Policy Acknowledgements"
      endpoint="policy-acknowledgements"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Policy', dataIndex: 'policy_title' },
        {
          title: 'Employee',
          render: (_: any, r: any) =>
            `${r.employee?.employee_number ?? ''} ${r.employee?.full_name ?? r.employee?.email ?? ''}`.trim(),
        },
        { title: 'Acknowledged At', dataIndex: 'acknowledged_at' },
      ]}
      fields={[
        { name: 'policy', label: 'Policy', type: 'select', required: true, options: policyOptions },
        { name: 'employee_id', label: 'Employee', type: 'select', required: true, options: employeeOptions },
      ]}
    />
  )
}
