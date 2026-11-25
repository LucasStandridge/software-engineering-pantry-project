
import { Link } from "react-router-dom";
import "./home.css";

export default function Home() {
  const cards = [
    { title: "Pantry Items", icon: "📦", path: "/pantry" },
    { title: "Grocery Lists", icon: "🛒", path: "/grocerylist" },
    { title: "Expiring Soon", icon: "⏰", path: "/pantry" },
    { title: "Recipes", icon: "📖", path: "/recipes" },
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-heading">
        <h2>Your Dashboard</h2>
        <p>Everything happening in your kitchen, all in one place.</p>
      </div>

      <div className="dashboard-stats">
        {cards.map((card) => (
          <Link to={card.path} className="dashboard-stat" key={card.title}>
            <span className="dashboard-stat-icon">{card.icon}</span>
            <h3>{card.title}</h3>
            <span className="dashboard-stat-link">View details →</span>
          </Link>
        ))}
      </div>

      <section className="dashboard-section">
        <h3>Quick Actions</h3>
        <div className="dashboard-actions">
          <Link to="/pantry" className="dashboard-action">
            + Add Pantry Item
          </Link>
          <Link to="/grocerylist" className="dashboard-action">
            + Create Grocery List
          </Link>
        </div>
      </section>

      <div className="dashboard-panels">
        <section className="dashboard-section">
          <h3>🛒 Your Grocery Lists</h3>
          <p>Your saved grocery lists will appear here.</p>
          <Link to="/grocerylist">View Grocery Lists →</Link>
        </section>

        <section className="dashboard-section">
          <h3>⏰ Expiring Soon</h3>
          <p>Keep track of food before it goes to waste.</p>
          <Link to="/pantry">View Pantry →</Link>
        </section>
      </div>
    </div>
  );
}
