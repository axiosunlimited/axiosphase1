import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function EstablishmentPage() {
  const { options: deptOptions } = useOptions('departments', (d) => d.name)
  const { options: posOptions } = useOptions('positions', (p) => `${p.title} — ${p.department?.name ?? ''}`)

  return (
    <CrudPage
      title="Staff Establishment"
      endpoint="establishment"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Year', dataIndex: 'year' },
        { title: 'Department', render: (_: any, r: any) => r.department?.name },
        { title: 'Position', render: (_: any, r: any) => r.position?.title },
        { title: 'Budgeted Headcount', dataIndex: 'budgeted_headcount' },
      ]}
      fields={[
        { name: 'year', label: 'Year', type: 'number', required: true },
        { name: 'department_id', label: 'Department', type: 'select', required: true, options: deptOptions },
        { name: 'position_id', label: 'Position', type: 'select', required: true, options: posOptions },
        { name: 'budgeted_headcount', label: 'Budgeted Headcount', type: 'number', required: true },
      ]}
    />
  )
}
