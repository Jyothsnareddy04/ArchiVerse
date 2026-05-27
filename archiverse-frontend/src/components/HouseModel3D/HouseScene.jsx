import React, { Suspense, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import RoomMesh from './RoomMesh';
import Lighting from './Lighting';
import CameraController from './CameraController';
import GridFloor from './GridFloor';
import { THEME } from './constants';
import './styles.css';

const HouseScene = ({ rooms = [], interiors = [] }) => {
  // Calculate center of the house to focus the camera intelligently
  const center = useMemo(() => {
    if (!rooms.length) return [0, 0, 0];
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    rooms.forEach(r => {
      minX = Math.min(minX, r.x);
      minY = Math.min(minY, r.y);
      maxX = Math.max(maxX, r.x + r.width);
      maxY = Math.max(maxY, r.y + r.height);
    });
    return [(minX + maxX) / 2, 0, (minY + maxY) / 2];
  }, [rooms]);

  return (
    <div className="house-scene-container">
      <Canvas shadows camera={{ position: [center[0], 60, center[2] + 60], fov: 45 }}>
        <color attach="background" args={[THEME.background]} />
        <fog attach="fog" args={[THEME.background, 50, 200]} />
        
        <Lighting />
        <CameraController target={center} />
        
        <Suspense fallback={null}>
          <GridFloor />
          <group>
            {rooms.map(room => {
              // Find matching interior configuration for this room
              const roomInterior = interiors.find(i => i.roomId === room.id);
              return (
                <RoomMesh key={room.id} room={room} interior={roomInterior} />
              )
            })}
          </group>
        </Suspense>
      </Canvas>
    </div>
  );
};

export default HouseScene;
