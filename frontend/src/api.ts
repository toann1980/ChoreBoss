import type { AuthSession, ChoreRead, LoginResponse } from './types';

const DEFAULT_API_BASE_URL = 'http://localhost:8055/api';

export class ApiError extends Error {
  public readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

function getApiBaseUrl(): string {
  return import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL;
}

async function parseResponseError(response: Response): Promise<string> {
  try {
    const payload: unknown = await response.json();
    if (payload && typeof payload === 'object') {
      const record = payload as Record<string, unknown>;
      const message = record.error ?? record.detail;
      if (typeof message === 'string' && message.trim()) {
        return message;
      }
    }
  } catch {
    // Fall through to generic error.
  }

  return `Request failed with status ${response.status}`;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    throw new ApiError(await parseResponseError(response), response.status);
  }

  return (await response.json()) as T;
}

export async function login(loginName: string, pin: string): Promise<LoginResponse> {
  return requestJson<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ login_name: loginName, pin }),
  });
}

export async function loadChores(token: string): Promise<ChoreRead[]> {
  const response = await fetch(`${getApiBaseUrl()}/chores/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new ApiError(await parseResponseError(response), response.status);
  }

  return (await response.json()) as ChoreRead[];
}

export function toSession(loginName: string, loginResponse: LoginResponse): AuthSession {
  return {
    loginName,
    ...loginResponse,
  };
}
