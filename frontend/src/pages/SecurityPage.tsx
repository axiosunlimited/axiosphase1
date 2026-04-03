import React, { useMemo, useState } from "react";
import { Alert, Button, Divider, Form, Input, Space, Typography, message } from "antd";
import { QRCodeSVG } from "qrcode.react";
import * as authApi from "../api/auth";
import { useAuth } from "../context/AuthContext";

type EnableForm = { otp: string };
type DisableForm = { otp?: string; backup_code?: string };

export default function SecurityPage() {
  const { user, reload } = useAuth();

  const [uri, setUri] = useState<string | null>(null);
  const [backupCodes, setBackupCodes] = useState<string[] | null>(null);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const enabled = !!user?.twofa_enabled;

  const setupHint = useMemo(() => {
    if (enabled) return "2FA is enabled. You can re-open setup to regenerate the QR code/URI if needed.";
    return "Generate a QR code and connect your authenticator app.";
  }, [enabled]);

  async function handleSetup() {
    setErrorMsg(null);
    setStatusMsg(null);
    setBackupCodes(null);

    setBusy(true);
    try {
      // POST to setup endpoint (secure - state-changing operation)
      const data = await authApi.setup2FA();
      setUri(data.otpauth_uri);
      setStatusMsg("Scan the QR code in an authenticator app, then confirm with a one-time code (OTP).");
    } catch (e: any) {
      setUri(null);
      setErrorMsg(e?.response?.data?.detail || "Failed to set up 2FA.");
    } finally {
      setBusy(false);
    }
  }

  async function handleEnable(values: EnableForm) {
    setErrorMsg(null);
    setStatusMsg(null);

    setBusy(true);
    try {
      const otp = (values.otp || "").trim();

      if (!otp) {
        setErrorMsg("OTP is required to enable 2FA.");
        setBusy(false);
        return;
      }

      const data = await authApi.enable2FA(otp);
      setBackupCodes(data.codes || []);
      setStatusMsg("2FA enabled successfully! Save your backup codes somewhere safe.");
      setUri(null); // Clear URI after successful enable
      await reload();
    } catch (e: any) {
      setErrorMsg(e?.response?.data?.detail || "Failed to enable 2FA. Please check your OTP and try again.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDisable(values: DisableForm) {
    setErrorMsg(null);
    setStatusMsg(null);

    const otp = (values.otp || "").trim();
    const backup = (values.backup_code || "").trim();

    if (!otp && !backup) {
      setErrorMsg("Enter either an OTP or a backup code to disable 2FA.");
      return;
    }

    setBusy(true);
    try {
      await authApi.disable2FA(otp || undefined, backup || undefined);
      setStatusMsg("2FA disabled successfully.");
      setUri(null);
      setBackupCodes(null);
      await reload();
    } catch (e: any) {
      setErrorMsg(e?.response?.data?.detail || "Failed to disable 2FA. Please check your credentials and try again.");
    } finally {
      setBusy(false);
    }
  }

  function copyUri() {
    if (!uri) return;
    navigator.clipboard
      .writeText(uri)
      .then(() => message.success("Copied setup URI to clipboard"))
      .catch(() => message.error("Could not copy to clipboard"));
  }

  function copyBackupCodes() {
    if (!backupCodes || backupCodes.length === 0) return;
    navigator.clipboard
      .writeText(backupCodes.join("\n"))
      .then(() => message.success("Copied backup codes to clipboard"))
      .catch(() => message.error("Could not copy to clipboard"));
  }

  return (
    <div className="panel">
      <Typography.Title level={3} style={{ marginTop: 0, fontWeight: 800, letterSpacing: '-0.3px' }}>
        Security Settings (Two-Factor Authentication)
      </Typography.Title>

      {statusMsg && <Alert type="success" message={statusMsg} showIcon closable style={{ marginBottom: 12 }} />}
      {errorMsg && <Alert type="error" message={errorMsg} showIcon closable style={{ marginBottom: 12 }} />}

      <Space direction="vertical" size="middle" style={{ width: "100%" }}>
        <Space align="start" style={{ width: "100%", flexWrap: "wrap" }}>
          <Button type="primary" loading={busy} onClick={handleSetup} disabled={busy}>
            {enabled ? "Regenerate 2FA Setup" : "Setup 2FA"}
          </Button>

          <Alert
            type={enabled ? "info" : "warning"}
            showIcon
            message={enabled ? "2FA is currently enabled on your account." : "2FA is not enabled yet."}
            description={setupHint}
            style={{ flex: 1, minWidth: 300 }}
          />
        </Space>

        {uri && (
          <>
            <Divider />
            <div style={{ display: "flex", gap: 24, alignItems: "flex-start", flexWrap: "wrap" }}>
              <div style={{ textAlign: "center" }}>
                <Typography.Title level={5}>Scan QR Code</Typography.Title>
                <QRCodeSVG value={uri} size={220} level="H" includeMargin />
              </div>

              <div style={{ minWidth: 300, flex: 1 }}>
                <Typography.Title level={5}>Manual Setup URI</Typography.Title>
                <Typography.Paragraph type="secondary">
                  If you can't scan the QR code, copy and paste this URI into your authenticator app:
                </Typography.Paragraph>

                <Input.TextArea value={uri} readOnly rows={3} style={{ marginBottom: 8 }} />
                <Button onClick={copyUri} style={{ marginBottom: 16 }}>
                  Copy URI
                </Button>

                {!enabled && (
                  <>
                    <Divider />
                    <Typography.Title level={5} style={{ marginTop: 0 }}>
                      Confirm & Enable 2FA
                    </Typography.Title>
                    <Typography.Paragraph type="secondary">
                      Enter the 6-digit code from your authenticator app to enable 2FA.
                    </Typography.Paragraph>

                    <Form layout="vertical" onFinish={handleEnable}>
                      <Form.Item
                        label="One-Time Password (OTP)"
                        name="otp"
                        rules={[
                          { required: true, message: "OTP is required to enable 2FA" },
                          { pattern: /^\d{6}$/, message: "OTP must be exactly 6 digits" },
                        ]}
                      >
                        <Input
                          inputMode="numeric"
                          placeholder="123456"
                          maxLength={6}
                          disabled={busy}
                        />
                      </Form.Item>

                      <Button type="primary" htmlType="submit" loading={busy} disabled={busy}>
                        Enable 2FA
                      </Button>
                    </Form>
                  </>
                )}
              </div>
            </div>
          </>
        )}

        {backupCodes && backupCodes.length > 0 && (
          <>
            <Divider />
            <Alert
              type="warning"
              showIcon
              message="Important: Save Your Backup Codes"
              description="These backup codes can be used to access your account if you lose access to your authenticator app. Save them in a secure location. They will not be shown again."
              style={{ marginBottom: 12 }}
            />

            <Typography.Title level={4}>Backup Codes</Typography.Title>
            <Typography.Paragraph>
              Each code can be used only once. Store them securely:
            </Typography.Paragraph>

            <pre style={{
              padding: 16,
              background: "rgba(100, 116, 139, 0.06)",
              borderRadius: 12,
              overflowX: "auto",
              border: "1px solid var(--border)"
            }}>
              {backupCodes.join("\n")}
            </pre>

            <Button onClick={copyBackupCodes} style={{ marginTop: 8 }}>
              Copy All Backup Codes
            </Button>
          </>
        )}

        {enabled && (
          <>
            <Divider />
            <Alert
              type="info"
              showIcon
              message="Disable Two-Factor Authentication"
              description="Disabling 2FA will make your account less secure. You'll need to verify your identity with either an OTP or a backup code."
              style={{ marginBottom: 16 }}
            />

            <Typography.Title level={4}>Disable 2FA</Typography.Title>

            <Form layout="vertical" onFinish={handleDisable}>
              <Form.Item
                label="One-Time Password (OTP) - Recommended"
                name="otp"
                help="Enter the 6-digit code from your authenticator app"
                rules={[
                  {
                    validator: async (_, val) => {
                      const v = (val || "").trim();
                      if (!v) return Promise.resolve();
                      if (!/^\d{6}$/.test(v)) return Promise.reject(new Error("OTP must be exactly 6 digits"));
                      return Promise.resolve();
                    },
                  },
                ]}
              >
                <Input
                  inputMode="numeric"
                  placeholder="123456"
                  maxLength={6}
                  disabled={busy}
                />
              </Form.Item>

              <Form.Item
                label="Backup Code - Alternative"
                name="backup_code"
                help="Use a backup code if you've lost access to your authenticator app"
              >
                <Input
                  placeholder="e.g. ABCD-EFGH-IJKL"
                  disabled={busy}
                />
              </Form.Item>

              <Button danger htmlType="submit" loading={busy} disabled={busy}>
                Disable 2FA
              </Button>
            </Form>
          </>
        )}
      </Space>
    </div>
  );
}