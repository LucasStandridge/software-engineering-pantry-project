import { useEffect, useState } from 'react';
import './pantry.css';
import { supabase } from '../lib/supabase.js';

const storageAreas = [
  { name: 'Fridge', icon: '🧊' },
  { name: 'Freezer', icon: '❄️' },
  { name: 'Dry Pantry', icon: '🫙' },
];

export default function Pantry() {
  const [groceries, setGroceries] = useState([]);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newItem, setNewItem] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [unit, setUnit] = useState('each');
  const [storageLocation, setStorageLocation] = useState('Dry Pantry');
  const [category, setCategory] = useState('Other');
  const [userId, setUserId] = useState(null);
  useEffect(() => {
    async function loadUser() {
      const { data: { user }, error } = await supabase.auth.getUser();

      if (error) {
        console.error('Unable to load user:', error.message);
        return;
      }

      setUserId(user?.id ?? null);
    }

    loadUser();
  }, []);


  useEffect(() => {
    async function loadGroceries() {
      try {
        const response = await fetch('/api/inventory');
        if (!response.ok) {
          throw new Error('Failed to load inventory');
        }

        const data = await response.json();

        setGroceries(
          data.items.map((item) => ({
            name: item.name,
            quantity: item.quantity,
            expires: item.expiration_date || 'Not set',
            storage_location: item.storage_location,
            icon: '🛒',
          }))
        );
      } catch (err) {
        setError(err.message);
      }
    }

    loadGroceries();
  }, []);

  return (
    <div className="pantry-dashboard">
      <main className="pantry-main">
        <div className="pantry-heading">
          <h1>My Pantry.</h1>
          <button
            type="button"
            onClick={() => setShowAddForm(true)}
          >
            + Add to Pantry
          </button>
          {showAddForm && (
<form onSubmit={async (e) => {
  e.preventDefault();
  if (!userId) {
  setError('Please log in before adding items to your pantry.');
  return;
}

  try {
    const response = await fetch('/api/inventory', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: newItem.trim(),
        quantity,
        unit,
        storage_location: storageLocation,
        category,
        user_id: userId
      })
    });

    if (!response.ok) {
      throw new Error('Failed to save item');
    }

    const updated = await fetch('/api/items');

    if (!updated.ok) {
      throw new Error('Failed to refresh pantry');
    }

    const data = await updated.json();

    setGroceries(data.items.map((item) => ({
      name: item.name,
      quantity: item.quantity,
      expires: item.expiration_date || 'Not set',
      storage_location: item.storage_location,
      icon: '🛒'
    })));

    setNewItem('');
    setShowAddForm(false);
    setError('');
  } catch (err) {
    setError(err.message);
    alert(err.message);
  }
}}>              <input
                type="text"
                placeholder="Enter grocery name"
                value={newItem}
                onChange={(e) => setNewItem(e.target.value)}
              />
<label>
  Quantity
  <input
    type="number"
    min="1"
    step="1"
    value={quantity}
    onChange={(e) => setQuantity(Number(e.target.value))}
    required
  />
</label>

  <label>
  Unit
  <select
    value={unit}
    onChange={(e) => setUnit(e.target.value)}
  >
    <option value="each">Each</option>
    <option value="lbs">Pounds (lbs)</option>
    <option value="oz">Ounces (oz)</option>
    <option value="g">Grams (g)</option>
    <option value="kg">Kilograms (kg)</option>
    <option value="cups">Cups</option>
    <option value="bottles">Bottles</option>
    <option value="cans">Cans</option>
  </select>
</label>

  <label>
  Storage Location
  <select
    value={storageLocation}
    onChange={(e) => setStorageLocation(e.target.value)}
  >
    <option value="Fridge">Fridge</option>
    <option value="Freezer">Freezer</option>
    <option value="Dry Pantry">Dry Pantry</option>
  </select>
</label>

  <label>
  Category
  <select
    value={category}
    onChange={(e) => setCategory(e.target.value)}
  >
    <option value="Other">Other</option>
    <option value="Produce">Produce</option>
    <option value="Dairy">Dairy</option>
    <option value="Meat">Meat & Seafood</option>
    <option value="Grains">Grains & Bread</option>
    <option value="Frozen">Frozen Foods</option>
    <option value="Canned">Canned Goods</option>
    <option value="Beverages">Beverages</option>
    <option value="Snacks">Snacks</option>
    <option value="Condiments">Condiments</option>
  </select>
</label>
              <button type="submit">Save Item</button>

              <button
                type="button"
                onClick={() => setShowAddForm(false)}
              >
                Cancel
              </button>
            </form>
          )}
        </div>

        <div className="pantry-items">
          {groceries.map((item) => (
            <div className="pantry-item" key={item.name}>
              <span className="pantry-item-icon">{item.icon}</span>
              <h3>{item.name}</h3>
              <p>{item.quantity}</p>
              <small>Expires {item.expires}</small>
            </div>
          ))}
        </div>

        <h2>Expiring Soon</h2>
        <div className="expiring-list">
          {groceries
            .filter((item) => {
              if (!item.expires || item.expires === 'Not set') return false;

              const expiration = new Date(item.expires);
              if (Number.isNaN(expiration.getTime())) return false;

              const daysLeft = (expiration - new Date()) / 86400000;

              return daysLeft >= 0 && daysLeft <= 7;
            })
            .map((item) => (
            <div key={item.name}>
              <strong>{item.name}</strong>
              <span>{item.expires}</span>
            </div>
          ))}
        </div>
      </main>

      <aside className="pantry-sidebar">
        <h2>My Inventory</h2>
          {storageAreas.map((area) => (
          <div className="storage-item" key={area.name}>
            <span>{area.icon}</span>
            <div>
              <strong>{area.name}</strong>
              <p>
                {groceries.filter(
                  (item) => item.storage_location === area.name
                ).length} items
              </p>
            </div>
          </div>
        ))}
      </aside>
    </div>
  );
}
