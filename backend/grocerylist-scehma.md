# PantryPlanner GroceryList class

## Overview

The goal of the GroceryList class is to have a way to easily access information in ListItems, as well as access data within them, change the quantity of them, etc. The idea is that it will make the displayal of the listitems within the grocery list page easier. 

The list will require all expected functionality of what a list should do, with added helper functions to change the status of items within it, such as calling helper functions inside ListItems to change quantity and is_checked_off. 

## Class Variables and Initialization

| Variable Name | Data Type | Constraints | Description |
| items | Array[ListItem] | Starts empty, only modifier by class methods | Array to hold all items within the grocery list | 
| next_id | integer | >0 | Keeps track of what id to assign to items within list |
## Proposed Class Functions

# instantiate items and add them to the list if they are not already in it, otherwise increment quantitiy
add_item(self, name, data):
    *pass through list*
    *if duplicate item: increment quantity by 1*
    *return old item id*
    
    *insantiate item and add it to list if not*
    *return new item id*

# Find items based on id, decrement quantity by 1, remove if quantity = 0
decrement_item(self, id_to_decrease):
    *pass through list*
    *if quantity > 1: decrement by 1*
    *if quantity == 1: remove from list*
    return item quantity

# Remove item from list regardless of quantity
remove(self, item_id):
    *remove item*

# Various Sorting Features
sort_alphabetically
sort_by_food_group
sort_by_expected_aisle_number
sort_by_storage_area

# Toggle being checked off or not
toggle_checked_off(item_id)
    *check off item*

# Check for duplicate data
check_duplicate_item(data):
    *pass through list*
    *if any id in list has data equal to parameter data, is duplicate*
    
## Implementation Notes
Implementation should require only python, with uuid4 depending on dev responses regarding ID
'item' list could change to dictionary for faster lookup times, pending dev responses 
If an invalid id is passed to a function, an error should be raised by that function
