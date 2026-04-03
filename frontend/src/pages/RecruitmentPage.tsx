import React, { useEffect, useState } from 'react'
import { Button, Form, Input, Modal, Table, Typography, Alert } from 'antd'
import * as api from '../api/hris'

export default function RecruitmentPage() {
  const [vacancies, setVacancies] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [open, setOpen] = useState(false)

  async function load() {
    try {
      const data = await api.listVacancies()
      setVacancies(data)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load vacancies')
    }
  }

  useEffect(() => { void load() }, [])

  async function create(values: any) {
    // For demo: requires department_id and position_id already created in backend admin.
    try {
      await api.createVacancy(values)
      setOpen(false)
      void load()
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to create vacancy')
    }
  }

  return (
    <>
      <Typography.Title level={3}>Recruitment</Typography.Title>
      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 12 }} />}
      <Button type="primary" onClick={() => setOpen(true)} style={{ marginBottom: 12 }}>New Vacancy</Button>
      <Table
        rowKey="id"
        dataSource={vacancies}
        pagination={{ pageSize: 5 }}
        columns={[
          { title: 'Title', dataIndex: 'title' },
          { title: 'Department', render: (_, r) => r.department?.name },
          { title: 'Position', render: (_, r) => r.position?.title },
          { title: 'Status', dataIndex: 'status' },
          { title: 'Closing', dataIndex: 'closing_date' },
        ]}
      />
      <Modal title="Create Vacancy" open={open} onCancel={() => setOpen(false)} footer={null}>
        <Form layout="vertical" onFinish={create}>
          <Form.Item label="Title" name="title" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item label="Description" name="description" rules={[{ required: true }]}><Input.TextArea rows={4} /></Form.Item>
          <Form.Item label="Department ID" name="department_id" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item label="Position ID" name="position_id" rules={[{ required: true }]}><Input /></Form.Item>
          <Button type="primary" htmlType="submit" block>Create</Button>
        </Form>
      </Modal>
    </>
  )
}
