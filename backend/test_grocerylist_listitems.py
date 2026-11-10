import unittest

from GroceryList import GroceryList

DATA = "2%, dairy"  #placeholder until real food data exists


class GroceryListTestCase(unittest.TestCase):

    def setUp(self):
        self.g_list = GroceryList()

    def add(self, name, data=DATA):
        return self.g_list.add_item(name, data)

    def names(self):
        return [entry["name"].casefold() for entry in self.g_list.read_all_items()]

class TestAddItem(GroceryListTestCase):

    def test_add_new_item(self):
        created, item_id = self.add("milk")
        self.assertIs(created, True)
        self.assertIsInstance(item_id, str)
        entries = self.g_list.read_all_items()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["id"], item_id)
        self.assertEqual(entries[0]["quantity"], 1)
        self.assertIs(entries[0]["checked_off"], False)

    def test_add_duplicate_merges_into_existing_item(self):
        _, first_id = self.add("milk")
        created, second_id = self.add("milk")
        self.assertIs(created, False)
        self.assertEqual(second_id, first_id)
        entries = self.g_list.read_all_items()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["quantity"], 2)

    def test_duplicate_of_first_item_is_detected(self):
        # index 0 is falsy, so this catches "if dupe_idx:" style bugs
        _, milk_id = self.add("milk")
        self.add("eggs")
        created, returned_id = self.add("milk")
        self.assertIs(created, False)
        self.assertEqual(returned_id, milk_id)
        self.assertEqual(len(self.g_list.read_all_items()), 2)

    def test_case_and_whitespace_variants_merge(self):
        _, first_id = self.add("Milk")
        created, second_id = self.add("  milk ")
        self.assertIs(created, False)
        self.assertEqual(second_id, first_id)
        entries = self.g_list.read_all_items()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["quantity"], 2)

    def test_stored_name_is_trimmed_and_collapsed(self):
        self.add("  chicken    breast ")
        name = self.g_list.read_all_items()[0]["name"]
        self.assertEqual(name.casefold(), "chicken breast")

    def test_empty_name_is_rejected(self):
        with self.assertRaises(ValueError):
            self.add("")

    def test_whitespace_only_name_is_rejected(self):
        with self.assertRaises(ValueError):
            self.add("     ")

    def test_missing_data_is_rejected(self):
        with self.assertRaises(ValueError):
            self.add("milk", None)


class TestDecrementItem(GroceryListTestCase):

    def test_decrement_lowers_quantity_and_returns_it(self):
        _, item_id = self.add("milk")
        self.add("milk")
        self.add("milk")  # quantity is now 3
        self.assertEqual(self.g_list.decrement_item(item_id), 2)
        self.assertEqual(self.g_list.decrement_item(item_id), 1)
        self.assertEqual(self.g_list.read_item_by_id(item_id)["quantity"], 1)

    def test_decrement_at_one_removes_item_and_returns_zero(self):
        _, item_id = self.add("milk")
        self.assertEqual(self.g_list.decrement_item(item_id), 0)
        self.assertEqual(self.g_list.read_all_items(), [])

    def test_decrement_affects_only_the_matching_item(self):
        # the target is the second item, so a loop that returns early on item 1 fails here
        _, milk_id = self.add("milk")
        _, eggs_id = self.add("eggs")
        self.add("eggs")  # eggs quantity is 2
        self.assertEqual(self.g_list.decrement_item(eggs_id), 1)
        self.assertEqual(self.g_list.read_item_by_id(milk_id)["quantity"], 1)
        self.assertEqual(self.g_list.read_item_by_id(eggs_id)["quantity"], 1)

class TestIncrementItem(GroceryListTestCase):
    def test_increment_quantity_and_returns_it(self):
        _, item_id = self.add("milk")
        self.assertEqual(self.g_list.increment_item(item_id), 2)
        self.assertEqual(self.g_list.read_item_by_id(item_id)["quantity"], 2)

    def test_increment_affects_only_the_matching_item(self):
        _, milk_id = self.add("milk")
        _, eggs_id = self.add("eggs")
       
        self.assertEqual(self.g_list.increment_item(eggs_id), 2)
        self.assertEqual(self.g_list.read_item_by_id(milk_id)["quantity"], 1)
        self.assertEqual(self.g_list.read_item_by_id(eggs_id)["quantity"], 2)
        
class TestRemoveToggleAndRead(GroceryListTestCase):

    def test_remove_item_removes_only_that_item(self):
        _, milk_id = self.add("milk")
        self.add("eggs")
        self.assertIsNone(self.g_list.remove_item(milk_id))
        self.assertEqual(self.names(), ["eggs"])

    def test_remove_ignores_quantity(self):
        _, milk_id = self.add("milk")
        self.add("milk")
        self.add("milk")
        self.g_list.remove_item(milk_id)
        self.assertEqual(self.g_list.read_all_items(), [])

    def test_toggle_returns_new_state_and_flips_back(self):
        _, item_id = self.add("milk")
        self.assertIs(self.g_list.toggle_item(item_id), True)
        self.assertIs(self.g_list.read_item_by_id(item_id)["checked_off"], True)
        self.assertIs(self.g_list.toggle_item(item_id), False)
        self.assertIs(self.g_list.read_item_by_id(item_id)["checked_off"], False)

    def test_toggle_affects_only_the_matching_item(self):
        self.add("milk")
        _, eggs_id = self.add("eggs")
        self.g_list.toggle_item(eggs_id)
        states = {e["name"].casefold(): e["checked_off"] for e in self.g_list.read_all_items()}
        self.assertEqual(states, {"milk": False, "eggs": True})

    def test_unknown_id_raises_key_error(self):
        self.add("milk")
        for method in (
            self.g_list.decrement_item,
            self.g_list.increment_item,
            self.g_list.remove_item,
            self.g_list.toggle_item,
            self.g_list.read_item_by_id,
        ):
            with self.subTest(method=method.__name__):
                with self.assertRaises(KeyError):
                    method("not-a-real-id")

    def test_read_all_items_on_empty_list(self):
        self.assertEqual(self.g_list.read_all_items(), [])

    def test_read_all_items_preserves_insertion_order(self):
        for name in ("milk", "eggs", "bread"):
            self.add(name)
        self.assertEqual(self.names(), ["milk", "eggs", "bread"])

    def test_read_item_by_id_returns_expected_fields(self):
        _, item_id = self.add("milk")
        entry = self.g_list.read_item_by_id(item_id)
        self.assertEqual(set(entry), {"id", "name", "quantity", "checked_off"})
        self.assertEqual(entry["id"], item_id)

    def test_returned_data_is_a_copy(self):
        _, item_id = self.add("milk")
        entry = self.g_list.read_item_by_id(item_id)
        entry["quantity"] = 99
        self.g_list.read_all_items().clear()
        self.assertEqual(self.g_list.read_item_by_id(item_id)["quantity"], 1)
        self.assertEqual(len(self.g_list.read_all_items()), 1)


class TestListIdentity(GroceryListTestCase):

    def test_ids_are_unique(self):
        ids = [self.add(name)[1] for name in ("milk", "eggs", "bread", "apples")]
        self.assertEqual(len(set(ids)), len(ids))

    def test_two_lists_do_not_share_items(self):
        other = GroceryList()
        self.add("milk")
        self.assertEqual(other.read_all_items(), [])


if __name__ == "__main__":
    unittest.main()