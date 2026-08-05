export const API_ENDPOINTS = {
  health: '/health',
  authLogin: '/auth/login',
  people: '/people/',
  personById: (personId: number): string => `/people/${personId}`,
  chores: '/chores/',
  choreById: (choreId: number): string => `/chores/${choreId}`,
  choreComplete: (choreId: number): string => `/chores/${choreId}/complete`,
} as const;
