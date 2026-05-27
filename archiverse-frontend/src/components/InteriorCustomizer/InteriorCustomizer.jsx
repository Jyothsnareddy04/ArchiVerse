import React, { useState, useMemo, useRef } from 'react';
import { useProject } from '../../context/ProjectContext';
import { getRoomType, getCategoriesForRoom } from '../../data/interiorData';
import ItemSVGIcon from './ItemSVGIcon';
import './InteriorCustomizer.css';

function OptionThumbnail({ option }) {
  if (option.image) {
    return (
      <div className="option-image-wrapper">
        <img src={option.image} alt={option.name} className="option-image" />
      </div>
    );
  }
  if (option.tileColors) {
    return (
      <div className="option-tile-preview">
        <div className="tile-pattern">
          {option.tileColors.map((color, i) => (
            <React.Fragment key={i}>
              <div className="tile-cell" style={{ backgroundColor: color }} />
              <div className="tile-cell" style={{ backgroundColor: option.tileColors[(i + 1) % option.tileColors.length] }} />
            </React.Fragment>
          ))}
        </div>
      </div>
    );
  }
  return (
    <div className="option-svg-icon">
      <ItemSVGIcon type={option.svgIcon || option.id} />
    </div>
  );
}

// Room icon helper
function getRoomIcon(roomType) {
  const icons = {
    living: '🛋️', bedroom: '🛏️', kitchen: '🍳',
    bathroom: '🚿', balcony: '🌿', store: '📦',
  };
  return icons[roomType] || '🏠';
}

// Furniture emoji mapping
function getFurnitureEmoji(categoryId) {
  const map = {
    sofa: '🛋️', beds: '🛏️', 'tv-stand': '📺', curtains: '🪟',
    'false-ceiling': '💡', lights: '💡', chandeliers: '🏮',
    bookshelves: '📚', lamps: '🪔', cupboards: '👔',
    'dressing-table': '💄', mirrors: '🪞', 'dining-table': '🍽️',
    'kitchen-cupboards': '🍳', 'floor-tiles': '🔲', 'bathroom-tiles': '🔲',
    taps: '🚰', washbasin: '🪥', 'office-setup': '💻',
  };
  return map[categoryId] || '📦';
}

