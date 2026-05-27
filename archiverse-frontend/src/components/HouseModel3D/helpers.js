export const generateWalls = (room, wallHeight, wallThickness) => {
  const { x, y, width, height } = room;
  const h = wallHeight;
  const t = wallThickness;

  return [
    {
      id: `${room.id}_wall_top`,
      position: [x + width / 2, h / 2, y],
      size: [width + t, h, t],
    },
    {
      id: `${room.id}_wall_bottom`,
      position: [x + width / 2, h / 2, y + height],
      size: [width + t, h, t],
    },
    {
      id: `${room.id}_wall_left`,
      position: [x, h / 2, y + height / 2],
      size: [t, h, height - t],
    },
    {
      id: `${room.id}_wall_right`,
      position: [x + width, h / 2, y + height / 2],
      size: [t, h, height - t],
    },
  ];
};

export const generatePlaceholders = (room) => {
  const t = 0.6; // slightly thicker than wall to prevent z-fighting
  const placeholders = [];

  // Add a fake door placeholder on the bottom wall (just for visualization)
  placeholders.push({
    id: `${room.id}_door`,
    type: 'door',
    position: [room.x + room.width / 2, 3.5, room.y + room.height],
    size: [3, 7, t], // 3ft wide, 7ft tall
    color: '#3e2723' // dark brown
  });

  // Add a fake window placeholder on the top wall
  placeholders.push({
    id: `${room.id}_window`,
    type: 'window',
    position: [room.x + room.width / 2, 5, room.y],
    size: [4, 4, t], // 4ft x 4ft
    color: '#81d4fa' // light blue
  });

  return placeholders;
};
