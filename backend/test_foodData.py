import unittest
from copy import deepcopy
from unittest.mock import patch, call

import requests

from foodData import parse_food_data, summarize_food, get_food_id, API_KEY, BASE


# ---------------------------------------------------------------------------
# Shared sample data
# Tests should never modify these directly. Use deepcopy() and change the copy.
# ---------------------------------------------------------------------------

SAMPLE_FDC_ID = 2054688

def make_nutrient(nutrient_id, number, name, unit, amount):
    """Build one entry of 'foodNutrients' in the same shape the FDC API returns."""
    return {
        "type": "FoodNutrient",
        "nutrient": {
            "id": nutrient_id,
            "number": number,
            "name": name,
            "unitName": unit,
        },
        "amount": amount,
    }


# Sample response from GET /food/{fdcId} for a branded food (American cheese)
SAMPLE_FOOD = {
    "fdcId": SAMPLE_FDC_ID,
    "dataType": "Branded",
    "description": "AMERICAN CHEESE",
    "brandOwner": "World Cheese Co. Inc.",
    "brandedFoodCategory": "Cheese",
    "servingSize": 28.0,
    "servingSizeUnit": "g",
    "foodNutrients": [
        make_nutrient(1003, "203", "Protein", "g", 21.05),
        make_nutrient(1004, "204", "Total lipid (fat)", "g", 31.58),
        make_nutrient(2000, "269", "Sugars, Total", "g", 0.0),
        make_nutrient(1005, "205", "Carbohydrate, by difference", "g", 5.26),
        make_nutrient(1008, "208", "Energy", "kcal", 368.0),
        # Nutrients that exist in the response but that parse_food_data doesn't track
        make_nutrient(1093, "307", "Sodium, Na", "mg", 1250.0),
        make_nutrient(1079, "291", "Fiber, total dietary", "g", 0.0),
    ],
}

# What parse_food_data should return for SAMPLE_FOOD
EXPECTED_SUMMARY = {
    "canonical_name": "AMERICAN CHEESE",
    "food_category": "Cheese",
    "brand": "World Cheese Co. Inc.",
    "nutrition": {
        "calories": 368.0,
        "protein": 21.05,
        "total_sugars": 0.0,
        "carbohydrates": 5.26,
        "fat": 31.58,
    },
}

# Sample response from GET /foods/search. Only the first result should be used
SAMPLE_SEARCH_RESPONSE = {
    "totalHits": 2,
    "currentPage": 1,
    "totalPages": 1,
    "foods": [
        {
            "fdcId": SAMPLE_FDC_ID,
            "dataType": "Branded",
            "description": "AMERICAN CHEESE",
            "brandOwner": "World Cheese Co. Inc.",
        },
        {
            "fdcId": 1538991,
            "dataType": "Branded",
            "description": "AMERICAN CHEESE",
            "brandOwner": "Another Cheese Co.",
        },
    ],
}


