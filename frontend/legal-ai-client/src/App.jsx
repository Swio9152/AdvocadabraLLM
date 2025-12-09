import React from "react";
import { Routes, Route, useLocation, Link } from "react-router-dom";
import { AuthProvider, Login, Signup, ProtectedRoute } from "./Auth.jsx";
import Landing from "./routes/Landing.jsx";
import Dashboard from "./routes/Dashboard.jsx";
import Team from "./routes/Team.jsx";

// Simple Navbar Component (embedded)
function Navbar() {
  return (
    <header className="sticky top-0 z-40 backdrop-blur-xl bg-white/80 border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 md:px-6 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center hover:opacity-80 transition-opacity">
          <img 
            src="/assets/advoca-dabra.jpeg" 
            alt="AdvocaDabra" 
            className="h-8 w-auto"
          />
        </Link>
        <nav className="hidden md:flex items-center gap-8 text-[14px] text-gray-600">
          <Link to="/team" className="hover:text-gray-900">Team</Link>
          <Link to="/login" className="hover:text-gray-900">Login</Link>
          <Link to="/signup" className="hover:text-gray-900">Signup</Link>
        </nav>
      </div>
    </header>
  );
}

function AppContent() {
  const location = useLocation();
  // Hide navbar on dashboard (authenticated pages)
  const showNavbar = location.pathname !== '/dashboard';

  return (
    <div className="min-h-screen bg-white text-gray-900">
      {showNavbar && <Navbar />}
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/team" element={<Team />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* 🔒 Protect Dashboard */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
