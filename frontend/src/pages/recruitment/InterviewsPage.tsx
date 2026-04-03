import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function InterviewsPage() {
  const { options: applicantOptions } = useOptions('applicants', (a) => `${a.first_name} ${a.last_name} — ${a.email}`)

  return (
    <CrudPage
      title="Interviews"
      endpoint="interviews"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Applicant', dataIndex: 'applicant' },
        { title: 'Scheduled At', dataIndex: 'scheduled_at' },
        { title: 'Location', dataIndex: 'location' },
        { title: 'Outcome', dataIndex: 'outcome' },
      ]}
      fields={[
        { name: 'applicant', label: 'Applicant', type: 'select', required: true, options: applicantOptions },
        { name: 'scheduled_at', label: 'Scheduled At', type: 'datetime', required: true },
        { name: 'location', label: 'Location', type: 'text' },
        { name: 'notes', label: 'Notes', type: 'textarea' },
        { name: 'outcome', label: 'Outcome', type: 'text' },
      ]}
    />
  )
}
