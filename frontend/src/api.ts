import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

export interface Source {
  id: number;
  name: string;
  source_type: string;
  url?: string | null;
  category_count: number;
  status: string;
  notes?: string | null;
  created_at: string;
}

export interface Category {
  id: number;
  source_id: number;
  original_name: string;
  description?: string | null;
  is_threat: boolean;
  status: string;
}

export interface Mapping {
  id: number;
  category_id: number;
  source_dim?: string[] | null;
  mech_dim?: string[] | null;
  target_dim?: string[] | null;
  vuln_tags: string[];
  carrier_tags?: string[] | null;
  confidence?: string | null;
  evidence?: string | null;
  notes?: string | null;
}

export interface DimValue {
  id: number;
  dimension: string;
  value_name: string;
  definition?: string | null;
  examples?: string | null;
  counter_examples?: string | null;
  decision_rules?: string | null;
  literature_ref?: string | null;
}

export interface SourceBreakdown {
  id: number;
  name: string;
  status: string;
  cats: number;
  mapped: number;
}

export interface Stats {
  total_sources: number;
  total_categories: number;
  total_mapped: number;
  total_threats: number;
  source_breakdown: SourceBreakdown[];
  dim_source_distribution: Record<string, number>;
  dim_mech_distribution: Record<string, number>;
  dim_target_distribution: Record<string, number>;
  confidence_distribution: Record<string, number>;
}

// Sources
export const api_getSources = () => api.get<Source[]>('/sources').then(r => r.data);
export const api_createSource = (d: { name: string; source_type: string; url?: string; notes?: string }) =>
  api.post<Source>('/sources', d).then(r => r.data);
export const api_deleteSource = (id: number) => api.delete(`/sources/${id}`);

// Categories
export const api_getCategories = (sid: number) =>
  api.get<Category[]>(`/sources/${sid}/categories`).then(r => r.data);
export const api_createCategory = (sid: number, d: { original_name: string; description?: string; is_threat?: boolean }) =>
  api.post<Category>(`/sources/${sid}/categories`, d).then(r => r.data);

export const api_deleteCategory = (cid: number) =>
  api.delete(`/categories/${cid}`).then(() => {});

export const api_updateCategory = (cid: number, d: { original_name?: string; description?: string }) =>
  api.put<Category>(`/categories/${cid}`, d).then(r => r.data);

// Mappings
export const api_getMapping = (cid: number): Promise<Mapping | null> =>
  api.get<Mapping>(`/categories/${cid}/mapping`)
    .then(r => r.data)
    .catch(() => null);

export const api_updateMapping = (cid: number, d: {
  source_dim?: string[] | null;
  mech_dim?: string[] | null;
  target_dim?: string[] | null;
  vuln_tags?: string[];
  carrier_tags?: string[] | null;
  confidence?: string | null;
  evidence?: string | null;
  notes?: string | null;
}) =>
  api.put<Mapping>(`/categories/${cid}/mapping`, d).then(r => r.data);

// Dimension Values
export const api_getDimValues = () => api.get<DimValue[]>('/dim-values').then(r => r.data);
export const api_createDimValue = (d: {
  dimension: string;
  value_name: string;
  definition?: string;
  examples?: string;
  counter_examples?: string;
  decision_rules?: string;
  literature_ref?: string;
}) => api.post<DimValue>('/dim-values', d).then(r => r.data);
export const api_updateDimValue = (id: number, d: {
  dimension: string;
  value_name: string;
  definition?: string;
  examples?: string;
  counter_examples?: string;
  decision_rules?: string;
  literature_ref?: string;
}) => api.put<DimValue>(`/dim-values/${id}`, d).then(r => r.data);
export const api_deleteDimValue = (id: number) => api.delete(`/dim-values/${id}`);

// Stats
export const api_getStats = () => api.get<Stats>('/stats').then(r => r.data);

// Export
export const api_exportCsv = () => api.get('/export/csv', { responseType: 'blob' });

export default api;
