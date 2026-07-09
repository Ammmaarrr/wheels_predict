import asyncio
import asyncpg
import json
import os
import sys
from datetime import datetime

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'config'))

try:
    from secure_config import config
except ImportError:
    print("❌ Warning: secure_config not found. Using environment variables.")
    config = None

class AsyncPostgresPipeline:
    def __init__(self, batch_size=100):
        self.batch_size = batch_size
        self.buffer = []
        self.loop = asyncio.get_event_loop()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(batch_size=100)

    async def open_spider_async(self):
        """Open database connection with secure configuration"""
        try:
            if config and config.validate_required_settings():
                # Use secure configuration
                self.conn = await asyncpg.connect(
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    database=config.DB_NAME,
                    host=config.DB_HOST,
                    port=config.DB_PORT
                )
                print("✅ Database connection established with secure configuration")
            else:
                # Fallback with environment variables
                db_password = os.getenv('DB_PASSWORD')
                if not db_password:
                    raise ValueError("❌ DB_PASSWORD environment variable is required. Please set it in your .env file.")
                
                self.conn = await asyncpg.connect(
                    user=os.getenv('DB_USER', 'postgres'),
                    password=db_password,
                    database=os.getenv('DB_NAME', 'pakwheelsdb'),
                    host=os.getenv('DB_HOST', 'localhost'),
                    port=int(os.getenv('DB_PORT', '5432'))
                )
                print("✅ Database connection established with environment variables")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("Please check your database configuration in .env file")
            raise

    def open_spider(self, spider):
        self.loop.run_until_complete(self.open_spider_async())

    async def close_spider_async(self):
        if self.buffer:
            await self.insert_batch()
        await self.conn.close()

    def close_spider(self, spider):
        self.loop.run_until_complete(self.close_spider_async())

    async def insert_batch(self):
        now = datetime.now().date()
        values = [
            (
                item['url'],
                json.dumps(dict(item)),
                'active',
                now,
                now,
                now
            ) for item in self.buffer
        ]
        await self.conn.executemany('''
            INSERT INTO pakwheels_cars (car_url, data, status, first_seen, last_seen)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (car_url) DO UPDATE
            SET data = EXCLUDED.data,
                status = 'active',
                last_seen = $6;
        ''', values)
        self.buffer = []

    async def process_item_async(self, item, spider):
        self.buffer.append(item)
        if len(self.buffer) >= self.batch_size:
            await self.insert_batch()
        return item

    def process_item(self, item, spider):
        return self.loop.run_until_complete(self.process_item_async(item, spider))
