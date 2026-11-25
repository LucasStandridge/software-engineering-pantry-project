
import { NavLink, Outlet } from "react-router-dom";
import "./AppLayout.css";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "./lib/supabase";

export default function AppLayout() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user);
    });

    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, session) => setUser(session?.user ?? null)
    );

    return () => listener.subscription.unsubscribe();
  }, []);

  async function handleSignOut() {
    const { error } = await supabase.auth.signOut();

    if (error) {
      alert(error.message);
      return;
    }

    navigate("/login", { replace: true });
  }
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
         {user && (
      <div className="app-user-profile">
        <img
          src={user.user_metadata?.avatar_url || user.user_metadata?.picture}
          alt="Profile"
          className="app-profile-picture"
          referrerPolicy="no-referrer"
        />
        <span>{user.user_metadata?.full_name || user.email}</span>
        <button type="button" onClick={handleSignOut}>
          Sign Out
        </button>
      </div>
    )}
        </header>

        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
