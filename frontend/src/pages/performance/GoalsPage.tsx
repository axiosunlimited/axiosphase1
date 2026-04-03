import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function GoalsPage() {
  const { options: appraisalOptions } = useOptions(
    'appraisals',
    (a) => {
      const emp = a.employee?.employee_number || ''
      const year = a.year || ''
      const period = a.period || ''
      return `${emp} ${year} ${period}`.trim()
    },
  )

  return (
    <CrudPage
      title="Goals"
      endpoint="goals"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Appraisal', dataIndex: 'appraisal' },
        { title: 'Description', dataIndex: 'description' },
        { title: 'Progress', dataIndex: 'progress_note' },
      ]}
      fields={[
        { name: 'appraisal', label: 'Appraisal', type: 'select', required: true, options: appraisalOptions },
        { name: 'description', label: 'Description', type: 'text', required: true },
        { name: 'progress_note', label: 'Progress Note', type: 'textarea' },
      ]}
    />
  )
}
