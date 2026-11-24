
import { NavLink, Outlet } from "react-router-dom";
import "./AppLayout.css";

export default function AppLayout() {
  return (
    <div className="app-layout">
      <aside className="app-sidebar">
        <div className="app-brand">
          <span>🥗</span>
          <h2>Pantry Manager</h2>
        </div>

        <nav className="app-navigation">
          <NavLink to="/" end>🏠 Home</NavLink>
          <NavLink to="/pantry">📦 My Pantry</NavLink>
          <NavLink to="/grocerylist">🛒 Grocery Lists</NavLink>
          <NavLink to="/recipes">📖 My Recipes</NavLink>
          <NavLink to="/login">🔐 Login</NavLink>
        </nav>

        <div className="app-sidebar-footer">
          <p>Pantry Manager</p>
          <small>Software Engineering Project</small>
        </div>
      </aside>

      <div className="app-main">
        <header className="app-header">
          <div>
            <h1>Welcome to Pantry Manager</h1>
            <p>Plan smarter. Waste less. Eat better.</p>
          </div>
          <div className="app-avatar">👤</div>
        </header>

        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
