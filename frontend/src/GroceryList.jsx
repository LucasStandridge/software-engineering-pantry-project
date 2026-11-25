import { useEffect, useState } from "react";
import { supabase } from "./lib/supabase.js";

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
    const [isTransferring, setIsTransferring] = useState(false);

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
        if (isTransferring) return;

        setError("");
        setIsTransferring(true);

        try {
            const { data: { user }, error: authError } =
                await supabase.auth.getUser();

            if (authError || !user) {
                setError("Please log in before completing your list.");
                return;
            }

            for (const item of items) {
                if (!item.checked_off) continue;

                const valid_item = transformItemsIntoInventoryUsable(
                    item, user.id
                );

                const response = await fetch("/api/inventory", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(valid_item),
                });

                if (!response.ok) {
                    const body = await response.json().catch(() => ({}));
                    setError(body.error?.message || "Could not save inventory item");
                    return;
                }

                const removed = await fetch(`/api/items/${item.id}/delete`, {
                    method: "DELETE",
                });

                if (!removed.ok) {
                    setError("Item saved to pantry but could not be removed from the grocery list.");
                    return;
                }
            }
        } catch {
            setError("Could not complete the grocery list.");
        } finally {
            try {
                setItems(await fetchItems());
            } catch {
                setError("Could not refresh the grocery list.");
            }

            setIsTransferring(false);
        }
    };

    const transformItemsIntoInventoryUsable = (item, userId) => {
        const location = item.storage_location?.location
            ?? item.storage_location
            ?? "refrigerator";

        const storageLocations = {
            refrigerator: "Fridge",
            freezer: "Freezer",
            pantry: "Dry Pantry",
        };

        return {
            name: item.name,
            quantity: item.quantity,
            unit: "each",
            storage_location:
                storageLocations[String(location).toLowerCase()] ?? "Fridge",
            category: item.data?.food_category || "Other",
            user_id: userId,
        };
    };

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
                            value={String(
                                item.storage_location?.location
                                ?? item.storage_location
                                ?? "refrigerator"
                            ).toLowerCase()}
                            onChange={(e) => handleLocationChange(e, item.id)}
                        >
                            <option value="refrigerator">Refrigerator</option>
                            <option value="pantry">Pantry</option>
                            <option value="freezer">Freezer</option>
                        </select>
                    </li>
                ))}
            </ul>
            <button
                onClick={pushItemsToInventory}
                disabled={isTransferring}
            >
                {isTransferring ? "Transferring..." : "Complete List"}
            </button>
        </>
    );
}