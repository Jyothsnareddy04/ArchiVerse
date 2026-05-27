import React from 'react';

const Lighting = () => {
  return (
    <>
      <ambientLight intensity={0.6} />
      <directionalLight 
        position={[30, 80, 30]} 
        intensity={1.5} 
        castShadow 
        shadow-mapSize-width={2048} 
        shadow-mapSize-height={2048}
        shadow-camera-left={-60}
        shadow-camera-right={60}
        shadow-camera-top={60}
        shadow-camera-bottom={-60}
        shadow-camera-near={0.1}
        shadow-camera-far={200}
        shadow-bias={-0.0005} // Prevent shadow acne
      />
      <directionalLight position={[-30, 40, -30]} intensity={0.5} />
    </>
  );
};

export default Lighting;
