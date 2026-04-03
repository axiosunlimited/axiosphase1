import { http } from './client'

export type TokenResponse = { access: string; refresh: string }

export async function login(email: string, password: string, otp?: string, backup_code?: string) {
  const res = await http.post<TokenResponse>('/auth/token/', { email, password, otp, backup_code })
  return res.data
}

export async function refreshToken(refresh: string) {
  const res = await http.post<{ access: string }>('/auth/token/refresh/', { refresh })
  return res.data
}

export async function me() {
  const res = await http.get('/auth/me/')
  return res.data
}

// ----------------------------
// Invite-based onboarding
// ----------------------------

export type InviteStatus = 'pending' | 'used' | 'expired'

export type InviteListItem = {
  id: number
  email: string
  role: string
  auto_activate: boolean
  created_at: string
  expires_at: string
  used_at: string | null
  status: InviteStatus
  created_by: number | null
  created_by_email: string | null
  user: number | null
}

export type CreateInvitePayload = {
  email: string
  first_name?: string
  last_name?: string
  role?: string
  auto_activate?: boolean
  expires_in_days?: number
}

export type CreateInviteResponse = {
  invite_id: number
  email: string
  role: string
  auto_activate: boolean
  expires_at: string
  activation_link: string
  email_sent: boolean
  email_error: string | null
}

export async function listInvites(params?: { status?: InviteStatus; email?: string }) {
  const res = await http.get<InviteListItem[]>('/auth/invites/', { params })
  return res.data
}

// Alias endpoint requested: POST /api/v1/auth/invite/
export async function createInvite(payload: CreateInvitePayload) {
  const res = await http.post<CreateInviteResponse>('/auth/invite/', payload)
  return res.data
}

export async function resendInvite(inviteId: number) {
  const res = await http.post<{
    invite_id: number
    activation_link: string
    expires_at: string
    email_sent: boolean
    email_error: string | null
  }>(`/auth/invites/${inviteId}/resend/`, {})
  return res.data
}

export async function validateInvite(token: string) {
  const res = await http.get<{
    email: string
    full_name: string
    role: string
    expires_at: string
    auto_activate: boolean
  }>('/auth/invites/validate/', { params: { token } })
  return res.data
}

// Endpoint requested: POST /api/v1/auth/accept-invite/
export async function acceptInvite(token: string, password: string) {
  const res = await http.post<{
    detail: string
    user_id: number
    email: string
    role: string
    is_active: boolean
  }>('/auth/accept-invite/', { token, password })
  return res.data
}

/**
 * POST to initialize/re-initialize 2FA setup
 * Returns OTPAuth URI for QR code generation
 */
export async function setup2FA(): Promise<{ otpauth_uri: string }> {
  const res = await http.post("/auth/2fa/setup/");
  return res.data;
}

/**
 * POST to confirm and enable 2FA
 * Requires valid OTP from authenticator app
 * Returns backup codes
 */
export async function enable2FA(otp: string): Promise<{ codes: string[] }> {
  const res = await http.post('/auth/2fa/enable/', { otp })
  return res.data
}

/**
 * POST to disable 2FA
 * Requires either OTP or backup code for security
 */
export async function disable2FA(otp?: string, backup_code?: string): Promise<{ detail: string }> {
  const res = await http.post('/auth/2fa/disable/', { otp, backup_code })
  return res.data
}

export async function fetchDashboard(): Promise<any> {
  const res = await http.get('/dashboard/')
  return res.data
}

export async function requestPasswordReset(email: string): Promise<{ detail: string }> {
  const res = await http.post('/auth/password-reset/', { email })
  return res.data
}

export async function confirmPasswordReset(token: string, new_password: string): Promise<{ detail: string }> {
  const res = await http.post('/auth/password-reset/confirm/', { token, new_password })
  return res.data
}