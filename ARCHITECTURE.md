# AI Freelance Search App - Architecture Design

## System Overview

The AI Freelance Search App is built on top of the Groq MCP Server infrastructure, leveraging Groq's AI capabilities for intelligent job search, client vetting, and fraud detection.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│         React.js + Tailwind CSS + Chart.js              │
└─────────────────────────────────────────────────────────┘
                           ↓ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                   Backend API Layer                      │
│              FastAPI + Python 3.11+                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Auth Service  │  Job Service  │  Vetting Service│   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   AI Integration Layer                   │
│              Groq API via existing MCP tools             │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Chat (TTT)  │  Compound-Beta  │  Vision API    │   │
│  │  ├─ NLP Search                 │  ├─ Web Research│   │
│  │  ├─ Sentiment Analysis         │  ├─ Data Lookup│   │
│  │  └─ Fraud Detection            │  └─ Company Info│   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                            │
│              PostgreSQL + Redis (Cache)                  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              External Services Layer                     │
│    Web Scrapers (Upwork, Freelancer, Fiverr, Guru)     │
└─────────────────────────────────────────────────────────┘
```

## Database Schema

### Core Tables

#### 1. users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    profile_picture_url TEXT,
    subscription_tier VARCHAR(50) DEFAULT 'free', -- free, pro, premium
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE
);
```

#### 2. user_skills
```sql
CREATE TABLE user_skills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_name VARCHAR(255) NOT NULL,
    proficiency_level INTEGER CHECK (proficiency_level >= 1 AND proficiency_level <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, skill_name)
);
```

#### 3. user_preferences
```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    min_hourly_rate DECIMAL(10, 2),
    max_hourly_rate DECIMAL(10, 2),
    min_fixed_price DECIMAL(10, 2),
    preferred_project_duration VARCHAR(50), -- short, medium, long
    preferred_locations TEXT[], -- Array of locations
    preferred_timezones TEXT[],
    notification_enabled BOOLEAN DEFAULT TRUE,
    email_alerts BOOLEAN DEFAULT TRUE,
    push_alerts BOOLEAN DEFAULT TRUE,
    alert_frequency VARCHAR(50) DEFAULT 'realtime', -- realtime, daily, weekly
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. freelance_platforms
```sql
CREATE TABLE freelance_platforms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL, -- Upwork, Freelancer, Fiverr, Guru
    base_url TEXT NOT NULL,
    logo_url TEXT,
    has_api BOOLEAN DEFAULT FALSE,
    scraper_enabled BOOLEAN DEFAULT TRUE,
    last_scraped TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. jobs
```sql
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    platform_id INTEGER REFERENCES freelance_platforms(id),
    external_job_id VARCHAR(255), -- Job ID on the platform
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(255),
    subcategory VARCHAR(255),
    skills_required TEXT[], -- Array of skills
    job_type VARCHAR(50), -- hourly, fixed
    budget_min DECIMAL(10, 2),
    budget_max DECIMAL(10, 2),
    hourly_rate DECIMAL(10, 2),
    fixed_price DECIMAL(10, 2),
    duration VARCHAR(100), -- 1-3 months, 3-6 months, etc.
    experience_level VARCHAR(50), -- entry, intermediate, expert
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
    ai_summary TEXT, -- AI-generated summary
    UNIQUE(platform_id, external_job_id)
);
```

#### 6. clients
```sql
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    platform_id INTEGER REFERENCES freelance_platforms(id),
    external_client_id VARCHAR(255), -- Client ID on platform
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
    average_response_time INTEGER, -- in hours
    hire_rate DECIMAL(5, 2), -- percentage
    avg_project_value DECIMAL(10, 2),
    repeat_hire_rate DECIMAL(5, 2),
    last_active TIMESTAMP,
    trust_score INTEGER, -- 0-100
    trust_score_updated_at TIMESTAMP,
    is_flagged BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform_id, external_client_id)
);
```

