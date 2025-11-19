# AI Freelance Search App

An AI-powered freelance job search and client vetting application built on top of the Groq MCP Server infrastructure.

## Features

### Core Features (MVP)

- **Job Aggregation**: Scrape and aggregate jobs from multiple freelance platforms (Upwork, Freelancer, Fiverr, Guru)
- **Client Vetting System**: Comprehensive AI-powered client background checks with trust scores
- **Trust Score Algorithm**: Calculate client trustworthiness based on 7 key factors
- **Red Flag Detection**: AI-powered fraud and scam detection
- **Company Research**: Automated company verification using Groq's compound-beta API
- **Sentiment Analysis**: Analyze client reviews to extract insights
- **Natural Language Search**: AI-powered job search with natural language queries
- **User Authentication**: Secure JWT-based authentication
- **Saved Searches**: Save search criteria and get alerts for new matching jobs
- **Scam Reports**: Community-driven scam reporting system

### Advanced Features

- **AI Review Analysis**: Extract common themes from client feedback
- **Multi-tier Subscriptions**: Free, Pro, and Premium tiers
- **Analytics Dashboard**: User and market analytics
- **Real-time Alerts**: Job alerts based on saved searches (planned)

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy
- **Cache**: Redis
- **Task Queue**: Celery
- **AI Integration**: Groq API (via existing MCP tools)
  - Chat: `llama-3.3-70b-versatile`
  - Advanced: `compound-beta`, `compound-beta-deep`

### Frontend (Planned)
- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Chart.js / Recharts
- **State**: Redux Toolkit / Zustand

## Project Structure

```
freelance_app/
├── main.py                    # FastAPI application entry point
├── config.py                  # Application configuration
├── requirements.txt           # Python dependencies
│
├── models/                    # SQLAlchemy database models
│   ├── base.py               # Database configuration
│   ├── user.py               # User, UserSkill, UserPreference
│   ├── platform.py           # FreelancePlatform
│   ├── client.py             # Client, ClientReview, ClientRedFlag
│   ├── job.py                # Job, JobApplication
│   ├── company.py            # CompanyResearch
│   ├── scam.py               # ScamReport
│   ├── search.py             # SavedSearch
│   └── analytics.py          # UserAnalytics, PlatformAnalytics
│
├── schemas/                   # Pydantic schemas for API
│   ├── user.py               # User-related schemas
│   ├── job.py                # Job-related schemas
│   └── client.py             # Client-related schemas
│
├── routers/                   # API route handlers
│   ├── auth.py               # Authentication endpoints
│   ├── users.py              # User management endpoints
│   ├── jobs.py               # Job search and applications
│   ├── clients.py            # Client vetting endpoints
│   ├── analytics.py          # Analytics endpoints
│   └── scam_reports.py       # Scam reporting endpoints
│
├── services/                  # Business logic layer
│   ├── ai_service.py         # Groq AI integration
│   ├── trust_score_service.py # Trust score calculation
│   ├── vetting_service.py    # Client vetting reports
│   └── scraper_service.py    # Web scraping (TODO)
│
├── utils/                     # Utility functions
│   └── auth.py               # JWT and password utilities
│
└── database/                  # Database setup
    ├── schema.sql            # PostgreSQL schema
    └── init_db.py            # Database initialization script
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis (for caching)
- Groq API key

### Step 1: Clone the repository

```bash
cd groq-mcp-server/freelance_app
```

### Step 2: Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set up PostgreSQL database

```bash
# Create database
createdb freelance_db

# Create user
psql -c "CREATE USER freelance_user WITH PASSWORD 'freelance_pass';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE freelance_db TO freelance_user;"

# Run schema
psql -U freelance_user -d freelance_db -f database/schema.sql
```

Or use the Python initialization script:

```bash
python database/init_db.py create
python database/init_db.py seed
```

### Step 5: Configure environment variables

Copy the example environment file:

```bash
cp ../.env.example .env
```

Edit `.env` and configure:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Database
DATABASE_URL=postgresql://freelance_user:freelance_pass@localhost:5432/freelance_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Secret (generate a random secret key)
SECRET_KEY=your-super-secret-jwt-key-here

# Optional
DEBUG=true
API_PORT=8000
```

### Step 6: Start Redis (if not running)

```bash
redis-server
```

### Step 7: Run the application

