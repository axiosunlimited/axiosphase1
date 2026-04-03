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

export default function EducationClaimDocumentsPage() {
  const { options: claimOptions } = useOptions('education-claims', (c) => `#${c.id} — ${c.dependant_name || ''}`.trim())
  const [downloadingId, setDownloadingId] = useState<number | null>(null)

  return (
    <CrudPage
      title="Education Claim Documents"
      endpoint="education-claim-documents"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Claim', render: (_: any, r: any) => (r.claim ? `#${r.claim}` : '') },
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
                    const blob = await downloadBlob(`/education-claim-documents/${r.id}/download/`)
                    downloadAsFile(blob, r.original_name || `claim_document_${r.id}`)
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
        { name: 'claim', label: 'Claim', type: 'select', required: true, options: claimOptions },
        {
          name: 'doc_type',
          label: 'Document Type',
          type: 'select',
          required: true,
          options: [
            { label: 'Invoice/Receipt', value: 'INVOICE' },
            { label: 'Proof of registration', value: 'REGISTRATION' },
            { label: 'Proof of payment', value: 'PAYMENT_PROOF' },
            { label: 'Other', value: 'OTHER' },
          ],
        },
        { name: 'file', label: 'File', type: 'file', required: true },
      ]}
    />
  )
}
