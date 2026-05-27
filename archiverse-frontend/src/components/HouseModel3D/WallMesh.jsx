import React from 'react';

const WallMesh = ({ position, size, materialProps }) => {
  return (
    <mesh position={position} castShadow receiveShadow>
      <boxGeometry args={size} />
      <meshStandardMaterial {...materialProps} />
    </mesh>
  );
};

export default WallMesh;
