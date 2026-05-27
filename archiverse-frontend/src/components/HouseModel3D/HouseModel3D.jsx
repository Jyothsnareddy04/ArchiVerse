import React, { useState, useMemo, useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Text, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';
import './HouseModel3D.css';

// ─── Constants ──────────────────────────────────────────────────────
const WALL_HEIGHT = 3.0;      // meters (one floor)
const WALL_THICKNESS = 0.15;  // meters
const FLOOR_THICKNESS = 0.1;
const SCALE = 0.1;            // ft → meters (1 ft = 0.1 units for camera ergonomics)

// ─── Color helpers ──────────────────────────────────────────────────
const ROOM_COLORS = {
  living:  '#E8D5B7',
  hall:    '#E8D5B7',
  bedroom: '#D5C4A1',
  master:  '#C9B896',
  suite:   '#C9B896',
  kitchen: '#D4E09B',
  dining:  '#E6D4A3',
  bath:    '#A8D8EA',
  balcony: '#C8E6C9',
  store:   '#D7CCC8',
  entry:   '#F8BBD0',
  foyer:   '#F8BBD0',
  corridor:'#E0E0E0',
  backyard:'#A5D6A7',
  porch:   '#BCAAA4',
  garden:  '#81C784',
  default: '#E0E0E0',
};

function getRoomColor(name) {
  const n = (name || '').toLowerCase();
  for (const [key, val] of Object.entries(ROOM_COLORS)) {
    if (n.includes(key)) return val;
  }
  return ROOM_COLORS.default;
}

const WALL_PALETTE = [
  '#6c5ce7', '#00cec9', '#fd79a8', '#fdcb6e', '#00b894', '#a29bfe',
  '#e17055', '#74b9ff', '#55efc4', '#fab1a0',
];

// ─── Room Floor ─────────────────────────────────────────────────────
function RoomFloor({ x, y, w, h, color, floorY = 0 }) {
  return (
    <mesh position={[x + w / 2, floorY + FLOOR_THICKNESS / 2, y + h / 2]} receiveShadow>
      <boxGeometry args={[w, FLOOR_THICKNESS, h]} />
      <meshStandardMaterial color={color} roughness={0.6} metalness={0.1} />
    </mesh>
  );
}

// ─── Wall Segment ───────────────────────────────────────────────────
function Wall({ start, end, height, color, opacity = 0.85 }) {
  const dx = end[0] - start[0];
  const dz = end[1] - start[1];
  const length = Math.sqrt(dx * dx + dz * dz);
  const angle = Math.atan2(dz, dx);

  const cx = (start[0] + end[0]) / 2;
  const cz = (start[1] + end[1]) / 2;

  return (
    <mesh
      position={[cx, height / 2 + FLOOR_THICKNESS, cz]}
      rotation={[0, -angle, 0]}
      castShadow
      receiveShadow
    >
      <boxGeometry args={[length, height, WALL_THICKNESS]} />
      <meshStandardMaterial
        color={color}
        roughness={0.7}
        metalness={0.05}
        transparent
        opacity={opacity}
      />
    </mesh>
  );
}

// ─── Door Cutout (visual gap in wall) ───────────────────────────────
function Door({ position, rotation, width = 0.6, height = 2.2 }) {
  return (
    <mesh position={position} rotation={rotation}>
      <boxGeometry args={[width, height, WALL_THICKNESS + 0.02]} />
      <meshStandardMaterial color="#2d1b0e" roughness={0.4} metalness={0.3} />
    </mesh>
  );
}

// ─── Room Component ─────────────────────────────────────────────────
function Room({ room, index, wallColors, showRoof, allRooms }) {
  const fragments = room.rects && room.rects.length > 0
    ? room.rects
    : [{ x: room.x, y: room.y, width: room.width || room.w, height: room.height || room.h }];

  const roomColor = getRoomColor(room.name);
  const wallColor = wallColors[index % wallColors.length];
  const isOutdoor = (room.name || '').toLowerCase().match(/backyard|lawn|garden|balcony|terrace/);
  const wallH = isOutdoor ? 0.8 : WALL_HEIGHT;

  // Check if a wall segment is shared with another room's fragment
  const isSharedWall = (fragX, fragY, fragW, fragH, side) => {
    const EPS = 0.5; // tolerance in ft
    for (const otherRoom of allRooms) {
      if (otherRoom === room) continue;
      const otherFrags = otherRoom.rects && otherRoom.rects.length > 0
        ? otherRoom.rects
        : [{ x: otherRoom.x, y: otherRoom.y, width: otherRoom.width || otherRoom.w, height: otherRoom.height || otherRoom.h }];
      
      for (const of of otherFrags) {
        const ox = of.x, oy = of.y;
        const ow = of.width || of.w;
        const oh = of.height || of.h;

        // Check overlap on the axis
        const hOverlap = fragX < ox + ow - EPS && fragX + fragW > ox + EPS;
        const vOverlap = fragY < oy + oh - EPS && fragY + fragH > oy + EPS;

        if (side === 'top'    && vOverlap === false && Math.abs(fragY - (oy + oh)) < EPS && hOverlap) return true;
        if (side === 'bottom' && vOverlap === false && Math.abs((fragY + fragH) - oy) < EPS && hOverlap) return true;
        if (side === 'left'   && hOverlap === false && Math.abs(fragX - (ox + ow)) < EPS && vOverlap) return true;
        if (side === 'right'  && hOverlap === false && Math.abs((fragX + fragW) - ox) < EPS && vOverlap) return true;
      }
    }
    return false;
  };

  return (
    <group>
      {fragments.map((frag, fi) => {
        const fx = (frag.x || 0) * SCALE;
        const fy = (frag.y || 0) * SCALE;
        const fw = ((frag.width || frag.w) || 1) * SCALE;
        const fh = ((frag.height || frag.h) || 1) * SCALE;
        const rawX = frag.x || 0;
        const rawY = frag.y || 0;
        const rawW = (frag.width || frag.w) || 1;
        const rawH = (frag.height || frag.h) || 1;

        const corners = {
          tl: [fx, fy],          // top-left
          tr: [fx + fw, fy],     // top-right
          bl: [fx, fy + fh],     // bottom-left
          br: [fx + fw, fy + fh], // bottom-right
        };

        const showTop = !isSharedWall(rawX, rawY, rawW, rawH, 'top');
        const showBottom = !isSharedWall(rawX, rawY, rawW, rawH, 'bottom');
        const showLeft = !isSharedWall(rawX, rawY, rawW, rawH, 'left');
        const showRight = !isSharedWall(rawX, rawY, rawW, rawH, 'right');

        return (
          <group key={`${room.id || index}-${fi}`}>
            {/* Floor */}
            <RoomFloor x={fx} y={fy} w={fw} h={fh} color={roomColor} />

            {/* Walls */}
            {showTop && <Wall start={corners.tl} end={corners.tr} height={wallH} color={wallColor} />}
            {showBottom && <Wall start={corners.bl} end={corners.br} height={wallH} color={wallColor} />}
            {showLeft && <Wall start={corners.tl} end={corners.bl} height={wallH} color={wallColor} />}
            {showRight && <Wall start={corners.tr} end={corners.br} height={wallH} color={wallColor} />}

            {/* Room label */}
            {fi === 0 && (
              <Text
                position={[fx + fw / 2, wallH + 0.3, fy + fh / 2]}
                fontSize={Math.min(fw, fh) * 0.12}
                color="#ffffff"
                anchorX="center"
                anchorY="middle"
                outlineWidth={0.02}
                outlineColor="#000000"
                font={undefined}
              >
                {room.name || 'Room'}
              </Text>
            )}

            {/* Door */}
            {fi === 0 && room.door && (() => {
              const d = room.door;
              const doorWidth = 0.7;
              let pos, rot;
              const relPos = d.pos || 0.5;

              if (d.side === 'top') {
                pos = [fx + fw * relPos, WALL_HEIGHT * 0.45, fy];
                rot = [0, 0, 0];
              } else if (d.side === 'bottom') {
                pos = [fx + fw * relPos, WALL_HEIGHT * 0.45, fy + fh];
                rot = [0, 0, 0];
              } else if (d.side === 'left') {
                pos = [fx, WALL_HEIGHT * 0.45, fy + fh * relPos];
                rot = [0, Math.PI / 2, 0];
              } else {
                pos = [fx + fw, WALL_HEIGHT * 0.45, fy + fh * relPos];
                rot = [0, Math.PI / 2, 0];
              }

              return <Door position={pos} rotation={rot} width={doorWidth} />;
            })()}

            {/* Roof slab (if toggled) */}
            {showRoof && !isOutdoor && (
              <mesh position={[fx + fw / 2, wallH + FLOOR_THICKNESS, fy + fh / 2]} receiveShadow>
                <boxGeometry args={[fw + 0.02, 0.08, fh + 0.02]} />
                <meshStandardMaterial
                  color="#5C4033"
                  roughness={0.8}
                  metalness={0.1}
                  transparent
                  opacity={0.65}
                />
              </mesh>
            )}
          </group>
        );
      })}
    </group>
  );
}

// ─── Ground Plane ───────────────────────────────────────────────────
function Ground({ size }) {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[size / 2, -0.01, size / 2]} receiveShadow>
      <planeGeometry args={[size * 2, size * 2]} />
      <meshStandardMaterial color="#1a1a2e" roughness={0.9} />
    </mesh>
  );
}

