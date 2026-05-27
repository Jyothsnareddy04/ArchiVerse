import React, { createContext, useContext, useReducer } from 'react';

const ProjectContext = createContext();

const initialState = {
  currentStep: 0, // 0 = home, 1-6 = wizard steps
  projectStarted: false,

  // Step 1: Layout
  layoutForm: {
    plotLength: '',
    plotWidth: '',
    bedrooms: '3',
    additionalRooms: [],
    roadFacing: 'West',
    budget: '',
    city: 'Bangalore',
    quality: 'standard',
    floors: '1',
  },
  generatedLayouts: [],
  selectedLayout: null,
  editedRooms: null, // rooms after user edits in the editor
  isGeneratingLayouts: false,

  // Step 2: Blueprint (West + North facing)
  blueprintData: null,
  blueprintReady: false,

  // Step 3: Exterior
  selectedExterior: null,

  // Step 4: Interior
  interiorSelections: {},
  furniturePlacements: {}, // { [roomName]: { [categoryId]: { x, y } } }

  // Step 5: Final overview (derived from above)

  // Step 6: Cost estimation
  costEstimation: null,
  isEstimatingCost: false,
};

function projectReducer(state, action) {
  switch (action.type) {
    case 'START_PROJECT':
      return { ...state, projectStarted: true, currentStep: 1 };

    case 'SET_STEP':
      return { ...state, currentStep: action.payload };

    case 'UPDATE_LAYOUT_FORM':
      return {
        ...state,
        layoutForm: { ...state.layoutForm, ...action.payload },
      };

    case 'SET_GENERATING_LAYOUTS':
      return { ...state, isGeneratingLayouts: action.payload };

    case 'SET_GENERATED_LAYOUTS':
      return {
        ...state,
        generatedLayouts: action.payload || [],
        isGeneratingLayouts: false,
      };

    case 'SELECT_LAYOUT':
      return { ...state, selectedLayout: action.payload, editedRooms: action.payload.rooms ? [...action.payload.rooms] : null };

    case 'SET_EDITED_ROOMS':
      return { ...state, editedRooms: action.payload };

    case 'SET_BLUEPRINT_DATA':
      return { ...state, blueprintData: action.payload, blueprintReady: true };

    case 'SELECT_EXTERIOR':
      return { ...state, selectedExterior: action.payload };

    case 'UPDATE_INTERIOR_SELECTION': {
      const { room, category, optionId } = action.payload;
      const roomSelections = state.interiorSelections[room] || {};
      return {
        ...state,
        interiorSelections: {
          ...state.interiorSelections,
          [room]: {
            ...roomSelections,
            [category]: optionId,
          },
        },
      };
    }

    case 'UPDATE_FURNITURE_PLACEMENT': {
      const { room, category, x, y } = action.payload;
      const roomPlacements = state.furniturePlacements[room] || {};
      return {
        ...state,
        furniturePlacements: {
          ...state.furniturePlacements,
          [room]: {
            ...roomPlacements,
            [category]: { x, y },
          },
        },
      };
    }

    case 'SET_COST_ESTIMATION':
      return {
        ...state,
        costEstimation: action.payload,
        isEstimatingCost: false,
      };

    case 'SET_ESTIMATING_COST':
      return { ...state, isEstimatingCost: action.payload };

    case 'RESET_PROJECT':
      return { ...initialState };

    default:
      return state;
  }
}

export function ProjectProvider({ children }) {
  const [state, dispatch] = useReducer(projectReducer, initialState);

  return (
    <ProjectContext.Provider value={{ state, dispatch }}>
      {children}
    </ProjectContext.Provider>
  );
}

export function useProject() {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error('useProject must be used within a ProjectProvider');
  }
  return context;
}

export default ProjectContext;
