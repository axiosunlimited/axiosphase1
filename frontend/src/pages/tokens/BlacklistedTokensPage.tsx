import React, { useMemo } from 'react'
import { Button, Popconfirm, Space, message } from 'antd'
import CrudPage from '../../components/CrudPage'
import { resource } from '../../api/resources'

export default function BlacklistedTokensPage() {
  const api = useMemo(() => resource('blacklisted-tokens'), [])

  return (
    <CrudPage
      title="Blacklisted Tokens"
      endpoint="blacklisted-tokens"
      readOnly
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'User', dataIndex: 'user_email' },
        { title: 'JTI', dataIndex: 'jti' },
        { title: 'Blacklisted At', dataIndex: 'blacklisted_at' },
        { title: 'Expires', dataIndex: 'expires_at' },
      ]}
      fields={[]}
      rowActions={(r, helpers) => (
        <Space wrap>
          <Popconfirm
            title="Un-blacklist this token?"
            onConfirm={async () => {
              try {
                await api.remove(r.id)
                message.success('Removed from blacklist')
                helpers.reload()
              } catch (e: any) {
                message.error(e?.response?.data?.detail || 'Failed to remove')
              }
            }}
          >
            <Button size="small" danger>
              Un-blacklist
            </Button>
          </Popconfirm>
        </Space>
      )}
    />
  )
}
