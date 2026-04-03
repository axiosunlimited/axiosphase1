import React, { useEffect, useMemo, useState } from 'react'
import { Alert, Button, Space, Table, Typography, message } from 'antd'
import { DownloadOutlined, ReloadOutlined } from '@ant-design/icons'
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

export default function BackupsPage() {
  const api = useMemo(() => resource('backups'), [])
  const [rows, setRows] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [running, setRunning] = useState(false)
  const [downloadingId, setDownloadingId] = useState<number | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.list()
      setRows(Array.isArray(data) ? data : [])
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load backups')
      setRows([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const runBackup = async () => {
    setRunning(true)
    try {
      await http.post('/backups/run_backup/', {})
      message.success('Backup started')
      await load()
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Backup failed')
    } finally {
      setRunning(false)
    }
  }

  const download = async (r: any) => {
    setDownloadingId(r.id)
    try {
      const res = await http.get(`/backups/${r.id}/download/`, { responseType: 'blob' })
      const name = (r.file && String(r.file).split('/').pop()) || `backup_${r.id}.zip`
      downloadAsFile(res.data, name)
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Download failed')
    } finally {
      setDownloadingId(null)
    }
  }

  return (
    <div className="panel">
      <div className="page-header">
        <div>
          <Typography.Title level={2} style={{ margin: 0, fontSize: 26, fontWeight: 800, letterSpacing: '-0.3px' }}>
            Backups
          </Typography.Title>
          <Typography.Text type="secondary">Manual and scheduled backup artifacts.</Typography.Text>
        </div>
        <Space wrap style={{ flex: 1, justifyContent: 'flex-end' }}>
          <Button icon={<ReloadOutlined />} onClick={load} loading={loading}>
            Refresh
          </Button>
          <Button type="primary" onClick={runBackup} loading={running}>
            Run Backup
          </Button>
        </Space>
      </div>

      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16, borderRadius: 10 }} />}

      <Table
        rowKey="id"
        loading={loading}
        dataSource={rows}
        pagination={{ pageSize: 10 }}
        columns={[
          { title: 'ID', dataIndex: 'id', width: 80 },
          { title: 'Created At', dataIndex: 'created_at' },
          { title: 'Created By', dataIndex: 'created_by' },
          { title: 'Size (bytes)', dataIndex: 'size_bytes' },
          {
            title: 'Actions',
            render: (_: any, r: any) => (
              <Button
                icon={<DownloadOutlined />}
                size="small"
                loading={downloadingId === r.id}
                onClick={() => download(r)}
              >
                Download
              </Button>
            ),
          },
        ]}
      />
    </div>
  )
}
