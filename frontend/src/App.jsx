import { useState } from 'react'
import AppLayout from "./AppLayout.jsx";
import './App.css'
import { BrowserRouter, Routes, Route, Link, NavLink, useNavigate } from 'react-router-dom';
import Pantry from './Pantry.jsx';
import Recipes from './Recipes.jsx';
import Home from './Home.jsx';
import GroceryList from './GroceryList.jsx'
import Login from './pages/login.jsx';
import AuthCallback from "./pages/AuthCallback.jsx";

function App() {

 return (
  <BrowserRouter basename="/">
    <Routes>
      <Route path="/auth/callback" element={<AuthCallback />} />

      <Route element={<AppLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/pantry" element={<Pantry />} />
        <Route path="/recipes" element={<Recipes />} />
        <Route path="/grocerylist" element={<GroceryList />} />
        <Route path="/login" element={<Login />} />
      </Route>
    </Routes>
  </BrowserRouter>
);
}

export default App
