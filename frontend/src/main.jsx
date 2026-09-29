import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App.jsx'
import ItemsPage from './pages/ItemsPage.jsx'
import AllPage from './pages/AllPage.jsx'
import ItemDetail from './pages/ItemDetail.jsx'
import HotTopicsPage from './pages/HotTopicsPage.jsx'
import DailyPage from './pages/DailyPage.jsx'
import LeaderboardPage from './pages/LeaderboardPage.jsx'
import FreshSnackPage from './pages/FreshSnackPage.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />}>
          <Route index element={<ItemsPage />} />
          <Route path="fresh" element={<FreshSnackPage />} />
          <Route path="all" element={<AllPage />} />
          <Route path="items/:id" element={<ItemDetail />} />
          <Route path="hot" element={<HotTopicsPage />} />
          <Route path="daily" element={<DailyPage />} />
          <Route path="leaderboard" element={<LeaderboardPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)