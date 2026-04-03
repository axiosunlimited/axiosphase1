import React, { useMemo } from 'react'
import { Button, Space, message } from 'antd'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'
import { resource } from '../../api/resources'

export default function VacanciesPage() {
  const { options: deptOptions } = useOptions('departments', (d) => d.name)
  const { options: posOptions } = useOptions('positions', (p) => `${p.title} — ${p.department?.name ?? ''}`)
  const api = useMemo(() => resource('vacancies'), [])

  return (
    <CrudPage
      title="Vacancies"
      endpoint="vacancies"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Title', dataIndex: 'title' },
        {
          title: 'Status',
          render: (_: any, r: any) => (
            <span className={`badge-pill ${r.status === 'PUBLISHED' || r.status === 'APPROVED' ? 'badge-success' : 'badge-neutral'}`}>
              {r.status}
            </span>
          )
        },
        { title: 'Department', render: (_: any, r: any) => r.department?.name },
        { title: 'Position', render: (_: any, r: any) => r.position?.title },
        { title: 'Closing', dataIndex: 'closing_date' },
        { title: 'Created', dataIndex: 'created_at' },
      ]}
      fields={[
        { name: 'title', label: 'Title', type: 'text', required: true },
        { name: 'description', label: 'Description', type: 'textarea' },
        { name: 'department_id', label: 'Department', type: 'select', required: true, options: deptOptions },
        { name: 'position_id', label: 'Position', type: 'select', required: true, options: posOptions },
        { name: 'closing_date', label: 'Closing Date', type: 'date' },
      ]}
      rowActions={(r, helpers) => (
        <Space wrap>
          <Button
            size="small"
            onClick={async () => {
              try {
                await api.action(r.id, 'submit')
                message.success('Submitted')
                helpers.reload()
              } catch (e: any) {
                message.error(e?.response?.data?.detail || 'Action failed')
              }
            }}
          >
            Submit
          </Button>
          <Button
            size="small"
            onClick={async () => {
              try {
                await api.action(r.id, 'approve')
                message.success('Approved')
                helpers.reload()
              } catch (e: any) {
                message.error(e?.response?.data?.detail || 'Action failed')
              }
            }}
          >
            Approve
          </Button>
          <Button
            size="small"
            type="primary"
            onClick={async () => {
              try {
                await api.action(r.id, 'publish')
                message.success('Published')
                helpers.reload()
              } catch (e: any) {
                message.error(e?.response?.data?.detail || 'Action failed')
              }
            }}
          >
            Publish
          </Button>
        </Space>
      )}
    />
  )
}
