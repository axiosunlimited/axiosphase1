import React from 'react'
import CrudPage from '../../components/CrudPage'
import { useOptions } from '../../hooks/useOptions'
import { useAuth } from '../../context/AuthContext'

export default function DependantsPage() {
  const { user } = useAuth()
  const role = user?.role || ''
  const isEmployee = role === 'EMPLOYEE'

  const { options: employeeOptions } = useOptions('employees', (e) => `${e.employee_number} — ${e.full_name || e.email}`)

  return (
    <CrudPage
      title="Dependants"
      endpoint="dependants"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        {
          title: 'Employee',
          render: (_: any, r: any) =>
            `${r.employee?.employee_number ?? ''} ${r.employee?.full_name ?? r.employee?.email ?? ''}`.trim(),
        },
        { title: 'Name', dataIndex: 'name' },
        { title: 'DOB', dataIndex: 'date_of_birth' },
        { title: 'Relationship', dataIndex: 'relationship' },
        { title: 'Level', dataIndex: 'education_level' },
        { title: 'Institution', dataIndex: 'institution_name' },
        { title: 'Student #', dataIndex: 'student_number' },
        { title: 'Eligible', dataIndex: 'benefit_eligible', render: (_: any, r: any) => (r.benefit_eligible ? 'Yes' : 'No') },
        { title: 'Ineligible Reason', dataIndex: 'ineligible_reason' },
        { title: 'Created', dataIndex: 'created_at' },
      ]}
      fields={[
        { name: 'employee_id', label: 'Employee', type: 'select', options: employeeOptions, hidden: () => isEmployee },
        { name: 'name', label: 'Name', type: 'text', required: true },
        { name: 'date_of_birth', label: 'Date of Birth', type: 'date', required: true },
        {
          name: 'relationship',
          label: 'Relationship',
          type: 'select',
          required: true,
          options: [
            { label: 'Child', value: 'CHILD' },
            { label: 'Spouse', value: 'SPOUSE' },
            { label: 'Father', value: 'FATHER' },
            { label: 'Mother', value: 'MOTHER' },
            { label: 'Other', value: 'OTHER' },
          ],
        },
        {
          name: 'education_level',
          label: 'Education Level',
          type: 'select',
          required: true,
          options: [
            { label: 'Primary', value: 'PRIMARY' },
            { label: 'Secondary', value: 'SECONDARY' },
            { label: 'Tertiary', value: 'TERTIARY' },
          ],
        },
        { name: 'institution_name', label: 'Institution', type: 'text' },
        { name: 'student_number', label: 'Student Number', type: 'text' },
      ]}
    />
  )
}
