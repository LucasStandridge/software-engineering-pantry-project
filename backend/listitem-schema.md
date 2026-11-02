# Pantry Planner ListItem Class

## Overview

The initial ListItem class design is meant to support basic ListItem functionsn and hold information such as quantity, name, a unique id, data whether it is checked off, etc. The class should be able to support all necessary capabilities that the list may require from it. 

As development progresses, extra data may be required for storage in this class. Similarly, certain variables and functions of this class may be changed depending on API usage and food data storage. The class should be modifiable to accomodate such changes. 

## Class Variables and Initialization

| Variable Name | Data Type | Constraints | Description |
| 'item_name' |  string | NOT NULL | Normalized string for data lookup/usage |
| 'item_data' | unknown | NOT NULL | Data package that will contain food information |
| 'item_id' | integer | NOT NULL, > 0 | A unique identifier to prevent issues when sorting, removing |
| 'checked_off | boolean | NOT NULL | Represents whether the user has checked off the item |
| 'quantity | integer | NOT NULL >= 1 | Represents how much of the item the user wants | 
| 'insertion_order | integer | NOT NULL, >0 | Represents a 'time stamp' of when the user added the item |

## Proposed Python Schema

```pseudocode
Class ListItem(data):
    item_id integer NOT NULL, >0
    item_name string NOT NULL, normalized
    item_data FOODDATA, NOT NULL
    checked_off false
    quantity integer >= 1
    insertion_order NOT NULL, datetime

```

The above is a proposed python schema. Normalization requirements, quantity measures, etc, will depend on application level implementation

## Proposed Helper Functions
```python
__init__(self, data):
    self.item_id = datetime.now()
    self.data = data
    self.name = self.data.name
    self.quantity = 1
    self.checked_off = False
    self.insertion_order = self.item_id

toggle_checked_off(self):
    self.checked_off = not self.checked_off
```
## Quantity Handling
ListItems should internally support incrementing their own quantity. If a GroceryList detects that the user has put the same item twice, the quantity of the item first added to the list should be incremented instead of adding another item to the list. 

Subject to dev approval, quantity is not representative of the amount of food that the item holds. For example, if the user adds 1 gallon of milk, milk should appear with a quantity of 1. If they then wish to add a half gallon of milk, that will be added as a separate item with a quantity of 1.

## Implementation Notes

Initial implementation should require only Python with the usage of the datetime module, pending confirmation from dev team.
Implementation should only cover ListItem as well as proposed helper functions and tests to ensure accuracy and reliability of items.

## Scope
This document defines proposed structure for a ListItem, and does not include implementation, which will be a separate task. 
This schema assumes that the data for food will contain names and identifiable quantity measures. For example, if the data for item lookup does not support searches such as 'Milk, gallon' or 'Eggs, 1 dozen', then this class will change to support that, and roll all of the same items into the same ListItem ('Milk', instead of '1 Gallon of Milk', '.5 Gallon of Milk')