import React from 'react';
import { FurnitureLibrary } from './FurnitureLibrary';

const FurnitureMesh = ({ item, roomX, roomY, roomWidth, roomHeight }) => {
  const type = item.type?.toLowerCase() || 'default';
  const Component = FurnitureLibrary[type] || FurnitureLibrary.default;
  
  // Default coordinate if none provided (center of the room)
  let posX = item.position?.[0];
  let posY = item.position?.[1] || 0; // elevation from floor
  let posZ = item.position?.[2];

  if (posX === undefined || posZ === undefined) {
    posX = roomWidth / 2;
    posZ = roomHeight / 2;
  }

  // Global world position
  const globalPosition = [
    roomX + posX,
    posY,
    roomY + posZ
  ];

  return (
    <Component 
      position={globalPosition} 
      rotation={item.rotation || [0, 0, 0]} 
      scale={item.scale || [1, 1, 1]} 
    />
  );
};

export default FurnitureMesh;
