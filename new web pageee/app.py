from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
import hashlib
import datetime
import threading
import schedule
import time
import logging
from dotenv import load_dotenv
import os
from scraper import MedicalGuidelineScraper
from ai_summarizer import AISummarizer

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
scraper = MedicalGuidelineScraper()
ai_summarizer = AISummarizer()

class DatabaseManager:
    def __init__(self, db_path="medical_guidelines.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the guidelines table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guidelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                link TEXT NOT NULL,
                date TEXT NOT NULL,
                summary TEXT,
                tags TEXT,
                content_hash TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def insert_guideline(self, title, source, link, date, summary, tags, content_hash):
        """Insert or update a guideline based on content hash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO guidelines 
                (title, source, link, date, summary, tags, content_hash, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (title, source, link, date, summary, tags, content_hash))
            
            conn.commit()
            logger.info(f"Guideline inserted/updated: {title}")
            return True
        except Exception as e:
            logger.error(f"Error inserting guideline: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_guidelines(self):
        """Retrieve all guidelines from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, source, link, date, summary, tags, created_at, updated_at
            FROM guidelines
            ORDER BY date DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        guidelines = []
        for row in rows:
            guidelines.append({
                'id': row[0],
                'title': row[1],
                'source': row[2],
                'link': row[3],
                'date': row[4],
                'summary': row[5],
                'tags': json.loads(row[6]) if row[6] else [],
                'created_at': row[7],
                'updated_at': row[8]
            })
        
        return guidelines
    
    def get_guidelines_by_filter(self, source=None, specialty=None, year=None):
        """Filter guidelines by various criteria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, title, source, link, date, summary, tags, created_at, updated_at
            FROM guidelines
            WHERE 1=1
        '''
        params = []
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        if year:
            query += " AND strftime('%Y', date) = ?"
            params.append(str(year))
        
        query += " ORDER BY date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        guidelines = []
        for row in rows:
            guideline = {
                'id': row[0],
                'title': row[1],
                'source': row[2],
                'link': row[3],
                'date': row[4],
                'summary': row[5],
                'tags': json.loads(row[6]) if row[6] else [],
                'created_at': row[7],
                'updated_at': row[8]
            }
            
            # Filter by specialty if specified
            if specialty and guideline['tags']:
                if specialty.lower() not in [tag.lower() for tag in guideline['tags']]:
                    continue
            
            guidelines.append(guideline)
        
        return guidelines

# Initialize database manager
db_manager = DatabaseManager()

def scrape_and_update():
    """Main scraping function that runs in background"""
    logger.info("Starting scheduled scraping...")
    
    try:
        # Scrape all sources
        all_guidelines = scraper.scrape_all_sources()
        
        for guideline in all_guidelines:
            # Generate content hash for deduplication
            content_hash = hashlib.md5(
                f"{guideline['title']}{guideline['source']}{guideline['link']}".encode()
            ).hexdigest()
            
            # Generate AI summary and tags
            summary = ai_summarizer.summarize_guideline(guideline['title'], guideline.get('content', ''))
            tags = ai_summarizer.extract_tags(guideline['title'], guideline.get('content', ''))
            
            # Store in database
            db_manager.insert_guideline(
                title=guideline['title'],
                source=guideline['source'],
                link=guideline['link'],
                date=guideline['date'],
                summary=summary,
                tags=json.dumps(tags),
                content_hash=content_hash
            )
        
        logger.info(f"Scraping completed. Processed {len(all_guidelines)} guidelines")
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")

def start_background_scraping():
    """Start the background scraping scheduler"""
    # Schedule scraping every 24 hours
    schedule.every(24).hours.do(scrape_and_update)
    
    # Also run initial scraping
    scrape_and_update()
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Background scraping scheduler started")

# API Endpoints
@app.route('/api/guidelines', methods=['GET'])
def get_guidelines():
    """Get all guidelines with optional filtering"""
    source = request.args.get('source')
    specialty = request.args.get('specialty')
    year = request.args.get('year')
    
    if source or specialty or year:
        guidelines = db_manager.get_guidelines_by_filter(source, specialty, year)
    else:
        guidelines = db_manager.get_all_guidelines()
    
    return jsonify({
        'guidelines': guidelines,
        'count': len(guidelines),
        'last_updated': datetime.datetime.now().isoformat()
    })

@app.route('/api/sources', methods=['GET'])
def get_sources():
    """Get list of available sources"""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT source FROM guidelines ORDER BY source')
    sources = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'sources': sources})

@app.route('/api/specialties', methods=['GET'])
def get_specialties():
    """Get list of available specialties from tags"""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT tags FROM guidelines WHERE tags IS NOT NULL')
    all_tags = []
    for row in cursor.fetchall():
        if row[0]:
            tags = json.loads(row[0])
            all_tags.extend(tags)
    
    # Get unique specialties
    specialties = list(set(all_tags))
    conn.close()
    
    return jsonify({'specialties': specialties})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about the guidelines database"""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Total guidelines
    cursor.execute('SELECT COUNT(*) FROM guidelines')
    total_guidelines = cursor.fetchone()[0]
    
    # Guidelines by source
    cursor.execute('SELECT source, COUNT(*) FROM guidelines GROUP BY source')
    source_counts = dict(cursor.fetchall())
    
    # Recent guidelines (last 30 days)
    cursor.execute('''
        SELECT COUNT(*) FROM guidelines 
        WHERE date(created_at) >= date('now', '-30 days')
    ''')
    recent_guidelines = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_guidelines': total_guidelines,
        'source_counts': source_counts,
        'recent_guidelines': recent_guidelines,
        'last_updated': datetime.datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'database': 'connected'
    })

if __name__ == '__main__':
    # Start background scraping
    start_background_scraping()
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000) 