import React, { useMemo } from 'react'
import { Button, Space, message } from 'antd'
import CrudPage from '../../components/CrudPage'
import { resource } from '../../api/resources'

export default function OutstandingTokensPage() {
  const api = useMemo(() => resource('outstanding-tokens'), [])

  return (
    <CrudPage
      title="Outstanding Tokens"
      endpoint="outstanding-tokens"
      readOnly
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'User', dataIndex: 'user_email' },
        { title: 'JTI', dataIndex: 'jti' },
        {
          title: 'Token',
          render: (_: any, r: any) => {
            const t = r.token || ''
            return t.length > 32 ? `${t.slice(0, 32)}…` : t
          },
        },
        { title: 'Created', dataIndex: 'created_at' },
        { title: 'Expires', dataIndex: 'expires_at' },
      ]}
      fields={[]}
      rowActions={(r, helpers) => (
        <Space wrap>
          <Button
            size="small"
            onClick={async () => {
              try {
                await api.action(r.id, 'blacklist')
                message.success('Token blacklisted')
                helpers.reload()
              } catch (e: any) {
                message.error(e?.response?.data?.detail || 'Failed to blacklist')
              }
            }}
          >
            Blacklist
          </Button>
        </Space>
      )}
    />
  )
}
