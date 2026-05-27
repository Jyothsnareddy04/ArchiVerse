import React from 'react';
import { useProject } from '../../context/ProjectContext';
import { categoryLabels } from '../../data/interiorData';
import './FinalOverview.css';

export default function FinalOverview() {
  const { state, dispatch } = useProject();
  const { selectedExterior, interiorSelections, layoutForm } = state;

  const totalSelections = Object.values(interiorSelections).reduce((sum, roomSel) => sum + Object.keys(roomSel).length, 0);

  // Count exterior items (1 selected exterior style)
  const exteriorItemCount = selectedExterior ? 1 : 0;

  // Count interior items (furniture pieces)
  const interiorItemCount = totalSelections;

  return (
    <div className="final-overview-container">
      <div className="step-header">
        <div className="step-header-icon">👁️</div>
        <div>
          <h2>Final Project Overview</h2>
          <p>Review your complete AI-generated house design before proceeding to cost estimation.</p>
        </div>
      </div>

      <div className="overview-grid">
        {/* Layout Summary */}
        <div className="overview-card">
          <div className="overview-card-header">
            <span className="overview-card-icon">📐</span>
            <h3>Plot & Layout</h3>
            <span className="badge badge-success">Completed</span>
          </div>
          <div className="overview-card-body">
            <h4>{layoutForm.plotLength}' × {layoutForm.plotWidth}' Plot</h4>
            <p>{layoutForm.bedrooms} Bedrooms • {layoutForm.floors} Floor(s)</p>
            <div className="overview-specs">
              <div className="overview-spec">
                <span className="spec-value">{(parseInt(layoutForm.plotLength) || 0) * (parseInt(layoutForm.plotWidth) || 0)}</span>
                <span className="spec-label">sq ft</span>
              </div>
              <div className="overview-spec">
                <span className="spec-value">{layoutForm.bedrooms}</span>
                <span className="spec-label">Bedrooms</span>
              </div>
              <div className="overview-spec">
                <span className="spec-value">{layoutForm.additionalRooms.length}</span>
                <span className="spec-label">Extra Rooms</span>
              </div>
            </div>
          </div>
        </div>

        {/* Blueprint Summary */}
        <div className="overview-card">
          <div className="overview-card-header">
            <span className="overview-card-icon">📋</span>
            <h3>Architectural Blueprint</h3>
            <span className="badge badge-success">Generated</span>
          </div>
          <div className="overview-card-body">
            <p>West-facing and North-facing blueprints generated for your {layoutForm.plotLength}' × {layoutForm.plotWidth}' plot.</p>
            <div className="overview-blueprint-tags">
              <span className="blueprint-tag">🧭 West Facing</span>
              <span className="blueprint-tag">🧭 North Facing</span>
            </div>
          </div>
        </div>

        {/* Exterior Summary */}
        <div className="overview-card">
          <div className="overview-card-header">
            <span className="overview-card-icon">🎨</span>
            <h3>Exterior Design</h3>
            <span className="badge badge-success">Applied</span>
          </div>
          <div className="overview-card-body">
            <h4>{selectedExterior?.name}</h4>
            <p>{selectedExterior?.description}</p>
            <div className="overview-palette">
              {selectedExterior?.colors.map((color, i) => (
                <div
                  key={i}
                  className="overview-color-block"
                  style={{ backgroundColor: color }}
                >
                  <span className="overview-hex">{color}</span>
                </div>
              ))}
            </div>
            <div className="overview-count-badge">
              <span>Exterior Style: 1 selected</span>
            </div>
          </div>
        </div>

        {/* Interior Summary */}
        <div className="overview-card overview-card-wide">
          <div className="overview-card-header">
            <span className="overview-card-icon">🛋️</span>
            <h3>Interior Selections</h3>
            <span className="badge badge-success">
              {totalSelections} Items Selected
            </span>
          </div>
          <div className="overview-card-body">
            <div className="overview-interior-grid">
              {Object.keys(interiorSelections).map(roomName => {
                const roomSels = interiorSelections[roomName];
                if (!roomSels || Object.keys(roomSels).length === 0) return null;
                
                return (
                  <div key={roomName} className="overview-room-group">
                    <h5 className="overview-room-title">{roomName}</h5>
                    <div className="overview-room-items">
                      {Object.keys(roomSels).map((catId) => {
                        const selectionId = roomSels[catId];
                        return (
                          <div key={catId} className="overview-interior-item">
                            <span className="interior-item-label">{categoryLabels[catId]}</span>
                            <span className="interior-item-value">
                              {selectionId.replace(/^[a-z]+-/, '').replace(/-/g, ' ')}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Cost Estimation Preview */}
        <div className="overview-card overview-card-wide overview-card-highlight">
          <div className="overview-card-header">
            <span className="overview-card-icon">💰</span>
            <h3>Items for Cost Estimation</h3>
          </div>
          <div className="overview-card-body">
            <div className="cost-preview-grid">
              <div className="cost-preview-item">
                <span className="cost-preview-label">Exterior Items</span>
                <span className="cost-preview-count">{exteriorItemCount}</span>
                <span className="cost-preview-desc">Style applied to facade</span>
              </div>
              <div className="cost-preview-item">
                <span className="cost-preview-label">Interior Furniture</span>
                <span className="cost-preview-count">{interiorItemCount}</span>
                <span className="cost-preview-desc">Items across all rooms</span>
              </div>
              <div className="cost-preview-item">
                <span className="cost-preview-label">Total Items</span>
                <span className="cost-preview-count cost-preview-total">{exteriorItemCount + interiorItemCount}</span>
                <span className="cost-preview-desc">Contributing to cost</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="wizard-nav">
        <button
          className="btn btn-secondary"
          onClick={() => dispatch({ type: 'SET_STEP', payload: 4 })}
        >
          ← Back to Interior
        </button>
        <button
          className="btn btn-primary btn-lg"
          onClick={() => dispatch({ type: 'SET_STEP', payload: 6 })}
          id="next-to-estimation-btn"
        >
          💰 Get Cost Estimation
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M4 10h12M12 6l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      </div>
    </div>
  );
}
