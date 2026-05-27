import React from 'react';
import FurnitureMesh from './FurnitureMesh';

const InteriorManager = ({ interior, room }) => {
  if (!interior || !interior.furniture) return null;

  return (
    <group>
      {interior.furniture.map((item, idx) => (
        <FurnitureMesh 
          key={`${interior.roomId}_furn_${idx}`} 
          item={item} 
          roomX={room.x} 
          roomY={room.y}
          roomWidth={room.width}
          roomHeight={room.height}
        />
      ))}
    </group>
  );
};

export default InteriorManager;
