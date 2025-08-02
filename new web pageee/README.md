# Global Medical Guidelines AI Hub

A real-time, AI-powered medical guideline aggregator that automatically scrapes and summarizes clinical practice guidelines from leading medical organizations worldwide.

## 🎯 Features

### 🔍 Real-Time Data Collection
- **Automated Scraping**: Daily scraping of 6 major medical organizations
- **No APIs Required**: Uses web scraping and RSS parsing
- **Content Deduplication**: Intelligent hash-based duplicate detection
- **Live Updates**: Background scheduler updates content every 24 hours

### 🧠 AI-Powered Intelligence
- **Smart Summarization**: OpenAI-powered 3-5 bullet point summaries
- **Tag Extraction**: Automatic medical specialty and condition tagging
- **Content Analysis**: Complexity and target audience assessment
- **Fallback System**: Works without AI when API is unavailable

### 🎨 Professional Medical Interface
- **Responsive Design**: Mobile-first, professional medical aesthetic
- **Advanced Filtering**: By organization, specialty, and year
- **Real-time Search**: Instant search across titles, summaries, and tags
- **Clean Cards**: Professional card layout with hover animations

### 📊 Comprehensive Data
- **Multiple Sources**: WHO, CDC, NICE, AHA, ADA, IDSA
- **Rich Metadata**: Titles, dates, links, summaries, tags
- **Statistics Dashboard**: Live counts and update timestamps
- **Direct Links**: One-click access to full guidelines

## 🏥 Target Sources

| Organization | URL | Type |
|--------------|-----|------|
| **WHO** | https://www.who.int/publications/guidelines | Selenium |
| **CDC** | https://www.cdc.gov/mmwr/index.html | Requests |
| **NICE** | https://www.nice.org.uk/guidance/published | Selenium |
| **AHA** | https://www.heart.org/en/professional/quality-improvement/clinical-guidance | Selenium |
| **ADA** | https://diabetesjournals.org/care/issue | Requests |
| **IDSA** | https://www.idsociety.org/practice-guideline/ | Selenium |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Chrome/Chromium (for Selenium scraping)
- OpenAI API key (optional, for AI features)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd medical-guidelines-ai-hub
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env with your OpenAI API key (optional)
nano .env
```

### 3. Frontend Setup
```bash
# Install Node.js dependencies
npm install

# Build the frontend
npm run build
```

### 4. Run the Application
```bash
# Start the Flask backend
python app.py

# In another terminal, start the React frontend
npm start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## 🔧 Configuration

### Environment Variables
```bash
# Required for AI features
OPENAI_API_KEY=your_openai_api_key_here

# Optional configurations
SCRAPING_INTERVAL_HOURS=24
MAX_GUIDELINES_PER_SOURCE=10
FLASK_DEBUG=True
```

### Database
- **Default**: SQLite (`medical_guidelines.db`)
- **Auto-created**: Tables and indexes created automatically
- **Deduplication**: Content hash-based duplicate prevention

## 📡 API Endpoints

### Core Endpoints
- `GET /api/guidelines` - Get all guidelines with optional filtering
- `GET /api/sources` - Get list of available sources
- `GET /api/specialties` - Get list of available specialties
- `GET /api/stats` - Get database statistics
- `GET /api/health` - Health check endpoint

### Query Parameters
```bash
# Filter by source
GET /api/guidelines?source=WHO

# Filter by specialty
GET /api/guidelines?specialty=Cardiology

# Filter by year
GET /api/guidelines?year=2024

# Combine filters
GET /api/guidelines?source=WHO&year=2024&specialty=Cardiology
```

## 🏗️ Architecture

### Backend (Python/Flask)
```
app.py              # Main Flask application
├── scraper.py      # Web scraping engine
├── ai_summarizer.py # AI integration
└── requirements.txt # Python dependencies
```

### Frontend (React/TailwindCSS)
```
src/
├── App.js          # Main React component
├── App.css         # Custom styles
├── index.js        # React entry point
└── index.css       # TailwindCSS styles
```

### Data Flow
1. **Scheduler** triggers scraping every 24 hours
2. **Scraper** collects guidelines from all sources
3. **AI Summarizer** generates summaries and tags
4. **Database** stores with deduplication
5. **API** serves data to frontend
6. **Frontend** displays with search/filtering

## 🎨 Design System

### Colors
- **Primary**: Medical Blue (`#0ea5e9`)
- **Background**: Light Gray (`#f9fafb`)
- **Cards**: White with subtle shadows
- **Source Badges**: Color-coded by organization

### Typography
- **Primary Font**: Inter (Google Fonts)
- **Secondary Font**: Roboto
- **Professional**: Clean, medical-grade readability

### Components
- **Cards**: Hover animations, professional layout
- **Buttons**: Consistent styling with focus states
- **Search**: Large, prominent search bar
- **Filters**: Collapsible filter panel
- **Badges**: Color-coded source indicators

## 🔒 Security & Ethics

### Web Scraping Best Practices
- **Respectful Rate Limiting**: 2-second delays between sources
- **User-Agent Headers**: Proper browser identification
- **Error Handling**: Graceful failure handling
- **Content Attribution**: Direct links to original sources

### Data Privacy
- **No Personal Data**: Only public medical guidelines
- **Source Attribution**: All content properly attributed
- **Direct Links**: Users access original sources
- **No Data Storage**: Only metadata and summaries

## 🚀 Deployment

### Production Setup
```bash
# Build frontend for production
npm run build

# Set production environment
export FLASK_ENV=production
export FLASK_DEBUG=False

# Run with production server
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
```dockerfile
# Example Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 📈 Monitoring & Maintenance

### Health Checks
- **API Health**: `/api/health` endpoint
- **Database Status**: Connection monitoring
- **Scraping Status**: Log-based monitoring
- **AI Service**: Fallback system monitoring

### Logging
- **Structured Logging**: JSON format for production
- **Error Tracking**: Comprehensive error logging
- **Performance Monitoring**: Response time tracking
- **Scraping Metrics**: Success/failure rates

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
npm install

# Run in development mode
python app.py  # Backend
npm start      # Frontend
```

### Code Style
- **Python**: PEP 8 with Black formatting
- **JavaScript**: ESLint with Prettier
- **CSS**: TailwindCSS utility classes
- **Documentation**: Comprehensive docstrings

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues
1. **Chrome Driver**: Ensure Chrome/Chromium is installed
2. **OpenAI API**: Set valid API key in `.env`
3. **Port Conflicts**: Check if ports 3000/5000 are available
4. **Database**: Ensure write permissions for SQLite file

### Getting Help
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Documentation**: Check this README and code comments

---

**Built with ❤️ for the medical community** 