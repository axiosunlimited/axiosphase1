import React from 'react'
import CrudPage from '../../components/CrudPage'

export default function PublicHolidaysPage() {
  return (
    <CrudPage
      title="Public Holidays"
      endpoint="public-holidays"
      columns={[
        { title: 'Date', dataIndex: 'date' },
        { title: 'Name', dataIndex: 'name' },
      ]}
      fields={[
        { name: 'date', label: 'Date', type: 'date', required: true },
        { name: 'name', label: 'Name', type: 'text', required: true },
      ]}
    />
  )
}
