import React, { useState } from 'react'
import {
  FileTextOutlined,
  LoadingOutlined,
} from '@ant-design/icons'
import {
  Button,
  Card,
  Col,
  DatePicker,
  Divider,
  Form,
  Input,
  InputNumber,
  message,
  Row,
  Select,
  Space,
  Spin,
  Switch,
  Tag,
  Typography,
} from 'antd'
import dayjs from 'dayjs'
import { http } from '../../api/client'

interface ContractFormData {
  employee_name: string
  national_id: string
  address: string
  mobile: string
  position: string
  department: string
  grade?: string
  contract_type?: string
  start_date: string
  end_date: string
  probation_months?: number
  basic_salary: number
  transport_allowance?: number
  housing_allowance?: number
  bonus_enabled?: boolean
  medical_aid_enabled?: boolean
  school_fees_enabled?: boolean
  reporting_to?: string
  signed_by?: string
  witness_name?: string
}

export default function DraftContractPage() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)

  const handleGenerateContract = async (values: any) => {
    setLoading(true)
    try {
      // Convert date objects to ISO string format
      const payload = {
        ...values,
        start_date: values.start_date ? values.start_date.format('YYYY-MM-DD') : '',
        end_date: values.end_date ? values.end_date.format('YYYY-MM-DD') : '',
        basic_salary: parseFloat(values.basic_salary),
        transport_allowance: values.transport_allowance ? parseFloat(values.transport_allowance) : 120,
        housing_allowance: values.housing_allowance ? parseFloat(values.housing_allowance) : 175,
      }

      const response = await http.post('/contracts/generate_contract/', payload, {
        responseType: 'blob',
      })

      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      const filename = `Contract_${values.employee_name.replace(/\s+/g, '_')}_${values.start_date.format('YYYY-MM-DD')}.docx`
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.parentNode?.removeChild(link)

      message.success('Contract generated and downloaded successfully!')
      form.resetFields()
    } catch (error: any) {
      const errorMsg = error?.response?.data?.detail || error?.message || 'Failed to generate contract'
      message.error(errorMsg)
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="panel">
      <div className="page-header">
        <div>
          <h1>Draft Employment Contract</h1>
          <p>Generate an employment contract from the AJU template</p>
        </div>
      </div>

      <Card style={{ maxWidth: 1000, marginBottom: 24 }}>
        <Spin spinning={loading} indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />}>
          <Form
            form={form}
            layout="vertical"
            onFinish={handleGenerateContract}
            autoComplete="off"
            requiredMark="optional"
          >
            {/* Employee Information */}
            <div style={{ marginBottom: 24 }}>
              <Typography.Title level={4}>Employee Information</Typography.Title>
              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="employee_name"
                    label="Full Name"
                    rules={[{ required: true, message: 'Please enter employee name' }]}
                  >
                    <Input placeholder="e.g., John Doe" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="national_id"
                    label="National ID / Passport Number"
                    rules={[{ required: true, message: 'Please enter national ID' }]}
                  >
                    <Input placeholder="e.g., 12-345678Z45" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="address"
                    label="Address"
                    rules={[{ required: true, message: 'Please enter address' }]}
                  >
                    <Input placeholder="e.g., Harare, Zimbabwe" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="mobile"
                    label="Mobile Number"
                    rules={[{ required: true, message: 'Please enter mobile number' }]}
                  >
                    <Input placeholder="e.g., +263 712 345678" />
                  </Form.Item>
                </Col>
              </Row>
            </div>

            <Divider />

            {/* Position and Employment Details */}
            <div style={{ marginBottom: 24 }}>
              <Typography.Title level={4}>Position & Employment Details</Typography.Title>
              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="position"
                    label="Position Title"
                    rules={[{ required: true, message: 'Please enter position' }]}
                  >
                    <Input placeholder="e.g., Lecturer, Senior Lecturer" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="department"
                    label="Department"
                    rules={[{ required: true, message: 'Please enter department' }]}
                  >
                    <Input placeholder="e.g., School of Education and Leadership" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col xs={24} md={6}>
                  <Form.Item
                    name="grade"
                    label="Grade (Optional)"
                  >
                    <Input placeholder="e.g., D1:2" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={6}>
                  <Form.Item
                    name="contract_type"
                    label="Contract Type"
                  >
                    <Select placeholder="Select type">
                      <Select.Option value="PERMANENT">Permanent</Select.Option>
                      <Select.Option value="FIXED_TERM">Fixed Term</Select.Option>
                      <Select.Option value="PART_TIME">Part time</Select.Option>
                      <Select.Option value="CASUAL">Casual</Select.Option>
                      <Select.Option value="CONSULTANCY">Consultancy</Select.Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} md={6}>
                  <Form.Item
                    name="reporting_to"
                    label="Reporting To"
                  >
                    <Input placeholder="e.g., Dean of School" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={6}>
                  <Form.Item
                    name="probation_months"
                    label="Probation (months)"
                  >
                    <InputNumber min={1} max={12} defaultValue={3} />
                  </Form.Item>
                </Col>
              </Row>
            </div>

            <Divider />

            {/* Employment Dates and Salary */}
            <div style={{ marginBottom: 24 }}>
              <Typography.Title level={4}>Contract Dates & Compensation</Typography.Title>
              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="start_date"
                    label="Start Date"
                    rules={[{ required: true, message: 'Please select start date' }]}
                  >
                    <DatePicker style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="end_date"
                    label="End Date"
                    rules={[{ required: true, message: 'Please select end date' }]}
                  >
                    <DatePicker style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="basic_salary"
                    label="Basic Salary (USD)"
                    rules={[{ required: true, message: 'Please enter salary' }]}
                  >
                    <InputNumber
                      min={0}
                      precision={2}
                      placeholder="0.00"
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="transport_allowance"
                    label="Transport Allowance (USD)"
                  >
                    <InputNumber
                      min={0}
                      precision={2}
                      defaultValue={120}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="housing_allowance"
                    label="Housing Allowance (USD)"
                  >
                    <InputNumber
                      min={0}
                      precision={2}
                      defaultValue={175}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
              </Row>
            </div>

            <Divider />

            {/* Benefits and Options */}
            <div style={{ marginBottom: 24 }}>
              <Typography.Title level={4}>Benefits & Options</Typography.Title>
              <Row gutter={16}>
                <Col xs={24} sm={12} md={8}>
                  <Form.Item
                    name="bonus_enabled"
                    label="Enable Bonus (13th Cheque)"
                    valuePropName="checked"
                  >
                    <Switch defaultChecked />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12} md={8}>
                  <Form.Item
                    name="medical_aid_enabled"
                    label="Enable Medical Aid"
                    valuePropName="checked"
                  >
                    <Switch defaultChecked />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12} md={8}>
                  <Form.Item
                    name="school_fees_enabled"
                    label="Enable School Fees"
                    valuePropName="checked"
                  >
                    <Switch defaultChecked />
                  </Form.Item>
                </Col>
              </Row>
            </div>

            <Divider />

            {/* Signatory Information */}
            <div style={{ marginBottom: 24 }}>
              <Typography.Title level={4}>Signatory Information</Typography.Title>
              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="signed_by"
                    label="Signed By (Employer Representative)"
                  >
                    <Input placeholder="e.g., Dr. T. Mbatna" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="witness_name"
                    label="Witness Name"
                  >
                    <Input defaultValue="Human Resources Officer" />
                  </Form.Item>
                </Col>
              </Row>
            </div>

            <Divider />

            {/* Action Buttons */}
            <Row gutter={16} justify="center">
              <Col>
                <Button
                  type="default"
                  size="large"
                  onClick={() => form.resetFields()}
                >
                  Clear Form
                </Button>
              </Col>
              <Col>
                <Button
                  type="primary"
                  size="large"
                  htmlType="submit"
                  loading={loading}
                  icon={<FileTextOutlined />}
                >
                  Generate & Download Contract
                </Button>
              </Col>
            </Row>
          </Form>
        </Spin>
      </Card>

      {/* Instructions Card */}
      <Card title="Instructions" size="small">
        <ol style={{ lineHeight: 1.8 }}>
          <li>Fill in all employee information and contract details</li>
          <li>Review the compensation and benefits settings</li>
          <li>Click "Generate & Download Contract" to create the .docx file</li>
          <li>The contract will be downloaded with the employee name and start date in the filename</li>
          <li>You can then open the document in Microsoft Word or compatible software</li>
          <li>Print and have all parties sign the contract</li>
          <li>Store the signed contract in the employee's file</li>
        </ol>
      </Card>
    </div>
  )
}