import React from 'react'
import { Button } from 'antd'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function ApplicantsPage() {
  const { options: vacancyOptions } = useOptions('vacancies', (v) => `${v.title} (${v.status})`)

  return (
    <CrudPage
      title="Applicants"
      endpoint="applicants"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Vacancy', dataIndex: 'vacancy' },
        { title: 'Name', render: (_: any, r: any) => `${r.first_name ?? ''} ${r.last_name ?? ''}`.trim() },
        { title: 'Email', dataIndex: 'email' },
        { title: 'Phone', dataIndex: 'phone' },
        { title: 'Status', dataIndex: 'status' },
        { title: 'Created', dataIndex: 'created_at' },
        {
          title: 'CV',
          render: (_: any, r: any) =>
            r.cv ? (
              <Button type="link" href={r.cv} target="_blank" rel="noreferrer">
                Download
              </Button>
            ) : (
              ''
            ),
        },
      ]}
      fields={[
        { name: 'vacancy', label: 'Vacancy', type: 'select', required: true, options: vacancyOptions },
        { name: 'first_name', label: 'First Name', type: 'text', required: true },
        { name: 'last_name', label: 'Last Name', type: 'text', required: true },
        { name: 'email', label: 'Email', type: 'text', required: true },
        { name: 'phone', label: 'Phone', type: 'text' },
        { name: 'status', label: 'Status', type: 'text' },
        { name: 'cv', label: 'CV', type: 'file' },
      ]}
    />
  )
}
