import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function AppraisalTemplatesPage() {
  return (
    <CrudPage
      title="Appraisal Templates"
      endpoint="appraisal-templates"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Name', dataIndex: 'name' },
      ]}
      fields={[
        { name: 'name', label: 'Name', type: 'text', required: true },
        { name: 'schema', label: 'Schema', type: 'json' },
      ]}
    />
  )
}
