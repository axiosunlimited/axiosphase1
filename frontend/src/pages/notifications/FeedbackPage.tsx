import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function FeedbackPage() {
  return (
    <CrudPage
      title="Feedback"
      endpoint="feedback"
      columns={[
        { title: 'ID', dataIndex: 'id' },
        { title: 'User', dataIndex: 'user_email' },
        { title: 'Category', dataIndex: 'category' },
        { title: 'Page', dataIndex: 'page' },
        { title: 'Message', dataIndex: 'message' },
        { title: 'Created', dataIndex: 'created_at' },
      ]}
      fields={[
        {
          name: 'category',
          label: 'Category',
          type: 'select',
          required: true,
          options: [
            { label: 'General', value: 'GENERAL' },
            { label: 'Bug Report', value: 'BUG' },
            { label: 'Feature Request', value: 'FEATURE_REQUEST' },
            { label: 'UI/UX Improvement', value: 'UI_UX' },
            { label: 'Performance Issue', value: 'PERFORMANCE' },
            { label: 'Other', value: 'OTHER' },
          ],
        },
        { name: 'page', label: 'Page', type: 'text' },
        { name: 'message', label: 'Message', type: 'textarea', required: true },
      ]}
    />
  )
}
