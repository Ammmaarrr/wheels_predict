import psycopg2
import os
import sys
from datetime import datetime
import logging
import json

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'config'))

try:
    from secure_config import config
except ImportError:
    print("❌ Warning: secure_config not found. Using environment variables.")
    config = None

class PostgresPipeline:
    def open_spider(self, spider):
        """Open database connection with secure configuration"""
        try:
            if config and config.validate_required_settings():
                # Use secure configuration
                db_params = config.get_sync_db_params()
                self.conn = psycopg2.connect(**db_params)
                print("✅ Database connection established with secure configuration")
            else:
                # Fallback with environment variables
                db_password = os.getenv('DB_PASSWORD')
                if not db_password:
                    raise ValueError("❌ DB_PASSWORD environment variable is required. Please set it in your .env file.")
                
                self.conn = psycopg2.connect(
                    dbname=os.getenv('DB_NAME', 'pakwheelsdb'),
                    user=os.getenv('DB_USER', 'postgres'),
                    password=db_password,
                    host=os.getenv('DB_HOST', 'localhost'),
                    port=int(os.getenv('DB_PORT', '5432'))
                )
                print("✅ Database connection established with environment variables")
            
            self.cur = self.conn.cursor()
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("Please check your database configuration in .env file")
            raise

    def close_spider(self, spider):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def process_item(self, item, spider):
        now = datetime.now().date()
        try:
            self.cur.execute("""
                INSERT INTO pakwheels_cars (car_url, data, status, first_seen, last_seen)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (car_url) DO UPDATE
                SET data = EXCLUDED.data,
                    status = 'active',
                    last_seen = %s;
            """, (
                item['url'], json.dumps(dict(item)), 'active', now, now, now
            ))
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error processing item {item.get('url', '')}: {e}")
            spider.logger.error(f"Error processing item {item.get('url', '')}: {e}")
        return item
