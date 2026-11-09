
import { supabase } from '../lib/supabase';
import './login.css';

export default function Login() {
  const loginWithGoogle = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin + '/login'
      }
    });

    if (error) {
      alert('Login failed: ' + error.message);
    }
  };

  return (
    <main className="login-page">
      <div className="floating-food food-one" aria-hidden="true">🥑</div>
      <div className="floating-food food-two" aria-hidden="true">🥕</div>
      <div className="floating-food food-three" aria-hidden="true">🍅</div>
      <div className="floating-food food-four" aria-hidden="true">🥬</div>

      <div className="login-layout">
        <section className="login-illustration">
          <div className="illustration-circle">
            <span className="grocery-bag" aria-hidden="true">🛍️</span>
          </div>
          <h2>Everything fresh, all in one place.</h2>
          <p>Track your groceries, plan smarter, and waste less.</p>
        </section>

        <section className="login-content">
          <div className="brand-icon" aria-hidden="true">🥑</div>
          <h1>Pantry Planner</h1>
          <p className="tagline">Less waste. More taste.</p>

          <div className="login-card">
            <h2>Welcome back!</h2>
            <p>
              Sign in to organize your pantry and
              keep track of your groceries.
            </p>

            <button
              type="button"
              className="google-button"
              onClick={loginWithGoogle}
            >
              Continue with Google
            </button>
          </div>
        </section>
      </div>
    </main>
  );
}
