import React from 'react'
import { Button } from 'antd'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function TrainingRecordsPage() {
  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)
  const { options: programOptions } = useOptions('training-programs', (p) => `${p.title}${p.provider ? ` — ${p.provider}` : ''}`)

  const statusOptions = [
    { value: 'PLANNED', label: 'Planned' },
    { value: 'ATTENDED', label: 'Attended' },
    { value: 'COMPLETED', label: 'Completed' },
    { value: 'CANCELLED', label: 'Cancelled' },
  ]

  return (
    <CrudPage
      title="Training Records"
      endpoint="training-records"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Employee', render: (_: any, r: any) => `${r.employee?.employee_number ?? ''} ${r.employee?.full_name ?? r.employee?.email ?? ''}`.trim() },
        { title: 'Program', render: (_: any, r: any) => r.program?.title },
        { title: 'Status', dataIndex: 'status' },
        { title: 'Cost', dataIndex: 'cost' },
        { title: 'Recorded By', dataIndex: 'recorded_by_email' },
        { title: 'Recorded At', dataIndex: 'recorded_at' },
        {
          title: 'Certificate',
          render: (_: any, r: any) =>
            r.certificate ? (
              <Button type="link" href={r.certificate} target="_blank" rel="noreferrer">
                Download
              </Button>
            ) : (
              ''
            ),
        },
      ]}
      fields={[
        { name: 'employee_id', label: 'Employee', type: 'select', required: true, options: employeeOptions },
        { name: 'program_id', label: 'Training Program', type: 'select', required: true, options: programOptions },
        { name: 'status', label: 'Status', type: 'select', required: true, options: statusOptions },
        { name: 'cost', label: 'Cost', type: 'number' },
        { name: 'outcome', label: 'Outcome', type: 'textarea' },
        { name: 'certificate', label: 'Certificate (optional)', type: 'file' },
      ]}
    />
  )
}