/* ===== Draggable Room Floor Plan ===== */
function RoomFloorPlan({ room, roomSelections, roomPlacements, activeRoom, dispatch }) {
  const svgRef = useRef(null);
  const [dragging, setDragging] = useState(null);

  const SCALE = 6;
  const rw = (room?.width || 20) * SCALE;
  const rh = (room?.height || 15) * SCALE;
  const padding = 20;
  const vw = rw + padding * 2;
  const vh = rh + padding * 2;

  const selectedItems = Object.keys(roomSelections);
  if (selectedItems.length === 0) return null;

  const getDefaultPos = (index, total) => {
    const cols = Math.ceil(Math.sqrt(total));
    const col = index % cols;
    const row = Math.floor(index / cols);
    const cellW = rw / (cols + 1);
    const cellH = rh / (Math.ceil(total / cols) + 1);
    return {
      x: padding + cellW * (col + 0.5),
      y: padding + cellH * (row + 0.5),
    };
  };

  const getSVGPoint = (e) => {
    const svg = svgRef.current;
    if (!svg) return { x: 0, y: 0 };
    const pt = svg.createSVGPoint();
    const ctm = svg.getScreenCTM();
    if (!ctm) return { x: 0, y: 0 };
    pt.x = e.clientX;
    pt.y = e.clientY;
    const svgP = pt.matrixTransform(ctm.inverse());
    return { x: svgP.x, y: svgP.y };
  };

  const handleMouseDown = (e, catId) => {
    e.preventDefault();
    const { x, y } = getSVGPoint(e);
    const pos = roomPlacements[catId] || getDefaultPos(selectedItems.indexOf(catId), selectedItems.length);
    setDragging({ catId, offsetX: x - pos.x, offsetY: y - pos.y });
  };

  const handleMouseMove = (e) => {
    if (!dragging) return;
    const { x, y } = getSVGPoint(e);
    const newX = Math.max(padding + 15, Math.min(padding + rw - 15, x - dragging.offsetX));
    const newY = Math.max(padding + 15, Math.min(padding + rh - 15, y - dragging.offsetY));
    dispatch({
      type: 'UPDATE_FURNITURE_PLACEMENT',
      payload: { room: activeRoom, category: dragging.catId, x: newX, y: newY },
    });
  };

  const handleMouseUp = () => setDragging(null);

  return (
    <div className="room-floorplan-wrapper">
      <div className="floorplan-header">
        <span className="floorplan-title">🗺️ Room Layout — Drag items to rearrange</span>
      </div>
      <svg
        ref={svgRef}
        viewBox={`0 0 ${vw} ${vh}`}
        className="room-floorplan-svg"
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {/* Grid */}
        <defs>
          <pattern id="fp-grid" width={SCALE * 5} height={SCALE * 5} patternUnits="userSpaceOnUse">
            <path d={`M ${SCALE * 5} 0 L 0 0 0 ${SCALE * 5}`} fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#fp-grid)" />

        {/* Room boundary */}
        <rect
          x={padding} y={padding} width={rw} height={rh}
          fill="rgba(255,255,255,0.02)"
          stroke="var(--accent-primary)"
          strokeWidth="1.5"
          strokeDasharray="6 3"
          rx="4"
        />
        <text x={padding + 6} y={padding + 14} fill="var(--text-tertiary)" fontSize="10" fontFamily="Inter">
          {room?.name || activeRoom}
        </text>
        <text x={padding + rw - 6} y={padding + 14} fill="var(--text-tertiary)" fontSize="8" fontFamily="Inter" textAnchor="end">
          {room?.width}'×{room?.height}'
        </text>

        {/* Draggable furniture items */}
        {selectedItems.map((catId, i) => {
          const pos = roomPlacements[catId] || getDefaultPos(i, selectedItems.length);
          const emoji = getFurnitureEmoji(catId);
          const isDragging = dragging?.catId === catId;

          return (
            <g
              key={catId}
              style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
              onMouseDown={(e) => handleMouseDown(e, catId)}
            >
              {/* Shadow / glow */}
              <circle
                cx={pos.x} cy={pos.y} r={isDragging ? 22 : 18}
                fill={isDragging ? 'rgba(108, 92, 231, 0.2)' : 'rgba(108, 92, 231, 0.08)'}
                stroke={isDragging ? 'var(--accent-primary)' : 'var(--border-accent)'}
                strokeWidth={isDragging ? 1.5 : 0.5}
                style={{ transition: isDragging ? 'none' : 'all 0.2s' }}
              />
              {/* Emoji */}
              <text
                x={pos.x} y={pos.y + 1}
                textAnchor="middle" dominantBaseline="middle"
                fontSize="18" style={{ pointerEvents: 'none', userSelect: 'none' }}
              >
                {emoji}
              </text>
              {/* Label */}
              <text
                x={pos.x} y={pos.y + 24}
                textAnchor="middle" dominantBaseline="middle"
                fill="var(--text-secondary)" fontSize="7" fontFamily="Inter" fontWeight="600"
                style={{ pointerEvents: 'none' }}
              >
                {catId.replace(/-/g, ' ')}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

export default function InteriorCustomizer() {
  const { state, dispatch } = useProject();
  const { interiorSelections, blueprintData, furniturePlacements, layoutForm } = state;

  // Build rooms list from layoutForm parameters (bedrooms + standard + additional rooms)
  const rooms = useMemo(() => {
    // If blueprint data has rooms, use those
    if (blueprintData && blueprintData.rooms && blueprintData.rooms.length > 0) {
      return blueprintData.rooms.map(r => ({
        ...r,
        name: r.name,
        type: getRoomType(r.name),
      }));
    }

    // Otherwise, build rooms from layoutForm
    const roomList = [];

    // Living Room (always present)
    roomList.push({ name: 'Living Room', type: 'living', width: 18, height: 15 });

    // Kitchen (always present)
    roomList.push({ name: 'Kitchen', type: 'kitchen', width: 17, height: 12 });

    // Bedrooms
    const bedroomCount = parseInt(layoutForm.bedrooms) || 3;
    roomList.push({ name: 'Master Bedroom', type: 'bedroom', width: 15, height: 17 });
    for (let i = 2; i <= bedroomCount; i++) {
      roomList.push({ name: `Bedroom ${i}`, type: 'bedroom', width: 12, height: 12 });
    }

    // Bathrooms (one per bedroom)
    roomList.push({ name: 'Master Bathroom', type: 'bathroom', width: 5, height: 7 });
    if (bedroomCount >= 2) {
      roomList.push({ name: 'Bathroom', type: 'bathroom', width: 5, height: 7 });
    }

    // Additional rooms from layoutForm
    if (layoutForm.additionalRooms.includes('Store')) {
      roomList.push({ name: 'Store Room', type: 'store', width: 6, height: 5 });
    }
    if (layoutForm.additionalRooms.includes('Dining')) {
      roomList.push({ name: 'Dining Room', type: 'kitchen', width: 17, height: 11 });
    }

    // Balcony (always add one)
    roomList.push({ name: 'Balcony', type: 'balcony', width: 10, height: 5 });

    return roomList;
  }, [blueprintData, layoutForm]);

  const [activeRoom, setActiveRoom] = useState('');

  // Set default room if not set
  React.useEffect(() => {
    if (rooms.length > 0 && !activeRoom) {
      setActiveRoom(rooms[0].name);
    }
  }, [rooms, activeRoom]);

  const activeRoomObj = rooms.find(r => r.name === activeRoom);
  const activeRoomType = activeRoomObj ? activeRoomObj.type : 'other';
  const roomCategories = getCategoriesForRoom(activeRoomType);
  const roomSelections = interiorSelections[activeRoom] || {};
  const roomPlacements = furniturePlacements[activeRoom] || {};

  const handleSelect = (categoryId, optionId) => {
    dispatch({
      type: 'UPDATE_INTERIOR_SELECTION',
      payload: { room: activeRoom, category: categoryId, optionId },
    });
  };

  // Count total selections across all rooms
  const totalSelections = Object.values(interiorSelections).reduce(
    (sum, roomSel) => sum + Object.keys(roomSel).length, 0
  );
  const allSelected = totalSelections >= 5;

  return (
    <div className="interior-customizer-container">
      <div className="step-header">
        <div className="step-header-icon">🛋️</div>
        <div>
          <h2>Interior Design — Room by Room</h2>
          <p>Select items for each room, then drag them to position where you want.</p>
        </div>
      </div>

      <div className="interior-progress">
        <div className="interior-progress-bar">
          <div className="interior-progress-fill" style={{ width: `${Math.min(100, (totalSelections / 5) * 100)}%` }} />
        </div>
        <span className="interior-progress-text">{totalSelections} items selected across all rooms</span>
      </div>

      {/* Room tabs */}
      <div className="room-tabs-bar">
        {rooms.map(room => {
          const rSel = interiorSelections[room.name] || {};
          const selCount = Object.keys(rSel).length;
          return (
            <button
              key={room.name}
              className={`room-tab ${activeRoom === room.name ? 'room-tab-active' : ''} ${selCount > 0 ? 'room-tab-has-items' : ''}`}
              onClick={() => setActiveRoom(room.name)}
            >
              <span className="room-tab-icon">{getRoomIcon(room.type)}</span>
              <span className="room-tab-name">{room.name}</span>
              {selCount > 0 && <span className="room-tab-badge">{selCount}</span>}
            </button>
          );
        })}
      </div>

      {/* Categories for active room */}
      <div className="room-label-bar">
        <span className="room-label-icon">{getRoomIcon(activeRoomType)}</span>
        <span className="room-label-text">{activeRoom}</span>
        <span className="room-label-count">{roomCategories.length} categories available</span>
      </div>

      <div className="interior-categories">
        {roomCategories.map((category, catIndex) => (
          <div
            key={category.id}
            className={`interior-category ${roomSelections[category.id] ? 'category-completed' : ''}`}
            style={{ animationDelay: `${catIndex * 0.03}s` }}
          >
            <div className="category-header">
              {category.headerImage ? (
                <img src={category.headerImage} alt={category.name} className="category-header-image" />
              ) : (
                <span className="category-icon">{category.icon}</span>
              )}
              <h4 className="category-name">{category.name}</h4>
              {roomSelections[category.id] && <span className="category-check">✓</span>}
            </div>

            <div className="options-row">
              {category.options.map((option) => {
                const isSelected = roomSelections[category.id] === option.id;
                return (
                  <div
                    key={option.id}
                    className={`interior-option ${isSelected ? 'option-selected' : ''}`}
                    onClick={() => handleSelect(category.id, option.id)}
                    id={`option-${option.id}`}
                  >
                    <div className="option-thumbnail">
                      <OptionThumbnail option={option} />
                      {isSelected && <span className="thumbnail-check">✓</span>}
                    </div>
                    <div className="option-info">
                      <span className="option-name">{option.name}</span>
                      <span className="option-material">{option.material}</span>
                    </div>
                    <span className="option-style-tag">{option.style}</span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {allSelected && (
        <div className="wizard-nav" style={{ animation: 'fadeInUp 0.4s ease-out' }}>
          <button className="btn btn-secondary" onClick={() => dispatch({ type: 'SET_STEP', payload: 3 })}>← Back</button>
          <button className="btn btn-primary btn-lg" onClick={() => dispatch({ type: 'SET_STEP', payload: 5 })} id="next-to-overview-btn">
            View Final Overview
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 10h12M12 6l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}
