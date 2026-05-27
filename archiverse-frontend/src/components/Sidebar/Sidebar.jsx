import React from 'react';
import { useProject } from '../../context/ProjectContext';
import { useAuth } from '../../context/AuthContext';
import './Sidebar.css';

const navItems = [
  { icon: '🏠', label: 'Home', step: 0 },
  { icon: '📐', label: 'Layout', step: 1 },
  { icon: '📋', label: 'Blueprint', step: 2 },
  { icon: '🎨', label: 'Exterior', step: 3 },
  { icon: '🛋️', label: 'Interior', step: 4 },
  { icon: '👁️', label: 'Overview', step: 5 },
  { icon: '💰', label: 'Estimation', step: 6 },
];

export default function Sidebar() {
  const { state, dispatch } = useProject();
  const { user, logout } = useAuth();
  const { currentStep, projectStarted } = state;

  const handleNavClick = (step) => {
    if (step === 0) {
      dispatch({ type: 'SET_STEP', payload: 0 });
    } else if (projectStarted && step <= getMaxAllowedStep(state)) {
      dispatch({ type: 'SET_STEP', payload: step });
    }
  };

  return (
    <aside className="app-sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-logo">A</div>
        <div className="sidebar-brand-text">
          <h2>ArchiVerse</h2>
          <span>AI Design Studio</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const isActive = currentStep === item.step;
          const isCompleted = projectStarted && item.step < currentStep && item.step > 0;
          const isDisabled = !projectStarted && item.step > 0;
          const isAllowed = item.step === 0 || (projectStarted && item.step <= getMaxAllowedStep(state));

          return (
            <button
              key={item.step}
              className={`sidebar-nav-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''} ${isDisabled ? 'disabled' : ''}`}
              onClick={() => handleNavClick(item.step)}
              disabled={!isAllowed}
              title={!isAllowed ? 'Complete previous steps first' : ''}
            >
              <span className="nav-icon">{isCompleted ? '✓' : item.icon}</span>
              <span>{item.label}</span>
              {isCompleted && <span className="nav-badge">Done</span>}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div
          className="sidebar-user"
          onClick={() => dispatch({ type: 'SET_STEP', payload: -1 })}
          style={{ cursor: 'pointer' }}
          title="View Profile"
        >
          <div className="sidebar-user-avatar">
            {(user?.name || user?.email || 'U')[0].toUpperCase()}
          </div>
          <div className="sidebar-user-info">
            <div className="name">{user?.name || 'User'}</div>
            <div className="role">{user?.email || 'Free Plan'}</div>
          </div>
        </div>
        <button
          className="sidebar-logout-btn"
          onClick={logout}
          title="Sign Out"
        >
          ⏻
        </button>
      </div>
    </aside>
  );
}

function getMaxAllowedStep(state) {
  if (state.costEstimation) return 6;
  if (state.interiorSelections && Object.keys(state.interiorSelections).length >= 5) return 6;
  if (state.selectedExterior) return 5;
  if (state.blueprintReady || state.selectedLayout || state.currentStep >= 2) return 3;
  if (state.projectStarted) return 2;
  return 0;
}
