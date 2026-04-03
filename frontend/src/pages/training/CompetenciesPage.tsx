import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function CompetenciesPage() {
  return (
    <CrudPage
      title="Competencies"
      endpoint="competencies"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Name', dataIndex: 'name' },
        { title: 'Category', dataIndex: 'category' },
        { title: 'Description', dataIndex: 'description' },
      ]}
      fields={[
        { name: 'name', label: 'Name', type: 'text', required: true },
        { name: 'category', label: 'Category', type: 'text' },
        { name: 'description', label: 'Description', type: 'textarea' },
      ]}
    />
  )
}
