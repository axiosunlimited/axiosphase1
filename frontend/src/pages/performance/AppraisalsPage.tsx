import React, { useMemo, useState } from 'react'
import { Button, Form, Input, Modal, Space, message } from 'antd'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'
import { resource } from '../../api/resources'
import { useAuth } from '../../context/AuthContext'

export default function AppraisalsPage() {
  const { user } = useAuth()
  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)
  const { options: templateOptions } = useOptions('appraisal-templates', (t) => t.name)

  const api = useMemo(() => resource('appraisals'), [])

  const [supOpen, setSupOpen] = useState(false)
  const [supId, setSupId] = useState<number | null>(null)
  const [supReload, setSupReload] = useState<(() => void) | null>(null)
  const [supForm] = Form.useForm()

  const [hrOpen, setHrOpen] = useState(false)
  const [hrId, setHrId] = useState<number | null>(null)
  const [hrReload, setHrReload] = useState<(() => void) | null>(null)
  const [hrForm] = Form.useForm()

  const openSup = (id: number, reload: () => void, current: any) => {
    setSupId(id)
    setSupReload(() => reload)
    supForm.setFieldsValue({ supervisor_feedback: current ? JSON.stringify(current, null, 2) : '' })
    setSupOpen(true)
  }

  const submitSup = async () => {
    const vals = await supForm.validateFields()
    if (!supId) return
    try {
      const raw = vals.supervisor_feedback || '{}'
      const payload = { supervisor_feedback: raw ? JSON.parse(raw) : {} }
      await api.action(supId, 'supervisor_review', payload)
      message.success('Supervisor review saved')
      setSupOpen(false)
      setSupId(null)
      const fn = supReload
      setSupReload(null)
      fn?.()
    } catch (e: any) {
      message.error(e?.response?.data?.detail || e?.message || 'Save failed')
    }
  }

  const openHr = (id: number, reload: () => void, current: any) => {
    setHrId(id)
    setHrReload(() => reload)
    hrForm.setFieldsValue({ hr_notes: current || '' })
    setHrOpen(true)
  }

  const submitHr = async () => {
    const vals = await hrForm.validateFields()
    if (!hrId) return
    try {
      await api.action(hrId, 'hr_review', { hr_notes: vals.hr_notes || '' })
      message.success('HR review saved')
      setHrOpen(false)
      setHrId(null)
      const fn = hrReload
      setHrReload(null)
      fn?.()
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Save failed')
    }
  }

  const canSup = user?.role === 'LINE_MANAGER' || user?.role === 'SYSTEM_ADMIN'
  const canHr = user?.role === 'HR_MANAGER' || user?.role === 'HR_OFFICER' || user?.role === 'SYSTEM_ADMIN'
  const canFinalize = user?.role === 'HR_MANAGER' || user?.role === 'SYSTEM_ADMIN'

  return (
    <>
      <CrudPage
        title="Appraisals"
        endpoint="appraisals"
        columns={[
          { title: 'ID', dataIndex: 'id' },
          {
            title: 'Employee',
            render: (_: any, r: any) => `${r.employee?.employee_number ?? ''} ${r.employee?.user?.full_name ?? r.employee?.user?.email ?? ''}`.trim(),
          },
          { title: 'Template', render: (_: any, r: any) => r.template?.name },
          { title: 'Year', dataIndex: 'year' },
          { title: 'Period', dataIndex: 'period' },
          {
            title: 'Status',
            render: (_: any, r: any) => (
              <span className={`badge-pill ${r.status === 'FINALIZED' ? 'badge-success' : 'badge-neutral'}`}>
                {r.status}
              </span>
            )
          },
          { title: 'Created', dataIndex: 'created_at' },
        ]}
        fields={[
          { name: 'employee_id', label: 'Employee', type: 'select', required: true, options: employeeOptions },
          { name: 'template_id', label: 'Template', type: 'select', required: true, options: templateOptions },
          { name: 'year', label: 'Year', type: 'number', required: true },
          {
            name: 'period',
            label: 'Period',
            type: 'select',
            required: true,
            options: [
              { value: 'ANNUAL', label: 'ANNUAL' },
              { value: 'PROBATION', label: 'PROBATION' },
            ],
          },
          { name: 'self_assessment', label: 'Self Assessment', type: 'json' },
          { name: 'supervisor_feedback', label: 'Supervisor Feedback', type: 'json' },
          { name: 'hr_notes', label: 'HR Notes', type: 'textarea' },
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
                  message.error(e?.response?.data?.detail || 'Submit failed')
                }
              }}
            >
              Submit
            </Button>

            {canSup && (
              <Button size="small" onClick={() => openSup(r.id, helpers.reload, r.supervisor_feedback)}>
                Supervisor Review
              </Button>
            )}

            {canHr && (
              <Button size="small" onClick={() => openHr(r.id, helpers.reload, r.hr_notes)}>
                HR Review
              </Button>
            )}

            {canFinalize && (
              <Button
                size="small"
                type="primary"
                onClick={async () => {
                  try {
                    await api.action(r.id, 'finalize')
                    message.success('Finalized')
                    helpers.reload()
                  } catch (e: any) {
                    message.error(e?.response?.data?.detail || 'Finalize failed')
                  }
                }}
              >
                Finalize
              </Button>
            )}
          </Space>
        )}
      />

      <Modal
        open={supOpen}
        title="Supervisor Review"
        onCancel={() => setSupOpen(false)}
        onOk={submitSup}
        okText="Save"
        destroyOnClose
      >
        <Form layout="vertical" form={supForm}>
          <Form.Item
            name="supervisor_feedback"
            label="Supervisor Feedback (JSON)"
            rules={[
              {
                validator: async (_rule, value) => {
                  if (!value) return
                  try {
                    JSON.parse(value)
                  } catch {
                    throw new Error('Must be valid JSON')
                  }
                },
              },
            ]}
          >
            <Input.TextArea rows={8} placeholder="{ }" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        open={hrOpen}
        title="HR Review"
        onCancel={() => setHrOpen(false)}
        onOk={submitHr}
        okText="Save"
        destroyOnClose
      >
        <Form layout="vertical" form={hrForm}>
          <Form.Item name="hr_notes" label="HR Notes">
            <Input.TextArea rows={6} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
