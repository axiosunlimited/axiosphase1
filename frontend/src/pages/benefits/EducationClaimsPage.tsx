import React, { useMemo, useState } from 'react'
import { Button, Form, Input, InputNumber, Modal, Space, message } from 'antd'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'
import { resource } from '../../api/resources'
import { useAuth } from '../../context/AuthContext'

export default function EducationClaimsPage() {
  const { user } = useAuth()
  const role = user?.role || ''

  const { options: dependantOptions } = useOptions('dependants', (d) => `${d.name}`)
  const api = useMemo(() => resource('education-claims'), [])

  const [hrApproveOpen, setHrApproveOpen] = useState(false)
  const [hrApproveId, setHrApproveId] = useState<number | null>(null)
  const [hrApproveReload, setHrApproveReload] = useState<(() => void) | null>(null)
  const [hrApproveForm] = Form.useForm()

  const [noteOpen, setNoteOpen] = useState(false)
  const [noteAction, setNoteAction] = useState<'request-info' | 'hr-reject'>('request-info')
  const [noteId, setNoteId] = useState<number | null>(null)
  const [noteReload, setNoteReload] = useState<(() => void) | null>(null)
  const [noteForm] = Form.useForm()

  const [financeOpen, setFinanceOpen] = useState(false)
  const [financeId, setFinanceId] = useState<number | null>(null)
  const [financeReload, setFinanceReload] = useState<(() => void) | null>(null)
  const [financeForm] = Form.useForm()

  const can = (roles: string[]) => roles.includes(role)

  const openHrApprove = (id: number, reload: () => void) => {
    setHrApproveId(id)
    setHrApproveReload(() => reload)
    hrApproveForm.resetFields()
    setHrApproveOpen(true)
  }

  const submitHrApprove = async () => {
    const vals = await hrApproveForm.validateFields()
    if (!hrApproveId) return
    try {
      await api.action(hrApproveId, 'hr-approve', { amount_approved: vals.amount_approved, hr_note: vals.hr_note || '' })
      message.success('HR approved')
      setHrApproveOpen(false)
      const fn = hrApproveReload
      setHrApproveReload(null)
      setHrApproveId(null)
      fn?.()
    } catch (e: any) {
      const detail = e?.response?.data?.detail || 'HR approve failed'
      const missing = e?.response?.data?.missing
      message.error(missing ? `${detail}: ${missing.join(', ')}` : detail)
    }
  }

  const openNote = (id: number, action: 'request-info' | 'hr-reject', reload: () => void) => {
    setNoteId(id)
    setNoteAction(action)
    setNoteReload(() => reload)
    noteForm.resetFields()
    setNoteOpen(true)
  }

  const submitNote = async () => {
    const vals = await noteForm.validateFields()
    if (!noteId) return
    try {
      await api.action(noteId, noteAction, { hr_note: vals.hr_note || '' })
      message.success(noteAction === 'request-info' ? 'Requested more info' : 'Rejected')
      setNoteOpen(false)
      const fn = noteReload
      setNoteReload(null)
      setNoteId(null)
      fn?.()
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Action failed')
    }
  }

  const openFinance = (id: number, reload: () => void) => {
    setFinanceId(id)
    setFinanceReload(() => reload)
    financeForm.resetFields()
    setFinanceOpen(true)
  }

  const submitFinance = async () => {
    const vals = await financeForm.validateFields()
    if (!financeId) return
    try {
      await api.action(financeId, 'finance-paid', { payment_reference: vals.payment_reference || '' })
      message.success('Marked as paid')
      setFinanceOpen(false)
      const fn = financeReload
      setFinanceReload(null)
      setFinanceId(null)
      fn?.()
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Finance action failed')
    }
  }

  return (
    <>
      <CrudPage
        title="Education Claims"
        endpoint="education-claims"
        columns={[
          { title: 'ID', dataIndex: 'id' },
          {
            title: 'Employee',
            render: (_: any, r: any) =>
              `${r.employee?.employee_number ?? ''} ${r.employee?.full_name ?? r.employee?.email ?? ''}`.trim(),
          },
          { title: 'Dependant', dataIndex: 'dependant_name' },
          { title: 'Academic Year', dataIndex: 'academic_year' },
          { title: 'Period Type', dataIndex: 'period_type' },
          { title: 'Period', dataIndex: 'period_label' },
          { title: 'Institution', dataIndex: 'institution_name' },
          { title: 'Claimed', dataIndex: 'amount_claimed' },
          { title: 'Approved', dataIndex: 'amount_approved' },
          { title: 'Status', dataIndex: 'status' },
          { title: 'HR Note', dataIndex: 'hr_note' },
          { title: 'Payment Ref', dataIndex: 'payment_reference' },
          { title: 'Created', dataIndex: 'created_at' },
        ]}
        fields={[
          { name: 'dependant', label: 'Dependant', type: 'select', required: true, options: dependantOptions },
          { name: 'academic_year', label: 'Academic Year', type: 'number', required: true },
          {
            name: 'period_type',
            label: 'Period Type',
            type: 'select',
            required: true,
            options: [
              { label: 'Term', value: 'TERM' },
              { label: 'Semester', value: 'SEMESTER' },
              { label: 'Year', value: 'YEAR' },
            ],
          },
          { name: 'period_label', label: 'Period Label', type: 'text', required: true, placeholder: 'e.g., Term 1' },
          { name: 'institution_name', label: 'Institution', type: 'text', required: true },
          { name: 'amount_claimed', label: 'Amount Claimed', type: 'number', required: true },
        ]}
        rowActions={(r, helpers) => (
          <Space wrap>
            {r.status === 'SUBMITTED' && can(['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER']) && (
              <Button size="small" onClick={() => openHrApprove(r.id, helpers.reload)}>
                HR Approve
              </Button>
            )}

            {r.status === 'NEEDS_INFO' && can(['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER']) && (
              <Button size="small" onClick={() => openHrApprove(r.id, helpers.reload)}>
                HR Approve
              </Button>
            )}

            {r.status === 'SUBMITTED' && can(['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER']) && (
              <Button size="small" onClick={() => openNote(r.id, 'request-info', helpers.reload)}>
                Request Info
              </Button>
            )}

            {['SUBMITTED', 'NEEDS_INFO'].includes(r.status) && can(['SYSTEM_ADMIN', 'HR_MANAGER', 'HR_OFFICER']) && (
              <Button size="small" danger onClick={() => openNote(r.id, 'hr-reject', helpers.reload)}>
                HR Reject
              </Button>
            )}

            {r.status === 'NEEDS_INFO' && role === 'EMPLOYEE' && (
              <Button
                size="small"
                onClick={async () => {
                  try {
                    await api.action(r.id, 'resubmit')
                    message.success('Resubmitted')
                    helpers.reload()
                  } catch (e: any) {
                    message.error(e?.response?.data?.detail || 'Resubmit failed')
                  }
                }}
              >
                Resubmit
              </Button>
            )}

            {r.status === 'FINANCE_PENDING' && can(['SYSTEM_ADMIN', 'FINANCE_OFFICER']) && (
              <Button size="small" onClick={() => openFinance(r.id, helpers.reload)}>
                Mark Paid
              </Button>
            )}
          </Space>
        )}
      />

      <Modal
        open={hrApproveOpen}
        title="HR Approve Claim"
        onCancel={() => setHrApproveOpen(false)}
        onOk={submitHrApprove}
        okText="Approve"
        destroyOnClose
      >
        <Form layout="vertical" form={hrApproveForm}>
          <Form.Item name="amount_approved" label="Amount Approved" rules={[{ required: false }]}>
            <InputNumber style={{ width: '100%' }} min={0} placeholder="Leave blank to approve full claimed amount" />
          </Form.Item>
          <Form.Item name="hr_note" label="HR Note">
            <Input.TextArea rows={4} placeholder="Optional" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        open={noteOpen}
        title={noteAction === 'request-info' ? 'Request Additional Info' : 'HR Reject Claim'}
        onCancel={() => setNoteOpen(false)}
        onOk={submitNote}
        okText={noteAction === 'request-info' ? 'Send' : 'Reject'}
        okButtonProps={noteAction === 'hr-reject' ? { danger: true } : undefined}
        destroyOnClose
      >
        <Form layout="vertical" form={noteForm}>
          <Form.Item name="hr_note" label="Note" rules={[{ required: false }]}>
            <Input.TextArea rows={5} placeholder="Optional" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        open={financeOpen}
        title="Mark Claim as Paid"
        onCancel={() => setFinanceOpen(false)}
        onOk={submitFinance}
        okText="Mark Paid"
        destroyOnClose
      >
        <Form layout="vertical" form={financeForm}>
          <Form.Item name="payment_reference" label="Payment Reference">
            <Input placeholder="Optional" />
          </Form.Item>
          <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
            Note: A payment proof document must be uploaded before marking paid.
          </div>
        </Form>
      </Modal>
    </>
  )
}
