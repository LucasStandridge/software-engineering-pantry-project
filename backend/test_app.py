import unittest

import app as app_module
from GroceryList import GroceryList

class APITestCase(unittest.TestCase):

    def setUp(self):
        app_module.g_list = GroceryList()
        app_module.app.config.update(TESTING = True)
        self.client = app_module.app.test_client()

    def post_item(self, name):
        return self.client.post("/api/items", json={"name": name})

    def add_and_get_id(self, name):
        response = self.post_item(name)
        return response.get_json()["item"]["id"]

    def current_items(self):
        return self.client.get("/api/items").get_json()["items"]

class TestItemsRoute(APITestCase):

    def test_get_empty_list(self):
        response = self.client.get("/api/items")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"items": []})

    def test_post_creates_items(self):
        response = self.post_item("milk")
        self.assertEqual(response.status_code, 201)
        body = response.get_json()
        self.assertIs(body["created"], True)
        self.assertEqual(body["item"]["quantity"], 1)
        self.assertEqual(len(self.current_items()), 1)

    def test_post_duplicate_merges_returns_200(self):
        base = self.post_item("milk").get_json()
        response = self.post_item("  MilK  ")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["item"]["id"], base["item"]["id"])
        self.assertIs(body["created"], False)
        self.assertEqual(body["item"]["quantity"], 2)
        self.assertEqual(len(self.current_items()), 1)

    def test_bad_input_returns_400_and_no_change(self):
        bad_bodies = [{}, {"name": 123}, {"name": "   "}, {"name": "x" * 111 }]
        for b_body in bad_bodies:
            with self.subTest(body = b_body):
                response = self.client.post("/api/items", json = b_body)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.get_json())
        self.assertEqual(self.current_items(), [])

class TestDecrementRoute(APITestCase):

    def test_decrement_returns_new_quantity(self):
        item_id = self.add_and_get_id("milk")
        self.post_item("milk")
        response = self.client.post(f"/api/items/{item_id}/decrement")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"quantity": 1})

    def test_decrement_at_one_removes_item(self):
        item_id = self.add_and_get_id("milk")
        response = self.client.post(f"/api/items/{item_id}/decrement")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"quantity": 0})
        self.assertEqual(self.current_items(), [])

    def test_decrement_unknown_id_returns_404(self):
        response = self.client.post("/api/items/{1}/decrement")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)

class TestIncrementRoute(APITestCase):

    def test_increment_returns_new_quantity(self):
        item_id = self.add_and_get_id("milk")
        response = self.client.post(f"/api/items/{item_id}/increment")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"quantity": 2})

    def test_increment_unknown_id_returns_404(self):
        response = self.client.post(f"/api/items/{1}/increment")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)

class TestRemoveRoute(APITestCase):

    def test_remove_item_returns_none(self):
        item_id = self.add_and_get_id("milk")
        response = self.client.delete(f"/api/items/{item_id}/delete")
        self.assertEqual(response.status_code, 204)
        
    def test_remove_item_removes_item(self):
        item_id = self.add_and_get_id("milk")
        response = self.client.delete(f"/api/items/{item_id}/delete")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.current_items(), [])


if __name__ == "__main__":
    unittest.main()