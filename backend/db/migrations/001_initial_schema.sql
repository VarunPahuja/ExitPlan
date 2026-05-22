-- Exit Plan — initial schema migration
-- Run once against your Supabase project via the SQL editor or psql.

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Countries table
CREATE TABLE countries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  code TEXT UNIQUE NOT NULL,
  region TEXT,
  active BOOLEAN DEFAULT true
);

-- Seed 10 MVP countries
INSERT INTO countries (name, code, region) VALUES
  ('United Kingdom', 'GB', 'Europe'),
  ('Canada', 'CA', 'North America'),
  ('Germany', 'DE', 'Europe'),
  ('Australia', 'AU', 'Oceania'),
  ('Netherlands', 'NL', 'Europe'),
  ('Portugal', 'PT', 'Europe'),
  ('Ireland', 'IE', 'Europe'),
  ('United Arab Emirates', 'AE', 'Middle East'),
  ('New Zealand', 'NZ', 'Oceania'),
  ('Singapore', 'SG', 'Asia');

-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  nationality TEXT,
  current_status TEXT,
  field TEXT,
  degree_level TEXT,
  savings_range TEXT,
  career_goal TEXT,
  weights JSONB,
  saved_countries TEXT[],
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Country scores cache
CREATE TABLE country_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  country_id UUID REFERENCES countries(id),
  profile_hash TEXT NOT NULL,
  job_score INT,
  pr_score INT,
  visa_score INT,
  salary_score INT,
  language_score INT,
  total_score INT,
  calculated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_country_scores_profile_hash ON country_scores(profile_hash);

-- Policy chunks with vector embeddings
CREATE TABLE policy_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  country_id UUID REFERENCES countries(id),
  visa_type TEXT,
  content TEXT NOT NULL,
  source_url TEXT,
  effective_date DATE,
  embedding vector(384),
  scraped_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_policy_chunks_country ON policy_chunks(country_id);
CREATE INDEX idx_policy_chunks_embedding ON policy_chunks
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Policy changes log
CREATE TABLE policy_changes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  country_id UUID REFERENCES countries(id),
  visa_type TEXT,
  change_summary TEXT,
  detected_at TIMESTAMPTZ DEFAULT now(),
  old_value TEXT,
  new_value TEXT
);

-- User alerts
CREATE TABLE user_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  country_id UUID REFERENCES countries(id),
  alert_type TEXT,
  message TEXT,
  plain_english TEXT,
  sent_at TIMESTAMPTZ,
  read_at TIMESTAMPTZ,
  source_url TEXT
);
CREATE INDEX idx_user_alerts_user_id ON user_alerts(user_id);

-- Outcome stories
CREATE TABLE outcomes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nationality TEXT,
  field TEXT,
  degree_level TEXT,
  destination_country TEXT,
  visa_type TEXT,
  months_to_job INT,
  summary TEXT,
  year INT,
  anonymous BOOLEAN DEFAULT true,
  verified BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);
