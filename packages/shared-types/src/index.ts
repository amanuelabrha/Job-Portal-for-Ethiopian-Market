/** Shared API contracts — keep in sync with FastAPI `schemas.py` and frontend usage. */

export type UserRole = "job_seeker" | "employer" | "admin";

export type JobType = "full_time" | "part_time" | "remote" | "contract";

export interface JobOut {
  id: number;
  company_id: number;
  company_name: string;
  title_en: string;
  title_am?: string | null;
  description_en: string;
  description_am?: string | null;
  requirements_en: string;
  requirements_am?: string | null;
  category: string;
  city: string;
  salary_min_etb?: number | null;
  salary_max_etb?: number | null;
  job_type: JobType;
  deadline?: string | null;
  is_premium: boolean;
  view_count: number;
  application_count: number;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserOut {
  id: number;
  email?: string | null;
  phone?: string | null;
  role: UserRole;
  preferred_locale: string;
}
