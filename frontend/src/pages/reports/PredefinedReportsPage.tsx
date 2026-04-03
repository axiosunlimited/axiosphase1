import React, { useEffect, useMemo, useState } from 'react'
import { Alert, Button, Card, Col, Divider, Dropdown, InputNumber, Modal, Row, Space, Spin, Typography, message } from 'antd'
import { DownloadOutlined, PlayCircleOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { http } from '../../api/client'

type Predef = {
  key: string
  name: string
  audience?: string
  description?: string
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

function isArrayOfObjects(v: any): v is Array<Record<string, any>> {
  return Array.isArray(v) && v.length > 0 && typeof v[0] === 'object' && v[0] !== null && !Array.isArray(v[0])
}

export default function PredefinedReportsPage() {
  const navigate = useNavigate()
  const [reports, setReports] = useState<Predef[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [year, setYear] = useState<number>(() => new Date().getFullYear())

  const [runOpen, setRunOpen] = useState(false)
  const [runTitle, setRunTitle] = useState('')
  const [runData, setRunData] = useState<any>(null)
  const [runLoading, setRunLoading] = useState(false)

  const metrics = useMemo(() => runData?.metrics ?? runData?.report?.metrics ?? runData?.data?.metrics ?? runData?.metrics, [runData])

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await http.get('/predefined-reports/')
      setReports(Array.isArray(res.data) ? res.data : [])
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load predefined reports')
      setReports([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const runReport = async (r: Predef) => {
    setRunLoading(true)
    setRunTitle(r.name)
    try {
      const res = await http.post(`/predefined-reports/${r.key}/run/`, { year })
      setRunData(res.data)
      setRunOpen(true)
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to run report')
    } finally {
      setRunLoading(false)
    }
  }

  const exportReport = async (r: Predef, fmt: 'pdf' | 'xlsx') => {
    try {
      const res = await http.get(`/predefined-reports/${r.key}/export/`, {
        params: { export_format: fmt, year },
        responseType: 'blob',
      })
      const ext = fmt === 'pdf' ? 'pdf' : 'xlsx'
      downloadBlob(res.data, `${r.key}_${year}.${ext}`)
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
    <div className="panel">
      <div className="page-header">
        <div>
          <Typography.Title level={2} style={{ margin: 0, fontSize: 26, fontWeight: 800, letterSpacing: '-0.3px' }}>Predefined Reports</Typography.Title>
          <Typography.Text type="secondary">Council, HR Committee and Workforce Planning reports with PDF/Excel export.</Typography.Text>
        </div>
        <Space wrap style={{ flex: 1, justifyContent: 'flex-end' }}>
          <Dropdown
            menu={{
              items: [
                {
                  key: 'predefined',
                  label: 'Predefined Reports',
                  onClick: () => navigate('/reports'),
                },
                {
                  key: 'custom',
                  label: 'Custom Reports',
                  onClick: () => navigate('/reports/custom'),
                },
                {
                  type: 'divider',
                },
                {
                  key: 'analytics',
                  label: 'Analytics Dashboard',
                  onClick: () => navigate('/analytics'),
                },
              ],
            }}
          >
            <Button type="default">Reports & Analytics ▼</Button>
          </Dropdown>
          <span style={{ color: 'var(--muted)', fontWeight: 600 }}>Year</span>
          <InputNumber min={2000} max={2100} value={year} onChange={(v) => setYear(Number(v ?? new Date().getFullYear()))} />
          <Button className="btn-refresh" onClick={load}>Refresh</Button>
        </Space>
      </div>

      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16, borderRadius: 10 }} />}

      {loading ? (
        <div style={{ padding: 24, display: 'flex', justifyContent: 'center' }}><Spin /></div>
      ) : (
        <Row gutter={[16, 16]}>
          {reports.map((r) => (
            <Col key={r.key} xs={24} md={12} lg={8}>
              <Card
                title={<div style={{ fontWeight: 800 }}>{r.name}</div>}
                bordered
                style={{ borderRadius: 'var(--radius-lg)' }}
                extra={r.audience ? <span style={{ color: 'var(--muted)' }}>{r.audience}</span> : null}
                actions={[
                  <Button
                    key="run"
                    type="text"
                    icon={<PlayCircleOutlined />}
                    loading={runLoading}
                    onClick={() => runReport(r)}
                  >
                    Run
                  </Button>,
                  <Button
                    key="pdf"
                    type="text"
                    icon={<DownloadOutlined />}
                    onClick={() => exportReport(r, 'pdf')}
                  >
                    PDF
                  </Button>,
                  <Button
                    key="xlsx"
                    type="text"
                    icon={<DownloadOutlined />}
                    onClick={() => exportReport(r, 'xlsx')}
                  >
                    Excel
                  </Button>,
                ]}
              >
                <Typography.Paragraph style={{ marginBottom: 0, color: 'var(--text-secondary)' }}>
                  {r.description}
                </Typography.Paragraph>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      <Modal
        open={runOpen}
        title={runTitle}
        onCancel={() => setRunOpen(false)}
        footer={null}
        width={980}
      >
        {!runData ? (
          <div style={{ padding: 24, display: 'flex', justifyContent: 'center' }}><Spin /></div>
        ) : (
          <>
            <Typography.Text type="secondary">Generated: {runData.generated_at || ''}</Typography.Text>
            <Divider />

            {metrics && typeof metrics === 'object' ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                {Object.entries(metrics).map(([k, v]) => (
                  <div key={k} style={{ background: 'var(--bg-hover)', border: '1px solid var(--border)', borderRadius: 12, padding: 14 }}>
                    <Typography.Title level={5} style={{ margin: 0, fontWeight: 800 }}>{k}</Typography.Title>

                    {typeof v === 'number' || typeof v === 'string' || v === null ? (
                      <Typography.Paragraph style={{ margin: '8px 0 0' }}>{v === null ? '—' : String(v)}</Typography.Paragraph>
                    ) : isArrayOfObjects(v) ? (
                      <div style={{ marginTop: 10 }}>
                        <pre style={{ display: 'none' }} />
                        <div style={{ overflowX: 'auto' }}>
                          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                              <tr>
                                {Object.keys(v[0] || {}).map((col) => (
                                  <th key={col} style={{ textAlign: 'left', padding: '8px 10px', borderBottom: '1px solid var(--border)', fontSize: 12, color: 'var(--text-secondary)' }}>{col}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {v.slice(0, 100).map((row, idx) => (
                                <tr key={idx}>
                                  {Object.keys(v[0] || {}).map((col) => (
                                    <td key={col} style={{ padding: '8px 10px', borderBottom: '1px solid var(--border-light)', fontSize: 13 }}>{String((row as any)?.[col] ?? '')}</td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                          {v.length > 100 ? (
                            <Typography.Text type="secondary">Showing first 100 rows.</Typography.Text>
                          ) : null}
                        </div>
                      </div>
                    ) : Array.isArray(v) ? (
                      <div style={{ marginTop: 10 }}>
                        <ul style={{ margin: 0, paddingLeft: 18 }}>
                          {v.slice(0, 50).map((item, idx) => (
                            <li key={idx}>{typeof item === 'string' || typeof item === 'number' ? String(item) : JSON.stringify(item)}</li>
                          ))}
                        </ul>
                        {v.length > 50 ? (
                          <Typography.Text type="secondary">Showing first 50 items.</Typography.Text>
                        ) : null}
                      </div>
                    ) : (
                      <pre style={{ marginTop: 10, background: 'var(--sidebar-bg)', color: 'var(--text)', padding: 12, borderRadius: 10, overflowX: 'auto' }}>
                        {JSON.stringify(v, null, 2)}
                      </pre>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <pre style={{ background: 'var(--sidebar-bg)', color: 'var(--text)', padding: 12, borderRadius: 10, overflowX: 'auto' }}>
                {JSON.stringify(runData, null, 2)}
              </pre>
            )}
          </>
        )}
      </Modal>
    </div>
  )
}
