import React, { useEffect, useState } from 'react'
import { Table, Typography, Alert } from 'antd'
import * as api from '../api/hris'

export default function EmployeesPage() {
  const [rows, setRows] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    (async () => {
      try {
        const data = await api.listEmployees()
        setRows(data)
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load employees')
      }
    })()
  }, [])

  return (
    <>
      <Typography.Title level={3}>Employees</Typography.Title>
      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 12 }} />}
      <Table
        rowKey="id"
        dataSource={rows}
        pagination={{ pageSize: 5 }}
        columns={[
          { title: 'Employee #', dataIndex: 'employee_number' },
          { title: 'Name', render: (_, r) => `${r.user?.first_name ?? ''} ${r.user?.last_name ?? ''}`.trim() || r.user?.email },
          { title: 'Email', render: (_, r) => r.user?.email },
          { title: 'Department', render: (_, r) => r.department?.name },
          { title: 'Position', render: (_, r) => r.position?.title },
          { title: 'Status', dataIndex: 'employment_status' },
        ]}
      />
    </>
  )
}
