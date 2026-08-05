export interface PersonRead {
  id: number;
  first_name: string;
  last_name: string;
  login_name: string;
  birthday: string;
  is_admin: boolean;
  assign_chores: boolean;
  sequence_num: number;
  created_at: string;
  updated_at: string;
}

export interface PersonCreateInput {
  first_name: string;
  last_name: string;
  login_name: string;
  birthday: string;
  is_admin?: boolean;
  assign_chores?: boolean;
  pin: string;
}

export interface PersonUpdateInput {
  first_name?: string;
  last_name?: string;
  login_name?: string;
  birthday?: string;
  is_admin?: boolean;
  assign_chores?: boolean;
}

export interface ChoreRead {
  id: number;
  name: string;
  description: string;
  person_id: number | null;
  recurrence: string;
  recurrence_day: number | null;
  last_completed_date: string | null;
  last_completed_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  person_id: number;
  is_admin: boolean;
}

export interface AuthSession extends LoginResponse {
  loginName: string;
}
