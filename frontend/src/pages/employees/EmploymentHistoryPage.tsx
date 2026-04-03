import React, { useEffect, useMemo, useState } from 'react'
import { Alert, Select, Space, Table, Typography } from 'antd'
import { http } from '../../api/client'
import { useOptions } from '../../hooks/useOptions'

export default function EmploymentHistoryPage() {
  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)
  const [employeeId, setEmployeeId] = useState<number | null>(null)

  const [rows, setRows] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const selectedEmployeeLabel = useMemo(() => {
    if (!employeeId) return null
    const opt = employeeOptions.find((o) => o.value === employeeId)
    return opt?.label ?? null
  }, [employeeId, employeeOptions])

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await http.get('/employment-history/', {
        params: employeeId ? { employee_id: employeeId } : {},
      })
      setRows(Array.isArray(res.data) ? res.data : [])
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load employment history')
      setRows([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [employeeId])

  return (
    <div className="panel">
      <div className="page-header">
        <div>
          <Typography.Title level={2} style={{ margin: 0, fontSize: 26, fontWeight: 800, letterSpacing: '-0.3px' }}>Employment History</Typography.Title>
          {selectedEmployeeLabel ? (
            <Typography.Text type="secondary">Showing history for: {selectedEmployeeLabel}</Typography.Text>
          ) : (
            <Typography.Text type="secondary">
              Tip: select an employee to filter results (HR/Managers).
            </Typography.Text>
          )}
        </div>

        <Space wrap>
          <Select
            allowClear
            placeholder="Filter by employee"
            style={{ width: 320 }}
            options={employeeOptions}
            showSearch
            optionFilterProp="label"
            value={employeeId ?? undefined}
            onChange={(v) => setEmployeeId(v ?? null)}
          />
        </Space>
      </div>

      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 12 }} />}

      <Table
        rowKey="id"
        loading={loading}
        dataSource={rows}
        columns={[
          { title: 'Department', render: (_: any, r: any) => r.department?.name },
          { title: 'Position', render: (_: any, r: any) => r.position?.title },
          { title: 'Status', dataIndex: 'employment_status' },
          { title: 'Contract', dataIndex: 'contract_type' },
          { title: 'Start', dataIndex: 'start_date' },
          { title: 'End', dataIndex: 'end_date', render: (_: any, r: any) => r.end_date || 'Current' },
          { title: 'Note', dataIndex: 'note' },
        ]}
        scroll={{ x: true }}
        pagination={{ pageSize: 6, showSizeChanger: false, position: ['bottomCenter'] }}
      />
    </div>
  )
}
