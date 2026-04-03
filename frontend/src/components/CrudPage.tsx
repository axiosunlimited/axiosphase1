import React, { useEffect, useMemo, useState } from 'react'
import {
  Alert,
  Button,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Switch,
  Table,
  Tooltip,
  Typography,
  Upload,
  message,
} from 'antd'
import {
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  ReloadOutlined,
  SearchOutlined,
} from '@ant-design/icons'
import type { UploadFile } from 'antd'
import { resource } from '../api/resources'

export type Option = { label: string; value: any }

export type FieldType =
  | 'text'
  | 'textarea'
  | 'number'
  | 'select'
  | 'multiselect'
  | 'date'
  | 'datetime'
  | 'boolean'
  | 'file'
  | 'json'

export type FieldDef = {
  name: string
  label: string
  type: FieldType
  required?: boolean
  placeholder?: string
  options?: Option[]
  disabled?: boolean
  /** Hide field (or compute dynamically) */
  hidden?: boolean | ((ctx: { mode: 'create' | 'edit'; record: any | null }) => boolean)
}

type Props = {
  title: string
  endpoint: string
  columns: any[]
  fields: FieldDef[]
  /** Provide extra actions per row (e.g., approve/reject) */
  rowActions?: (record: any, helpers: { reload: () => void }) => React.ReactNode
  /** Read-only mode disables create/edit/delete */
  readOnly?: boolean
  idField?: string
  /** Transform values before submit (create/edit) */
  transformSubmit?: (values: any, ctx: { mode: 'create' | 'edit'; record: any | null }) => any
}

function isHidden(def: FieldDef, mode: 'create' | 'edit', record: any | null) {
  if (typeof def.hidden === 'function') return def.hidden({ mode, record })
  return !!def.hidden
}

function hasFile(fields: FieldDef[]) {
  return fields.some((f) => f.type === 'file')
}

function normalizePayload(fields: FieldDef[], raw: any) {
  const out: any = {}
  for (const f of fields) {
    if (!(f.name in raw)) continue
    const v = raw[f.name]

    if (f.type === 'number') {
      out[f.name] = v === '' || v === null || v === undefined ? null : Number(v)
      continue
    }

    if (f.type === 'json') {
      if (v === '' || v === null || v === undefined) {
        out[f.name] = {}
      } else if (typeof v === 'string') {
        out[f.name] = JSON.parse(v)
      } else {
        out[f.name] = v
      }
      continue
    }

    if (f.type === 'file') {
      // handled separately as multipart
      continue
    }

    out[f.name] = v
  }
  return out
}

function buildMultipart(fields: FieldDef[], raw: any) {
  const fd = new FormData()
  for (const f of fields) {
    if (!(f.name in raw)) continue
    const v = raw[f.name]

    if (f.type === 'file') {
      const fileList = (v as UploadFile[]) || []
      const fileObj: any = fileList[0]?.originFileObj
      if (fileObj) fd.append(f.name, fileObj)
      continue
    }

    if (f.type === 'json') {
      if (v === '' || v === null || v === undefined) fd.append(f.name, JSON.stringify({}))
      else if (typeof v === 'string') fd.append(f.name, v)
      else fd.append(f.name, JSON.stringify(v))
      continue
    }

    if (Array.isArray(v)) {
      // DRF accepts repeated keys for many=True
      v.forEach((item) => fd.append(f.name, String(item)))
      continue
    }

    if (typeof v === 'boolean') {
      fd.append(f.name, v ? 'true' : 'false')
      continue
    }

    if (v !== undefined && v !== null && v !== '') {
      fd.append(f.name, String(v))
    }
  }
  return fd
}

