import { http } from './client'

export type Id = number | string

export type ListResponse<T> = T[]

export type ResourceClient<T = any> = {
  list: () => Promise<ListResponse<T>>
  retrieve: (id: Id) => Promise<T>
  create: (payload: any, config?: any) => Promise<T>
  update: (id: Id, payload: any, config?: any) => Promise<T>
  patch: (id: Id, payload: any, config?: any) => Promise<T>
  remove: (id: Id) => Promise<void>
  action: (id: Id, action: string, payload?: any, config?: any) => Promise<any>
}

export function resource<T = any>(path: string): ResourceClient<T> {
  const base = path.endsWith('/') ? path : `${path}/`
  return {
    list: async () => (await http.get(base)).data,
    retrieve: async (id) => (await http.get(`${base}${id}/`)).data,
    create: async (payload, config) => (await http.post(base, payload, config)).data,
    update: async (id, payload, config) => (await http.put(`${base}${id}/`, payload, config)).data,
    patch: async (id, payload, config) => (await http.patch(`${base}${id}/`, payload, config)).data,
    remove: async (id) => {
      await http.delete(`${base}${id}/`)
    },
    action: async (id, action, payload, config) => (await http.post(`${base}${id}/${action}/`, payload ?? {}, config)).data,
  }
}

export async function downloadBlob(url: string): Promise<Blob> {
  const res = await http.get(url, { responseType: 'blob' })
  return res.data
}
