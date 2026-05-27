export const getRoomMaterial = (roomType, style) => {
  // Base architectural theme defaults
  const theme = {
    floor: { color: '#8ecae6', roughness: 0.8, metalness: 0.1 },
    wall: { color: '#333333', roughness: 0.9, metalness: 0.1 }
  };

  // Determine material properties based on room type and interior style
  if (roomType === 'bedroom') {
    theme.floor.color = style === 'luxury' ? '#5c4033' : '#d4a373'; // dark wood vs light wood
    theme.wall.color = style === 'luxury' ? '#2f3640' : '#f5f6fa';
  } else if (roomType === 'living') {
    theme.floor.color = style === 'modern' ? '#bdc3c7' : '#e0e0e0';
    theme.wall.color = style === 'luxury' ? '#353b48' : '#ffffff';
  } else if (roomType === 'kitchen') {
    theme.floor.color = '#7f8c8d';
    theme.wall.color = '#ecf0f1';
  } else if (roomType === 'bathroom') {
    theme.floor.color = '#95a5a6'; // Tiles
    theme.wall.color = '#bdc3c7';
    theme.floor.roughness = 0.2; // Shiny tiles
  } else if (roomType === 'dining') {
    theme.floor.color = style === 'luxury' ? '#7f8fa6' : '#dcdde1';
    theme.wall.color = '#f5f6fa';
  }

  // Generic style overrides
  if (style === 'minimal') {
    theme.floor.color = '#ecf0f1';
    theme.wall.color = '#ffffff';
  } else if (style === 'contemporary') {
    theme.floor.color = '#a4b0be';
    theme.wall.color = '#dfe4ea';
  }

  return theme;
};
