import unittest
from unittest.mock import patch

import requests

from foodData import parse_food_data, summarize_food, get_food_id, API_KEY, BASE


class TestParseFoodData(unittest.TestCase):

    # Test if dict strucured with branded structure parses correctly
    def test_parse_food_data_correct_summary_for_branded(self):
        # Sample food item data
        food_item = {
            "description": "Sample Food",
            "brandedFoodCategory": "Sample Category",
            "brandOwner": "Sample Brand",
            "foodNutrients": [
                {"nutrient": {"number": '203'}, "amount": 10.0},  # Protein
                {"nutrient": {"number": '204'}, "amount": 5.0},   # Fat
                {"nutrient": {"number": '269'}, "amount": 2.0},   # Total Sugars
                {"nutrient": {"number": '205'}, "amount": 20.0},  # Carbohydrates
                {"nutrient": {"number": '208'}, "amount": 150.0}  # Calories
            ]
        }

        expected_summary = {
            "canonical_name": "Sample Food",
            "food_category": "Sample Category",
            "brand": "Sample Brand",
            "nutrition": {
                "calories": 150.0,
                "protein": 10.0,
                "total_sugars": 2.0,
                "carbohydrates": 20.0,
                "fat": 5.0
            }
        }

        self.assertEqual(parse_food_data(food_item), expected_summary)

    # Test if dict with unbranded structure parses correctly
    def test_parse_food_data_correct_summary_for_unbranded(self):
            # Sample food item data
            food_item = {
                "description": "Sample Food",
                "foodCategory": {"description": "Sample Category"},
                "foodNutrients": [
                    {"nutrient": {"number": '203'}, "amount": 10.0},  # Protein
                    {"nutrient": {"number": '204'}, "amount": 5.0},   # Fat
                    {"nutrient": {"number": '269'}, "amount": 2.0},   # Total Sugars
                    {"nutrient": {"number": '205'}, "amount": 20.0},  # Carbohydrates
                    {"nutrient": {"number": '208'}, "amount": 150.0}  # Calories
                ]
            }
    
            expected_summary = {
                "canonical_name": "Sample Food",
                "food_category": "Sample Category",
                "brand": None,
                "nutrition": {
                    "calories": 150.0,
                    "protein": 10.0,
                    "total_sugars": 2.0,
                    "carbohydrates": 20.0,
                    "fat": 5.0
                }
            }
    
            self.assertEqual(parse_food_data(food_item), expected_summary)

    # Test that it correctly parses nutrients, leaving as None if it isn't in the dict
    def test_parse_food_data_handles_missing_nutrients(self):

        # Sample food item data with missing nutrients
        food_item = {
            "description": "Sample Food",
            "foodNutrients": [
                {"nutrient": {"number": '203'}, "amount": 10.0},  # Protein
                # Missing Fat, Total Sugars, Carbohydrates, Calories
            ]
        }

        expected_summary = {
            "canonical_name": "Sample Food",
            "food_category": None,
            "brand": None,
            "nutrition": {
                "calories": None,
                "protein": 10.0,
                "total_sugars": None,
                "carbohydrates": None,
                "fat": None
            }
        }

        self.assertEqual(parse_food_data(food_item), expected_summary)

    # test if food_category remains None if nothing is in the response
    def test_parse_food_data_leaves_food_category_none(self):
                # Sample food item data
                food_item = {
                    "description": "Sample Food",
                    "brandOwner": "Sample Brand",
                    "foodNutrients": [
                        {"nutrient": {"number": '203'}, "amount": 10.0},  # Protein
                        {"nutrient": {"number": '204'}, "amount": 5.0},   # Fat
                        {"nutrient": {"number": '269'}, "amount": 2.0},   # Total Sugars
                        {"nutrient": {"number": '205'}, "amount": 20.0},  # Carbohydrates
                        {"nutrient": {"number": '208'}, "amount": 150.0}  # Calories
                    ]
                }
        
                expected_summary = {
                    "canonical_name": "Sample Food",
                    "food_category": None,
                    "brand": "Sample Brand",
                    "nutrition": {
                        "calories": 150.0,
                        "protein": 10.0,
                        "total_sugars": 2.0,
                        "carbohydrates": 20.0,
                        "fat": 5.0
                    }
                }
        
                self.assertEqual(parse_food_data(food_item), expected_summary)

