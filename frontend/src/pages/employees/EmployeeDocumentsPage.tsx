import React, { useState } from 'react'
import { Button, Space, message } from 'antd'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'
import { downloadBlob } from '../../api/resources'
import { useAuth } from '../../context/AuthContext'

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

export default function EmployeeDocumentsPage() {
  const { user } = useAuth()
  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)

  const [downloadingId, setDownloadingId] = useState<number | null>(null)

  const isEmployee = user?.role === 'EMPLOYEE'

  return (
    <CrudPage
      title="Employee Documents"
      endpoint="employee-documents"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Employee', render: (_: any, r: any) => `${r.employee?.employee_number ?? ''} ${r.employee?.full_name ?? r.employee?.email ?? ''}`.trim() },
        { title: 'Category', dataIndex: 'category' },
        { title: 'Version', dataIndex: 'version' },
        { title: 'Latest', dataIndex: 'is_latest', render: (_: any, r: any) => (r.is_latest ? 'Yes' : 'No') },
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
                    // Backend decrypts and streams the file.
                    const blob = await downloadBlob(`/employee-documents/${r.id}/download/`)
                    downloadAsFile(blob, r.original_name || `employee_document_${r.id}`)
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
        { name: 'employee_id', label: 'Employee', type: 'select', required: true, options: employeeOptions, hidden: () => isEmployee },
        {
          name: 'category',
          label: 'Category',
          type: 'select',
          required: true,
          options: [
            { label: 'National ID / Passport', value: 'NATIONAL_ID_OR_PASSPORT' },
            { label: 'Academic Certificates', value: 'ACADEMIC_CERTIFICATES' },
            { label: 'Professional Certifications', value: 'PROFESSIONAL_CERTIFICATIONS' },
            { label: 'CV', value: 'CV' },
            { label: 'Banking Details', value: 'BANKING_DETAILS' },
            { label: 'Other', value: 'OTHER' },
          ],
        },
        { name: 'file', label: 'File', type: 'file', required: true },
      ]}
    />
  )
}
