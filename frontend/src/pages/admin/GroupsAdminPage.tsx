import React, { useMemo } from 'react'
import { Tag } from 'antd'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'

export default function GroupsAdminPage() {
  const { options: permOptions } = useOptions(
    'permissions',
    (p) => `${p.content_type?.app_label}.${p.content_type?.model}: ${p.codename}`,
  )

  const permMap = useMemo(() => new Map(permOptions.map((o) => [o.value, o.label])), [permOptions])

  return (
    <CrudPage
      title="Groups"
      endpoint="groups"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Name', dataIndex: 'name' },
        {
          title: 'Permissions',
          render: (_: any, r: any) => {
            const ids = Array.isArray(r.permissions) ? r.permissions : []
            if (ids.length === 0) return '-'
            const labels = ids.map((id: any) => permMap.get(id) ?? `#${id}`)
            const first = labels.slice(0, 4)
            return (
              <>
                {first.map((l: string) => (
                  <Tag key={`${r.id}-${l}`}>{l}</Tag>
                ))}
                {labels.length > 4 ? <Tag>+{labels.length - 4} more</Tag> : null}
              </>
            )
          },
        },
      ]}
      fields={[
        { name: 'name', label: 'Name', type: 'text', required: true },
        {
          name: 'permissions',
          label: 'Permissions',
          type: 'multiselect',
          options: permOptions,
          placeholder: 'Search permissions...',
        },
      ]}
    />
  )
}