import React from 'react';
import { useProject } from '../../context/ProjectContext';
import './LayoutSelector.css';

export default function LayoutSelector() {
  const { state, dispatch } = useProject();
  const { generatedLayouts, selectedLayout } = state;

  const handleSelect = (layout) => {
    dispatch({ type: 'SELECT_LAYOUT', payload: layout });
  };

  if (generatedLayouts.length === 0) return null;

  return (
    <div className="layout-selector-container">
      <div className="selector-header">
        <span className="badge badge-success">AI Generated</span>
        <h3>Choose Your Layout</h3>
        <p>Our AI generated 3 optimized floor plans based on your requirements. Select the one you prefer.</p>
      </div>

      <div className="layouts-grid">
        {generatedLayouts.map((layout, index) => {
          // Hardcoded presentation mode: Dynamically load variant 1, 2, and 3
          const fallbackImage = `/images/demo/layout_variant_${index + 1}.png`;
          
          return (
            <div
              key={layout.id}
              className={`layout-card card card-interactive ${
                selectedLayout?.id === layout.id ? 'card-selected' : ''
              }`}
              onClick={() => handleSelect(layout)}
              style={{ animationDelay: `${index * 0.15}s` }}
              id={`layout-card-${layout.id}`}
            >
              {/* Variant Preview Image Area */}
              <div className="layout-preview">
                <img 
                  src={fallbackImage} 
                  alt={`Variant ${index + 1}`} 
                  className="layout-variant-img" 
                  onError={(e) => {
                    // Fail nicely by reverting to a CSS generated blueprint if file cannot be loaded
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
                
                {/* Fallback component if image loading fails */}
                <div style={{ display: 'none', width: '100%', height: '100%' }}>
                  <MiniBlueprint rooms={layout.rooms} />
                </div>
              </div>

              <div className="layout-card-body">
                <div className="layout-card-header">
                  <h4>{layout.name}</h4>
                  <span className="layout-option-badge">Option {index + 1}</span>
                </div>
                <p className="layout-desc">{layout.description}</p>
                <div className="layout-specs">
                  <span className="spec-item"><span className="spec-icon">📐</span> {layout.area || 2500} sq ft</span>
                  <span className="spec-item"><span className="spec-icon">🛏️</span> {layout.bedrooms || 2} Beds</span>
                  <span className="spec-item"><span className="spec-icon">🛁</span> {layout.bathrooms || 2} Baths</span>
                </div>
                {layout.features && (
                  <div className="layout-features">
                    {layout.features.map((feature, i) => (
                      <span key={i} className="feature-tag">{feature}</span>
                    ))}
                  </div>
                )}
              </div>

              {selectedLayout?.id === layout.id && (
                <div className="selected-overlay">
                  <span className="selected-badge">✓ Selected</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {selectedLayout && (
        <div className="wizard-nav" style={{ animation: 'fadeInUp 0.4s ease-out' }}>
          <button
            className="btn btn-primary btn-lg"
            onClick={() => dispatch({ type: 'SET_STEP', payload: 3 })}
            id="next-to-blueprint-btn"
          >
            Generate Final Blueprint & 3D
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 10h12M12 6l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}

/* Mini blueprint preview using SVG (Fallback only) */
function MiniBlueprint({ rooms }) {
  if (!rooms || rooms.length === 0) return null;

  let maxX = 0, maxY = 0;
  rooms.forEach((r) => {
    maxX = Math.max(maxX, r.x + (r.width || r.w || 0));
    maxY = Math.max(maxY, r.y + (r.height || r.h || 0));
  });

  const padding = 5;
  const viewWidth = maxX + padding * 2;
  const viewHeight = maxY + padding * 2;

  const getRoomColor = (name = '') => {
    const n = name.toLowerCase();
    if (n.includes('living') || n.includes('hall')) return '#FDF5E6';
    if (n.includes('bedroom') || n.includes('suite') || n.includes('kitchen')) return '#FFF9C4';
    if (n.includes('entry') || n.includes('foyer')) return '#F8BBD0';
    if (n.includes('bath')) return '#B3E5FC';
    if (n.includes('balcony') || n.includes('terrace')) return '#DCEDC8';
    return '#FFFFFF';
  };

  return (
    <svg viewBox={`0 0 ${viewWidth} ${viewHeight}`} className="mini-blueprint-svg">
      <defs>
        <pattern id="stairHatch" patternUnits="userSpaceOnUse" width="4" height="4">
          <path d="M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2" stroke="#333" strokeWidth="0.5" />
        </pattern>
      </defs>

      {rooms.map((room, i) => {
        const isStair = room.name?.toLowerCase().includes('stair');
        const fragments = room.rects && room.rects.length > 0 ? room.rects : [{
          x: room.x, 
          y: room.y, 
          width: room.width || room.w, 
          height: room.height || room.h
        }];

        return (
          <g key={room.id || i}>
            {fragments.map((rect, rectIdx) => (rect.x !== null) && (
              <rect
                key={`${room.id}-${rectIdx}`}
                x={rect.x}
                y={rect.y}
                width={rect.width || rect.w}
                height={rect.height || rect.h}
                fill={isStair ? 'url(#stairHatch)' : getRoomColor(room.name)}
                stroke="#000"
                strokeWidth="0.8"
              />
            ))}
            
            {/* Label with white padding background */}
            <g transform={`translate(${room.x + (room.width || room.w) / 2}, ${room.y + (room.height || room.h) / 2})`}>
              <rect
                x="-6"
                y="-3"
                width="12"
                height="6"
                fill="rgba(255,255,255,0.9)"
                rx="0.5"
              />
              <text
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="2.5"
                fontWeight="bold"
                fill="#000"
                style={{ pointerEvents: 'none', textTransform: 'uppercase' }}
              >
                {room.name?.split('_')[0]}
              </text>
            </g>
          </g>
        );
      })}
    </svg>
  );
}
