import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function PermissionsPage() {
  return (
    <CrudPage
      title="Permissions"
      endpoint="permissions"
      readOnly
      columns={[
        { title: 'ID', dataIndex: 'id' },
        {
          title: 'App.Model',
          render: (_: any, r: any) => `${r.content_type?.app_label}.${r.content_type?.model}`,
        },
        { title: 'Codename', dataIndex: 'codename' },
        { title: 'Name', dataIndex: 'name' },
      ]}
      fields={[]}
    />
  )
}
