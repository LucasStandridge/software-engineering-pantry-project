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

    // TODO: disable the button while a request is in flight. Two quick clicks
    // send two POSTs, and the second one bumps the quantity.
    const postFood = async () => {
        setError("");
        try {
            const response = await fetch("/api/items", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name }),
            });

            if (!response.ok) {
                const body = await response.json().catch(() => ({}));
                setError(body.error || "Something went wrong");
                return;
            }

            setName("");
            setItems(await fetchItems());
        } catch (err) {
            setError("Could not reach the server");
        }
    };

    const handleClick = () => {
        alert("Button was clicked")
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
                onChange={(e) => setName(e.target.value)}
            />
            <button name="submit_food" onClick={postFood}>Submit</button>

            {error && <p>{error}</p>}

            <ul>
                {items.map((item) => ( 
                    <li key={item.id}>{item.name} x {item.quantity}
                    {/* <button onClick = {handleClick}></button> */}
                        <button onClick = {() => updateListItemQuantity(item.id, "increment")}>+</button>
                        <button onClick = {() => updateListItemQuantity(item.id, "decrement")}>-</button>
                        <button onClick = {() => removeListItem(item.id)}>Del</button>
                    </li>
                ))}
            </ul>
        </>
    );
}