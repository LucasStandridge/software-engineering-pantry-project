"""ListItem: one entry on a grocery list.

A ListItem owns the state of a single entry (how many, checked off or not).
It knows nothing about the other items on the list. Rules that involve the
whole collection (duplicate detection, removal, ordering) live in GroceryList,
because an item cannot see its siblings or remove itself from its container.
"""
import datetime
import uuid


class ListItem():
    """One row on the grocery list.

    Fields:
        name:            The cleaned text the user typed
        data:            Dictionary containing food data. Should include canonical name, amount per-unit, nutrition info, and expiration date if provided
        quantity:        How many of this entry the user wants. Always >= 1.
                         NOTE: Does not distinguish size yet. 1 Gallon of milk
                         is treated == to a Half Gallon for now
        checked_off:     True once the user has marked the item as bought.
        insertion_order: When the item was created.
        id:              Unique string used to refer to this item from outside

    Limitations / future changes:
        - Nothing distinguishes sizes yet. GroceryList merges by name, so
          "milk" (1 gallon) and "milk" (half gallon) would merge. The planned
          fix is an extra size field next to ``name``. Relevant for tracking how much
          of each grocery the user has stored in their pantry (grocery list should push 
          half gallon or gallon to pantry respectively)
        - ``data`` is stored but never inspected.
        - There is no way to attach or replace ``data`` after creation
    """

    def __init__(self, name, data):
        # ``name`` is its own field instead of being read from ``data.name``:
        #   1. The list needs something to display and compare no matter what
        #      shape the food data ends up taking (dict, object, string...).
        #   2. It keeps ListItem independent of the data layer, so changing the
        #      data source cannot break display or duplicate detection.
        #   3. It records what the user typed (cleaned), which may differ from
        #      the database's canonical name.
        # Trade-off: ``name`` and anything inside ``data`` can drift apart.
        # If that causes confusion later, derive name from data at creation.
        self.name = name
        self.data = data

        self.quantity = 1
        self.checked_off = False

        # Local wall-clock time. Becomes useful once sorting is 
        # implemented and storage order stops being the added order.
        # Note: datetime is not JSON-serializable, so read_information()
        # leaves it out.
        self.insertion_order = datetime.datetime.now()

        # A str (not a uuid.UUID object) because ids must travel to the frontend
        self.id = str(uuid.uuid4())

    def toggle_checked_off(self):
        """Flip the checked-off state. (Returns nothing; read ``checked_off``.)"""
        self.checked_off = not self.checked_off

    def decrement_quantity(self):
        """Lower quantity by one, but never below 1.

        Returns True if the quantity was lowered, False if it was already 1.
        On False, the caller decides what to do (GroceryList removes the item):
        the item cannot remove itself.
        """
        if self.quantity > 1:
            self.quantity -= 1
            return True
        else:
            return False

    def increment_quantity(self):
        """Raise quantity by one."""
        self.quantity += 1

    def read_information(self):
        """Return a plain-dict snapshot of this item for display.

        A new dict is built on every call, so callers cannot change the live
        item through it. ``insertion_order`` is left out (not JSON-serializable)
        and so is ``data`` (unsure of data structure - may not be serializable).
        """
        return {
            "name": self.name,
            "quantity": self.quantity,
            "checked_off": self.checked_off,
            "id": self.id
        }