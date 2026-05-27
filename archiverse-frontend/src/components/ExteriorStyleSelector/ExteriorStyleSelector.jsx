import React from 'react';
import { useProject } from '../../context/ProjectContext';
import './ExteriorStyleSelector.css';

const exteriorStyles = [
  {
    id: 'grey-navy',
    name: 'Urban Sophisticate',
    description: 'Soft greys paired with navy blue',
    colors: ['#B0B3B8', '#C8CACD', '#1B2A4A', '#2C3E6B'],
    primary: '#B0B3B8',
    secondary: '#1B2A4A',
  },
  {
    id: 'grey-white',
    name: 'Minimalist Elegance',
    description: 'Soft greys paired with white',
    colors: ['#A8AAAE', '#C5C7CB', '#F5F5F5', '#FFFFFF'],
    primary: '#A8AAAE',
    secondary: '#F5F5F5',
  },
  {
    id: 'sage-beige',
    name: 'Organic Retreat',
    description: 'Sage green complemented by warm beige',
    colors: ['#87A878', '#A3BE8C', '#D4B896', '#E8D5B7'],
    primary: '#87A878',
    secondary: '#D4B896',
  },
  {
    id: 'charcoal-blush',
    name: 'Bold Contemporary',
    description: 'Deep charcoal accented with light blush tones',
    colors: ['#2D2D2D', '#404040', '#F4C2C2', '#F9E4E4'],
    primary: '#2D2D2D',
    secondary: '#F4C2C2',
  },
  {
    id: 'stone-wood',
    name: 'Rustic Modern',
    description: 'Light stone textures combined with dark wood',
    colors: ['#D4C5A9', '#E8DCC8', '#5C3A21', '#8B6914'],
    primary: '#D4C5A9',
    secondary: '#5C3A21',
  },
  {
    id: 'coastal-breeze',
    name: 'Coastal Breeze',
    description: 'Sky blue tones paired with sandy beige',
    colors: ['#7EC8E3', '#B5E2F4', '#E8D5B0', '#F5E6CC'],
    primary: '#7EC8E3',
    secondary: '#E8D5B0',
  },
  {
    id: 'mediterranean',
    name: 'Mediterranean Sun',
    description: 'Warm terracotta with olive green accents',
    colors: ['#C67B4B', '#D4956A', '#6B7F3B', '#8A9F5A'],
    primary: '#C67B4B',
    secondary: '#6B7F3B',
  },
  {
    id: 'nordic-frost',
    name: 'Nordic Frost',
    description: 'Ice blue and cool slate grey tones',
    colors: ['#C8D8E4', '#A4BFD2', '#5B6E7A', '#47596B'],
    primary: '#C8D8E4',
    secondary: '#5B6E7A',
  },
  {
    id: 'desert-dusk',
    name: 'Desert Palette',
    description: 'Warm amber and burnt clay hues',
    colors: ['#D4A76A', '#E8C088', '#9B5E3C', '#7A4528'],
    primary: '#D4A76A',
    secondary: '#9B5E3C',
  },
  {
    id: 'industrial-chic',
    name: 'Industrial Chic',
    description: 'Gunmetal grey with raw concrete tones',
    colors: ['#4A4E54', '#6B7078', '#B0B0A8', '#D0D0C8'],
    primary: '#4A4E54',
    secondary: '#B0B0A8',
  },
];

export default function ExteriorStyleSelector() {
  const { state, dispatch } = useProject();
  const { selectedExterior } = state;

  const handleSelect = (style) => {
    dispatch({ type: 'SELECT_EXTERIOR', payload: style });
  };

  return (
    <div className="exterior-selector-container">
      <div className="step-header">
        <div className="step-header-icon">🎨</div>
        <div>
          <h2>Exterior Design Style</h2>
          <p>Choose a color palette for your home's exterior. Each style combines two complementary tones.</p>
        </div>
      </div>

      <div className="exterior-cards-grid">
        {exteriorStyles.map((style, index) => (
          <div
            key={style.id}
            className={`exterior-card card card-interactive ${
              selectedExterior?.id === style.id ? 'card-selected' : ''
            }`}
            onClick={() => handleSelect(style)}
            style={{ animationDelay: `${index * 0.1}s` }}
            id={`exterior-card-${style.id}`}
          >
            {/* Color Palette Swatch */}
            <div className="color-palette-preview">
              <div className="palette-swatch-row">
                {style.colors.map((color, ci) => (
                  <div
                    key={ci}
                    className="palette-swatch"
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
              <div className="palette-duo">
                <div
                  className="palette-duo-half"
                  style={{ backgroundColor: style.primary }}
                />
                <div
                  className="palette-duo-half"
                  style={{ backgroundColor: style.secondary }}
                />
              </div>
            </div>

            <div className="exterior-card-body">
              <h4>{style.name}</h4>
              <p>{style.description}</p>

              {/* Color dots */}
              <div className="color-dots-row">
                {style.colors.map((color, ci) => (
                  <span
                    key={ci}
                    className="color-dot"
                    style={{ backgroundColor: color }}
                    title={color}
                  />
                ))}
              </div>
            </div>

            {selectedExterior?.id === style.id && (
              <div className="exterior-selected-badge">✓ Selected</div>
            )}
          </div>
        ))}
      </div>

      {/* Selected Preview with AI Render fallback */}
      {selectedExterior && (
        <div className="selected-exterior-preview-container" style={{ animation: 'fadeInUp 0.4s ease-out' }}>
          {state.selectedLayout?.demoImages?.exterior && (
            <div className="ai-render-preview">
              <span className="demo-badge">AI Exterior Visualization</span>
              <img src={state.selectedLayout.demoImages.exterior} alt="AI Exterior" className="exterior-demo-img" />
              <p className="image-caption">Realistic rendering based on selected layout and style</p>
            </div>
          )}
          
          <div className="selected-exterior-preview">
            <div className="preview-label">Selected Color Palette</div>
            <div className="preview-bar">
              <div className="preview-color-strip">
                {selectedExterior.colors.map((color, i) => (
                  <div
                    key={i}
                    className="preview-color-block"
                    style={{ backgroundColor: color }}
                  >
                    <span className="color-hex">{color}</span>
                  </div>
                ))}
              </div>
              <div className="preview-info">
                <h4>{selectedExterior.name}</h4>
                <p>{selectedExterior.description}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedExterior && (
        <div className="wizard-nav" style={{ animation: 'fadeInUp 0.4s ease-out' }}>
          <button
            className="btn btn-secondary"
            onClick={() => dispatch({ type: 'SET_STEP', payload: 2 })}
          >
            ← Back
          </button>
          <button
            className="btn btn-primary btn-lg"
            onClick={() => dispatch({ type: 'SET_STEP', payload: 4 })}
            id="next-to-interior-btn"
          >
            Continue to Interior Design
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 10h12M12 6l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}
