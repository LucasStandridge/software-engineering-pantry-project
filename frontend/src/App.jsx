import { useState } from 'react'
import './App.css'
import { BrowserRouter, Routes, Route, Link, NavLink, useNavigate } from 'react-router-dom';
import Pantry from './Pantry.jsx';
import Recipes from './Recipes.jsx';
import Home from './Home.jsx';
import GroceryList from './GroceryList.jsx'
import Login from './pages/login.jsx';

function App() {

  return (
    <>
      <BrowserRouter basename = '/'>
        <nav className='navBar'>
          <NavLink className = 'navLink' to='/'>Home</NavLink>
          <NavLink className = 'navLink' to='/pantry'>My Pantry</NavLink>
          <NavLink className = 'navLink' to='/recipes'>My Recipes</NavLink>
          <NavLink className = 'navLink' to='/grocerylist'>My Grocery Lists</NavLink>
        </nav>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path='/pantry' element={<Pantry/>}></Route>
          <Route path='/recipes' element={<Recipes/>}></Route>
          <Route path='/grocerylist' element={<GroceryList/>}></Route>
          <Route path="/login" element={<Login />} />
        </Routes>
      </BrowserRouter> 
    </>
  )
}

export default App