class TestParseFoodData(unittest.TestCase):

    # Test if dict structured with branded structure parses correctly
    def test_parse_food_data_correct_summary_for_branded(self):
        food_item = deepcopy(SAMPLE_FOOD)

        self.assertEqual(parse_food_data(food_item), EXPECTED_SUMMARY)

    # Test if dict with unbranded structure parses correctly
    def test_parse_food_data_correct_summary_for_unbranded(self):
        # Unbranded foods have no brand fields and use a nested 'foodCategory' instead
        food_item = deepcopy(SAMPLE_FOOD)
        food_item["dataType"] = "SR Legacy"
        del food_item["brandOwner"]
        del food_item["brandedFoodCategory"]
        food_item["foodCategory"] = {"description": "Dairy and Egg Products"}

        expected_summary = deepcopy(EXPECTED_SUMMARY)
        expected_summary["brand"] = None
        expected_summary["food_category"] = "Dairy and Egg Products"

        self.assertEqual(parse_food_data(food_item), expected_summary)

    # Test that it correctly parses nutrients, leaving as None if it isn't in the dict
    def test_parse_food_data_handles_missing_nutrients(self):
        # Keep only protein, remove every other nutrient
        food_item = deepcopy(SAMPLE_FOOD)
        food_item["foodNutrients"] = [
            n for n in food_item["foodNutrients"] if n["nutrient"]["number"] == "203"
        ]

        expected_summary = deepcopy(EXPECTED_SUMMARY)
        for key in expected_summary["nutrition"]:
            if key != "protein":
                expected_summary["nutrition"][key] = None

        self.assertEqual(parse_food_data(food_item), expected_summary)

    # Test if food_category remains None if nothing is in the response
    def test_parse_food_data_leaves_food_category_none(self):
        food_item = deepcopy(SAMPLE_FOOD)
        del food_item["brandedFoodCategory"]

        expected_summary = deepcopy(EXPECTED_SUMMARY)
        expected_summary["food_category"] = None

        self.assertEqual(parse_food_data(food_item), expected_summary)

    # Test that an empty nutrient list leaves every nutrition value as None
    def test_parse_food_data_handles_empty_nutrient_list(self):
        food_item = deepcopy(SAMPLE_FOOD)
        food_item["foodNutrients"] = []

        expected_summary = deepcopy(EXPECTED_SUMMARY)
        for key in expected_summary["nutrition"]:
            expected_summary["nutrition"][key] = None

        self.assertEqual(parse_food_data(food_item), expected_summary)

    # Test that nutrient numbers we don't track (ex. 307 = sodium) don't affect the summary
    def test_parse_food_data_ignores_unrecognized_nutrients(self):
        # SAMPLE_FOOD already contains sodium (307) and fiber (291)
        food_item = deepcopy(SAMPLE_FOOD)

        result = parse_food_data(food_item)

        self.assertEqual(result, EXPECTED_SUMMARY)
        self.assertEqual(
            set(result["nutrition"].keys()),
            {"calories", "protein", "total_sugars", "carbohydrates", "fat"}
        )
        self.assertNotIn(1250.0, result["nutrition"].values())  # Sodium amount

    # Test that a nutrient with an amount of 0.0 is kept as 0.0 rather than treated as missing
    def test_parse_food_data_keeps_zero_amounts(self):
        # Total sugars is 0.0 in SAMPLE_FOOD
        food_item = deepcopy(SAMPLE_FOOD)

        result = parse_food_data(food_item)

        self.assertEqual(result["nutrition"]["total_sugars"], 0.0)
        self.assertIsNotNone(result["nutrition"]["total_sugars"])


# Pretty much just tests that the API is calling correctly, does not test logic of parsing results
class TestSummarizeFood(unittest.TestCase):

    @patch("foodData.requests.get")
    def test_summarize_food_outputs_correct_summary(self, mock_get):
        # Mock the API response so no real request is made
        mock_get.return_value.json.return_value = deepcopy(SAMPLE_FOOD)

        self.assertEqual(summarize_food(SAMPLE_FDC_ID), EXPECTED_SUMMARY)

    @patch("foodData.requests.get")
    def test_summarize_food_calls_api_with_correct_url_and_key(self, mock_get):
        mock_get.return_value.json.return_value = deepcopy(SAMPLE_FOOD)

        summarize_food(SAMPLE_FDC_ID)

        mock_get.assert_called_once_with(f"{BASE}/food/{SAMPLE_FDC_ID}", params={"api_key": API_KEY})

    @patch("foodData.requests.get")
    def test_summarize_food_returns_none_on_network_error(self, mock_get):
        # Simulate the request failing (no internet, timeout, etc.)
        mock_get.side_effect = requests.ConnectionError("Network down")

        self.assertIsNone(summarize_food(SAMPLE_FDC_ID))

    @patch("foodData.requests.get")
    def test_summarize_food_returns_none_on_error_response(self, mock_get):
        # The API returns an error body (no "description" or "foodNutrients") for a bad ID
        mock_get.return_value.json.return_value = {"error": "Not found"}

        self.assertIsNone(summarize_food(0))

    @patch("foodData.requests.get")
    def test_summarize_food_returns_none_on_invalid_json(self, mock_get):
        # Simulate a response body that can't be decoded (ex. an HTML error page)
        mock_get.return_value.json.side_effect = ValueError("No JSON object could be decoded")

        self.assertIsNone(summarize_food(SAMPLE_FDC_ID))


