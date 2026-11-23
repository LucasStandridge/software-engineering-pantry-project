import { useEffect, useState } from 'react';
import './Pantry.css';

const storage = [
  { name: 'Fridge', count: 12, icon: '🧊' },
  { name: 'Freezer', count: 8, icon: '❄️' },
  { name: 'Dry Pantry', count: 24, icon: '🫙' },
];

export default function Pantry() {
  const [groceries, setGroceries] = useState([]);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newItem, setNewItem] = useState('');
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    async function loadGroceries() {
      try {
        const response = await fetch('/api/items');

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

  try {
    const response = await fetch('/api/items', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name: newItem.trim() })
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
        {storage.map((area) => (
          <div className="storage-item" key={area.name}>
            <span>{area.icon}</span>
            <div>
              <strong>{area.name}</strong>
              <p>{area.count} items</p>
            </div>
          </div>
        ))}
      </aside>
    </div>
  );
}
