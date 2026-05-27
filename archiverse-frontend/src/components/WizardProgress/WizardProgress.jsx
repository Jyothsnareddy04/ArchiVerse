import React from 'react';
import { useProject } from '../../context/ProjectContext';

const steps = [
  { num: 1, label: 'Layout', displayNum: 1 },
  { num: 2, label: 'Blueprint', displayNum: 2 },
  { num: 3, label: 'Exterior', displayNum: 3 },
  { num: 4, label: 'Interior', displayNum: 4 },
  { num: 5, label: 'Overview', displayNum: 5 },
  { num: 6, label: 'Estimation', displayNum: 6 },
];

export default function WizardProgress() {
  const { state } = useProject();
  const { currentStep } = state;

  if (currentStep === 0) return null;

  return (
    <div className="wizard-progress">
      {steps.map((step, index) => (
        <React.Fragment key={step.num}>
          <div
            className={`wizard-step ${
              currentStep === step.num ? 'active' : ''
            } ${currentStep > step.num ? 'completed' : ''}`}
          >
            <div className="wizard-step-number">
              {currentStep > step.num ? '✓' : step.displayNum}
            </div>
            <span className="wizard-step-label">{step.label}</span>
          </div>
          {index < steps.length - 1 && (
            <div
              className={`wizard-step-connector ${
                currentStep > step.num ? 'active' : ''
              }`}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
