import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ===== Layout Generation =====
export const generateLayouts = async (formData) => {
  try {
    // Transform frontend layoutForm to backend LayoutRequest schema
    const payload = {
      plot_width: parseInt(formData.plotWidth) || 0,
      plot_depth: parseInt(formData.plotLength) || 0,
      floors: parseInt(formData.floors) || 1,
      preferences: {
        bedrooms: parseInt(formData.bedrooms) || 3,
        has_store: formData.additionalRooms?.includes('Store') || false,
        has_backyard: formData.additionalRooms?.includes('Backyard') || false,
        has_dining: formData.additionalRooms?.includes('Dining') || false,
        plant_sides: formData.additionalRooms?.includes('Plants Space') || false,
        budget: formData.budget ? parseInt(formData.budget) : null,
        city: formData.city || 'Bangalore',
        quality: formData.quality || 'standard',
      }
    };

    const response = await api.post('/layout/generate', payload);
    
    // Transform backend UI output mapping
    if (response.data && response.data.data && response.data.data.layouts) {
      const layoutsDict = response.data.data.layouts;
      const transformedLayouts = Object.values(layoutsDict).map((layout, idx) => {
        const processedRooms = (layout.rooms || []).map(r => {
          if (r.rects && r.rects.length > 0) {
            // Find largest rect for canonical labeling and coordinates
            let largest = r.rects[0];
            let maxArea = (largest.width || largest.w) * (largest.height || largest.h);
            r.rects.forEach(rect => {
              const area = (rect.width || rect.w) * (rect.height || rect.h);
              if (area > maxArea) {
                maxArea = area;
                largest = rect;
              }
            });

            return {
              id: r.id || `room-${Math.random()}`,
              name: r.name,
              x: largest.x,
              y: largest.y,
              width: largest.width || largest.w,
              height: largest.height || largest.h,
              rects: r.rects, // Provide the full geometric data for the renderer
              door: r.door || null,
              area: r.area || (layout.plot_width * layout.plot_depth) // Use room area if available
            };
          } else {
            // Single rectangle room
            return {
              id: r.id || `room-${Math.random()}`,
              name: r.name || 'Room',
              x: r.x,
              y: r.y,
              width: r.w || r.width,
              height: r.h || r.height,
              area: r.area || ((r.w || r.width) * (r.h || r.height)),
              door: r.door || null
            };
          }
        });

        return {
          id: layout.id || `layout-${idx}-${Math.random()}`,
          name: layout.name || `Variant ${idx + 1}`,
          area: layout.area || payload.plot_width * payload.plot_depth,
          rooms: processedRooms,
          image: layout.image, // Pass the backend generated base64 image
        };
      });
      return { layouts: transformedLayouts };
    }

    return response.data;
  } catch (error) {
    console.error('Layout generation failed:', error);
    // Return mock data as fallback
    return getMockLayouts(formData);
  }
};

// ===== Blueprint Generation =====
export const generateBlueprint = async (layoutData) => {
  try {
    const response = await api.post('/blueprint/generate', { 
      layout_id: layoutData.id || 'custom',
      layout_data: layoutData 
    });
    return response.data;
  } catch (error) {
    console.error('Blueprint generation failed:', error);
    return null;
  }
};

// ===== 3D Model Generation =====
export const generate3DModel = async (blueprintData) => {
  try {
    const response = await api.post('/models/generate-3d', blueprintData);
    return response.data;
  } catch (error) {
    console.error('3D model generation failed:', error);
    return null;
  }
};

// ===== Apply Exterior =====
export const applyExteriorDesign = async (projectId, designId) => {
  try {
    const response = await api.post('/exterior/generate', { projectId, designId });
    return response.data;
  } catch (error) {
    console.error('Exterior design application failed:', error);
    return null;
  }
};

// ===== Apply Interior =====
export const applyInteriorDesign = async (projectId, selections) => {
  try {
    const response = await api.post('/interior/generate', { projectId, selections });
    return response.data;
  } catch (error) {
    console.error('Interior design application failed:', error);
    return null;
  }
};