export default function CrudPage({
  title,
  endpoint,
  columns,
  fields,
  rowActions,
  readOnly,
  idField = 'id',
  transformSubmit,
}: Props) {
  const api = useMemo(() => resource(endpoint), [endpoint])
  const [rows, setRows] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [open, setOpen] = useState(false)
  const [mode, setMode] = useState<'create' | 'edit'>('create')
  const [record, setRecord] = useState<any | null>(null)

  const [form] = Form.useForm()

  const [search, setSearch] = useState('')

  const reload = async () => {
    setError(null)
    setLoading(true)
    try {
      const data = await api.list()
      setRows(Array.isArray(data) ? data : [])
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const filteredRows = useMemo(() => {
    if (!search) return rows
    const s = search.toLowerCase()
    return rows.filter((r) =>
      Object.values(r).some((v) => String(v).toLowerCase().includes(s))
    )
  }, [search, rows])

  useEffect(() => {
    void reload()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [endpoint])

  const openCreate = () => {
    setMode('create')
    setRecord(null)
    form.resetFields()
    setOpen(true)
  }

  const openEdit = (r: any) => {
    setMode('edit')
    setRecord(r)
    const initial: any = {}
    for (const f of fields) {
      if (f.type === 'file') continue
      const v = r?.[f.name]
      if (f.type === 'json') initial[f.name] = v ? JSON.stringify(v, null, 2) : ''
      else initial[f.name] = v
    }
    form.setFieldsValue(initial)
    setOpen(true)
  }

  const onDelete = async (r: any) => {
    const id = r?.[idField]
    if (id === undefined || id === null) return
    try {
      await api.remove(id)
      message.success('Deleted')
      await reload()
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Delete failed')
    }
  }

  const submit = async () => {
    const raw = await form.validateFields()
    const ctx = { mode, record }
    let values = raw
    if (transformSubmit) values = transformSubmit(raw, ctx)

    const visibleFields = fields.filter((f) => !isHidden(f, mode, record))

    try {
      if (hasFile(visibleFields)) {
        const fd = buildMultipart(visibleFields, values)
        if (mode === 'create') await api.create(fd, { headers: { 'Content-Type': 'multipart/form-data' } })
        else await api.patch(record?.[idField], fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      } else {
        const payload = normalizePayload(visibleFields, values)
        if (mode === 'create') await api.create(payload)
        else await api.patch(record?.[idField], payload)
      }
      message.success(mode === 'create' ? 'Created' : 'Updated')
      setOpen(false)
      await reload()
    } catch (e: any) {
      const data = e?.response?.data
      let msg = 'Save failed'
      if (data) {
        if (typeof data === 'string') msg = data
        else if (data.detail) msg = data.detail
        else if (typeof data === 'object') {
          // Flatten field errors: { name: ["This field is required"], ... }
          msg = Object.entries(data)
            .map(([field, errs]: [string, any]) => {
              const label = fields.find(f => f.name === field)?.label || field
              const details = Array.isArray(errs) ? errs.join(', ') : String(errs)
              return `${label}: ${details}`
            })
            .join(' | ')
        }
      }
      message.error(msg)
    }
  }

  const tableColumns = useMemo(() => {
    const base = [...columns]
    if (readOnly) {
      if (rowActions) {
        base.push({
          title: 'Actions',
          key: 'actions',
          align: 'right',
          render: (_: any, r: any) => <>{rowActions(r, { reload })}</>,
        })
      }
      return base
    }
    base.push({
      title: 'Actions',
      key: 'actions',
      align: 'right',
      width: 120,
      render: (_: any, r: any) => (
        <Space wrap>
          {rowActions ? rowActions(r, { reload }) : null}
          <Tooltip title="Edit">
            <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
          </Tooltip>
          <Popconfirm title="Delete this item?" onConfirm={() => onDelete(r)}>
            <Tooltip title="Delete">
              <Button size="small" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    })
    return base
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [columns, rowActions, readOnly, rows])

  return (
    <>
      <div className="panel">
        <div className="page-header">
          <Typography.Title level={2} style={{ margin: 0, fontSize: 26, fontWeight: 800, letterSpacing: '-0.3px' }}>{title}</Typography.Title>

          <Space size="middle" wrap style={{ flex: 1, justifyContent: 'flex-end' }}>
            <Input
              placeholder="Search..."
              prefix={<SearchOutlined style={{ color: 'var(--muted)' }} />}
              value={search}
              onChange={e => setSearch(e.target.value)}
              allowClear
              style={{ width: 260 }}
            />
            <Button
              className="btn-refresh"
              icon={<ReloadOutlined />}
              onClick={reload}
            >
              Refresh
            </Button>
            {!readOnly && (
              <Button
                type="primary"
                className="btn-new"
                icon={<PlusOutlined />}
                onClick={openCreate}
              >
                New
              </Button>
            )}
          </Space>
        </div>

        {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16, borderRadius: 10 }} />}

        <Table
          rowKey={idField}
          loading={loading}
          dataSource={filteredRows}
          columns={tableColumns}
          scroll={{ x: true }}
          pagination={{
            pageSize: 8,
            showSizeChanger: false,
            position: ['bottomCenter'],
          }}
        />
      </div>

      <Modal
        open={open}
        title={mode === 'create' ? `New ${title}` : `Edit ${title}`}
        onCancel={() => setOpen(false)}
        onOk={submit}
        okText={mode === 'create' ? 'Create' : 'Save'}
      >
        <Form layout="vertical" form={form}>
          {fields.map((f) => {
            if (isHidden(f, mode, record)) return null
            const rules = f.required ? [{ required: true, message: `${f.label} is required` }] : undefined
            if (f.type === 'text') {
              return (
                <Form.Item key={f.name} label={f.label} name={f.name} rules={rules}>
                  <Input placeholder={f.placeholder} disabled={f.disabled} />
                </Form.Item>
              )
            }
            if (f.type === 'textarea') {
              return (
                <Form.Item key={f.name} label={f.label} name={f.name} rules={rules}>
                  <Input.TextArea rows={4} placeholder={f.placeholder} disabled={f.disabled} />
                </Form.Item>
              )
            }
            if (f.type === 'number') {
              return (
                <Form.Item key={f.name} label={f.label} name={f.name} rules={rules}>
                  <Input type="number" placeholder={f.placeholder} disabled={f.disabled} />
                </Form.Item>
              )
            }
            if (f.type === 'date') {
              return (
                <Form.Item key={f.name} label={f.label} name={f.name} rules={rules}>
                  <Input type="date" disabled={f.disabled} />
                </Form.Item>
              )
            }
            if (f.type === 'datetime') {
              return (
                <Form.Item key={f.name} label={f.label} name={f.name} rules={rules}>
                  <Input type="datetime-local" disabled={f.disabled} />
                </Form.Item>
              )
            }
            if (f.type === 'boolean') {
              return (
                <Form.Item key={f.name} label={f.label} name={f.name} valuePropName="checked" rules={rules}>
                  <Switch disabled={f.disabled} />
                </Form.Item>
              )
            }
            if (f.type === 'select') {
              return (
                <Form.Item key={f.name} label={f.label} name={f.name} rules={rules}>
                  <Select
                    options={f.options}
                    showSearch
                    optionFilterProp="label"
                    placeholder={f.placeholder}
                    disabled={f.disabled}
                  />
                </Form.Item>
              )
            }
            if (f.type === 'multiselect') {
              return (
                <Form.Item key={f.name} label={f.label} name={f.name} rules={rules}>
                  <Select
                    mode="multiple"
                    options={f.options}
                    showSearch
                    optionFilterProp="label"
                    placeholder={f.placeholder}
                    disabled={f.disabled}
                  />
                </Form.Item>
              )
            }
            if (f.type === 'json') {
              return (
                <Form.Item
                  key={f.name}
                  label={f.label}
                  name={f.name}
                  rules={rules}
                  extra="Enter valid JSON"
                >
                  <Input.TextArea rows={6} placeholder={f.placeholder || '{ }'} disabled={f.disabled} />
                </Form.Item>
              )
            }
            if (f.type === 'file') {
              return (
                <Form.Item
                  key={f.name}
                  label={f.label}
                  name={f.name}
                  valuePropName="fileList"
                  getValueFromEvent={(e: any) => (Array.isArray(e) ? e : e?.fileList)}
                  rules={rules}
                >
                  <Upload beforeUpload={() => false} maxCount={1}>
                    <Button>Choose file</Button>
                  </Upload>
                </Form.Item>
              )
            }
            return null
          })}
        </Form>
      </Modal>
    </>
  )
}
