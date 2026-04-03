import React, { useEffect, useState } from 'react'
import { Table, Typography, Alert } from 'antd'
import * as api from '../api/hris'

export default function PerformancePage() {
  const [rows, setRows] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    (async () => {
      try {
        const data = await api.listAppraisals()
        setRows(data)
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load appraisals')
      }
    })()
  }, [])

  return (
    <>
      <Typography.Title level={3}>Performance</Typography.Title>
      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 12 }} />}
      <Table
        rowKey="id"
        dataSource={rows}
        pagination={{ pageSize: 5 }}
        columns={[
          { title: 'Employee', render: (_, r) => r.employee?.employee_number },
          { title: 'Template', render: (_, r) => r.template?.name },
          { title: 'Year', dataIndex: 'year' },
          { title: 'Period', dataIndex: 'period' },
          { title: 'Status', dataIndex: 'status' },
        ]}
      />
    </>
  )
}
