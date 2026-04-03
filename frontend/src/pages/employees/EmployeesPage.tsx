import React from 'react'
import { Link } from 'react-router-dom'
import { Button } from 'antd'
import { EyeOutlined } from '@ant-design/icons'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'
import { useAuth } from '../../context/AuthContext'

export default function EmployeesPage() {
  const { user } = useAuth()
  const isEmployee = user?.role === 'EMPLOYEE'
  const { options: deptOptions } = useOptions('departments', (d) => d.name)
  const { options: posOptions } = useOptions('positions', (p) => `${p.title} — ${p.department?.name ?? ''}`)
  const { options: userOptions } = useOptions('users', (u) => `${u.email} (${u.role})`)

  return (
    <CrudPage
      title="Employees"
      endpoint="employees"
      readOnly={isEmployee}
      columns={[
        { title: 'Employee #', dataIndex: 'employee_number' },
        {
          title: 'Name',
          render: (_: any, r: any) => r.user?.full_name || `${r.user?.first_name ?? ''} ${r.user?.last_name ?? ''}`.trim() || r.user?.email,
        },
        { title: 'Email', render: (_: any, r: any) => r.user?.email },
        { title: 'Department', render: (_: any, r: any) => r.department?.name },
        { title: 'Position', render: (_: any, r: any) => r.position?.title },
        {
          title: 'Status',
          render: (_: any, r: any) => (
            <span className={`badge-pill ${r.employment_status === 'Active' || r.employment_status === 'FULL_TIME' ? 'badge-success' : 'badge-neutral'}`}>
              {r.employment_status}
            </span>
          )
        },
        {
          title: '',
          width: 100,
          render: (_: any, r: any) => (
            <Link to={`/employees/profile/${r.id}`}>
              <Button size="small" icon={<EyeOutlined />}>Profile</Button>
            </Link>
          ),
        },
      ]}
      fields={[
        { name: 'user_id', label: 'User', type: 'select', required: true, options: userOptions },
        { name: 'employee_number', label: 'Employee Number', type: 'text', required: true },
        { name: 'department_id', label: 'Department', type: 'select', required: true, options: deptOptions },
        { name: 'position_id', label: 'Position', type: 'select', required: true, options: posOptions },
        { name: 'employment_status', label: 'Employment Status', type: 'text' },
        {
          name: 'contract_type',
          label: 'Contract Type',
          type: 'select',
          options: [
            { label: 'Permanent', value: 'PERMANENT' },
            { label: 'Fixed Term', value: 'FIXED_TERM' },
            { label: 'Part time', value: 'PART_TIME' },
            { label: 'Casual', value: 'CASUAL' },
            { label: 'Consultancy', value: 'CONSULTANCY' },
          ],
        },
        {
          name: 'title',
          label: 'Title',
          type: 'select',
          options: [
            { label: 'Mr', value: 'MR' },
            { label: 'Ms', value: 'MS' },
            { label: 'Mrs', value: 'MRS' },
            { label: 'Dr', value: 'DR' },
            { label: 'Prof', value: 'PROF' },
            { label: 'Rev', value: 'REV' },
          ],
        },
        {
          name: 'gender',
          label: 'Gender',
          type: 'select',
          options: [
            { label: 'Male', value: 'MALE' },
            { label: 'Female', value: 'FEMALE' },
            { label: 'Other', value: 'OTHER' },
          ],
        },
        { name: 'grade', label: 'Grade', type: 'text' },
        { name: 'school', label: 'School', type: 'text' },
        { name: 'hire_date', label: 'Hire Date', type: 'date' },
        { name: 'end_date', label: 'End Date (Current Contract)', type: 'date' },
        { name: 'date_of_birth', label: 'Date of Birth', type: 'date' },
        { name: 'national_id', label: 'National ID', type: 'text' },
        { name: 'phone', label: 'Phone', type: 'text' },
        { name: 'address', label: 'Address', type: 'textarea' },
      ]}
    />
  )
}
