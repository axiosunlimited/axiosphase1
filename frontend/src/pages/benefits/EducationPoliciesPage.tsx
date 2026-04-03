import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function EducationPoliciesPage() {
  return (
    <CrudPage
      title="Education Assistance Policy"
      endpoint="education-assistance-policies"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'Max Children', dataIndex: 'max_children_per_employee' },
        { title: 'Allowed Levels', dataIndex: 'allowed_levels', render: (_: any, r: any) => (Array.isArray(r.allowed_levels) ? r.allowed_levels.join(', ') : '') },
        { title: 'Max Amount / Child', dataIndex: 'max_claim_amount_per_child' },
        { title: 'Frequency', dataIndex: 'frequency' },
        { title: 'Eligible Contract Types', dataIndex: 'eligible_contract_types', render: (_: any, r: any) => (Array.isArray(r.eligible_contract_types) ? r.eligible_contract_types.join(', ') : '') },
        { title: 'Probation Required', dataIndex: 'require_completed_probation', render: (_: any, r: any) => (r.require_completed_probation ? 'Yes' : 'No') },
        { title: 'Max Child Age', dataIndex: 'max_child_age' },
        { title: 'Updated', dataIndex: 'updated_at' },
      ]}
      fields={[
        { name: 'max_children_per_employee', label: 'Max Children per Employee', type: 'number', required: true },
        {
          name: 'allowed_levels',
          label: 'Allowed Levels (JSON array)',
          type: 'json',
          required: true,
          placeholder: '["PRIMARY","SECONDARY","TERTIARY"]',
        },
        { name: 'max_claim_amount_per_child', label: 'Max Claim Amount per Child', type: 'number' },
        {
          name: 'frequency',
          label: 'Frequency',
          type: 'select',
          required: true,
          options: [
            { label: 'Per Term', value: 'TERM' },
            { label: 'Per Semester', value: 'SEMESTER' },
            { label: 'Per Year', value: 'YEAR' },
          ],
        },
        {
          name: 'eligible_contract_types',
          label: 'Eligible Contract Types (JSON array)',
          type: 'json',
          required: true,
          placeholder: '["PERMANENT", "FIXED_TERM"]',
        },
        { name: 'require_completed_probation', label: 'Require Completed Probation', type: 'boolean' },
        { name: 'max_child_age', label: 'Max Child Age', type: 'number' },
      ]}
    />
  )
}