// ===== Cost Estimation =====
export const estimateCost = async (projectData) => {
  try {
    // Build the payload matching the backend cost_service.estimate_cost() expected input:
    // Required: city, quality, built_up_area, floors
    // Optional: budget, interior_preferences, exterior_style, interior_items
    const payload = {
      city: projectData.city || 'Bangalore',
      quality: projectData.quality || 'standard',
      built_up_area: projectData.area || projectData.built_up_area || 2000,
      floors: parseInt(projectData.floors) || 1,
      budget: projectData.budget ? parseInt(projectData.budget) : null,
      interior_preferences: projectData.interior_preferences || {
        kitchen: 'standard',
        bathroom: 'standard',
      },
      // Exterior and interior selections for cost calculation
      exterior_style: projectData.exterior_style || null,
      exterior_item_count: projectData.exterior_item_count || 0,
      interior_items: projectData.interior_items || [],
      interior_item_count: projectData.interior_item_count || 0,
    };

    const response = await api.post('/cost/estimate', payload);
    
    // Transform backend response to frontend expected format
    if (response.data && response.data.cost) {
      const cost = response.data.cost;
      return {
        breakdown: [
          { category: 'Construction & Structure', cost: cost.construction_cost, description: 'Foundation, columns, beams, slabs, masonry' },
          { category: 'Cement', cost: cost.material_breakdown?.cement || 0, description: `${(cost.material_ratio?.cement * 100)?.toFixed(1) || 0}% of materials` },
          { category: 'Steel', cost: cost.material_breakdown?.steel || 0, description: `${(cost.material_ratio?.steel * 100)?.toFixed(1) || 0}% of materials` },
          { category: 'Sand & Aggregates', cost: cost.material_breakdown?.sand || 0, description: `${(cost.material_ratio?.sand * 100)?.toFixed(1) || 0}% of materials` },
          { category: 'Interior Design', cost: cost.interior_cost, description: `${payload.interior_item_count} furniture items selected` },
          { category: 'Exterior Design', cost: cost.exterior_cost, description: `${payload.exterior_item_count} exterior style applied` },
          { category: 'Plumbing', cost: cost.plumbing_cost, description: 'Pipes, fixtures, tanks, drainage' },
          { category: 'Electrical', cost: cost.electrical_cost, description: 'Wiring, switches, panels, fixtures' },
          { category: 'Labor', cost: cost.labor_cost, description: 'Skilled & unskilled labor charges' },
          { category: 'Contractor Margin', cost: cost.contractor_margin, description: '12% contractor profit margin' },
          { category: 'Contingency', cost: cost.contingency, description: '8% contingency reserve' },
          { category: 'GST', cost: cost.gst, description: '5% Goods & Services Tax' },
        ],
        summary: {
          constructionCost: cost.construction_cost,
          interiorCost: cost.interior_cost,
          exteriorCost: cost.exterior_cost,
          totalCost: cost.total_cost,
          costPerSqFt: Math.round(cost.total_cost / (payload.built_up_area * payload.floors)),
          area: payload.built_up_area,
          baseCost: cost.base_cost,
        },
        budgetStatus: response.data.status,
        budgetGap: response.data.budget_gap || null,
        llmOptimization: response.data.llm_optimization || null,
        marketContext: response.data.market_context || null,
        boq: cost.boq || null,
      };
    }

    return response.data;
  } catch (error) {
    console.error('Cost estimation failed:', error);
    return getMockCostEstimation(projectData);
  }
};

// ===== Mock Data Generators =====

const getMockLayouts = (formData) => {
  const { additionalRooms = [] } = formData || {};
  
  return {
    layouts: [
      {
        id: 'layout-signature',
        name: 'Signature Boxy Layout',
        description: 'A 2500 sq ft 2BHK layout following your exact structural drawing. Optimized for a grand living experience.',
        area: 2500,
        bedrooms: 2,
        bathrooms: 2,
        additionalRooms: ['Balcony', 'Dining Room'],
        features: ['Signature Design', 'Boxy Structure', 'Maximized Hall'],
        demoImages: {
          layout: '/images/demo/layout_user.png',
        },
        rooms: generateRooms(2500, 2, 2, ['Balcony', 'Dining Room'], 'luxury'),
      },
      {
        id: 'layout-1',
        name: 'Variation A - Open Hall',
        description: `2500 sq ft open-concept version of your signature structure.`,
        area: 2500,
        bedrooms: 2,
        bathrooms: 2,
        additionalRooms: additionalRooms,
        features: ['Increased Ventilation', 'Integrated Dining'],
        demoImages: {
          layout: '/images/demo/layout_1.png',
        },
        rooms: generateRooms(2500, 2, 2, additionalRooms, 'open'),
      },
      {
        id: 'layout-2',
        name: 'Variation B - Compact Core',
        description: `2500 sq ft version with optimized utility zones and a traditional hall layout.`,
        area: 2500,
        bedrooms: 2,
        bathrooms: 2,
        additionalRooms: additionalRooms,
        features: ['Compact Utility', 'Privacy Zones'],
        demoImages: {
          layout: '/images/demo/layout_2.png',
        },
        rooms: generateRooms(2500, 2, 2, additionalRooms, 'traditional'),
      },
    ],
  };
};

