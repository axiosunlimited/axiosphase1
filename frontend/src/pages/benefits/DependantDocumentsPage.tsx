import React, { useState } from 'react'
import { Button, Space, message } from 'antd'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'
import { downloadBlob } from '../../api/resources'

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

export default function DependantDocumentsPage() {
  const { options: dependantOptions } = useOptions('dependants', (d) => `${d.name}`)
  const [downloadingId, setDownloadingId] = useState<number | null>(null)

  return (
    <CrudPage
      title="Dependant Documents"
      endpoint="dependant-documents"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Dependant', render: (_: any, r: any) => r.dependant?.name || r.dependant },
        { title: 'Doc Type', dataIndex: 'doc_type' },
        { title: 'Original Name', dataIndex: 'original_name' },
        { title: 'Size (bytes)', dataIndex: 'size_bytes' },
        { title: 'Uploaded', dataIndex: 'uploaded_at' },
        {
          title: 'Actions',
          render: (_: any, r: any) => (
            <Space>
              <Button
                size="small"
                loading={downloadingId === r.id}
                onClick={async () => {
                  try {
                    setDownloadingId(r.id)
                    const blob = await downloadBlob(`/dependant-documents/${r.id}/download/`)
                    downloadAsFile(blob, r.original_name || `dependant_document_${r.id}`)
                  } catch (e: any) {
                    message.error(e?.response?.data?.detail || 'Download failed')
                  } finally {
                    setDownloadingId(null)
                  }
                }}
              >
                Download
              </Button>
            </Space>
          ),
        },
      ]}
      fields={[
        { name: 'dependant', label: 'Dependant', type: 'select', required: true, options: dependantOptions },
        {
          name: 'doc_type',
          label: 'Document Type',
          type: 'select',
          required: true,
          options: [
            { label: 'Birth certificate', value: 'BIRTH_CERTIFICATE' },
            { label: 'Other', value: 'OTHER' },
          ],
        },
        { name: 'file', label: 'File', type: 'file', required: true },
      ]}
    />
  )
}
