import React from 'react'
import CrudPage from '../../components/CrudPage'

const roleOptions = [
  { value: 'SYSTEM_ADMIN', label: 'System Administrator' },
  { value: 'HR_MANAGER', label: 'HR Manager' },
  { value: 'HR_OFFICER', label: 'HR Officer' },
  { value: 'LINE_MANAGER', label: 'Line Manager' },
  { value: 'FINANCE_OFFICER', label: 'Finance Officer' },
  { value: 'EMPLOYEE', label: 'Employee' },
]

const processOptions = [
  { value: 'LEAVE_LINE_MANAGER', label: 'Leave: Line Manager Approval' },
  { value: 'LEAVE_HR', label: 'Leave: HR Approval' },
  { value: 'VACANCY_APPROVAL', label: 'Recruitment: Vacancy Approval' },
  { value: 'VACANCY_PUBLISH', label: 'Recruitment: Vacancy Publish' },
]

export default function ApprovalConfigsPage() {
  return (
    <CrudPage
      title="Approval Workflows"
      endpoint="approval-process-configs"
      columns={[
        { title: 'Process', dataIndex: 'process_code' },
        { title: 'Name', dataIndex: 'name' },
        { title: 'Active', render: (_: any, r: any) => (r.is_active ? 'Yes' : 'No') },
        {
          title: 'Allowed Roles',
          render: (_: any, r: any) => Array.isArray(r.allowed_roles) ? r.allowed_roles.join(', ') : '',
        },
        { title: 'Updated', dataIndex: 'updated_at' },
      ]}
      fields={[
        { name: 'process_code', label: 'Process Code', type: 'select', required: true, options: processOptions },
        { name: 'name', label: 'Name', type: 'text', required: true },
        { name: 'description', label: 'Description', type: 'textarea' },
        { name: 'allowed_roles', label: 'Allowed Roles', type: 'multiselect', options: roleOptions },
        { name: 'is_active', label: 'Is Active', type: 'boolean' },
      ]}
      transformSubmit={(values, ctx) => {
        // prevent changing process_code after creation
        if (ctx.mode === 'edit' && ctx.record?.process_code) {
          return { ...values, process_code: ctx.record.process_code }
        }
        return values
      }}
    />
  )
}
