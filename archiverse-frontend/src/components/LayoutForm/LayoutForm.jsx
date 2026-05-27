import React, { useState } from 'react';
import { useProject } from '../../context/ProjectContext';
import { generateLayouts } from '../../services/api';
import './LayoutForm.css';

const additionalRoomOptions = [
  { id: 'Store', label: 'Store Room', icon: '📦' },
  { id: 'Backyard', label: 'Backyard', icon: '🌳' },
  { id: 'Dining', label: 'Dining Room', icon: '🍽️' },
  { id: 'Plants Space', label: 'Plants Space', icon: '🌿' },
];

const cityOptions = [
  'Bangalore', 'Hyderabad', 'Chennai', 'Mumbai', 'Delhi',
  'Pune', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Lucknow',
  'Kochi', 'Coimbatore', 'Visakhapatnam', 'Mysore', 'Mangalore',
];

export default function LayoutForm() {
  const { state, dispatch } = useProject();
  const { layoutForm, isGeneratingLayouts } = state;
  const [errors, setErrors] = useState({});

  const handleChange = (field, value) => {
    dispatch({ type: 'UPDATE_LAYOUT_FORM', payload: { [field]: value } });
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  const toggleAdditionalRoom = (room) => {
    const current = layoutForm.additionalRooms;
    const updated = current.includes(room)
      ? current.filter((r) => r !== room)
      : [...current, room];
    handleChange('additionalRooms', updated);
  };

  const validate = () => {
    const errs = {};
    const length = parseInt(layoutForm.plotLength);
    const width = parseInt(layoutForm.plotWidth);

    if (!layoutForm.plotLength || length < 10) {
      errs.plotLength = 'Min length is 10 ft';
    }
    if (length > 500) {
      errs.plotLength = 'Max length is 500 ft';
    }
    if (!layoutForm.plotWidth || width < 10) {
      errs.plotWidth = 'Min width is 10 ft';
    }
    if (width > 500) {
      errs.plotWidth = 'Max width is 500 ft';
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const computedArea = (() => {
    const l = parseInt(layoutForm.plotLength) || 0;
    const w = parseInt(layoutForm.plotWidth) || 0;
    return l * w;
  })();

  const formatBudget = (val) => {
    if (!val) return '';
    const num = parseInt(val);
    if (isNaN(num)) return '';
    if (num >= 10000000) return `₹${(num / 10000000).toFixed(2)} Cr`;
    if (num >= 100000) return `₹${(num / 100000).toFixed(2)} Lakh`;
    return `₹${num.toLocaleString('en-IN')}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    dispatch({ type: 'SET_GENERATING_LAYOUTS', payload: true });

    try {
      const result = await generateLayouts(layoutForm);
      dispatch({ type: 'SET_GENERATED_LAYOUTS', payload: result.layouts });

      // Auto-select first layout if available
      if (result.layouts && result.layouts.length > 0) {
        dispatch({ type: 'SELECT_LAYOUT', payload: result.layouts[0] });
      }
    } catch (err) {
      console.error('Layout generation failed:', err);
      dispatch({ type: 'SET_GENERATING_LAYOUTS', payload: false });
    }

    // Always go to Blueprint page — images are shown based on road facing
    dispatch({ type: 'SET_STEP', payload: 2 });
  };

  return (
    <div className="layout-form-container">
      <div className="step-header">
        <div className="step-header-icon">📐</div>
        <div>
          <h2>Design Your Layout</h2>
          <p>Tell us about your dream home and our AI will generate optimized floor plans.</p>
        </div>
      </div>

      <form className="layout-form" onSubmit={handleSubmit}>
        {/* Plot Size Section */}
        <div className="form-section">
          <h3 className="form-section-title">
            <span className="section-icon">📏</span>
            Plot Dimensions
          </h3>
          <div className="form-grid form-grid-2">
            <div className="form-group">
              <label className="form-label">Plot Length (ft)</label>
              <input
                type="number"
                className={`form-input ${errors.plotLength ? 'form-input-error' : ''}`}
                placeholder="e.g. 50"
                value={layoutForm.plotLength}
                onChange={(e) => handleChange('plotLength', e.target.value)}
                min="10"
                max="500"
                id="plot-length-input"
              />
              {errors.plotLength && (
                <span className="form-error">{errors.plotLength}</span>
              )}
            </div>

            <div className="form-group">
              <label className="form-label">Plot Width (ft)</label>
              <input
                type="number"
                className={`form-input ${errors.plotWidth ? 'form-input-error' : ''}`}
                placeholder="e.g. 40"
                value={layoutForm.plotWidth}
                onChange={(e) => handleChange('plotWidth', e.target.value)}
                min="10"
                max="500"
                id="plot-width-input"
              />
              {errors.plotWidth && (
                <span className="form-error">{errors.plotWidth}</span>
              )}
            </div>
          </div>
          {computedArea > 0 && (
            <div className="computed-area">
              <span className="area-label">Total Plot Area:</span>
              <span className="area-value">{computedArea.toLocaleString()} sq ft</span>
            </div>
          )}
        </div>

        {/* Budget & Project Configuration Section */}
        <div className="form-section budget-section">
          <h3 className="form-section-title">
            <span className="section-icon">💰</span>
            Budget & Project Configuration
          </h3>
          <div className="budget-input-wrapper">
            <div className="form-group budget-group">
              <label className="form-label">Total Budget (₹)</label>
              <div className="budget-field-container">
                <span className="budget-currency-prefix">₹</span>
                <input
                  type="number"
                  className="form-input budget-input"
                  placeholder="e.g. 5000000"
                  value={layoutForm.budget}
                  onChange={(e) => handleChange('budget', e.target.value)}
                  min="0"
                  id="budget-input"
                />
              </div>
              {layoutForm.budget && (
                <span className="budget-display">{formatBudget(layoutForm.budget)}</span>
              )}
              <span className="form-hint">Optional — helps AI optimize material and design choices</span>
            </div>
          </div>
          <div className="form-grid form-grid-3">
            <div className="form-group">
              <label className="form-label">City / Location</label>
              <select
                className="form-select"
                value={layoutForm.city || 'Bangalore'}
                onChange={(e) => handleChange('city', e.target.value)}
                id="city-select"
              >
                {cityOptions.map(city => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>
              <span className="form-hint">Used for local market rates in cost estimation</span>
            </div>

            <div className="form-group">
              <label className="form-label">Construction Quality</label>
              <select
                className="form-select"
                value={layoutForm.quality || 'standard'}
                onChange={(e) => handleChange('quality', e.target.value)}
                id="quality-select"
              >
                <option value="low">Economy</option>
                <option value="standard">Standard</option>
                <option value="premium">Premium</option>
              </select>
              <span className="form-hint">Affects material & finishing selections</span>
            </div>

            <div className="form-group">
              <label className="form-label">Number of Floors</label>
              <select
                className="form-select"
                value={layoutForm.floors || '1'}
                onChange={(e) => handleChange('floors', e.target.value)}
                id="floors-select"
              >
                <option value="1">1 Floor (Ground)</option>
                <option value="2">2 Floors (G+1)</option>
                <option value="3">3 Floors (G+2)</option>
                <option value="4">4 Floors (G+3)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Rooms Section */}
        <div className="form-section">
          <h3 className="form-section-title">
            <span className="section-icon">🏠</span>
            Rooms Configuration
          </h3>
          <div className="form-grid form-grid-2">
            {/* Bedrooms */}
            <div className="form-group">
              <label className="form-label">Number of Bedrooms</label>
              <select
                className="form-select"
                value={layoutForm.bedrooms}
                onChange={(e) => handleChange('bedrooms', e.target.value)}
                id="bedrooms-select"
              >
                <option value="1">1 Bedroom</option>
                <option value="2">2 Bedrooms</option>
                <option value="3">3 Bedrooms</option>
                <option value="4">4 Bedrooms</option>
                <option value="5">5 Bedrooms</option>
              </select>
            </div>

            {/* Road Facing */}
            <div className="form-group">
              <label className="form-label">Road Facing Direction</label>
              <select
                className="form-select"
                value={layoutForm.roadFacing || 'West'}
                onChange={(e) => handleChange('roadFacing', e.target.value)}
                id="road-facing-select"
              >
                <option value="West">🧭 West Facing</option>
                <option value="North">🧭 North Facing</option>
                <option value="East">🧭 East Facing</option>
                <option value="South">🧭 South Facing</option>
              </select>
              <span className="form-hint">Determines main gate & room orientation</span>
            </div>
          </div>
        </div>

        {/* Additional Rooms */}
        <div className="form-section">
          <h3 className="form-section-title">
            <span className="section-icon">✨</span>
            Additional Rooms
          </h3>
          <div className="additional-rooms-grid">
            {additionalRoomOptions.map((room) => (
              <button
                key={room.id}
                type="button"
                className={`room-chip ${
                  layoutForm.additionalRooms.includes(room.id) ? 'room-chip-active' : ''
                }`}
                onClick={() => toggleAdditionalRoom(room.id)}
              >
                <span className="chip-icon">{room.icon}</span>
                {room.label}
                {layoutForm.additionalRooms.includes(room.id) && (
                  <span className="chip-check">✓</span>
                )}
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-primary btn-lg generate-btn"
          disabled={isGeneratingLayouts}
          id="generate-layouts-btn"
        >
          {isGeneratingLayouts ? (
            <>
              <span className="loading-spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
              AI is Generating Blueprints...
            </>
          ) : (
            <>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 2L12.9 7.6L19 8.5L14.5 12.9L15.8 19L10 15.9L4.2 19L5.5 12.9L1 8.5L7.1 7.6L10 2Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
              </svg>
              Generate AI Blueprints
            </>
          )}
        </button>
      </form>
    </div>
  );
}