# Pretty much just tests that the API is calling correctly, does not test logic of parsing results
class TestSummarizeFood(unittest.TestCase):

    def setUp(self):
        # Sample API response for a food item (American cheese)
        self.food_item = {
            "description": "AMERICAN CHEESE",
            "brandedFoodCategory": "Cheese",
            "brandOwner": "World Cheese Co. Inc.",
            "foodNutrients": [
                {"nutrient": {"number": '203'}, "amount": 21.05},  # Protein
                {"nutrient": {"number": '204'}, "amount": 31.58},  # Fat
                {"nutrient": {"number": '269'}, "amount": 0.0},    # Total Sugars
                {"nutrient": {"number": '205'}, "amount": 5.26},   # Carbohydrates
                {"nutrient": {"number": '208'}, "amount": 368.0}   # Calories
            ]
        }

        self.expected_summary = {
            "canonical_name": "AMERICAN CHEESE",
            "food_category": "Cheese",
            "brand": "World Cheese Co. Inc.",
            "nutrition": {
                "calories": 368.0,
                "protein": 21.05,
                "total_sugars": 0.0,
                "carbohydrates": 5.26,
                "fat": 31.58
            }
        }

    @patch("foodData.requests.get")
    def test_summarize_food_outputs_correct_summary(self, mock_get):
        # Mock the API response so no real request is made
        mock_get.return_value.json.return_value = self.food_item

        self.assertEqual(summarize_food(2054688), self.expected_summary)

    @patch("foodData.requests.get")
    def test_summarize_food_calls_api_with_correct_url_and_key(self, mock_get):
        mock_get.return_value.json.return_value = self.food_item

        summarize_food(2054688)

        mock_get.assert_called_once_with(f"{BASE}/food/2054688", params={"api_key": API_KEY})

    @patch("foodData.requests.get")
    def test_summarize_food_returns_none_on_network_error(self, mock_get):
        # Simulate the request failing (no internet, timeout, etc.)
        mock_get.side_effect = requests.ConnectionError("Network down")

        self.assertIsNone(summarize_food(2054688))


class TestGetFoodId(unittest.TestCase):

    @patch("foodData.requests.get")
    def test_get_food_id_returns_first_result_id(self, mock_get):
        # Only choose the first item found after searching
        mock_get.return_value.json.return_value = {
            "foods": [
                {"fdcId": 2054688, "description": "AMERICAN CHEESE"},
                {"fdcId": 1538991, "description": "AMERICAN CHEESE"}
            ]
        }

        self.assertEqual(get_food_id("american cheese"), 2054688)

    @patch("foodData.requests.get")
    def test_get_food_id_calls_api_with_correct_url_and_params(self, mock_get):
        mock_get.return_value.json.return_value = {"foods": [{"fdcId": 2054688}]}

        get_food_id("american cheese")

        mock_get.assert_called_once_with(
            f"{BASE}/foods/search",
            params={"api_key": API_KEY, "query": "american cheese", "pageSize": 1}
        )

    @patch("foodData.requests.get")
    def test_get_food_id_returns_none_when_no_results(self, mock_get):
        # Search found nothing
        mock_get.return_value.json.return_value = {"foods": []}

        self.assertIsNone(get_food_id("not a real food"))

    @patch("foodData.requests.get")
    def test_get_food_id_returns_none_on_network_error(self, mock_get):
        mock_get.side_effect = requests.Timeout("Request timed out")

        self.assertIsNone(get_food_id("american cheese"))


if __name__ == "__main__":
    unittest.main()