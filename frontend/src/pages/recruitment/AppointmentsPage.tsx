import React, { useMemo } from 'react'
import { Button, Space, message } from 'antd'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'
import { downloadBlob, resource } from '../../api/resources'

function saveBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(url)
}

export default function AppointmentsPage() {
  const { options: applicantOptions } = useOptions('applicants', (a) => `${a.first_name} ${a.last_name} — ${a.email}`)
  const api = useMemo(() => resource('appointments'), [])

  return (
    <CrudPage
      title="Appointments"
      endpoint="appointments"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Applicant', dataIndex: 'applicant' },
        { title: 'Start Date', dataIndex: 'start_date' },
        { title: 'Created', dataIndex: 'created_at' },
      ]}
      fields={[
        { name: 'applicant', label: 'Applicant', type: 'select', required: true, options: applicantOptions },
        { name: 'start_date', label: 'Start Date', type: 'date', required: true },
        { name: 'salary_note', label: 'Salary Note', type: 'textarea' },
      ]}
      rowActions={(r, helpers) => (
        <Space wrap>
          <Button
            size="small"
            onClick={async () => {
              try {
                const blob = await downloadBlob(`/appointments/${r.id}/letter/`)
                saveBlob(blob, `appointment_letter_${r.id}.pdf`)
              } catch (e: any) {
                message.error(e?.response?.data?.detail || 'Download failed')
              }
            }}
          >
            Download Letter
          </Button>
        </Space>
      )}
    />
  )
}
