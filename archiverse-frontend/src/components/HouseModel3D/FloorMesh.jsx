import React from 'react';

const FloorMesh = ({ room, materialProps }) => {
  return (
    <mesh 
      position={[room.x + room.width / 2, 0, room.y + room.height / 2]} 
      rotation={[-Math.PI / 2, 0, 0]}
      receiveShadow
    >
      <planeGeometry args={[room.width, room.height]} />
      <meshStandardMaterial {...materialProps} />
    </mesh>
  );
};

export default FloorMesh;