#### 7. client_reviews
```sql
CREATE TABLE client_reviews (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    freelancer_name VARCHAR(255),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    project_title VARCHAR(255),
    project_value DECIMAL(10, 2),
    review_date TIMESTAMP,
    sentiment_score DECIMAL(3, 2), -- -1 to 1 (negative to positive)
    key_themes TEXT[], -- Array of extracted themes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 8. client_red_flags
```sql
CREATE TABLE client_red_flags (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    flag_type VARCHAR(100) NOT NULL, -- new_account, low_spend, cancelled_projects, off_platform, etc.
    severity VARCHAR(50), -- low, medium, high, critical
    description TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 9. company_research
```sql
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
    social_media_presence_score INTEGER, -- 0-100
    business_registration_found BOOLEAN DEFAULT FALSE,
    recent_news_count INTEGER DEFAULT 0,
    digital_footprint_score INTEGER, -- 0-100
    research_data JSONB, -- Store all research data
    researched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 10. scam_reports
```sql
CREATE TABLE scam_reports (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    reporter_user_id INTEGER REFERENCES users(id),
    job_id INTEGER REFERENCES jobs(id),
    report_type VARCHAR(100), -- scam, fake, non_payment, harassment
    description TEXT NOT NULL,
    evidence_urls TEXT[], -- Screenshots, emails, etc.
    status VARCHAR(50) DEFAULT 'pending', -- pending, verified, rejected
    verified_by_admin INTEGER REFERENCES users(id),
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0
);
```

#### 11. saved_searches
```sql
CREATE TABLE saved_searches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    search_query TEXT,
    filters JSONB, -- Store all filter parameters
    alert_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_triggered TIMESTAMP
);
```

#### 12. job_applications
```sql
CREATE TABLE job_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'applied', -- applied, shortlisted, hired, rejected
    notes TEXT,
    UNIQUE(user_id, job_id)
);
```

#### 13. user_analytics
```sql
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
```

#### 14. platform_analytics
```sql
CREATE TABLE platform_analytics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_jobs_scraped INTEGER DEFAULT 0,
    total_active_jobs INTEGER DEFAULT 0,
    avg_hourly_rate DECIMAL(10, 2),
    avg_fixed_price DECIMAL(10, 2),
    top_skills JSONB, -- {skill: count}
    top_categories JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);
```

## AI Integration Strategy

### 1. Job Search & Analysis
- **Tool Used**: `groq_ttt.py` (chat_completion)
- **Model**: `llama-3.3-70b-versatile`
- **Use Cases**:
  - Natural language job search queries
  - Job description summarization
  - Skill matching and recommendations

### 2. Client Vetting & Sentiment Analysis
- **Tool Used**: `groq_ttt.py` + `groq_compound.py`
- **Models**: `llama-3.3-70b-versatile`, `compound-beta`
- **Use Cases**:
  - Analyze client review sentiment
  - Extract common themes from reviews
  - Generate trust score explanations
  - Detect fraud patterns

### 3. Company Research
- **Tool Used**: `groq_compound.py` (compound_tool)
- **Model**: `compound-beta-deep`
- **Use Cases**:
  - Web search for company information
  - LinkedIn company verification
  - News article aggregation
  - Digital footprint analysis

### 4. Red Flag Detection
- **Tool Used**: `groq_ttt.py`
- **Model**: `llama-3.3-70b-versatile`
- **Use Cases**:
  - Pattern recognition in client behavior
  - Anomaly detection (suspicious pay rates, etc.)
  - Multi-factor scam detection

## API Endpoints Design

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/verify-email` - Email verification
- `POST /api/auth/forgot-password` - Password reset request

### Jobs
- `GET /api/jobs` - List jobs (with filters)
- `GET /api/jobs/{id}` - Get job details
- `POST /api/jobs/search` - AI-powered natural language search
- `GET /api/jobs/{id}/vetting-report` - Get client vetting report
- `POST /api/jobs/{id}/apply` - Apply to job
- `GET /api/jobs/trending` - Get trending jobs

### Clients
- `GET /api/clients/{id}` - Get client profile
- `GET /api/clients/{id}/vetting-report` - Get detailed vetting report
- `GET /api/clients/{id}/reviews` - Get client reviews
- `GET /api/clients/{id}/red-flags` - Get red flags
- `GET /api/clients/{id}/company-research` - Get company research

