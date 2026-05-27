import React, { useState, useRef, useCallback, useEffect } from 'react';
import { useProject } from '../../context/ProjectContext';
import './LayoutEditor.css';

const SCALE = 8; // pixels per foot
const HANDLE_SIZE = 8;
const MIN_ROOM_SIZE = 5; // minimum 5ft

const getRoomColor = (name = '') => {
  const n = name.toLowerCase();
  if (n.includes('backyard') || n.includes('lawn') || n.includes('garden')) return '#ffffff';
  if (n.includes('living') || n.includes('hall')) return 'rgba(253, 245, 230, 0.85)';
  if (n.includes('bedroom') || n.includes('suite') || n.includes('master')) return 'rgba(255, 249, 196, 0.85)';
  if (n.includes('kitchen')) return 'rgba(255, 224, 178, 0.85)';
  if (n.includes('bath')) return 'rgba(179, 229, 252, 0.85)';
  if (n.includes('balcony') || n.includes('terrace')) return 'rgba(220, 237, 200, 0.85)';
  if (n.includes('dining')) return 'rgba(248, 187, 208, 0.85)';
  if (n.includes('store')) return 'rgba(225, 190, 231, 0.85)';
  if (n.includes('entry') || n.includes('foyer')) return 'rgba(255, 205, 210, 0.85)';
  return 'rgba(255, 255, 255, 0.85)';
};

// Helper to create a unified SVG path for compound rooms (removes internal lines)
const getRoomPath = (rects, scale) => {
  if (!rects || rects.length === 0) return '';
  const edges = [];
  rects.forEach(r => {
    const x = r.x * scale, y = r.y * scale, w = (r.width || r.w) * scale, h = (r.height || r.h) * scale;
    // Edge segments: [x1, y1, x2, y2]
    edges.push({x1: x, y1: y, x2: x+w, y2: y}); // Top
    edges.push({x1: x+w, y1: y, x2: x+w, y2: y+h}); // Right
    edges.push({x1: x+w, y1: y+h, x2: x, y2: y+h}); // Bottom
    edges.push({x1: x, y1: y+h, x2: x, y2: y}); // Left
  });

  // Filter out edges that appear twice (shared internal boundaries)
  const uniqueEdges = edges.filter(e1 => {
    const isShared = edges.some(e2 => 
       Math.abs(e1.x1 - e2.x2) < 1 && Math.abs(e1.y1 - e2.y2) < 1 &&
       Math.abs(e1.x2 - e2.x1) < 1 && Math.abs(e1.y2 - e2.y1) < 1
    );
    return !isShared;
  });

  return uniqueEdges.map(e => `M ${e.x1} ${e.y1} L ${e.x2} ${e.y2}`).join(' ');
};

