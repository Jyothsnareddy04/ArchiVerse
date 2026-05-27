import React from 'react';
import { Grid } from '@react-three/drei';

const GridFloor = () => {
  return (
    <Grid
      position={[0, -0.05, 0]}
      args={[200, 200]}
      cellSize={1}
      cellThickness={0.5}
      cellColor="#555555"
      sectionSize={10}
      sectionThickness={1}
      sectionColor="#888888"
      fadeDistance={100}
      fadeStrength={1}
      infiniteGrid
    />
  );
};

export default GridFloor;
