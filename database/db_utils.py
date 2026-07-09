import psycopg2
from psycopg2.extras import execute_values
from pymongo import MongoClient
import logging

def save_predictions_postgres(df, table_name='car_predictions', db_params=None):
    if db_params is None:
        logging.warning("No DB params provided. Skipping PostgreSQL save.")
        return
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        create_table = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            model VARCHAR(100),
            predicted_price FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cur.execute(create_table)
        records = df[['model', 'predicted_price']].values.tolist()
        insert_query = f"INSERT INTO {table_name} (model, predicted_price) VALUES %s"
        execute_values(cur, insert_query, records)
        conn.commit()
        logging.info(f"Saved {len(records)} predictions to PostgreSQL table '{table_name}'.")
    except Exception as e:
        logging.error(f"Error saving predictions to PostgreSQL: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def save_recommendations_mongo(recommendations, db_name='car_db', collection_name='recommendations', mongo_uri='mongodb+srv://mammar6364:speakers@cluster0.adkwpe8.mongodb.net/'):
    client = None
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        if isinstance(recommendations, list):
            collection.insert_many([{'recommendation': r} for r in recommendations])
            logging.info(f"Saved {len(recommendations)} recommendations to MongoDB collection '{collection_name}'.")
        else:
            logging.warning("Recommendations should be a list.")
    except Exception as e:
        logging.error(f"Error saving recommendations to MongoDB: {e}")
    finally:
        if client:
            client.close()
