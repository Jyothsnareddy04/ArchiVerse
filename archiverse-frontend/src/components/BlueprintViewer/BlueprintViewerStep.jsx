import React from 'react';
import { useProject } from '../../context/ProjectContext';
import './BlueprintViewer.css';

export default function BlueprintViewerStep() {
  const { state, dispatch } = useProject();
  const { layoutForm } = state;

  const plotSize = `${layoutForm.plotLength || '45'}' × ${layoutForm.plotWidth || '70'}'`;
  const facing = layoutForm.roadFacing || 'West';

  // Map facing to image paths
  const blueprintImages = {
    West: '/images/demo/blueprint_west.png',
    North: '/images/demo/blueprint_north.png',
    East: '/images/demo/blueprint_west.png',   // Fallback to West
    South: '/images/demo/blueprint_north.png',  // Fallback to North
  };

  const currentImage = blueprintImages[facing] || blueprintImages.West;

  return (
    <div className="blueprint-viewer-container">
      {/* Studio Header */}
      <div className="blueprint-studio-header">
        <div className="studio-brand">
          <span className="studio-icon">📋</span>
          <div>
            <h1>Blueprint Studio</h1>
            <p>AI-Generated Floor Plan • {plotSize} Plot • {facing} Facing</p>
          </div>
        </div>
      </div>

      {/* Facing Badge */}
      <div className="blueprint-facing-label">
        <span className="facing-badge">
          {facing === 'West' && '⬅️'}
          {facing === 'North' && '⬆️'}
          {facing === 'East' && '➡️'}
          {facing === 'South' && '⬇️'}
          {' '}{facing.toUpperCase()} Facing Layout
        </span>
      </div>

      {/* Main Canvas */}
      <div className="blueprint-canvas-wrapper">
        <div className="blueprint-image-container fade-in" key={facing}>
          <img
            src={currentImage}
            alt={`${facing} Facing Blueprint`}
            className="blueprint-final-img"
            onError={(e) => {
              e.target.style.display = 'none';
              const fallback = e.target.parentElement.querySelector('.blueprint-fallback');
              if (fallback) fallback.style.display = 'flex';
            }}
          />
          {/* Fallback if image missing */}
          <div className="blueprint-fallback" style={{ display: 'none' }}>
            <p>⚠️ Blueprint image not available for {facing} facing.</p>
            <p style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>
              Place your image at: /images/demo/blueprint_{facing.toLowerCase()}.png
            </p>
          </div>
        </div>
      </div>

      {/* Layout Info Summary */}
      <div className="blueprint-info-bar">
        <div className="info-item">
          <span className="info-icon">📐</span>
          <span className="info-text">{plotSize} Plot</span>
        </div>
        <div className="info-item">
          <span className="info-icon">🛏️</span>
          <span className="info-text">{layoutForm.bedrooms} Bedrooms</span>
        </div>
        <div className="info-item">
          <span className="info-icon">🧭</span>
          <span className="info-text">{facing} Facing</span>
        </div>
        <div className="info-item">
          <span className="info-icon">📦</span>
          <span className="info-text">{layoutForm.additionalRooms.length} Additional Rooms</span>
        </div>
        <div className="info-item">
          <span className="info-icon">🏗️</span>
          <span className="info-text">{layoutForm.floors} Floor(s)</span>
        </div>
      </div>

      {/* Footer Navigation */}
      <div className="studio-footer-nav">
        <button
          className="btn btn-secondary"
          onClick={() => dispatch({ type: 'SET_STEP', payload: 1 })}
        >
          ← Back to Layout Form
        </button>
        <button
          className="btn btn-primary btn-lg"
          onClick={() => dispatch({ type: 'SET_STEP', payload: 3 })}
          id="next-to-exterior-btn"
        >
          Continue to Exterior Design →
        </button>
      </div>
    </div>
  );
}
