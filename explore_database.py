"""
Database Explorer - Test database connection and examine structure
"""

import sys
sys.path.append('/Users/frederickmarvel/Blockchain Monitoring/backend')

from database_service import DatabaseService
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Database credentials
DB_CONFIG = {
    'host': '217.216.110.33',
    'port': 3306,
    'username': 'root',
    'password': 'nobicuan888',
    'database': 'nobi_wallet_tracker'
}

def explore_database():
    """Explore database structure"""
    
    logger.info("="*80)
    logger.info("🔍 EXPLORING DATABASE STRUCTURE")
    logger.info("="*80)
    
    # Create database service
    db = DatabaseService(**DB_CONFIG)
    
    # Connect
    if not db.connect():
        logger.error("Failed to connect to database")
        return
    
    try:
        # 1. Get list of tables
        logger.info("\n📊 TABLES IN DATABASE:")
        logger.info("-"*80)
        tables = db.get_tables()
        for i, table in enumerate(tables, 1):
            logger.info(f"{i}. {table}")
        
        # 2. Examine structure of each table
        for table in tables:
            logger.info(f"\n📋 STRUCTURE OF TABLE: {table}")
            logger.info("-"*80)
            columns = db.get_table_structure(table)
            
            if columns:
                logger.info(f"{'Field':<30} {'Type':<20} {'Null':<8} {'Key':<8} {'Default':<15}")
                logger.info("-"*80)
                for col in columns:
                    logger.info(
                        f"{col['field']:<30} "
                        f"{col['type']:<20} "
                        f"{col['null']:<8} "
                        f"{col['key']:<8} "
                        f"{str(col['default']):<15}"
                    )
            else:
                logger.warning(f"Could not get structure for table: {table}")
        
        # 3. Sample data from each table (first 3 rows)
        for table in tables:
            logger.info(f"\n💾 SAMPLE DATA FROM: {table} (first 3 rows)")
            logger.info("-"*80)
            
            try:
                cursor = db.connection.cursor(dictionary=True)
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()
                cursor.close()
                
                if rows:
                    for i, row in enumerate(rows, 1):
                        logger.info(f"\nRow {i}:")
                        for key, value in row.items():
                            logger.info(f"  {key}: {value}")
                else:
                    logger.info("  (No data in this table)")
                    
            except Exception as e:
                logger.error(f"  Error reading from {table}: {e}")
        
        # 4. Count records per table
        logger.info(f"\n📈 RECORD COUNTS:")
        logger.info("-"*80)
        for table in tables:
            try:
                cursor = db.connection.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                cursor.close()
                logger.info(f"{table:<40} {count:>10} records")
            except Exception as e:
                logger.error(f"Error counting {table}: {e}")
        
    finally:
        db.disconnect()
    
    logger.info("\n" + "="*80)
    logger.info("✅ DATABASE EXPLORATION COMPLETE")
    logger.info("="*80)

if __name__ == '__main__':
    explore_database()