### User
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile
- `GET /api/user/preferences` - Get user preferences
- `PUT /api/user/preferences` - Update preferences
- `POST /api/user/skills` - Add skill
- `DELETE /api/user/skills/{id}` - Remove skill

### Saved Searches
- `GET /api/saved-searches` - List saved searches
- `POST /api/saved-searches` - Create saved search
- `PUT /api/saved-searches/{id}` - Update saved search
- `DELETE /api/saved-searches/{id}` - Delete saved search

### Scam Reports
- `GET /api/scam-reports` - List scam reports (admin/public)
- `POST /api/scam-reports` - Submit scam report
- `PUT /api/scam-reports/{id}/vote` - Upvote/downvote report
- `PUT /api/scam-reports/{id}/verify` - Verify report (admin)

### Analytics
- `GET /api/analytics/user` - User analytics dashboard
- `GET /api/analytics/market` - Market insights
- `GET /api/analytics/trends` - Trending skills and categories

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL 15+
- **Cache**: Redis
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Web Scraping**:
  - BeautifulSoup4
  - Scrapy
  - Selenium (for dynamic content)
- **Task Queue**: Celery + Redis
- **API Client**: httpx (already in use)

### Frontend
- **Framework**: React 18+
- **Styling**: Tailwind CSS
- **State Management**: Redux Toolkit / Zustand
- **Data Visualization**: Chart.js / Recharts
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **Form Handling**: React Hook Form
- **UI Components**: Headless UI / Shadcn UI

### AI Integration
- **Groq API**: Via existing MCP tools
- **Models**:
  - Chat: `llama-3.3-70b-versatile`
  - Advanced: `compound-beta`, `compound-beta-deep`
  - Vision: `scout`, `maverick` (for screenshot analysis)

### DevOps
- **Containerization**: Docker + Docker Compose
- **Deployment**: AWS EC2 / Google Cloud Run
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

## Security Considerations

1. **API Key Management**: Store in environment variables, never in code
2. **JWT Tokens**: Short expiration (15 min access, 7 day refresh)
3. **Rate Limiting**: Implement per-user and per-IP rate limits
4. **Data Encryption**:
   - TLS for all connections
   - Encrypt sensitive DB fields (API keys, passwords)
5. **Input Validation**: Pydantic models for all inputs
6. **SQL Injection Prevention**: Use ORM parameterized queries
7. **XSS Prevention**: Sanitize all user inputs
8. **CORS**: Whitelist only frontend domain
9. **CSRF Protection**: Use tokens for state-changing operations

## Scalability Strategy

1. **Database**:
   - Read replicas for analytics queries
   - Partitioning for jobs table by date
   - Indexing on frequently queried fields

2. **Caching**:
   - Redis for session storage
   - Cache vetting reports for 24 hours
   - Cache job listings for 1 hour

3. **Job Scraping**:
   - Distributed scraping with Celery workers
   - Rate limiting per platform
   - Incremental updates (only new jobs)

4. **API**:
   - Horizontal scaling with load balancer
   - Async request handling
   - Background processing for heavy tasks

## MVP Feature Priority

### Phase 1 (Weeks 1-4): Core Infrastructure
1. ✅ Database setup and models
2. ✅ User authentication system
3. ✅ Job aggregation (3 platforms: Upwork, Freelancer, Fiverr)
4. ✅ Basic client vetting with trust score
5. ✅ Simple React UI with search and filters

### Phase 2 (Weeks 5-8): AI Enhancement
1. ✅ AI-powered natural language search
2. ✅ Sentiment analysis on reviews
3. ✅ Red flag detection system
4. ✅ Company research integration
5. ✅ Enhanced vetting reports

### Phase 3 (Weeks 9-12): Polish & Launch
1. ✅ Real-time alerts system
2. ✅ Analytics dashboard
3. ✅ Scam reporting feature
4. ✅ Mobile-responsive design
5. ✅ Testing and bug fixes
6. ✅ Beta launch

## Next Steps

1. Set up PostgreSQL database
2. Create FastAPI backend structure
3. Implement job scraping services
4. Build AI integration layer using existing Groq tools
5. Develop React frontend
6. Integration testing
7. Deployment
