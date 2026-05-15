/** Demo logins displayed on the site for presentations */
export const DEMO_SEEKER = {
  email: "amanuelabrha02@gmail.com",
  password: "12345678",
  name: "Amanuel Abrha",
  role: "job_seeker" as const,
};

export const DEMO_EMPLOYER = {
  email: "employer@ethiojobs.et",
  password: "Employer123!",
  name: "Ethio Tech Solutions",
  role: "employer" as const,
};

export const DEMO_ADMIN = {
  email: "admin@ethiojobs.et",
  password: "Admin12345!",
  role: "admin" as const,
};

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const ETHIOPIAN_CITIES = [
  "Addis Ababa",
  "Bahir Dar",
  "Mekelle",
  "Hawassa",
  "Dire Dawa",
  "Gondar",
  "Adama",
];

export const JOB_CATEGORIES = [
  "Technology",
  "Finance",
  "Healthcare",
  "Education",
  "Engineering",
  "Sales & Marketing",
  "NGO",
  "Hospitality",
  "Manufacturing",
];

export const JOB_TYPES = ["full_time", "part_time", "remote", "contract"] as const;
