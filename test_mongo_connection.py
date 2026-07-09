import logging
from db_utils import save_recommendations_mongo

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Example recommendations list
    recommendations = [
        {"model": "Toyota Corolla", "score": 0.95},
        {"model": "Honda Civic", "score": 0.92}
    ]
    save_recommendations_mongo(recommendations)
    print("Test complete. Check MongoDB Atlas for the 'car_db' database and 'recommendations' collection.")
