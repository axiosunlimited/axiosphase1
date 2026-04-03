import React, { useEffect, useMemo, useState } from 'react'
import { Alert, Button, Form, Input, Spin, Typography, message } from 'antd'
import { useLocation, useNavigate } from 'react-router-dom'
import { acceptInvite, validateInvite } from '../api/auth'

const { Title, Text } = Typography

function formatDateTime(val?: string | null) {
  if (!val) return ''
  const d = new Date(val)
  if (Number.isNaN(d.getTime())) return val
  return d.toLocaleString()
}

export default function AcceptInvitePage() {
  const location = useLocation()
  const navigate = useNavigate()

  const token = useMemo(() => {
    const q = new URLSearchParams(location.search)
    return (q.get('token') || '').trim()
  }, [location.search])

  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<null | {
    email: string
    full_name: string
    role: string
    expires_at: string
    auto_activate: boolean
  }>(null)

  const [done, setDone] = useState<null | { email: string; is_active: boolean }>(null)

  useEffect(() => {
    ;(async () => {
      setError(null)
      setInfo(null)
      if (!token) {
        setLoading(false)
        setError('Missing invite token. Please use the invite link you received.')
        return
      }
      setLoading(true)
      try {
        const data = await validateInvite(token)
        setInfo(data)
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to validate invite token')
      } finally {
        setLoading(false)
      }
    })()
  }, [token])

  const [form] = Form.useForm()

  const onFinish = async (values: any) => {
    if (!token) return
    setSubmitting(true)
    try {
      const res = await acceptInvite(token, values.password)
      message.success(res.detail || 'Invite accepted')
      setDone({ email: res.email, is_active: res.is_active })
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to accept invite')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 24,
        background: 'var(--bg-app)',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 520,
          background: 'var(--bg-panel)',
          borderRadius: 'var(--radius-xl)',
          padding: '28px 28px 22px',
          boxShadow: 'var(--shadow-lg)',
          border: '1px solid var(--border)',
        }}
      >
        <Title level={3} style={{ marginTop: 0, marginBottom: 6, fontWeight: 800 }}>
          Activate your account
        </Title>
        <Text type="secondary">
          Set your password to finish account setup.
        </Text>

        <div style={{ marginTop: 16 }}>
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 24 }}>
              <Spin size="large" />
            </div>
          ) : error ? (
            <Alert type="error" showIcon message={error} />
          ) : done ? (
            <Alert
              type={done.is_active ? 'success' : 'info'}
              showIcon
              message={
                done.is_active
                  ? 'Your account is active. You can sign in now.'
                  : 'Password set. Your account is pending activation by HR/Admin.'
              }
              description={
                <div style={{ marginTop: 8 }}>
                  <Button type="primary" onClick={() => navigate('/login')}>
                    Go to sign in
                  </Button>
                </div>
              }
            />
          ) : (
            <>
              {info && (
                <div
                  style={{
                    marginBottom: 14,
                    padding: 12,
                    borderRadius: 12,
                    background: 'var(--bg-hover)',
                    border: '1px solid var(--border)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
                    <div>
                      <Text type="secondary">Account</Text>
                      <div style={{ fontWeight: 700 }}>{info.full_name || info.email}</div>
                      <div>{info.email}</div>
                    </div>
                    <div>
                      <Text type="secondary">Role</Text>
                      <div style={{ fontWeight: 700 }}>{info.role}</div>
                    </div>
                  </div>
                  <div style={{ marginTop: 10 }}>
                    <Text type="secondary">Invite expires</Text>
                    <div style={{ fontWeight: 600 }}>{formatDateTime(info.expires_at)}</div>
                    <div style={{ marginTop: 6, color: 'var(--muted)' }}>
                      {info.auto_activate
                        ? 'Your account will become active immediately after you set your password.'
                        : 'After you set your password, HR/Admin will activate your account.'}
                    </div>
                  </div>
                </div>
              )}

              <Form layout="vertical" form={form} onFinish={onFinish} requiredMark={false}>
                <Form.Item
                  name="password"
                  label="New password"
                  rules={[
                    { required: true, message: 'Password is required' },
                    { min: 8, message: 'Must be at least 8 characters' },
                  ]}
                >
                  <Input.Password placeholder="Choose a strong password" />
                </Form.Item>

                <Form.Item
                  name="confirm"
                  label="Confirm password"
                  dependencies={['password']}
                  rules={[
                    { required: true, message: 'Please confirm your password' },
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (!value || getFieldValue('password') === value) return Promise.resolve()
                        return Promise.reject(new Error('Passwords do not match'))
                      },
                    }),
                  ]}
                >
                  <Input.Password placeholder="Re-enter password" />
                </Form.Item>

                <Button type="primary" htmlType="submit" loading={submitting} block style={{ height: 44, borderRadius: 12 }}>
                  Set password & activate
                </Button>
              </Form>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
