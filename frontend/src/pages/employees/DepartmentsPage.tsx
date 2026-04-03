import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function DepartmentsPage() {
  return (
    <CrudPage
      title="Departments"
      endpoint="departments"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Name', dataIndex: 'name' },
        { title: 'Code', dataIndex: 'code' },
      ]}
      fields={[
        { name: 'name', label: 'Name', type: 'text', required: true },
        { name: 'code', label: 'Code', type: 'text' },
      ]}
    />
  )
}
