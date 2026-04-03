import React, { useEffect, useState } from 'react'
import { Button, Form, Input, Modal, Table, Typography, Alert, DatePicker, Upload } from 'antd'
import { UploadOutlined, FileOutlined } from '@ant-design/icons'
import * as api from '../api/hris'

export default function LeavePage() {
  const [balances, setBalances] = useState<any[]>([])
  const [requests, setRequests] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [open, setOpen] = useState(false)
  const [fileList, setFileList] = useState<any[]>([])

  async function load() {
    try {
      const [b, r] = await Promise.all([api.listLeaveBalances(), api.listLeaveRequests()])
      setBalances(b)
      setRequests(r)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load leave data')
    }
  }

  useEffect(() => { void load() }, [])

  async function create(values: any) {
    try {
      const formData = new FormData()
      formData.append('leave_type_id', values.leave_type)
      formData.append('start_date', values.range[0].format('YYYY-MM-DD'))
      formData.append('end_date', values.range[1].format('YYYY-MM-DD'))
      formData.append('reason', values.reason || '')
      
      if (fileList.length > 0) {
        formData.append('supporting_document', fileList[0].originFileObj)
      }

      await api.createLeaveRequest(formData)
      setOpen(false)
      setFileList([])
      void load()
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to create leave request')
    }
  }

  return (
    <>
      <Typography.Title level={3}>Leave</Typography.Title>
      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 12 }} />}
      <Typography.Title level={4}>Balances</Typography.Title>
      <Table
        rowKey="id"
        dataSource={balances}
        pagination={false}
        columns={[
          { title: 'Type', render: (_, r) => r.leave_type?.name },
          { title: 'Year', dataIndex: 'year' },
          { title: 'Entitled', dataIndex: 'days_entitled' },
          { title: 'Used', dataIndex: 'days_used' },
          { title: 'Remaining', dataIndex: 'days_remaining' },
        ]}
      />
      <div style={{ height: 16 }} />
      <Typography.Title level={4}>Requests</Typography.Title>
      <Button type="primary" onClick={() => setOpen(true)} style={{ marginBottom: 12 }}>New Leave Request</Button>
      <Table
        rowKey="id"
        dataSource={requests}
        pagination={{ pageSize: 5 }}
        columns={[
          { title: 'Type', render: (_, r) => (typeof r.leave_type === 'object' ? r.leave_type.name : r.leave_type) },
          { title: 'Start', dataIndex: 'start_date' },
          { title: 'End', dataIndex: 'end_date' },
          { title: 'Days', dataIndex: 'days_requested' },
          { title: 'Status', dataIndex: 'status' },
          {
            title: 'Document',
            dataIndex: 'supporting_document',
            render: (val) => val ? (
              <a href={val} target="_blank" rel="noreferrer">
                <FileOutlined /> View
              </a>
            ) : '-'
          },
        ]}
      />

      <Modal title="New Leave Request" open={open} onCancel={() => setOpen(false)} footer={null}>
        <Form layout="vertical" onFinish={create}>
          <Form.Item label="Leave Type ID" name="leave_type" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item label="Date Range" name="range" rules={[{ required: true }]}>
            <DatePicker.RangePicker />
          </Form.Item>
          <Form.Item label="Reason" name="reason"><Input.TextArea rows={3} /></Form.Item>
          
          <Form.Item label="Supporting Document">
            <Upload
              beforeUpload={() => false}
              fileList={fileList}
              onChange={({ fileList }) => setFileList(fileList)}
              maxCount={1}
            >
              <Button icon={<UploadOutlined />}>Click to Upload</Button>
            </Upload>
          </Form.Item>

          <Button type="primary" htmlType="submit" block>Submit</Button>
        </Form>
      </Modal>
    </>
  )
}
