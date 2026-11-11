"""GroceryList: collection of ListItems and rules that keep them consistent
Callers should route methods through GroceryList instead of touching items directly
"""

from backend.ListItem import ListItem

"""Trim the ends and outside whitespace. Keeps capitalization
Case insensitive comparison happens within find_duplicate_index

Limitations: Does not handle plurals 
Module level so future data lookup can access
Cleaning can change based on data needs (cleaning plurals, etc)"""
def clean_name(name):
        return " ".join(name.split())


class GroceryList():
    """Ordered list of ListItems. Keeps the following rules consistent:
    1) Items are only changed through GrocerList methods
    2) Items with the same cleaned names (size as well in the future) are merged
    3) Item quantity cannot decrease below 1 - doing so removes it from the list
    4) Every unique item has its own string ID
    
    Limitations: 
    1) Items are merged based on name, not actual data or size
        - In the future, a half gallon of milk should not merge with a full gallon. This
            ensures that when items are added to the pantry, counting is consistent
    2) Lookups perform in O(n) time complexity. Should be fine as grocery lists are relatively small
    3) Sorting algorithms are not implemented yet"""
    def __init__(self):
        self.items = []

    def add_item(self, name, data):
        """Add an item, or increase quantity if the same item already exists. 
        Returns True if an item was created, followed by the new item's ID
        Returns False if the item already exists in the list, followed by the original's ID
        
        Raises value errors if the name is invalid (empty space) or if no data is passed through
        Errors are raised before items are added so they should leave list intact"""
        cleaned_name = clean_name(name)
        if not cleaned_name:
            raise ValueError("Name is empty")
        if not self.is_valid_data(data):
            raise ValueError("Not valid data structure")
        
        dupe_idx = self.find_duplicate_index(cleaned_name)
        if dupe_idx is not None:
            self.items[dupe_idx].increment_quantity()
            return (False, self.items[dupe_idx].id) 

        new_item = ListItem(cleaned_name, data)
        self.items.append(new_item)
        return (True, new_item.id)

    def decrement_item(self, item_id):
        """Lower an item's quantity by one; remove it if it was already 1.
 
        Returns the new quantity, or 0 if the item was removed, since items cannot
        have a quantity of 0.
 
        Raises KeyError if the id is not found.
        """

        for item in self.items:
            if item.id == item_id:
                if item.decrement_quantity():
                    return item.quantity
                else:
                    self.remove_item(item_id)
                    #Returns 0 instead of (now gone) item quantity
                    return 0
        raise KeyError("ID not found")
        
    def remove_item(self, item_id):
        """Remove an item regardless of quantity. Returns None
        Raises KeyError if the item is not found."""
        for item in self.items:
            if item.id == item_id:
                self.items.remove(item)
                return None
        raise KeyError("ID not found")

    def toggle_item(self, item_id):
        "Flips an items checked_off state. Returns the new state"
        "Raises KeyError if the ID is not found."
        for item in self.items:
            if item.id == item_id:
                item.toggle_checked_off()
                #Return new state of item
                return item.checked_off
        raise KeyError("ID not found")

    def sort_alphabetically(self):
        #TODO: not implemented. Should return a sorted view (new list) and leave
        #'''items''' intact to preserve original order.
        #Other sorting algorithms are similarly not created yet
        pass

    def find_duplicate_index(self, name):
        """Return index of item whose name matches, or None.
        Comparison ignores capitalization. Name should already be cleaned"""
        for idx, item in enumerate(self.items):
            if item.name.casefold() == name.casefold():
                return idx
        return None

    def read_all_items(self):
        """Returns a list of plain dicts in order."""
        return [item.read_information() for item in self.items]
    
    def read_item_by_id(self, item_id):
        """Return one item as a plain dict. Raise KeyError if item is not found"""
        for item in self.items:
            if item.id == item_id:
                return item.read_information()
        raise KeyError("ID not found")
    
    # TODO: replace with real checks once dev team confirms data source    
    def is_valid_data(self, data):
        if data is not None:
            return True
        else:
            return False

