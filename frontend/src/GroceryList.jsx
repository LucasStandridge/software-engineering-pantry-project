import { useEffect, useState } from "react";

async function fetchItems() {
    const response = await fetch("/api/items");

    if (!response.ok) {
        throw new Error("Could not load the list");
    }
    const data = await response.json();
    return data.items; 
}

export default function GroceryList() {
    const [items, setItems] = useState([]); // what the list shows
    const [name, setName] = useState("");   // what is typed in the box
    const [error, setError] = useState(""); // message to show, if any
    const [foodMatches, setFoodMatches] = useState([]);
    const [selectedFood, setSelectedFood] = useState(null);
    const [location, setLocation] = useState("refrigerator")

    // TODO: disable the button while a request is in flight. Two quick clicks
    // send two POSTs, and the second one bumps the quantity.
    const postFood = async () => {
        setError("");
        try {
            const response = await fetch("/api/items", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name,
                    ...(selectedFood && {
                        data: {
                            fdc_id: selectedFood.fdc_id,
                            canonical_name: selectedFood.description,
                            brand: selectedFood.brand,
                        },
                    }),
                }),
            });

            if (!response.ok) {
                const body = await response.json().catch(() => ({}));
                setError(body.error || "Something went wrong");
                return;
            }

            setName("");
            setSelectedFood(null);
            setFoodMatches([]);
            setItems(await fetchItems());
        } catch (err) {
            setError("Could not reach the server");
        }
    };

    const searchFoods = async () => {
        setError("");
        setFoodMatches([]);
        setSelectedFood(null);

        if (!name.trim()) {
            return;
        }

        try {
            const response = await fetch(
                `/api/foods/search?q=${encodeURIComponent(name.trim())}`
            );

            if (!response.ok) {
                setError("Could not search USDA food data");
                return;
            }

            const data = await response.json();
            setFoodMatches(data.foods);
        } catch {
            setError("Could not reach the food search service");
        }
    };

    const updateListItemQuantity = async (item_id, method) => {
        setError("");

        try{
            const response = await fetch(`/api/items/${item_id}/${method}`, {
                method: "POST",
            });
            
            if (!response.ok) {
                const body = await response.json().catch(() => ({}));
                setError(body.error || "Something went wrong");
                return;
            }
            setItems(await fetchItems());
        } catch (err) {
            setError("Could not reach the server");
        }
    };

    const removeListItem = async(item_id) => {
        setError("");

        try{
            const response = await fetch(`/api/items/${item_id}/delete`,{
                method: "DELETE"
            });

            if(!response.ok) {
                const body = await response.json().catch(() => ({}));
                setError(body.error || "Something went wrong");
                return;
            }
            setItems(await fetchItems());
        }catch (err){
            setError("Could not reach the server");
        }
    };

    const toggleItemChecked = async (item_id) => {
        setError("")

        try{
            const response = await fetch(`/api/items/${item_id}/toggle-checked`,{
                method: "POST"
            });
            if (!response.ok){
                const body = await response.json().catch(() => ({}));
                setError(body.error || "Something went wrong")
                return;
            }
            setItems(await fetchItems())
        }catch(err){
            setError("Could not reach server")
        }
    
    }

    const pushItemsToInventory = async () => {
        setError("");
        for (const item of items) {
            if (!item.checked_off) continue;
            const valid_item = transformItemsIntoInventoryUsable(item)
            try {
                const response = await fetch("/api/inventory", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(valid_item),
                });
                if (response.ok) {
                    console.log("Posted:", item);
                } else {
                    const body = await response.json().catch(() => ({}));
                    setError(body.error || "Something went wrong");
                    return;
                }
            } catch (err) {
                const body = await response.json().catch(() => ({}));
                setError(body.error?.message || body.error || "Something went wrong");
                return;
            }
        }
    };

    const transformItemsIntoInventoryUsable = (item) => {
        // Potentially temporary function to make item data usable with 'validate_inventory_data (inventory.py)
        //Could be replaced if item.data is correctly formatted from API. Otherwise could be done with this function
        console.log(item.storage_location.location)
        return{
            "name" : item.data,
            "quantity" : item.quantity,
            "unit" : "temp",
            "storage_location" : item.storage_location.location,
            "category" : "dairy",
            "user_id" : "550e8400-e29b-41d4-a716-446655440000",
        }
    }

    const handleLocationChange = async (e, item_id) => {
        const newLocation = e.target.value;
        setItems(prev =>
            prev.map(it =>
                it.id === item_id
                    ? { ...it, storage_location: { ...it.storage_location, location: newLocation } }
                    : it
            )
        );
        
        try{
            const response = await fetch(`/api/items/${item_id}/storage-location`,{
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({location: newLocation})
            });

            if (!response.ok){
                const body = await response.json().catch(() => ({}));
                setError(body.error?.message || "Could not update location");
            }
        }catch(err){
            setError("Could not reach server")
        }
    }
    useEffect(() => {
        fetchItems()
            .then(setItems)
            .catch(() => setError("Could not load the list"));
    }, []);

    return (
        <>
            <label htmlFor="food_name">Enter a food to add:</label>

            <input
                type="text"
                id="food_name"
                name="food_name"
                placeholder="Enter your food"
                value={name}
                onChange={(e) => {
                    setName(e.target.value);
                    setSelectedFood(null);
                    setFoodMatches([]);
                }}
            />
            <button type="button" onClick={searchFoods}>
                Search USDA
            </button>

            <button name="submit_food" onClick={postFood}>Submit</button>

            {foodMatches.length > 0 && (
                <ul>
                    {foodMatches.map((food) => (
                        <li key={food.fdc_id}>
                            <button
                                type="button"
                                onClick={() => {
                                    setSelectedFood(food);
                                    setName(food.description);
                                    setFoodMatches([]);
                                }}
                            >
                                {food.description}
                                {food.brand ? ` — ${food.brand}` : ""}
                            </button>
                        </li>
                    ))}
                </ul>
            )}

            {error && <p>{error}</p>}

            <ul>
                {items.map((item) => ( 
                    <li key={item.id}>{item.name} x {item.quantity}
                        <button onClick = {() => updateListItemQuantity(item.id, "increment")}>+</button>
                        <button onClick = {() => updateListItemQuantity(item.id, "decrement")}>-</button>
                        <button onClick = {() => removeListItem(item.id)}>Del</button>
                        <input type = "checkbox" 
                            onChange = { () => toggleItemChecked(item.id)}
                            checked = {item.checked_off}>
                        </input>
                        <label htmlFor="storage-select">Storage Location:</label>
                        <select id={`storage-select-${item.id}`}
                        name="location"
                        value={item.storage_location?.location ?? "Refrigerator"}
                        onChange={(e) => handleLocationChange(e, item.id)}>
                            <option value="refrigerator">Refrigerator</option>
                            <option value="pantry">Pantry</option>
                            <option value="freezer">Freezer</option>
                        </select>
                    </li>
                ))}
            </ul>
            <button onClick = {() => pushItemsToInventory()}n>Complete List</button>
        </>
    );
}