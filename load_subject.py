import sqlite3
import os

# Use os.path.expanduser to get the path to the user's home directory
HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)

def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Enable access by column name
    return conn




def upsert_programme_records(records):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Programme table creation with is_core column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS programme (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            programme_name TEXT NOT NULL UNIQUE,
            category TEXT,
            short_name TEXT NOT NULL UNIQUE,
            is_core INTEGER NOT NULL DEFAULT 0
        )
    ''')

    # Upsert records
    for programme_name, details in records.items():
        category = details.get('category')
        short_name = details.get('short_name')
        is_core = details.get('is_core')
        
        cursor.execute('''
            INSERT INTO programme (programme_name, category, short_name, is_core)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(programme_name) DO UPDATE SET
                category=excluded.category,
                short_name=excluded.short_name,
                is_core=excluded.is_core
        ''', (programme_name, category, short_name, is_core))
    
    conn.commit()
    conn.close()

# Example usage
subject_categories = {
    "SOCIAL STUDIES": {"category": "CORE_SUBJECT", "short_name": "SS", "is_core": 1},
    "ENGLISH LANG": {"category": "CORE_SUBJECT", "short_name": "EL", "is_core": 1},
    "MATHEMATICS(CORE)": {"category": "CORE_SUBJECT", "short_name": "MC", "is_core": 1},
    "INTEGRATED SCIENCE": {"category": "CORE_SUBJECT", "short_name": "IS", "is_core": 1},
    "BIOLOGY": {"category": "GENERAL_SCIENCE", "short_name": "BIOLO", "is_core": 0},
    "FOODS & NUTRITION": {"category": "HOME_ECONOMICS", "short_name": "F&N", "is_core": 0},
    "MGT IN LIVING": {"category": "HOME_ECONOMICS", "short_name": "MIL", "is_core": 0},
    "GEN KNOW IN ART": {"category": "VISUAL_ARTS", "short_name": "GKIA", "is_core": 0},
    "CHRISTIAN REL STUD": {"category": "GENERAL_ARTS", "short_name": "CRS", "is_core": 0},
    "ECONOMICS": {"category": "GENERAL_ARTS", "short_name": "ECONO", "is_core": 0},
    "GEOGRAPHY": {"category": "GENERAL_ARTS", "short_name": "GEOGR", "is_core": 0},
    "GOVERNMENT": {"category": "GENERAL_ARTS", "short_name": "GOVER", "is_core": 0},
    "HISTORY": {"category": "GENERAL_ARTS", "short_name": "HISTO", "is_core": 0},
    "LIT-IN ENGLISH": {"category": "GENERAL_ARTS", "short_name": "LIE", "is_core": 0},
    "TWI(ASANTE)": {"category": "GENERAL_ARTS", "short_name": "TWI", "is_core": 0},
    "BUSINESS MANAGEMENT": {"category": "BUSINESS", "short_name": "BM", "is_core": 0},
    "FINANCIAL ACCOUNTING": {"category": "BUSINESS", "short_name": "FA", "is_core": 0},
    "MATHEMATICS(ELECT)": {"category": "GENERAL_SCIENCE", "short_name": "ME", "is_core": 0},
    "CHEMISTRY": {"category": "GENERAL_SCIENCE", "short_name": "CHEMI", "is_core": 0},
    "PHYSICS": {"category": "GENERAL_SCIENCE", "short_name": "PHY", "is_core": 0},
    "CLOTHING & TEXTILES": {"category": "HOME_ECONOMICS", "short_name": "C&T", "is_core": 0},
    "TEXTILES": {"category": "VISUAL_ARTS", "short_name": "TEXTI", "is_core": 0},
    "GENERAL AGRICULTURE": {"category": "GENERAL_SCIENCE", "short_name": "GA", "is_core": 0},
    "ANIMAL HUSBANDRY": {"category": "GENERAL_SCIENCE", "short_name": "AH", "is_core": 0},
    "PRIN OF COST ACCTS": {"category": "BUSINESS", "short_name": "POCA", "is_core": 0},
    "FRENCH": {"category": "GENERAL_ARTS", "short_name": "FRENC", "is_core": 0},
    "LEATHERWORK": {"category": "VISUAL_ARTS", "short_name": "LEAT", "is_core": 0},
    "PICTURE MAKING": {"category": "VISUAL_ARTS", "short_name": "PM", "is_core": 0},
    "GRAPHIC DESIGN": {"category": "VISUAL_ARTS", "short_name": "GD", "is_core": 0},
    "MUSIC": {"category": "GENERAL_ARTS", "short_name": "MUSIC", "is_core": 0},
    "SCULPTURE": {"category": "ART", "short_name": "SCULP", "is_core": 0},
    "INFO. & COMM.TECHNOLOGY": {"category": "GENERAL_SCIENCE", "short_name": "ICT", "is_core": 0},
    "MATHEMATIC (FURTHER)": {"category": "GENERAL_SCIENCE", "short_name": "MF", "is_core": 0},
    "CERAMICS": {"category": "VISUAL_ARTS", "short_name": "CERAM", "is_core": 0},
    "FOOD AND NUTRITION": {"category": "HOME_ECONOMICS", "short_name": "F&N", "is_core": 0},
    "MANAGEMENT IN LIVING": {"category": "HOME_ECONOMICS", "short_name": "MIL", "is_core": 0},
    "CLOTHING AND TEXTILES": {"category": "HOME_ECONOMICS", "short_name": "C&T", "is_core": 0},
    "FINANCIAL ACCOUNTING": {"category": "BUSINESS", "short_name": "FA", "is_core": 0},
    "BUSINESS MANAGEMENT": {"category": "BUSINESS", "short_name": "BM", "is_core": 0},
    "PRIN. OF COST ACCTS": {"category": "BUSINESS", "short_name": "POCA", "is_core": 0},
    "TEXTILES": {"category": "VISUAL_ARTS", "short_name": "TEXTI", "is_core": 0},
}

upsert_programme_records(subject_categories)
