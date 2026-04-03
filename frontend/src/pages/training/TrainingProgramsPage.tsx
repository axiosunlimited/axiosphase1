import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function TrainingProgramsPage() {
  return (
    <CrudPage
      title="Training Programs"
      endpoint="training-programs"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Title', dataIndex: 'title' },
        { title: 'Provider', dataIndex: 'provider' },
        { title: 'Category', dataIndex: 'category' },
        { title: 'Start', dataIndex: 'start_date' },
        { title: 'End', dataIndex: 'end_date' },
        { title: 'Estimated Cost', dataIndex: 'estimated_cost' },
      ]}
      fields={[
        { name: 'title', label: 'Title', type: 'text', required: true },
        { name: 'provider', label: 'Provider', type: 'text' },
        { name: 'category', label: 'Category', type: 'text' },
        { name: 'description', label: 'Description', type: 'textarea' },
        { name: 'start_date', label: 'Start Date', type: 'date' },
        { name: 'end_date', label: 'End Date', type: 'date' },
        { name: 'estimated_cost', label: 'Estimated Cost', type: 'number' },
      ]}
    />
  )
}
