-- AI Freelance Search App - Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    profile_picture_url TEXT,
    subscription_tier VARCHAR(50) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'premium')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_tier);

-- User skills table
CREATE TABLE user_skills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_name VARCHAR(255) NOT NULL,
    proficiency_level INTEGER CHECK (proficiency_level >= 1 AND proficiency_level <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, skill_name)
);

CREATE INDEX idx_user_skills_user_id ON user_skills(user_id);

-- User preferences table
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    min_hourly_rate DECIMAL(10, 2),
    max_hourly_rate DECIMAL(10, 2),
    min_fixed_price DECIMAL(10, 2),
    preferred_project_duration VARCHAR(50),
    preferred_locations TEXT[],
    preferred_timezones TEXT[],
    notification_enabled BOOLEAN DEFAULT TRUE,
    email_alerts BOOLEAN DEFAULT TRUE,
    push_alerts BOOLEAN DEFAULT TRUE,
    alert_frequency VARCHAR(50) DEFAULT 'realtime' CHECK (alert_frequency IN ('realtime', 'daily', 'weekly')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Freelance platforms table
CREATE TABLE freelance_platforms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    base_url TEXT NOT NULL,
    logo_url TEXT,
    has_api BOOLEAN DEFAULT FALSE,
    scraper_enabled BOOLEAN DEFAULT TRUE,
    last_scraped TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_platforms_name ON freelance_platforms(name);

-- Insert default platforms
INSERT INTO freelance_platforms (name, base_url, has_api, scraper_enabled) VALUES
('Upwork', 'https://www.upwork.com', FALSE, TRUE),
('Freelancer', 'https://www.freelancer.com', FALSE, TRUE),
('Fiverr', 'https://www.fiverr.com', FALSE, TRUE),
('Guru', 'https://www.guru.com', FALSE, TRUE);

-- Clients table
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    platform_id INTEGER REFERENCES freelance_platforms(id),
    external_client_id VARCHAR(255),
    name VARCHAR(255),
    company_name VARCHAR(255),
    profile_url TEXT,
    account_created_date TIMESTAMP,
    location VARCHAR(255),
    timezone VARCHAR(100),
    verified_payment BOOLEAN DEFAULT FALSE,
    total_jobs_posted INTEGER DEFAULT 0,
    total_hires INTEGER DEFAULT 0,
    total_spent DECIMAL(12, 2) DEFAULT 0,
    average_rating DECIMAL(3, 2),
    review_count INTEGER DEFAULT 0,
    average_response_time INTEGER,
    hire_rate DECIMAL(5, 2),
    avg_project_value DECIMAL(10, 2),
    repeat_hire_rate DECIMAL(5, 2),
    last_active TIMESTAMP,
    trust_score INTEGER CHECK (trust_score >= 0 AND trust_score <= 100),
    trust_score_updated_at TIMESTAMP,
    is_flagged BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform_id, external_client_id)
);

CREATE INDEX idx_clients_platform ON clients(platform_id);
CREATE INDEX idx_clients_trust_score ON clients(trust_score);
CREATE INDEX idx_clients_flagged ON clients(is_flagged);

-- Jobs table
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    platform_id INTEGER REFERENCES freelance_platforms(id),
    external_job_id VARCHAR(255),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(255),
    subcategory VARCHAR(255),
    skills_required TEXT[],
    job_type VARCHAR(50) CHECK (job_type IN ('hourly', 'fixed', 'both')),
    budget_min DECIMAL(10, 2),
    budget_max DECIMAL(10, 2),
    hourly_rate DECIMAL(10, 2),
    fixed_price DECIMAL(10, 2),
    duration VARCHAR(100),
    experience_level VARCHAR(50) CHECK (experience_level IN ('entry', 'intermediate', 'expert', 'any')),
    client_id INTEGER REFERENCES clients(id),
    location VARCHAR(255),
    timezone VARCHAR(100),
    posted_date TIMESTAMP,
    deadline TIMESTAMP,
    applicants_count INTEGER DEFAULT 0,
    url TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ai_summary TEXT,
    UNIQUE(platform_id, external_job_id)
);