```bash
# Development mode
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints Overview

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user profile

### Users
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update profile
- `GET /api/user/skills` - Get user skills
- `POST /api/user/skills` - Add skill
- `GET /api/user/preferences` - Get preferences
- `PUT /api/user/preferences` - Update preferences

### Jobs
- `GET /api/jobs` - List jobs with filters
- `GET /api/jobs/{id}` - Get job details
- `POST /api/jobs/search` - AI-powered search
- `POST /api/jobs/{id}/apply` - Apply to job
- `GET /api/jobs/applications/me` - Get my applications
- `POST /api/jobs/saved-searches` - Create saved search

### Clients (Vetting)
- `GET /api/clients/{id}` - Get client profile
- `GET /api/clients/{id}/vetting-report` - **Get comprehensive vetting report**
- `GET /api/clients/{id}/reviews` - Get client reviews
- `GET /api/clients/{id}/red-flags` - Get red flags
- `GET /api/clients/{id}/company-research` - Get company research
- `POST /api/clients/{id}/research` - Trigger company research (Pro/Premium)

### Analytics
- `GET /api/analytics/user` - User analytics
- `GET /api/analytics/market` - Market insights
- `GET /api/analytics/trends` - Trending skills
- `GET /api/analytics/client-stats` - Client statistics

### Scam Reports
- `GET /api/scam-reports` - List scam reports
- `POST /api/scam-reports` - Submit scam report
- `POST /api/scam-reports/{id}/vote` - Vote on report

## Trust Score Algorithm

The trust score is calculated based on 7 weighted factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Account Age | 20% | Older accounts are more trustworthy |
| Payment Verification | 15% | Verified payment method |
| Total Spent | 15% | Higher spending indicates commitment |
| Hire Rate | 15% | Ratio of hires to job postings |
| Average Rating | 20% | Client feedback ratings |
| Response Time | 10% | How quickly client responds |
| Completion Rate | 5% | Project completion success |

**Trust Score Levels:**
- 80-100: Excellent
- 60-79: Good
- 40-59: Fair
- 20-39: Poor
- 0-19: Very Poor

## Client Vetting Report

The vetting report is the **core feature** of this application. It provides:

1. **Trust Score**: 0-100 score with breakdown
2. **Strengths**: Positive indicators about the client
3. **Concerns**: Warning signs to be aware of
4. **Red Flags**: AI-detected fraud indicators
5. **Review Analysis**: Sentiment analysis and common themes
6. **Company Research**: LinkedIn, website, social media verification
7. **AI Recommendation**: Whether to proceed with the client

Example vetting report format:

```json
{
  "client": {...},
  "trust_score": 78,
  "trust_score_breakdown": {
    "account_age": {"raw_score": 100, "weight": 20, "weighted_score": 20},
    "payment_verification": {"raw_score": 100, "weight": 15, "weighted_score": 15},
    ...
  },
  "strengths": [
    "Verified payment method",
    "45 successful hires",
    "$125,000+ total spent"
  ],
  "concerns": [
    "Last hire was 6 months ago"
  ],
  "red_flags": [],
  "reviews_summary": {
    "total_reviews": 45,
    "average_rating": 4.8,
    "average_sentiment": 0.85
  },
  "common_themes": [
    "Pays promptly",
    "Clear requirements",
    "Good communication"
  ],
  "company_research": {...},
  "recommendation": "Proceed with confidence. This client has excellent track record."
}
```

## AI Integration

This application leverages the existing Groq MCP Server infrastructure:

### AI Services Used

1. **Chat Completions** (`groq_ttt.py`)
   - Sentiment analysis
   - Theme extraction
   - Red flag detection
   - Job summarization
   - Natural language search parsing

2. **Compound-Beta API** (`groq_compound.py`)
   - Company research with web search
   - Real-time data gathering
   - Multi-step reasoning

### Models

- **Primary**: `llama-3.3-70b-versatile`
- **Advanced**: `compound-beta`, `compound-beta-deep`

## Development

### Running Tests

```bash
pytest
pytest --cov=. --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Lint
ruff check .

# Type checking
mypy .
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Subscription Tiers

| Feature | Free | Pro ($15/mo) | Premium ($30/mo) |
|---------|------|--------------|------------------|
| Job Search | ✅ | ✅ | ✅ |
| Basic Vetting | 5/month | Unlimited | Unlimited |
| AI Search | ❌ | ✅ | ✅ |
| Company Research | ❌ | ✅ | ✅ |
| Real-time Alerts | ❌ | ✅ | ✅ |
| Analytics Dashboard | ❌ | ✅ | ✅ |
| Priority Support | ❌ | ❌ | ✅ |

## Roadmap

### Phase 1: MVP (Current)
- [x] Core backend API
- [x] Database models
- [x] Authentication
- [x] Trust score algorithm
- [x] Client vetting system
- [x] AI integration
- [ ] Job scraping implementation
- [ ] Frontend development

### Phase 2: Enhancement
- [ ] Real-time job alerts
- [ ] Email notifications
- [ ] Advanced analytics
- [ ] Mobile app (React Native)

### Phase 3: Advanced Features
- [ ] AI cover letter generator
- [ ] Proposal analyzer
- [ ] Freelancer community forum
- [ ] Chrome extension
- [ ] Invoice and time tracking integration

## Security

- JWT-based authentication
- Password hashing with bcrypt
- SQL injection prevention via ORM
- Input validation with Pydantic
- CORS protection
- Rate limiting (TODO)
- Environment variable secrets

## Contributing

This project is part of the Groq MCP Server ecosystem. Contributions are welcome!

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: [groq-mcp-server/issues](https://github.com/anthropics/groq-mcp-server/issues)
- Documentation: `/docs`

## Acknowledgments

- Built on top of [Groq MCP Server](https://github.com/anthropics/groq-mcp-server)
- Powered by [Groq AI](https://groq.com)
- Uses [FastAPI](https://fastapi.tiangolo.com/)

---

**Note**: This application requires a valid Groq API key. Get yours at [https://console.groq.com](https://console.groq.com)
