import React, { useMemo, useState } from 'react'
import { Button, Divider, Modal, Space, Table, Tag, Typography, message } from 'antd'
import { DownloadOutlined, PlayCircleOutlined } from '@ant-design/icons'
import CrudPage from '../../components/CrudPage'
import { http } from '../../api/client'

const datasetOptions = [
  { value: 'EMPLOYEES', label: 'Employees' },
  { value: 'EMPLOYMENT_HISTORY', label: 'Employment History' },
  { value: 'LEAVE_REQUESTS', label: 'Leave Requests' },
  { value: 'LEAVE_BALANCES', label: 'Leave Balances' },
  { value: 'VACANCIES', label: 'Vacancies' },
  { value: 'APPLICANTS', label: 'Applicants' },
  { value: 'APPRAISALS', label: 'Appraisals' },
  { value: 'TRAINING_RECORDS', label: 'Training Records' },
  { value: 'ESTABLISHMENT', label: 'Staff Establishment' },
  { value: 'SEPARATIONS', label: 'Separations' },
]

const exampleDefinition = {
  fields: ['id', 'employee_number', 'department__name', 'position__title'],
  filters: [{ field: 'employment_status', op: 'eq', value: 'ACTIVE' }],
  order_by: ['department__name', 'employee_number'],
  limit: 2000,
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export default function ReportDefinitionsPage() {
  const [runOpen, setRunOpen] = useState(false)
  const [runTitle, setRunTitle] = useState('')
  const [runMeta, setRunMeta] = useState<any>(null)
  const [runRows, setRunRows] = useState<any[]>([])
  const [runLoading, setRunLoading] = useState(false)

  const runColumns = useMemo(() => {
    const first = runRows?.[0]
    if (!first || typeof first !== 'object') return []
    return Object.keys(first).map((k) => ({ title: k, dataIndex: k, key: k }))
  }, [runRows])

  const runReport = async (r: any) => {
    setRunLoading(true)
    setRunTitle(r.name)
    try {
      const res = await http.post(`/report-definitions/${r.id}/run/`)
      setRunMeta(res.data?.meta)
      setRunRows(Array.isArray(res.data?.rows) ? res.data.rows : [])
      setRunOpen(true)
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to run report')
    } finally {
      setRunLoading(false)
    }
  }

  const exportReport = async (r: any, fmt: 'pdf' | 'xlsx') => {
    try {
      const res = await http.get(`/report-definitions/${r.id}/export/`, { params: { export_format: fmt }, responseType: 'blob' })
      downloadBlob(res.data, `report_${r.id}.${fmt === 'pdf' ? 'pdf' : 'xlsx'}`)
    } catch (e: any) {
      let detail = 'Export failed'
      const blob = e?.response?.data
      if (blob instanceof Blob) {
        try {
          const text = await blob.text()
          const json = JSON.parse(text)
          if (json.detail) detail = json.detail
        } catch { /* keep default */ }
      } else if (e?.response?.data?.detail) {
        detail = e.response.data.detail
      }
      message.error(detail)
    }
  }

  return (
    <>
      <CrudPage
        title="Custom Reports"
        endpoint="report-definitions"
        columns={[
          { title: 'ID', dataIndex: 'id' },
          { title: 'Name', dataIndex: 'name' },
          { title: 'Dataset', dataIndex: 'dataset', render: (v: any) => <Tag>{v}</Tag> },
          { title: 'Created By', dataIndex: 'created_by_email' },
          { title: 'System', render: (_: any, r: any) => (r.is_system ? 'Yes' : 'No') },
          { title: 'Updated', dataIndex: 'updated_at' },
        ]}
        fields={[
          { name: 'name', label: 'Name', type: 'text', required: true },
          { name: 'description', label: 'Description', type: 'textarea' },
          { name: 'dataset', label: 'Dataset', type: 'select', required: true, options: datasetOptions },
          {
            name: 'definition',
            label: 'Definition (JSON)',
            type: 'json',
            placeholder: JSON.stringify(exampleDefinition, null, 2),
          },
        ]}
        rowActions={(r) => (
          <Space wrap>
            <Button size="small" icon={<PlayCircleOutlined />} loading={runLoading} onClick={() => runReport(r)}>
              Run
            </Button>
            <Button size="small" icon={<DownloadOutlined />} onClick={() => exportReport(r, 'pdf')}>
              PDF
            </Button>
            <Button size="small" icon={<DownloadOutlined />} onClick={() => exportReport(r, 'xlsx')}>
              Excel
            </Button>
          </Space>
        )}
      />

      <Modal
        open={runOpen}
        title={runTitle}
        onCancel={() => setRunOpen(false)}
        footer={null}
        width={1000}
      >
        {runMeta ? (
          <>
            <Typography.Text type="secondary">Dataset: {runMeta.dataset}</Typography.Text>
            <Divider />
          </>
        ) : null}

        <Table
          rowKey={(r) => r.id ?? JSON.stringify(r)}
          dataSource={runRows}
          columns={runColumns}
          loading={runLoading}
          scroll={{ x: true }}
          pagination={{ pageSize: 10, showSizeChanger: false, position: ['bottomCenter'] }}
        />
      </Modal>
    </>
  )
}
