import React, { useEffect, useMemo, useState } from 'react'
import { Alert, Button, Card, Divider, Form, Input, Select, Space, Table, Typography, Upload, message } from 'antd'
import type { UploadFile } from 'antd'
import { DownloadOutlined, EyeOutlined, PlayCircleOutlined, ReloadOutlined } from '@ant-design/icons'
import { http } from '../../api/client'
import { resource } from '../../api/resources'

function downloadAsFile(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export default function ImportsPage() {
  const jobsApi = useMemo(() => resource('import-jobs'), [])

  const [jobs, setJobs] = useState<any[]>([])
  const [jobsLoading, setJobsLoading] = useState(false)
  const [jobsError, setJobsError] = useState<string | null>(null)

  const [kind, setKind] = useState<'EMPLOYEES' | 'LEAVE_BALANCES' | 'CONTRACTS'>('EMPLOYEES')
  const [format, setFormat] = useState<'csv' | 'xlsx'>('csv')
  const [mapping, setMapping] = useState<string>('{}')
  const [fileList, setFileList] = useState<UploadFile[]>([])

  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewError, setPreviewError] = useState<string | null>(null)
  const [previewRows, setPreviewRows] = useState<any[]>([])
  const [previewJob, setPreviewJob] = useState<any | null>(null)
  const [previewValidationErrors, setPreviewValidationErrors] = useState<any[]>([])

  const loadJobs = async () => {
    setJobsLoading(true)
    setJobsError(null)
    try {
      const data = await jobsApi.list()
      setJobs(Array.isArray(data) ? data : [])
    } catch (e: any) {
      setJobsError(e?.response?.data?.detail || 'Failed to load import jobs')
      setJobs([])
    } finally {
      setJobsLoading(false)
    }
  }

  useEffect(() => {
    void loadJobs()
  }, [])

  const downloadTemplate = async () => {
    try {
      const res = await http.get(`/import-jobs/templates/${kind}/`, {
        params: { format },
        responseType: 'blob',
      })
      downloadAsFile(res.data, `template_${kind.toLowerCase()}.${format}`)
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Template download failed')
    }
  }

  const preview = async () => {
    setPreviewLoading(true)
    setPreviewError(null)
    setPreviewRows([])
    setPreviewJob(null)
    setPreviewValidationErrors([])
    try {
      const fileObj: any = fileList[0]?.originFileObj
      if (!fileObj) {
        setPreviewError('Please choose a file')
        return
      }
      // Validate mapping JSON client-side so we can show clean errors.
      let mappingObj: any = {}
      try {
        mappingObj = mapping ? JSON.parse(mapping) : {}
      } catch {
        setPreviewError('Mapping must be valid JSON')
        return
      }

      const fd = new FormData()
      fd.append('kind', kind)
      fd.append('file', fileObj)
      fd.append('mapping', JSON.stringify(mappingObj))

      const res = await http.post('/import-jobs/preview/', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setPreviewJob(res.data?.job)
      setPreviewRows(Array.isArray(res.data?.preview_rows) ? res.data.preview_rows : [])
      setPreviewValidationErrors(Array.isArray(res.data?.errors) ? res.data.errors : [])
      message.success('Preview created')
      await loadJobs()
    } catch (e: any) {
      setPreviewError(e?.response?.data?.detail || 'Preview failed')
    } finally {
      setPreviewLoading(false)
    }
  }

  const commit = async () => {
    if (!previewJob?.id) return
    try {
      const res = await http.post(`/import-jobs/${previewJob.id}/commit/`, {})
      message.success(res.data?.detail || 'Committed')
      setPreviewJob(null)
      setPreviewRows([])
      setPreviewValidationErrors([])
      await loadJobs()
    } catch (e: any) {
      const detail = e?.response?.data?.detail || 'Commit failed'
      const errs = e?.response?.data?.errors
      message.error(detail)
      if (Array.isArray(errs)) setPreviewValidationErrors(errs)
    }
  }

  return (
    <div className="panel">
      <div className="page-header">
        <div>
          <Typography.Title level={2} style={{ margin: 0, fontSize: 26, fontWeight: 800, letterSpacing: '-0.3px' }}>
            Data Imports
          </Typography.Title>
          <Typography.Text type="secondary">Upload templates, preview validation, then commit.</Typography.Text>
        </div>
        <Space wrap style={{ flex: 1, justifyContent: 'flex-end' }}>
          <Button icon={<ReloadOutlined />} onClick={loadJobs} loading={jobsLoading}>Refresh</Button>
        </Space>
      </div>

      <Card style={{ borderRadius: 'var(--radius-lg)', marginBottom: 16 }}>
        <Space wrap style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space wrap>
            <div>
              <div style={{ color: 'var(--muted)', fontSize: 12, fontWeight: 700 }}>Kind</div>
              <Select
                value={kind}
                style={{ width: 220 }}
                onChange={(v) => setKind(v)}
                options={[
                  { label: 'Employees', value: 'EMPLOYEES' },
                  { label: 'Leave Balances', value: 'LEAVE_BALANCES' },
                  { label: 'Contracts', value: 'CONTRACTS' },
                ]}
              />
            </div>
            <div>
              <div style={{ color: 'var(--muted)', fontSize: 12, fontWeight: 700 }}>Template Format</div>
              <Select
                value={format}
                style={{ width: 140 }}
                onChange={(v) => setFormat(v)}
                options={[
                  { label: 'CSV', value: 'csv' },
                  { label: 'Excel (.xlsx)', value: 'xlsx' },
                ]}
              />
            </div>
          </Space>

          <Button icon={<DownloadOutlined />} onClick={downloadTemplate}>
            Download Template
          </Button>
        </Space>

        <Divider style={{ margin: '16px 0' }} />

        <Form layout="vertical">
          <Form.Item label="Mapping (optional JSON)" help='Example: {"department":"department"}'>
            <Input.TextArea rows={3} value={mapping} onChange={(e) => setMapping(e.target.value)} />
          </Form.Item>

          <Form.Item label="File">
            <Upload
              fileList={fileList}
              beforeUpload={() => false}
              onChange={({ fileList: fl }) => setFileList(fl.slice(-1))}
              maxCount={1}
            >
              <Button>Choose File</Button>
            </Upload>
          </Form.Item>

          <Space wrap>
            <Button type="primary" icon={<EyeOutlined />} onClick={preview} loading={previewLoading}>
              Preview
            </Button>
            <Button
              icon={<PlayCircleOutlined />}
              onClick={commit}
              disabled={!previewJob?.id || (previewValidationErrors?.length ?? 0) > 0}
            >
              Commit
            </Button>
          </Space>
        </Form>

        {(previewError || previewValidationErrors.length > 0) && (
          <div style={{ marginTop: 16 }}>
            {previewError && <Alert type="error" showIcon message={previewError} style={{ borderRadius: 10, marginBottom: 12 }} />}
            {previewValidationErrors.length > 0 && (
              <Alert
                type="warning"
                showIcon
                message="Validation errors"
                description={
                  <div style={{ maxHeight: 220, overflow: 'auto', paddingRight: 8 }}>
                    <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify(previewValidationErrors, null, 2)}</pre>
                  </div>
                }
                style={{ borderRadius: 10 }}
              />
            )}
          </div>
        )}

        {previewRows.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <Typography.Text type="secondary">Preview rows (first {previewRows.length})</Typography.Text>
            <Table
              size="small"
              rowKey={(_, idx) => String(idx)}
              dataSource={previewRows}
              pagination={{ pageSize: 10 }}
              scroll={{ x: true }}
              columns={Object.keys(previewRows[0] || {}).map((k) => ({ title: k, dataIndex: k }))}
            />
          </div>
        )}
      </Card>

      {jobsError && <Alert type="error" message={jobsError} showIcon style={{ marginBottom: 16, borderRadius: 10 }} />}

      <Card title="Import Jobs" style={{ borderRadius: 'var(--radius-lg)' }}>
        <Table
          rowKey="id"
          loading={jobsLoading}
          dataSource={jobs}
          pagination={{ pageSize: 10 }}
          columns={[
            { title: 'ID', dataIndex: 'id', width: 80 },
            { title: 'Kind', dataIndex: 'kind' },
            { title: 'Status', dataIndex: 'status' },
            { title: 'Created By', dataIndex: 'created_by' },
            { title: 'Created At', dataIndex: 'created_at' },
          ]}
        />
      </Card>
    </div>
  )
}
