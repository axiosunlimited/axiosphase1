import React, { useMemo, useState } from 'react'
import { Button, Form, Input, Modal, Space, message } from 'antd'
import { FileOutlined } from '@ant-design/icons'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'
import { resource } from '../../api/resources'
import { useAuth } from '../../context/AuthContext'

export default function LeaveRequestsPage() {
  const { user } = useAuth()
  const { options: employeeOptions } = useOptions('employees', (e: any) => `${e.employee_number} — ${e.full_name || e.email}`)
  const { options: leaveTypeOptions } = useOptions('leave-types', (lt: any) => lt.name)

  const api = useMemo(() => resource('leave-requests'), [])

  const [rejectOpen, setRejectOpen] = useState(false)
  const [rejectId, setRejectId] = useState<number | null>(null)
  const [rejectReload, setRejectReload] = useState<(() => void) | null>(null)
  const [rejectForm] = Form.useForm()

  const openReject = (id: number, reload: () => void) => {
    setRejectId(id)
    setRejectReload(() => reload)
    rejectForm.resetFields()
    setRejectOpen(true)
  }

  const submitReject = async () => {
    const vals = await rejectForm.validateFields()
    if (!rejectId) return
    try {
      await api.action(rejectId, 'reject', { decision_note: vals.decision_note || '' })
      message.success('Rejected')
      setRejectOpen(false)
      setRejectId(null)
      const fn = rejectReload
      setRejectReload(null)
      fn?.()
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Reject failed')
    }
  }

  const isEmployee = user?.role === 'EMPLOYEE'
  const role = user?.role || ''
  const can = (roles: string[]) => roles.includes(role)

  return (
    <>
      <CrudPage
        title="Leave Requests"
        endpoint="leave-requests"
        columns={[
          { title: 'ID', dataIndex: 'id' },
          {
            title: 'Employee',
            render: (_: any, r: any) =>
              `${r.employee?.employee_number ?? ''} ${r.employee?.full_name ?? r.employee?.email ?? ''}`.trim(),
          },
          { title: 'Leave Type', render: (_: any, r: any) => r.leave_type?.name },
          { title: 'Start', dataIndex: 'start_date' },
          { title: 'End', dataIndex: 'end_date' },
          { title: 'Days', dataIndex: 'days_requested' },
          {
            title: 'Status',
            render: (_: any, r: any) => (
              <span className={`badge-pill ${r.status === 'APPROVED' ? 'badge-success' : 'badge-neutral'}`}>
                {r.status}
              </span>
            )
          },
          {
            title: 'Document',
            dataIndex: 'supporting_document',
            render: (val: string) => val ? (
              <a href={val} target="_blank" rel="noreferrer">
                <FileOutlined /> View
              </a>
            ) : '-'
          },
          { title: 'Reason', dataIndex: 'reason' },
          { title: 'Decision Note', dataIndex: 'decision_note' },
          { title: 'Line Manager', dataIndex: 'line_manager_email' },
          { title: 'HR Officer', dataIndex: 'hr_officer_email' },
          { title: 'PVC', dataIndex: 'pvc_officer_email' },
          { title: 'Admin', dataIndex: 'admin_officer_email' },
          { title: 'Finance', dataIndex: 'finance_officer_email' },
          { title: 'Approved At', dataIndex: 'approved_at' },
        ]}
        fields={[
          {
            name: 'employee_id',
            label: 'Employee',
            type: 'select',
            options: employeeOptions,
            hidden: () => isEmployee,
          },
          { name: 'leave_type_id', label: 'Leave Type', type: 'select', required: true, options: leaveTypeOptions },
          { name: 'start_date', label: 'Start Date', type: 'date', required: true },
          { name: 'end_date', label: 'End Date', type: 'date', required: true },
          { name: 'reason', label: 'Reason', type: 'textarea' },
          { name: 'supporting_document', label: 'Supporting Document', type: 'file' },
        ]}
        rowActions={(r, helpers) => (
          <Space wrap>
            {r.status === 'PENDING_LM' && can(['LINE_MANAGER', 'SYSTEM_ADMIN']) && (
              <Button
                size="small"
                onClick={async () => {
                  try {
                    await api.action(r.id, 'approve_line_manager')
                    message.success('Approved (Line Manager)')
                    helpers.reload()
                  } catch (e: any) {
                    message.error(e?.response?.data?.detail || 'Action failed')
                  }
                }}
              >
                LM Approve
              </Button>
            )}

            {['PENDING_HR', 'PENDING_LM'].includes(r.status) && can(['HR_MANAGER', 'HR_OFFICER', 'SYSTEM_ADMIN']) && (
              <Button
                size="small"
                onClick={async () => {
                  try {
                    await api.action(r.id, 'approve_hr')
                    message.success('Approved (HR)')
                    helpers.reload()
                  } catch (e: any) {
                    message.error(e?.response?.data?.detail || 'Action failed')
                  }
                }}
              >
                HR Approve
              </Button>
            )}

            {r.status === 'PENDING_PVC' && can(['PVC', 'SYSTEM_ADMIN']) && (
              <Button
                size="small"
                onClick={async () => {
                  try {
                    await api.action(r.id, 'approve_pvc')
                    message.success('Approved (PVC)')
                    helpers.reload()
                  } catch (e: any) {
                    message.error(e?.response?.data?.detail || 'Action failed')
                  }
                }}
              >
                PVC Approve
              </Button>
            )}

            {r.status === 'PENDING_ADMIN' && can(['ADMIN_OFFICER', 'SYSTEM_ADMIN']) && (
              <Button
                size="small"
                onClick={async () => {
                  try {
                    await api.action(r.id, 'approve_admin')
                    message.success('Approved (Admin)')
                    helpers.reload()
                  } catch (e: any) {
                    message.error(e?.response?.data?.detail || 'Action failed')
                  }
                }}
              >
                Admin Approve
              </Button>
            )}

            {r.status === 'PENDING_FINANCE' && can(['FINANCE_OFFICER', 'SYSTEM_ADMIN']) && (
              <Button
                size="small"
                onClick={async () => {
                  try {
                    await api.action(r.id, 'approve_finance')
                    message.success('Approved (Finance)')
                    helpers.reload()
                  } catch (e: any) {
                    message.error(e?.response?.data?.detail || 'Action failed')
                  }
                }}
              >
                Finance Approve
              </Button>
            )}

            {!['APPROVED', 'REJECTED', 'CANCELLED'].includes(r.status) &&
              can(['LINE_MANAGER', 'HR_MANAGER', 'HR_OFFICER', 'PVC', 'ADMIN_OFFICER', 'FINANCE_OFFICER', 'SYSTEM_ADMIN']) && (
                <Button size="small" danger onClick={() => openReject(r.id, helpers.reload)}>
                  Reject
                </Button>
              )}
          </Space>
        )}
      />

      <Modal
        open={rejectOpen}
        title="Reject Leave Request"
        onCancel={() => setRejectOpen(false)}
        onOk={submitReject}
        okText="Reject"
        okButtonProps={{ danger: true }}
        destroyOnClose
      >
        <Form layout="vertical" form={rejectForm}>
          <Form.Item name="decision_note" label="Decision Note">
            <Input.TextArea rows={5} placeholder="Optional" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
