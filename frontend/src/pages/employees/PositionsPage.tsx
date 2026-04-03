import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function PositionsPage() {
  const { options: deptOptions } = useOptions('departments', (d) => `${d.name}${d.code ? ` (${d.code})` : ''}`)

  return (
    <CrudPage
      title="Positions"
      endpoint="positions"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Title', dataIndex: 'title' },
        { title: 'Department', render: (_: any, r: any) => r.department?.name },
        { title: 'Academic', render: (_: any, r: any) => String(!!r.is_academic) },
      ]}
      fields={[
        { name: 'title', label: 'Title', type: 'text', required: true },
        { name: 'department_id', label: 'Department', type: 'select', required: true, options: deptOptions },
        { name: 'is_academic', label: 'Academic', type: 'boolean' },
      ]}
    />
  )
}
