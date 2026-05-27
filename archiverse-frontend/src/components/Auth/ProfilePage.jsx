import React from 'react';
import { useAuth } from '../../context/AuthContext';
import './Auth.css';

export default function ProfilePage() {
  const { user, logout } = useAuth();

  if (!user) return null;

  const initial = (user.name || user.email || '?')[0].toUpperCase();

  return (
    <div className="profile-page">
      <div className="profile-card">
        <div className="profile-avatar">{initial}</div>
        <div className="profile-name">{user.name || 'ArchiVerse User'}</div>
        <div className="profile-email">{user.email}</div>

        <div className="profile-stats">
          <div className="profile-stat">
            <span className="profile-stat-value">0</span>
            <span className="profile-stat-label">Projects</span>
          </div>
          <div className="profile-stat">
            <span className="profile-stat-value">0</span>
            <span className="profile-stat-label">Layouts</span>
          </div>
          <div className="profile-stat">
            <span className="profile-stat-value">0</span>
            <span className="profile-stat-label">Saved</span>
          </div>
        </div>

        <div className="profile-actions">
          <button className="btn btn-secondary" onClick={logout}>
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