CREATE INDEX idx_jobs_platform ON jobs(platform_id);
CREATE INDEX idx_jobs_client ON jobs(client_id);
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date DESC);
CREATE INDEX idx_jobs_active ON jobs(is_active);
CREATE INDEX idx_jobs_skills ON jobs USING GIN(skills_required);
CREATE INDEX idx_jobs_category ON jobs(category);

-- Client reviews table
CREATE TABLE client_reviews (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    freelancer_name VARCHAR(255),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    project_title VARCHAR(255),
    project_value DECIMAL(10, 2),
    review_date TIMESTAMP,
    sentiment_score DECIMAL(3, 2),
    key_themes TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reviews_client ON client_reviews(client_id);
CREATE INDEX idx_reviews_rating ON client_reviews(rating);

-- Client red flags table
CREATE TABLE client_red_flags (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    flag_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_red_flags_client ON client_red_flags(client_id);
CREATE INDEX idx_red_flags_severity ON client_red_flags(severity);

-- Company research table
CREATE TABLE company_research (
    id SERIAL PRIMARY KEY,
    client_id INTEGER UNIQUE REFERENCES clients(id) ON DELETE CASCADE,
    company_name VARCHAR(255),
    linkedin_url TEXT,
    linkedin_verified BOOLEAN DEFAULT FALSE,
    linkedin_employee_count INTEGER,
    website_url TEXT,
    website_verified BOOLEAN DEFAULT FALSE,
    twitter_url TEXT,
    facebook_url TEXT,
    instagram_url TEXT,
    social_media_presence_score INTEGER CHECK (social_media_presence_score >= 0 AND social_media_presence_score <= 100),
    business_registration_found BOOLEAN DEFAULT FALSE,
    recent_news_count INTEGER DEFAULT 0,
    digital_footprint_score INTEGER CHECK (digital_footprint_score >= 0 AND digital_footprint_score <= 100),
    research_data JSONB,
    researched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_company_research_client ON company_research(client_id);

-- Scam reports table
CREATE TABLE scam_reports (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    reporter_user_id INTEGER REFERENCES users(id),
    job_id INTEGER REFERENCES jobs(id),
    report_type VARCHAR(100) CHECK (report_type IN ('scam', 'fake', 'non_payment', 'harassment', 'other')),
    description TEXT NOT NULL,
    evidence_urls TEXT[],
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'verified', 'rejected')),
    verified_by_admin INTEGER REFERENCES users(id),
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0
);

CREATE INDEX idx_scam_reports_client ON scam_reports(client_id);
CREATE INDEX idx_scam_reports_status ON scam_reports(status);

-- Saved searches table
CREATE TABLE saved_searches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    search_query TEXT,
    filters JSONB,
    alert_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_triggered TIMESTAMP
);

CREATE INDEX idx_saved_searches_user ON saved_searches(user_id);

-- Job applications table
CREATE TABLE job_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'applied' CHECK (status IN ('applied', 'shortlisted', 'hired', 'rejected')),
    notes TEXT,
    UNIQUE(user_id, job_id)
);

CREATE INDEX idx_applications_user ON job_applications(user_id);
CREATE INDEX idx_applications_job ON job_applications(job_id);
CREATE INDEX idx_applications_status ON job_applications(status);

-- User analytics table
CREATE TABLE user_analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    jobs_viewed INTEGER DEFAULT 0,
    jobs_applied INTEGER DEFAULT 0,
    vetting_reports_viewed INTEGER DEFAULT 0,
    avg_client_trust_score DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

CREATE INDEX idx_user_analytics_user_date ON user_analytics(user_id, date);

-- Platform analytics table
CREATE TABLE platform_analytics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_jobs_scraped INTEGER DEFAULT 0,
    total_active_jobs INTEGER DEFAULT 0,
    avg_hourly_rate DECIMAL(10, 2),
    avg_fixed_price DECIMAL(10, 2),
    top_skills JSONB,
    top_categories JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

CREATE INDEX idx_platform_analytics_date ON platform_analytics(date);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_research_updated_at BEFORE UPDATE ON company_research
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
