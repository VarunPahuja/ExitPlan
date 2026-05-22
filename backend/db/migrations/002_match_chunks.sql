-- Exit Plan — pgvector similarity search function
-- Run in Supabase SQL editor after 001_initial_schema.sql

CREATE OR REPLACE FUNCTION match_policy_chunks(
  query_embedding vector(384),
  match_country_id uuid,
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id uuid,
  content text,
  source_url text,
  visa_type text,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    id,
    content,
    source_url,
    visa_type,
    1 - (embedding <=> query_embedding) AS similarity
  FROM policy_chunks
  WHERE country_id = match_country_id
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
$$;
