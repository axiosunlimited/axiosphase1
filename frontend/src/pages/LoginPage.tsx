import React, { useEffect, useState } from 'react'
import { Alert, Button, Form, Input, Modal, Tooltip, Typography, message } from 'antd'
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import {
  ArrowRightOutlined,
  InfoCircleOutlined,
  LockOutlined,
  MailOutlined,
  MoonOutlined,
  SunOutlined,
} from '@ant-design/icons'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { requestPasswordReset, confirmPasswordReset } from '../api/auth'

const { Text, Link } = Typography

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation() as any
  const [searchParams, setSearchParams] = useSearchParams()
  const { login } = useAuth()
  const { mode, toggle } = useTheme()

  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  // Forgot password modal
  const [forgotOpen, setForgotOpen] = useState(false)
  const [forgotLoading, setForgotLoading] = useState(false)
  const [forgotForm] = Form.useForm()

  // Reset confirm modal (when user clicks link with ?reset_token=...)
  const [resetOpen, setResetOpen] = useState(false)
  const [resetLoading, setResetLoading] = useState(false)
  const [resetForm] = Form.useForm()
  const resetToken = searchParams.get('reset_token')

  useEffect(() => {
    if (resetToken) {
      setResetOpen(true)
    }
  }, [resetToken])

  async function onFinish(values: any) {
    setError(null)
    setLoading(true)
    try {
      await login(values.email, values.password, values.otp, values.backup_code)
      const dest = location?.state?.from || '/'
      navigate(dest)
    } catch (e: any) {
      const msg = e?.response?.data?.detail || 'Login failed'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  async function onForgotSubmit() {
    const vals = await forgotForm.validateFields()
    setForgotLoading(true)
    try {
      await requestPasswordReset(vals.email)
      message.success('If the email exists, a reset link has been sent. Check your inbox.')
      setForgotOpen(false)
      forgotForm.resetFields()
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Request failed')
    } finally {
      setForgotLoading(false)
    }
  }

  async function onResetSubmit() {
    const vals = await resetForm.validateFields()
    if (vals.new_password !== vals.confirm_password) {
      message.error('Passwords do not match')
      return
    }
    setResetLoading(true)
    try {
      await confirmPasswordReset(resetToken!, vals.new_password)
      message.success('Password has been reset. You can now sign in.')
      setResetOpen(false)
      resetForm.resetFields()
      setSearchParams({})
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Reset failed')
    } finally {
      setResetLoading(false)
    }
  }

  return (
    <div className="auth-shell">
      {/* ── Left branding panel ── */}
      <div className="auth-left">
        <div className="auth-left__brand">
          <div className="brand__icon" aria-hidden>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="7" height="7" rx="1"/>
              <rect x="14" y="3" width="7" height="7" rx="1"/>
              <rect x="3" y="14" width="7" height="7" rx="1"/>
              <rect x="14" y="14" width="7" height="7" rx="1"/>
            </svg>
          </div>
          <span>HRIS Portal</span>
        </div>

        <div className="auth-left__copy">
          <h1 className="auth-left__headline">
            Empowering your<br />workforce journey.
          </h1>
          <p className="auth-left__sub">
            Manage employees, recruitment, and performance in one unified,
            professional workspace designed for modern growth.
          </p>
        </div>
      </div>

      {/* ── Right form panel ── */}
      <div className="auth-right">
        <Tooltip title={mode === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}>
          <button className="theme-fab" onClick={toggle}>
            {mode === 'dark' ? <SunOutlined /> : <MoonOutlined />}
          </button>
        </Tooltip>

        <div className="auth-card">
          <h2 className="auth-card__title">Welcome Back</h2>
          <p className="auth-card__subtitle">Please enter your details to sign in.</p>

          {error && (
            <Alert
              message={error}
              type="error"
              showIcon
              style={{ marginBottom: 14, borderRadius: 10 }}
            />
          )}

          <Form layout="vertical" onFinish={onFinish} requiredMark={false} className="auth-grid">
            <Form.Item
              label="Email Address"
              name="email"
              rules={[{ required: true, type: 'email' }]}
              style={{ marginBottom: 12 }}
            >
              <Input
                prefix={<MailOutlined style={{ color: 'var(--muted)' }} />}
                placeholder="you@example.com"
                size="large"
              />
            </Form.Item>

            <Form.Item
              label={
                <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                  <span>Password</span>
                  <Link
                    href="#"
                    style={{ fontSize: 13, fontWeight: 600 }}
                    onClick={(e) => { e.preventDefault(); setForgotOpen(true) }}
                  >
                    Forgot password?
                  </Link>
                </div>
              }
              name="password"
              rules={[{ required: true }]}
              style={{ marginBottom: 14 }}
            >
              <Input.Password
                prefix={<LockOutlined style={{ color: 'var(--muted)' }} />}
                size="large"
              />
            </Form.Item>

            <div className="auth-divider">SECURITY DETAILS</div>

            <div className="auth-two-col">
              <Form.Item
                label="OTP (2FA)"
                name="otp"
                style={{ marginBottom: 0 }}
              >
                <Input placeholder="123456" />
              </Form.Item>
              <Form.Item
                label="Backup Code"
                name="backup_code"
                style={{ marginBottom: 0 }}
              >
                <Input placeholder="Optional" />
              </Form.Item>
            </div>

            <Form.Item style={{ marginBottom: 8, marginTop: 4 }}>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                icon={<ArrowRightOutlined />}
                block
                size="large"
                style={{ height: 46, borderRadius: 12, fontWeight: 700 }}
              >
                Sign in to Dashboard
              </Button>
            </Form.Item>

            <div className="auth-footer">
              Don't have an account?{' '}
              <Link href="#" onClick={(e) => e.preventDefault()}>
                Contact HR Admin
              </Link>
            </div>
          </Form>

          <Alert
            style={{ marginTop: 16, borderRadius: 10 }}
            icon={<InfoCircleOutlined />}
            type="info"
            showIcon
            message="Default dev administrator credentials are configured in your backend environment settings for local testing."
          />
        </div>
      </div>

      {/* ── Forgot Password Modal ── */}
      <Modal
        open={forgotOpen}
        title="Reset Password"
        onCancel={() => setForgotOpen(false)}
        onOk={onForgotSubmit}
        okText="Send Reset Link"
        confirmLoading={forgotLoading}
        destroyOnClose
      >
        <p style={{ color: 'var(--muted)', marginBottom: 16 }}>
          Enter your email address and we'll send you a link to reset your password.
        </p>
        <Form layout="vertical" form={forgotForm}>
          <Form.Item name="email" label="Email Address" rules={[{ required: true, type: 'email' }]}>
            <Input prefix={<MailOutlined />} placeholder="you@example.com" size="large" />
          </Form.Item>
        </Form>
      </Modal>

      {/* ── Reset Confirm Modal (from email link) ── */}
      <Modal
        open={resetOpen}
        title="Set New Password"
        onCancel={() => { setResetOpen(false); setSearchParams({}) }}
        onOk={onResetSubmit}
        okText="Reset Password"
        confirmLoading={resetLoading}
        destroyOnClose
      >
        <p style={{ color: 'var(--muted)', marginBottom: 16 }}>
          Enter your new password below.
        </p>
        <Form layout="vertical" form={resetForm}>
          <Form.Item name="new_password" label="New Password" rules={[{ required: true, min: 8 }]}>
            <Input.Password prefix={<LockOutlined />} size="large" />
          </Form.Item>
          <Form.Item name="confirm_password" label="Confirm Password" rules={[{ required: true, min: 8 }]}>
            <Input.Password prefix={<LockOutlined />} size="large" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}