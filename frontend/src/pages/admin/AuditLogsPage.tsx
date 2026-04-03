import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function AuditLogsPage() {
  return (
    <CrudPage
      title="Audit Logs"
      endpoint="audit-logs"
      readOnly
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Time', dataIndex: 'created_at' },
        { title: 'Actor Email', dataIndex: 'actor_email' },
        { title: 'Actor Role', dataIndex: 'actor_role' },
        {
          title: 'Action',
          render: (_: any, r: any) => (
            <span className={`badge-pill ${r.action === 'CREATE' || r.action === 'LOGIN' ? 'badge-success' : 'badge-neutral'}`}>
              {r.action}
            </span>
          )
        },
        { title: 'Model', dataIndex: 'model' },
        { title: 'Object ID', dataIndex: 'object_id' },
        {
          title: 'Changes',
          render: (_: any, r: any) => {
            try {
              const txt = typeof r.changes === 'string' ? r.changes : JSON.stringify(r.changes)
              return txt && txt.length > 80 ? `${txt.slice(0, 80)}…` : txt
            } catch {
              return ''
            }
          },
        },
      ]}
      fields={[]}
    />
  )
}
