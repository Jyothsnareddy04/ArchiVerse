import React from 'react';

const BoxFurniture = ({ size, color, position, rotation, scale }) => {
  // Auto-align vertically so furniture rests exactly on the floor
  const yOffset = position[1] + size[1] / 2;
  return (
    <mesh 
      position={[position[0], yOffset, position[2]]} 
      rotation={rotation} 
      scale={scale}
      castShadow 
      receiveShadow
    >
      <boxGeometry args={size} />
      <meshStandardMaterial color={color} roughness={0.6} />
    </mesh>
  );
};

export const FurnitureLibrary = {
  bed: (props) => <BoxFurniture size={[6, 2, 7]} color="#ecf0f1" {...props} />, // Whiteish bed
  sofa: (props) => <BoxFurniture size={[7, 2.5, 3]} color="#34495e" {...props} />, // Dark sofa
  wardrobe: (props) => <BoxFurniture size={[4, 8, 2]} color="#8e44ad" {...props} />, // Purple wardrobe
  tvunit: (props) => <BoxFurniture size={[6, 2, 1.5]} color="#2c3e50" {...props} />, 
  diningtable: (props) => <BoxFurniture size={[6, 2.5, 4]} color="#d35400" {...props} />, // Wooden dining
  chair: (props) => <BoxFurniture size={[1.5, 3, 1.5]} color="#27ae60" {...props} />,
  kitchenplatform: (props) => <BoxFurniture size={[8, 3, 2]} color="#7f8c8d" {...props} />,
  sink: (props) => <BoxFurniture size={[2, 2.5, 1.5]} color="#bdc3c7" {...props} />,
  toilet: (props) => <BoxFurniture size={[1.5, 2, 2.5]} color="#ecf0f1" {...props} />,
  lights: (props) => {
    const yOffset = props.position[1] + 9; // Place near ceiling (assuming 10ft wall)
    return (
      <group position={[props.position[0], yOffset, props.position[2]]} rotation={props.rotation}>
        <mesh>
          <sphereGeometry args={[0.5]} />
          <meshStandardMaterial color="#f1c40f" emissive="#f1c40f" emissiveIntensity={1} />
        </mesh>
        <pointLight intensity={1} distance={15} color="#f1c40f" castShadow />
      </group>
    );
  },
  default: (props) => <BoxFurniture size={[2, 2, 2]} color="#95a5a6" {...props} />
};