class TestGetFoodId(unittest.TestCase):

    # Make sure it returns the first id it finds
    @patch("foodData.requests.get")
    def test_get_food_id_returns_first_result_id(self, mock_get):
        mock_get.return_value.json.return_value = deepcopy(SAMPLE_SEARCH_RESPONSE)

        self.assertEqual(get_food_id("american cheese"), SAMPLE_FDC_ID)

    # Make sure api is called correctly
    @patch("foodData.requests.get")
    def test_get_food_id_calls_api_with_correct_url_and_params(self, mock_get):
        mock_get.return_value.json.return_value = deepcopy(SAMPLE_SEARCH_RESPONSE)

        get_food_id("american cheese")

        mock_get.assert_called_once_with(
            f"{BASE}/foods/search",
            params={"api_key": API_KEY, "query": "american cheese", "pageSize": 1}
        )

    # Make sure none is returned if there are no results
    @patch("foodData.requests.get")
    def test_get_food_id_returns_none_when_no_results(self, mock_get):
        search_response = deepcopy(SAMPLE_SEARCH_RESPONSE)
        search_response["totalHits"] = 0
        search_response["foods"] = []
        mock_get.return_value.json.return_value = search_response

        self.assertIsNone(get_food_id("not a real food"))

    # Make sure none is returned if a network error occurs
    @patch("foodData.requests.get")
    def test_get_food_id_returns_none_on_network_error(self, mock_get):
        mock_get.side_effect = requests.Timeout("Request timed out")

        self.assertIsNone(get_food_id("american cheese"))

    # Make sure that id is returned when including a brand
    @patch("foodData.requests.get")
    def test_get_food_id_returns_id_when_brand_search_has_hits(self, mock_get):
        mock_get.return_value.json.return_value = deepcopy(SAMPLE_SEARCH_RESPONSE)

        self.assertEqual(get_food_id("american cheese", "World Cheese Co. Inc."), SAMPLE_FDC_ID)

    # Make sure the general search is used when the brand search finds nothing
    @patch("foodData.requests.get")
    def test_get_food_id_falls_back_to_general_search_when_brand_has_no_hits(self, mock_get):
        # First call (brand search) finds nothing, second call (general search) finds results
        no_brand_hits = deepcopy(SAMPLE_SEARCH_RESPONSE)
        no_brand_hits["totalHits"] = 0
        no_brand_hits["foods"] = []

        mock_get.return_value.json.side_effect = [
            no_brand_hits,
            deepcopy(SAMPLE_SEARCH_RESPONSE),
        ]

        self.assertEqual(get_food_id("american cheese", "Unknown Brand"), SAMPLE_FDC_ID)

        self.assertEqual(mock_get.call_args_list, [
            call(f"{BASE}/foods/search",
                 params={"api_key": API_KEY, "query": "american cheese", "brandOwner": "Unknown Brand", "pageSize": 1}),
            call(f"{BASE}/foods/search",
                 params={"api_key": API_KEY, "query": "american cheese", "pageSize": 1}),
        ])

    # Make sure none is returned if the response is missing the expected structure
    @patch("foodData.requests.get")
    def test_get_food_id_returns_none_when_response_missing_foods_key(self, mock_get):
        search_response = deepcopy(SAMPLE_SEARCH_RESPONSE)
        del search_response["foods"]
        mock_get.return_value.json.return_value = search_response

        self.assertIsNone(get_food_id("american cheese"))


if __name__ == "__main__":
    unittest.main()