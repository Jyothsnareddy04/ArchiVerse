import React, { useState } from 'react';
import './index.css';
import './styles/global.css';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProjectProvider, useProject } from './context/ProjectContext';
import Sidebar from './components/Sidebar/Sidebar';
import WizardProgress from './components/WizardProgress/WizardProgress';
import HomePage from './components/HomePage/HomePage';
import LayoutForm from './components/LayoutForm/LayoutForm';
import BlueprintViewerStep from './components/BlueprintViewer/BlueprintViewerStep';
import ExteriorStyleSelector from './components/ExteriorStyleSelector/ExteriorStyleSelector';
import InteriorCustomizer from './components/InteriorCustomizer/InteriorCustomizer';
import FinalOverview from './components/FinalOverview/FinalOverview';
import CostEstimator from './components/CostEstimator/CostEstimator';
import LoginPage from './components/Auth/LoginPage';
import SignupPage from './components/Auth/SignupPage';
import ProfilePage from './components/Auth/ProfilePage';

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

function AppContent() {
  const { isAuthenticated } = useAuth();
  const [authMode, setAuthMode] = useState('login'); // 'login' | 'signup'

  if (!isAuthenticated) {
    return authMode === 'login'
      ? <LoginPage onSwitch={() => setAuthMode('signup')} />
      : <SignupPage onSwitch={() => setAuthMode('login')} />;
  }

  return (
    <ProjectProvider>
      <MainApp />
    </ProjectProvider>
  );
}

function MainApp() {
  const { state } = useProject();
  const { currentStep } = state;

  // Show profile page when step is -1
  if (currentStep === -1) {
    return (
      <div className="app-layout">
        <Sidebar />
        <main className="app-main">
          <ProfilePage />
        </main>
      </div>
    );
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="app-main">
        <WizardProgress />
        <StepRenderer />
      </main>
    </div>
  );
}

function StepRenderer() {
  const { state } = useProject();
  const { currentStep } = state;

  switch (currentStep) {
    case 0:
      return <HomePage />;
    case 1:
      return <LayoutForm />;
    case 2:
      return <BlueprintViewerStep />;
    case 3:
      return <ExteriorStyleSelector />;
    case 4:
      return <InteriorCustomizer />;
    case 5:
      return <FinalOverview />;
    case 6:
      return <CostEstimator />;
    default:
      return <HomePage />;
  }
}

export default App;