export default function LayoutEditor() {
  const { state, dispatch } = useProject();
  const { selectedLayout, editedRooms } = state;
  const svgRef = useRef(null);

  const [rooms, setRooms] = useState([]);
  const [dragging, setDragging] = useState(null); // { roomIndex, handle, startX, startY, origRoom }
  const [hoveredHandle, setHoveredHandle] = useState(null);

  useEffect(() => {
    if (editedRooms && editedRooms.length > 0) {
      setRooms(editedRooms.map(r => ({ ...r })));
    } else if (selectedLayout?.rooms) {
      setRooms(selectedLayout.rooms.map(r => ({ ...r })));
    }
  }, [selectedLayout, editedRooms]);

  // Compute SVG viewBox
  const computeViewBox = useCallback(() => {
    if (rooms.length === 0) return { vw: 600, vh: 400 };
    let maxX = 0, maxY = 0;
    rooms.forEach(r => {
      maxX = Math.max(maxX, (r.x + r.width) * SCALE);
      maxY = Math.max(maxY, (r.y + r.height) * SCALE);
    });
    return { vw: maxX + 40, vh: maxY + 40 };
  }, [rooms]);

  const snapToGrid = (val) => Math.round(val * 2) / 2; // 0.5ft grid

  const getSVGPoint = useCallback((e) => {
    const svg = svgRef.current;
    if (!svg) return { x: 0, y: 0 };
    const pt = svg.createSVGPoint();
    const ctm = svg.getScreenCTM();
    if (!ctm) return { x: 0, y: 0 };
    pt.x = e.clientX;
    pt.y = e.clientY;
    const svgP = pt.matrixTransform(ctm.inverse());
    return { x: svgP.x, y: svgP.y };
  }, []);

  const handleMouseDown = useCallback((e, roomIndex, handle) => {
    e.preventDefault();
    e.stopPropagation();
    const { x, y } = getSVGPoint(e);
    
    // For magnetic drafting: find shared edges if dragging a border
    const sharedHandles = [];
    if (handle !== 'move') {
      const currentRoom = rooms[roomIndex];
      const EPS = 0.5; // tolerance
      
      rooms.forEach((other, oIdx) => {
        if (oIdx === roomIndex) return;
        
        const isXShared = (handle === 'right' && Math.abs((currentRoom.x + currentRoom.width) - other.x) < EPS) ||
                          (handle === 'left' && Math.abs(currentRoom.x - (other.x + other.width)) < EPS);
        const isYShared = (handle === 'bottom' && Math.abs((currentRoom.y + currentRoom.height) - other.y) < EPS) ||
                          (handle === 'top' && Math.abs(currentRoom.y - (other.y + other.height)) < EPS);
                          
        if (isXShared || isYShared) {
          sharedHandles.push({
            index: oIdx,
            type: handle === 'right' ? 'left' : handle === 'left' ? 'right' : handle === 'bottom' ? 'top' : 'bottom'
          });
        }
      });
    }

    setDragging({
      roomIndex,
      handle,
      startX: x,
      startY: y,
      origRoom: { ...rooms[roomIndex] },
      sharedHandles,
      origShared: sharedHandles.map(sh => ({ ...rooms[sh.index] }))
    });
  }, [rooms, getSVGPoint]);

  const handleMouseMove = useCallback((e) => {
    if (!dragging) return;
    const { x, y } = getSVGPoint(e);
    const dx = (x - dragging.startX) / SCALE;
    const dy = (y - dragging.startY) / SCALE;

    setRooms(prev => {
      const updated = [...prev];
      
      const updateRoom = (room, orig, handle, deltaX, deltaY) => {
        switch (handle) {
          case 'right':
            room.width = Math.max(MIN_ROOM_SIZE, snapToGrid(orig.width + deltaX));
            break;
          case 'bottom':
            room.height = Math.max(MIN_ROOM_SIZE, snapToGrid(orig.height + deltaY));
            break;
          case 'left':
            room.x = snapToGrid(orig.x + deltaX);
            room.width = Math.max(MIN_ROOM_SIZE, snapToGrid(orig.width - deltaX));
            break;
          case 'top':
            room.y = snapToGrid(orig.y + deltaY);
            room.height = Math.max(MIN_ROOM_SIZE, snapToGrid(orig.height - deltaY));
            break;
          case 'move':
            room.x = snapToGrid(orig.x + deltaX);
            room.y = snapToGrid(orig.y + deltaY);
            if (room.rects && room.rects.length > 0) {
              room.rects = orig.rects.map(r => ({
                ...r,
                x: snapToGrid(r.x + deltaX),
                y: snapToGrid(r.y + deltaY)
              }));
            }
            break;
          default: break;
        }
      };

      const primary = { ...dragging.origRoom };
      updateRoom(primary, dragging.origRoom, dragging.handle, dx, dy);
      updated[dragging.roomIndex] = primary;

      // Magnetic Adapting: update shared neighbors
      dragging.sharedHandles.forEach((sh, i) => {
        const neighbor = { ...dragging.origShared[i] };
        updateRoom(neighbor, dragging.origShared[i], sh.type, dx, dy);
        updated[sh.index] = neighbor;
      });

      return updated;
    });
  }, [dragging, getSVGPoint]);

  const handleMouseUp = useCallback(() => {
    if (dragging) {
      setDragging(null);
    }
  }, [dragging]);

  const handleSave = () => {
    dispatch({ type: 'SET_EDITED_ROOMS', payload: rooms });
    dispatch({ type: 'SET_STEP', payload: 3 });
  };

  if (!selectedLayout) {
    return (
      <div className="editor-empty">
        <div className="empty-state">
          <div className="empty-state-icon">✏️</div>
          <h3>No Layout Selected</h3>
          <p>Go back to Layout step and select a variant to edit.</p>
        </div>
      </div>
    );
  }

  const { vw, vh } = computeViewBox();

  return (
    <div className="layout-editor-container">
      <div className="step-header">
        <div className="step-header-icon">✏️</div>
        <div>
          <h2>Edit Layout</h2>
          <p>Drag room boundaries to resize. Click and drag inside a room to move it.</p>
        </div>
      </div>

      <div className="editor-canvas-wrapper">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${vw} ${vh}`}
          className="editor-svg"
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          {/* Grid & Patterns */}
          <defs>
            <pattern id="grid" width={SCALE * 5} height={SCALE * 5} patternUnits="userSpaceOnUse">
              <path d={`M ${SCALE * 5} 0 L 0 0 0 ${SCALE * 5}`} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="0.5" />
            </pattern>
            <pattern id="stairHatch" patternUnits="userSpaceOnUse" width={SCALE * 2} height={SCALE * 2}>
              <path d={`M -${SCALE/2},${SCALE/2} l${SCALE},-${SCALE} M 0,${SCALE*2} l${SCALE*2},-${SCALE*2} M ${SCALE*1.5},${SCALE*2.5} l${SCALE},-${SCALE}`} stroke="rgba(0,0,0,0.3)" strokeWidth="1" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />

          {rooms.map((room, i) => {
            const isHovered = hoveredHandle?.roomIndex === i;
            const isCompound = room.rects && room.rects.length > 0;
            const isStair = room.name.toLowerCase().includes('stair');
            
            const rects = isCompound ? room.rects : [{
              x: room.x, y: room.y, width: room.width, height: room.height
            }];

            // Define coordinates for handles and labels
            const rx = room.x * SCALE;
            const ry = room.y * SCALE;
            const rw = (room.width || 0) * SCALE;
            const rh = (room.height || 0) * SCALE;

            const fillColor = isStair ? 'url(#stairHatch)' : getRoomColor(room.name);

            return (
              <g key={room.id || i}>
                {/* Single Unified Perimeter Stroke (Zero Strips / Proper Blocks) */}
                <path
                  d={getRoomPath(rects, SCALE)}
                  fill={fillColor} // Fill the whole perimeter path for ultimate seamlessness
                  stroke={isHovered ? 'var(--accent-primary)' : '#000'}
                  strokeWidth={isHovered ? 2.5 : 1.5}
                  strokeLinejoin="round"
                  strokeLinecap="round"
                  style={{ cursor: 'move' }}
                  onMouseDown={(e) => handleMouseDown(e, i, 'move')}
                  onMouseEnter={() => setHoveredHandle({ roomIndex: i })}
                  onMouseLeave={() => !dragging && setHoveredHandle(null)}
                />

                {/* Invisible interaction layer (the fragments) */}
                {rects.map((rect, rectIdx) => (
                  <rect
                    key={`${room.id}-${rectIdx}-interaction`}
                    x={rect.x * SCALE}
                    y={rect.y * SCALE}
                    width={(rect.width || rect.w) * SCALE}
                    height={(rect.height || rect.h) * SCALE}
                    fill="transparent"
                    style={{ pointerEvents: 'none' }}
                  />
                ))}

                {/* Single Room Label (No background) */}
                <g transform={`translate(${(room.x + room.width / 2) * SCALE}, ${(room.y + room.height / 2) * SCALE})`}>
                  <text
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="room-label"
                    style={{ 
                      pointerEvents: 'none', 
                      textTransform: 'uppercase', 
                      fontWeight: '800', 
                      fontSize: '10px',
                      fill: '#000',
                      paintOrder: 'stroke',
                      stroke: '#ffffff',
                      strokeWidth: '3px',
                      strokeLinejoin: 'round'
                    }}
                    y="-4"
                  >
                    {room.name}
                  </text>
                  <text
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="room-dimensions"
                    style={{ 
                      pointerEvents: 'none', 
                      fontSize: '7px',
                      fontWeight: '600',
                      fill: '#555',
                      paintOrder: 'stroke',
                      stroke: '#ffffff',
                      strokeWidth: '2px',
                      strokeLinejoin: 'round'
                    }}
                    y="10"
                  >
                    {room.width.toFixed(0)}' × {room.height.toFixed(0)}'
                  </text>
                </g>

                {/* Resize handles - only show for single rect rooms for now */}
                {!isCompound && (
                  <>
                    {/* Right */}
                    <rect
                      x={rx + rw - HANDLE_SIZE / 2}
                      y={ry + rh / 2 - HANDLE_SIZE / 2}
                      width={HANDLE_SIZE}
                      height={HANDLE_SIZE}
                      className="resize-handle"
                      style={{ cursor: 'ew-resize' }}
                      onMouseDown={(e) => handleMouseDown(e, i, 'right')}
                    />
                    {/* Bottom */}
                    <rect
                      x={rx + rw / 2 - HANDLE_SIZE / 2}
                      y={ry + rh - HANDLE_SIZE / 2}
                      width={HANDLE_SIZE}
                      height={HANDLE_SIZE}
                      className="resize-handle"
                      style={{ cursor: 'ns-resize' }}
                      onMouseDown={(e) => handleMouseDown(e, i, 'bottom')}
                    />
                    {/* Left */}
                    <rect
                      x={rx - HANDLE_SIZE / 2}
                      y={ry + rh / 2 - HANDLE_SIZE / 2}
                      width={HANDLE_SIZE}
                      height={HANDLE_SIZE}
                      className="resize-handle"
                      style={{ cursor: 'ew-resize' }}
                      onMouseDown={(e) => handleMouseDown(e, i, 'left')}
                    />
                    {/* Top */}
                    <rect
                      x={rx + rw / 2 - HANDLE_SIZE / 2}
                      y={ry - HANDLE_SIZE / 2}
                      width={HANDLE_SIZE}
                      height={HANDLE_SIZE}
                      className="resize-handle"
                      style={{ cursor: 'ns-resize' }}
                      onMouseDown={(e) => handleMouseDown(e, i, 'top')}
                    />
                  </>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Room list sidebar */}
      <div className="editor-room-list">
        <h4>Room Sizes</h4>
        {rooms.map((room, i) => (
          <div key={room.id || i} className="room-info-row">
            <span className="room-color-dot" style={{ background: getRoomColor(room.name) }} />
            <span className="room-info-name">{room.name}</span>
            <span className="room-info-size">
              {room.width.toFixed(0)}' × {room.height.toFixed(0)}'
            </span>
          </div>
        ))}
      </div>

      <div className="wizard-nav">
        <button
          className="btn btn-secondary"
          onClick={() => dispatch({ type: 'SET_STEP', payload: 1 })}
        >
          ← Back to Layout
        </button>
        <button
          className="btn btn-primary btn-lg"
          onClick={handleSave}
          id="save-and-continue-btn"
        >
          Save & Generate Blueprint
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M4 10h12M12 6l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      </div>
    </div>
  );
}
