import { http } from './client'

export async function listEmployees() {
  const res = await http.get('/employees/')
  return res.data
}

export async function listDepartments() {
  const res = await http.get('/departments/')
  return res.data
}

export async function listVacancies() {
  const res = await http.get('/vacancies/')
  return res.data
}

export async function createVacancy(payload: any) {
  const res = await http.post('/vacancies/', payload)
  return res.data
}

export async function listApplicants() {
  const res = await http.get('/applicants/')
  return res.data
}

export async function listLeaveBalances() {
  const res = await http.get('/leave-balances/')
  return res.data
}

export async function listLeaveRequests() {
  const res = await http.get('/leave-requests/')
  return res.data
}

export async function createLeaveRequest(payload: FormData | any) {
  const res = await http.post('/leave-requests/', payload)
  return res.data
}

export async function listAppraisals() {
  const res = await http.get('/appraisals/')
  return res.data
}
