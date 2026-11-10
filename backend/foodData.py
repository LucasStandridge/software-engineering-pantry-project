import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("USDA_API_KEY")
BASE: str = "https://api.nal.usda.gov/fdc/v1"

"""
The API is the USDA FoodData Central (FDC) database. Requires an API key, but free to use

- Nutrient info is grabbed using IDs found in 'nutrient.csv'
- The API uses both the "id" and "nutrient_nbr" columns as IDs for nutrients, but they are nested differently in the response.
- Nutrients have multiple nutrient categories with equivalent or similar meanings (ex. "carbohydrates", "carbohydrate, by difference", "carbohydrate, total").


Capabilities:
    - 'get_food_id' searches the database using a keyword search, and returns the FDC ID of the first food item from the search
        - Optionally include a brand name when searching
    - 'summarize_food' takes an FDC ID and returns a summary of the information
    - 'parse_food_data' takes a food item from the API response and returns a dict containing:
        - Name as it appears in the database
        - Alternative food description if given by database (ex. milk, bread, beef, etc.)
        - Brand used for nutrition info (if applicable)
        - Calories (Kcal)
        - Protein (g)
        - Total Sugars (g)
        - Carbohydrates (g)
        - Fat (g)
        * Nutrition information is per 100g



Things to improve
    - In 'parse_food_data', nutrients are each grabbed using one ID, but the database has multiple IDs with equivalent nutrient categories.
        - Some database entries do not all use those specific ones, so add fallbacks to IDs for equivalent nutrient categories (ex. fallback to ID for 'total_carbs' if the ID for 'carbs' had None)
    
    - 'get_food_id' search is kind of janky. Not enough specificity can return things that are close, but not correct (ex. searching 'hotdogs' will return info for hotdog bun, not actual hotdogs)
        - Currently no way to verify the food item is what the user wanted to add
    
    - Unless other features could benefit from 'summarize_food' finding info for specific FDC IDs, 'get_food_id' could return the full food info instead of just the FDC ID
        - Reduces the number of API calls since 'summarize_food' no longer needs to make another call using the specific ID
    
    - Error handling is very basic, just returns None to avoid crashes. Does not give meaningful information
"""

def parse_food_data(food_item: dict) -> dict:
    """Parse the data returned from the USDA FoodData Central API.
        - food_item: The API response as a dictionary."""
    
    summary: dict = {"canonical_name": None,                # Name in the database
                     "food_category": None,                 # Alternative food description, more standardized but also sometimes vague
                    "brand": None,                          # Specific brand the nutrition info was pulled from. 
                    "nutrition": {                          # Nutrition info per 100g
                            "calories": None,                   # Kcal
                            "protein": None,                    # g
                            "total_sugars": None,               # g
                            "carbohydrates": None,              # g
                            "fat": None                         # g
                    }}
    summary["canonical_name"] = food_item["description"]
    summary["brand"] = food_item.get("brandOwner") 

    # Check for category from brand first, then check general food category
    summary["food_category"] = food_item.get("brandedFoodCategory")
    if summary["food_category"] == None:
        summary["food_category"] = food_item.get("foodCategory", {}).get("description")
    

    # Loop through the full nutrient list to grab each value
    for nutrient in food_item["foodNutrients"]:
        
        # Specific nutrient IDs are used to grab the relevant nutrition info. See 'nutrient.csv' for the specific codes under 'nutrition_nbr'.

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


def summarize_food(fdcId: int) -> dict:
    """Return a summary of the food item using the given FDC ID.
        - fdcId: The FDC ID of the food item to summarize."""
    try:
        food_item: dict = requests.get(f"{BASE}/food/{fdcId}", params = {"api_key": API_KEY}).json()
        return parse_food_data(food_item)
    
    except Exception as e:
        print(e)
        return None


def get_food_id(food_query: str, brand_name: str = None) -> int:
    """Return the FDC ID of the food item using the given name. Defaults to first result, but can also filter by brand if provided.
        - food_query: The name of the food item to search for.
        - brand_name: Optional. The brand name to filter by. If provided, will return the first result with that brand name.
    """

    try:
        # If a brand name is given, use it for searching
        if brand_name:
            r: dict = requests.get(f"{BASE}/foods/search", params = {"api_key": API_KEY, "query": food_query, "brandOwner": brand_name, "pageSize": 1}).json()
            # If there is a result from brand search, use it.
            if r["totalHits"] != 0:
                food_id = r["foods"][0]["fdcId"]
                return r["foods"][0]

        # Otherwise, just grab the first item returned
        r: dict = requests.get(f"{BASE}/foods/search", params = {"api_key": API_KEY, "query": food_query, "pageSize": 1}).json()
        food_id = r["foods"][0]["fdcId"]
        return food_id
     
    except Exception as e:
        return None



if __name__ == "__main__":
    query = "american cheese"
    brand = None
    food_id = get_food_id(query, brand)
    summary = summarize_food(food_id)
    print(summary)
