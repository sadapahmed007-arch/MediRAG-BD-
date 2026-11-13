import axios from 'axios';

const api = axios.create({ baseURL: '/api', headers: { 'Content-Type': 'application/json' } });

export async function askQuestion(question) {
  const { data } = await api.post('/ask', { question });
  return data;
}

export async function getDashboard() {
  const { data } = await api.get('/dashboard');
  return data;
}

export async function healthCheck() {
  const { data } = await api.get('/health');
  return data;
}

export async function getSuggestions(query) {
  if (!query || query.trim().length < 2) return [];
  const { data } = await api.get('/suggestions', { params: { q: query } });
  return data.suggestions || [];
}