// ─── Camera auto-framing ────────────────────────────────────────────
function CameraSetup({ center, distance }) {
  const { camera } = useThree();
  const initialized = useRef(false);

  useFrame(() => {
    if (!initialized.current) {
      camera.position.set(
        center[0] + distance * 0.8,
        distance * 0.9,
        center[2] + distance * 0.8
      );
      camera.lookAt(center[0], 0, center[2]);
      initialized.current = true;
    }
  });

  return null;
}

// ─── Main Component ─────────────────────────────────────────────────
export default function HouseModel3D({
  rooms,
  exteriorStyle,
  interiorSelections = {},
  height = 500,
  showControls = true,
  technicalData = null,
}) {
  const [showRoof, setShowRoof] = useState(false);

  // Compute scene bounds
  const { center, maxDim, wallColors } = useMemo(() => {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    (rooms || []).forEach(r => {
      const frags = r.rects && r.rects.length > 0
        ? r.rects
        : [{ x: r.x, y: r.y, width: r.width || r.w, height: r.height || r.h }];
      frags.forEach(f => {
        const fx = f.x || 0, fy = f.y || 0;
        const fw = (f.width || f.w) || 0;
        const fh = (f.height || f.h) || 0;
        minX = Math.min(minX, fx);
        minY = Math.min(minY, fy);
        maxX = Math.max(maxX, fx + fw);
        maxY = Math.max(maxY, fy + fh);
      });
    });

    if (!isFinite(minX)) { minX = 0; minY = 0; maxX = 50; maxY = 40; }

    const cx = ((minX + maxX) / 2) * SCALE;
    const cy = ((minY + maxY) / 2) * SCALE;
    const dx = (maxX - minX) * SCALE;
    const dy = (maxY - minY) * SCALE;
    const md = Math.max(dx, dy);

    const colors = exteriorStyle
      ? exteriorStyle.colors || WALL_PALETTE
      : WALL_PALETTE;

    return {
      center: [cx, 0, cy],
      maxDim: md,
      wallColors: colors,
    };
  }, [rooms, exteriorStyle]);

  if (!rooms || rooms.length === 0) {
    return (
      <div className="house-3d-viewer" style={{ height }}>
        <div className="empty-3d-state">
          <span>🏗️</span>
          <p>No room data available for 3D view</p>
        </div>
      </div>
    );
  }

  return (
    <div className="house-3d-viewer" style={{ height }}>
      {/* HUD Controls */}
      {showControls && (
        <div className="viewer-hud">
          <div className="hud-controls">
            <span className="hud-hint">🖱️ Drag to rotate</span>
            <span className="hud-hint">🔍 Scroll to zoom</span>
            <span className="hud-hint">⇧+Drag pan</span>
          </div>
          <div className="hud-actions">
            <button
              className={`hud-btn ${showRoof ? 'hud-btn-active' : ''}`}
              onClick={() => setShowRoof(r => !r)}
              title="Toggle roof"
            >
              ⌂
            </button>
          </div>
        </div>
      )}

      {/* Three.js Canvas */}
      <Canvas
        shadows
        camera={{
          fov: 45,
          near: 0.1,
          far: 1000,
          position: [
            center[0] + maxDim * 0.8,
            maxDim * 0.9,
            center[2] + maxDim * 0.8,
          ],
        }}
        gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.2 }}
        style={{ borderRadius: 'var(--radius-lg)' }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.4} />
        <directionalLight
          position={[maxDim * 2, maxDim * 2, maxDim * 1.5]}
          intensity={1.2}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
          shadow-camera-far={maxDim * 6}
          shadow-camera-left={-maxDim * 2}
          shadow-camera-right={maxDim * 2}
          shadow-camera-top={maxDim * 2}
          shadow-camera-bottom={-maxDim * 2}
        />
        <directionalLight
          position={[-maxDim, maxDim * 1.5, -maxDim]}
          intensity={0.3}
        />
        <hemisphereLight
          skyColor="#b1e1ff"
          groundColor="#1a1a2e"
          intensity={0.5}
        />

        {/* Environment for reflections */}
        <fog attach="fog" args={['#0a0a1a', maxDim * 3, maxDim * 8]} />

        {/* Ground */}
        <Ground size={maxDim * 1.5} />

        {/* Contact shadows */}
        <ContactShadows
          position={[center[0], 0, center[2]]}
          opacity={0.4}
          scale={maxDim * 3}
          blur={2}
          far={maxDim * 2}
        />

        {/* Rooms */}
        {rooms.map((room, i) => (
          <Room
            key={room.id || i}
            room={room}
            index={i}
            wallColors={wallColors}
            showRoof={showRoof}
            allRooms={rooms}
          />
        ))}

        {/* Orbit Controls */}
        <OrbitControls
          target={center}
          enableDamping
          dampingFactor={0.08}
          minDistance={maxDim * 0.3}
          maxDistance={maxDim * 4}
          maxPolarAngle={Math.PI / 2 - 0.05}
          minPolarAngle={0.1}
        />

        <CameraSetup center={center} distance={maxDim} />
      </Canvas>

      {/* Applied styles bar */}
      {exteriorStyle && (
        <div className="viewer-applied-bar">
          <div className="applied-chip">
            <span className="applied-dot" style={{ background: exteriorStyle.primary }} />
            <span className="applied-dot" style={{ background: exteriorStyle.secondary }} />
            <span>{exteriorStyle.name}</span>
          </div>
        </div>
      )}
    </div>
  );
}
