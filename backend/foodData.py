import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("USDA_API_KEY")
BASE: str = "https://api.nal.usda.gov/fdc/v1"

"""
The API is the USDA FoodData Central (FDC) database. Requires an API key, but free to use

- Nutrient info is grabbed using IDs found in 'nutrient.csv'
- The API uses both the "id" and "nutrient_nbr" to identify nutrients.
- Nutrients have multiple entries with the same general description (ex. "carbohydrates", "carbohydrate, by difference", "carbohydrate, total").


Capabilities:
    - 'get_food_id' returns the FDC ID of a food item given its name
    - 'summarize_food' takes an FDC ID and returns a dict containg:
        - Name as it appears in the database
        - Brand (if applicable)
        - Calories (Kcal)
        - Protein (g)
        - Total Sugars (g)
        - Carbohydrates (g)
        - Fat (g)
        * Nutrition information is per 100g

Things to improve
    - API Key is hardcoded 
    - In 'parse_food_data', nutrients are each grabbed using one ID, but the database has multiple IDs.
        - Did some light testing and seems accurate so far
        - Some foods may not all use those specific ones though, so may need to grab all and filter for the right one
    - 'get_food_id' only returns the first result, but there will be multiple results for a food name
        - Could include filtering by a brand
        - Could also filter for unbranded by default if no brand is given in order to get a generic result
        - Could also return a list of results and be used to display options for the user to choose from
    - Error handling is very basic, just returns None to avoid crashes.
"""

def parse_food_data(food_item: dict) -> dict:
    """Parse the data returned from the USDA FoodData Central API.
        - food_item: The API response as a dictionary."""
    
    summary: dict = {"canonical_name": None,                # Name in the database
                    "brand": None,                          # Specific brand name if applicable, else None
                    "nutrition": {                          # Nutrition info per 100g
                            "calories": None,               # Kcal
                            "protein": None,                # g
                            "total_sugars": None,           # g
                            "carbohydrates": None,          # g
                            "fat": None                     # g
                    }}
    summary["canonical_name"] = food_item["description"]
    summary["brand"] = food_item.get("brandOwner") 

    # Loop through the full nutrient list to grab each value
    for nutrient in food_item["foodNutrients"]:
        
        # Specific nutrient IDs are used to grab the relevant nutrition info. See 'nutrient.csv' for the specific codes under 'nutrition_nbr'.
        # Could also technically 

        # Protein (g)
        if nutrient["nutrient"]["number"] == '203':                     
            summary["nutrition"]["protein"] = nutrient["amount"]

        # Fat (g)
        elif nutrient["nutrient"]["number"] == '204':
            summary["nutrition"]["fat"] = nutrient["amount"]

        # Total Sugars (g)
        elif nutrient["nutrient"]["number"] == '269':
            summary["nutrition"]["total_sugars"] = nutrient["amount"]

        # Carbohydrates (g)
        elif nutrient["nutrient"]["number"] == '205':
            summary["nutrition"]["carbohydrates"] = nutrient["amount"]

        # Calories (Kcal)
        elif nutrient["nutrient"]["number"] == '208':
            summary["nutrition"]["calories"] = nutrient["amount"]

    return summary


def summarize_food(fdcId: int, ) -> dict:
    """Return a summary of the food item using the given FDC ID.
        - fdcId: The FDC ID of the food item to summarize."""
    try:
        food_item: dict = requests.get(f"{BASE}/food/{fdcId}", params = {"api_key": API_KEY}).json()
        return parse_food_data(food_item)
    
    except Exception as e:
        return None


def get_food_id(food_name: str) -> int:
    """Return the FDC ID of the food item using the given name.
        - food_name: The name of the food item to search for."""
    try:
        r: dict = requests.get(f"{BASE}/foods/search", params = {"api_key": API_KEY, "query": food_name, "pageSize": 1}).json()
        return r["foods"][0]["fdcId"]

    except Exception as e:
        return None

