import React, { useMemo } from 'react';
import FloorMesh from './FloorMesh';
import WallMesh from './WallMesh';
import InteriorManager from './InteriorManager';
import { generateWalls, generatePlaceholders } from './helpers';
import { WALL_HEIGHT, WALL_THICKNESS } from './constants';
import { getRoomMaterial } from './MaterialLibrary';
import { Text } from '@react-three/drei';

const RoomMesh = ({ room, interior }) => {
  const walls = useMemo(() => generateWalls(room, WALL_HEIGHT, WALL_THICKNESS), [room]);
  const placeholders = useMemo(() => generatePlaceholders(room), [room]);
  
  // Real-time material calculation based on style
  const materialProps = useMemo(() => {
    const style = interior?.style || room.interiorStyle;
    return getRoomMaterial(room.type, style);
  }, [room.type, interior?.style, room.interiorStyle]);

  return (
    <group>
      <FloorMesh room={room} materialProps={materialProps.floor} />
      
      {walls.map(wall => (
        <WallMesh key={wall.id} position={wall.position} size={wall.size} materialProps={materialProps.wall} />
      ))}

      {placeholders.map(ph => (
        <mesh key={ph.id} position={ph.position} castShadow receiveShadow>
          <boxGeometry args={ph.size} />
          <meshStandardMaterial 
            color={ph.color} 
            transparent={ph.type === 'window'} 
            opacity={ph.type === 'window' ? 0.4 : 1}
            roughness={ph.type === 'window' ? 0.1 : 0.8}
            metalness={ph.type === 'window' ? 0.8 : 0.1}
          />
        </mesh>
      ))}

      {/* Render Furniture & Decor */}
      <InteriorManager interior={interior} room={room} />

      <Text
        position={[room.x + room.width / 2, 0.2, room.y + room.height / 2]}
        rotation={[-Math.PI / 2, 0, 0]}
        fontSize={1.2}
        color="#ffffff"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.05}
        outlineColor="#000000"
      >
        {room.id.toUpperCase().replace('_', ' ')}
      </Text>
    </group>
  );
};

export default RoomMesh;