function generateRooms(totalArea, bedrooms, bathrooms, additionalRooms, style) {
  const rooms = [];
  const padding = 10;
  const unitScale = totalArea / 2500; // adjust sizes relative to 2500sqft base

  // 1. Central Grand Hall
  const hallW = 40 * Math.sqrt(unitScale);
  const hallH = 25 * Math.sqrt(unitScale);
  const hallX = padding + 15;
  const hallY = padding + 5;
  
  rooms.push({
    id: 'hall',
    name: 'Grand Living & Dining Hall',
    width: hallW,
    height: hallH,
    x: hallX,
    y: hallY,
    area: Math.round(totalArea * 0.35),
    door: { side: 'top', pos: 0.2 }, // Entrance from Foyer
  });

  // 2. Kitchen (Attached to Hall)
  const kitchenW = 15;
  const kitchenH = 15;
  rooms.push({
    id: 'kitchen',
    name: 'Modular Kitchen',
    width: kitchenW,
    height: kitchenH,
    x: hallX - kitchenW, // Flush but distinct wall
    y: hallY + 2,
    area: Math.round(totalArea * 0.1),
    door: { side: 'right', pos: 0.3 }, // Entrance into kitchen from hall
  });

  // 3. Master Bedroom + Attached Bath
  const mbW = 20;
  const mbH = 18;
  const mbX = hallX;
  const mbY = hallY + hallH + 1;
  
  rooms.push({
    id: 'master-bed',
    name: 'Master Suite',
    width: mbW,
    height: mbH,
    x: mbX,
    y: mbY,
    area: Math.round(totalArea * 0.2),
    door: { side: 'top', pos: 0.3 }, // Entrance from hall
  });

  // Attached Bath for Master
  rooms.push({
    id: 'master-bath',
    name: 'Primary Bath (Attached)',
    width: 8,
    height: 8,
    x: mbX + 1,
    y: mbY + mbH,
    area: 80,
    door: { side: 'top', pos: 0.5 }, // Internal entrance from suite
  });

  // 4. Guest Bedroom + Attached/Common Bath
  const gbW = 18;
  const gbH = 18;
  const gbX = hallX + hallW - 18;
  const gbY = hallY + hallH + 1;

  rooms.push({
    id: 'guest-bed',
    name: 'Guest Bedroom',
    width: gbW,
    height: gbH,
    x: gbX,
    y: gbY,
    area: Math.round(totalArea * 0.15),
    door: { side: 'top', pos: 0.7 }, // Entrance from hall
  });

  // Attached/Common Bath for Guest
  rooms.push({
    id: 'guest-bath',
    name: 'Common Bath',
    width: 8,
    height: 8,
    x: gbX + gbW - 9,
    y: gbY + gbH,
    area: 75,
    door: { side: 'top', pos: 0.5 }, // Internal entrance from bedroom
  });

  // 5. Entry Foyer & Balcony
  rooms.push({
    id: 'entry',
    name: 'Entry Foyer',
    width: 10,
    height: 6,
    x: hallX + 3,
    y: hallY - 6.5,
    area: 120,
    door: { side: 'top', pos: 0.5 }, // Main outside door
  });

  if (additionalRooms.includes('Balcony')) {
    rooms.push({
      id: 'balcony',
      name: 'Sky Balcony',
      width: hallW,
      height: 5,
      x: hallX,
      y: hallY - 6,
      area: 250,
      door: { side: 'bottom', pos: 0.5 }, // Entrance from hall
    });
  }

  return rooms;
}

const getMockCostEstimation = (projectData) => {
  const area = projectData.area || 2000;
  const baseRate = 1800; // per sq ft
  const interiorCount = projectData.interior_item_count || 0;
  const exteriorCount = projectData.exterior_item_count || 0;

  // Calculate furniture cost based on items
  const furnitureCostPerItem = 25000;
  const selectedFurnitureCost = interiorCount * furnitureCostPerItem;

  const constructionCost = area * baseRate;
  const exteriorCost = Math.round(constructionCost * 0.12);
  const interiorCost = Math.round(constructionCost * 0.15) + selectedFurnitureCost;
  const miscCost = Math.round(constructionCost * 0.08);

  return {
    breakdown: [
      { category: 'Foundation & Structure', cost: Math.round(constructionCost * 0.3), description: 'RCC frame, foundation, columns, beams, slabs' },
      { category: 'Walls & Masonry', cost: Math.round(constructionCost * 0.15), description: 'Brick work, plastering, waterproofing' },
      { category: 'Electrical & Plumbing', cost: Math.round(constructionCost * 0.12), description: 'Wiring, switches, pipes, fixtures' },
      { category: 'Flooring', cost: Math.round(constructionCost * 0.1), description: 'Vitrified tiles, marble, wooden flooring' },
      { category: 'Doors & Windows', cost: Math.round(constructionCost * 0.08), description: 'Wooden doors, UPVC windows, hardware' },
      { category: 'Exterior Design', cost: exteriorCost, description: `${exteriorCount} exterior style applied` },
      { category: 'Interior Design', cost: interiorCost, description: `${interiorCount} furniture items selected` },
      { category: 'Painting & Finishing', cost: Math.round(constructionCost * 0.05), description: 'Interior & exterior paint, polish, POP' },
      { category: 'Miscellaneous', cost: miscCost, description: 'Permits, architect fees, contingency' },
    ],
    summary: {
      constructionCost,
      exteriorCost,
      interiorCost,
      totalCost: constructionCost + exteriorCost + interiorCost + miscCost,
      costPerSqFt: baseRate + Math.round((exteriorCost + interiorCost + miscCost) / area),
      area,
    },
  };
};

export default api;
