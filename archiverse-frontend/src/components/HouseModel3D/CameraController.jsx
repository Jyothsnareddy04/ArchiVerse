import React from 'react';
import { OrbitControls } from '@react-three/drei';

const CameraController = ({ target = [0, 0, 0] }) => {
  return (
    <OrbitControls 
      makeDefault 
      target={target}
      minPolarAngle={0} 
      maxPolarAngle={Math.PI / 2 - 0.1} // Prevent going below ground
      minDistance={5}
      maxDistance={250}
      enableDamping={true}
      dampingFactor={0.05}
    />
  );
};

export default CameraController;
