import React from 'react';
import { useProject } from '../../context/ProjectContext';
import './HomePage.css';

export default function HomePage() {
  const { dispatch } = useProject();

  return (
    <div className="home-page">
      <div className="home-bg-glow" />
      <div className="home-bg-glow-2" />

      <div className="home-content">
        <div className="home-hero">
          <span className="home-badge">
            <span className="badge-dot" />
            AI-Powered Design Platform
          </span>
          <h1 className="home-title">
            Design Your Dream Home
            <br />
            <span className="gradient-text">With Artificial Intelligence</span>
          </h1>
          <p className="home-subtitle">
            From layout planning to cost estimation — our AI guides you through
            every step of creating your perfect house design.
          </p>
        </div>

        <div className="home-cards-grid">
          {/* Main CTA Card */}
          <div
            className="create-project-card"
            onClick={() => dispatch({ type: 'START_PROJECT' })}
            id="create-project-card"
          >
            <div className="create-card-glow" />
            <div className="create-card-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect x="6" y="6" width="36" height="36" rx="4" stroke="currentColor" strokeWidth="2.5" strokeDasharray="6 3" />
                <line x1="24" y1="16" x2="24" y2="32" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                <line x1="16" y1="24" x2="32" y2="24" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
              </svg>
            </div>
            <h2 className="create-card-title">Create Your Own Project</h2>
            <p className="create-card-desc">
              Start a new house design project with AI-powered layout generation,
              blueprint creation, and complete customization.
            </p>
            <div className="create-card-cta">
              <span>Start Designing</span>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M4 10h12M12 6l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
          </div>

          {/* Feature cards */}
          <div className="feature-cards-row">
            <div className="feature-card">
              <div className="feature-icon">📐</div>
              <h3>AI Layout Generator</h3>
              <p>Generate optimized floor plans based on your requirements</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🏗️</div>
              <h3>3D Visualization</h3>
              <p>View your design in immersive 3D with realistic rendering</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎨</div>
              <h3>Style Customization</h3>
              <p>Choose exterior and interior styles from curated collections</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">💰</div>
              <h3>Cost Estimation</h3>
              <p>Get detailed cost breakdowns for your entire project</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
