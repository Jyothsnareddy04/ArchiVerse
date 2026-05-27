import React, { useEffect, useState, useMemo } from 'react';
import { useProject } from '../../context/ProjectContext';
import { estimateCost } from '../../services/api';
import './CostEstimator.css';

export default function CostEstimator() {
  const { state, dispatch } = useProject();
  const { costEstimation, layoutForm, selectedExterior, interiorSelections } = state;
  const [isLoading, setIsLoading] = useState(!costEstimation);

  // Count exterior and interior items
  const exteriorItemCount = selectedExterior ? 1 : 0;
  const interiorItemCount = Object.values(interiorSelections).reduce(
    (sum, roomSel) => sum + Object.keys(roomSel).length, 0
  );

  // Build interior items list for cost calculation (memoized)
  const interiorItemsList = useMemo(() => {
    const items = [];
    Object.entries(interiorSelections).forEach(([roomName, roomSel]) => {
      Object.entries(roomSel).forEach(([catId, optionId]) => {
        items.push({ room: roomName, category: catId, option: optionId });
      });
    });
    return items;
  }, [interiorSelections]);

  useEffect(() => {
    if (costEstimation) return;

    const fetchEstimation = async () => {
      setIsLoading(true);

      const area = (parseInt(layoutForm.plotLength) || 40) * (parseInt(layoutForm.plotWidth) || 60);

      // Pass complete data including exterior and interior selections for cost
      const result = await estimateCost({
        area: area,
        city: layoutForm.city || 'Bangalore',
        quality: layoutForm.quality || 'standard',
        floors: parseInt(layoutForm.floors) || 1,
        budget: layoutForm.budget ? parseInt(layoutForm.budget) : null,
        bedrooms: parseInt(layoutForm.bedrooms) || 3,
        // Exterior and interior counts for cost estimation
        exterior_style: selectedExterior?.id || null,
        exterior_item_count: exteriorItemCount,
        interior_items: interiorItemsList,
        interior_item_count: interiorItemCount,
      });
      dispatch({ type: 'SET_COST_ESTIMATION', payload: result });
      setIsLoading(false);
    };

    fetchEstimation();
  }, [costEstimation, layoutForm, selectedExterior, dispatch, exteriorItemCount, interiorItemCount, interiorItemsList]);

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner" />
        <p>Calculating cost estimation...</p>
        <span style={{ color: 'var(--text-tertiary)', fontSize: 12 }}>
          AI is analyzing layout, materials, exterior & interior selections
        </span>
      </div>
    );
  }

  if (!costEstimation) return null;

  const { breakdown, summary } = costEstimation;

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const budgetAmount = layoutForm.budget ? parseInt(layoutForm.budget) : null;
  const isOverBudget = costEstimation.budgetStatus === 'over_budget';
  const budgetGap = costEstimation.budgetGap;

  return (
    <div className="cost-estimator-container">
      <div className="step-header">
        <div className="step-header-icon">💰</div>
        <div>
          <h2>Cost Estimation</h2>
          <p>Detailed cost breakdown for your {layoutForm.plotLength}' × {layoutForm.plotWidth}' house design
            {layoutForm.city && <> in <strong>{layoutForm.city}</strong></>}
            {layoutForm.quality && <> ({layoutForm.quality} quality)</>}.
          </p>
        </div>
      </div>

      {/* Selection Summary Bar */}
      <div className="selection-summary-bar">
        <div className="selection-summary-item">
          <span className="summary-icon">🎨</span>
          <span className="summary-label">Exterior</span>
          <span className="summary-count">{exteriorItemCount} style</span>
        </div>
        <div className="selection-summary-divider" />
        <div className="selection-summary-item">
          <span className="summary-icon">🛋️</span>
          <span className="summary-label">Interior Furniture</span>
          <span className="summary-count">{interiorItemCount} items</span>
        </div>
        <div className="selection-summary-divider" />
        <div className="selection-summary-item">
          <span className="summary-icon">🏗️</span>
          <span className="summary-label">Total for Costing</span>
          <span className="summary-count summary-count-total">{exteriorItemCount + interiorItemCount} items</span>
        </div>
      </div>

      {/* Budget Status Alert */}
      {budgetAmount && (
        <div className={`budget-status-alert ${isOverBudget ? 'budget-over' : 'budget-ok'}`}>
          <div className="budget-status-icon">
            {isOverBudget ? '⚠️' : '✅'}
          </div>
          <div className="budget-status-content">
            <strong>{isOverBudget ? 'Over Budget' : 'Within Budget'}</strong>
            <span>
              Your budget: {formatCurrency(budgetAmount)} •
              Estimated: {formatCurrency(summary.totalCost)}
              {isOverBudget && budgetGap && (
                <> • Gap: <strong className="budget-gap">{formatCurrency(budgetGap)}</strong></>
              )}
            </span>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="cost-summary-grid">
        <div className="cost-summary-card cost-card-total">
          <span className="cost-card-label">Total Project Cost</span>
          <span className="cost-card-value cost-value-total">
            {formatCurrency(summary.totalCost)}
          </span>
          <span className="cost-card-sub">{formatCurrency(summary.costPerSqFt)} / sq ft</span>
        </div>
        <div className="cost-summary-card">
          <span className="cost-card-label">Construction</span>
          <span className="cost-card-value">{formatCurrency(summary.constructionCost)}</span>
          <span className="cost-card-sub">Structure & Build</span>
        </div>
        <div className="cost-summary-card">
          <span className="cost-card-label">Exterior Design</span>
          <span className="cost-card-value">{formatCurrency(summary.exteriorCost)}</span>
          <span className="cost-card-sub">{exteriorItemCount} style applied</span>
        </div>
        <div className="cost-summary-card">
          <span className="cost-card-label">Interior Design</span>
          <span className="cost-card-value">{formatCurrency(summary.interiorCost)}</span>
          <span className="cost-card-sub">{interiorItemCount} furniture items</span>
        </div>
      </div>

      {/* LLM Optimization Suggestions (if over budget) */}
      {isOverBudget && costEstimation.llmOptimization && (
        <div className="llm-optimization-card">
          <h3>💡 AI Cost Optimization Suggestions</h3>
          <p className="optimization-text">{costEstimation.llmOptimization}</p>
        </div>
      )}

      {/* Market Context */}
      {costEstimation.marketContext && (
        <div className="market-context-card">
          <h4>📊 Market Rates ({layoutForm.city})</h4>
          <div className="market-rates-grid">
            {Object.entries(costEstimation.marketContext).map(([material, rate]) => (
              <div key={material} className="market-rate-item">
                <span className="market-material">{material}</span>
                <span className="market-rate">{formatCurrency(rate)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Breakdown */}
      <div className="cost-breakdown-card">
        <h3>Detailed Breakdown</h3>
        <div className="breakdown-table">
          <div className="breakdown-header">
            <span>Category</span>
            <span>Description</span>
            <span>Cost</span>
            <span>Share</span>
          </div>
          {breakdown.map((item, index) => {
            const share = ((item.cost / summary.totalCost) * 100).toFixed(1);
            return (
              <div
                key={index}
                className="breakdown-row"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <span className="breakdown-category">{item.category}</span>
                <span className="breakdown-desc">{item.description}</span>
                <span className="breakdown-cost">{formatCurrency(item.cost)}</span>
                <span className="breakdown-share">
                  <div className="share-bar">
                    <div
                      className="share-fill"
                      style={{ width: `${share}%` }}
                    />
                  </div>
                  <span>{share}%</span>
                </span>
              </div>
            );
          })}
          <div className="breakdown-row breakdown-total">
            <span className="breakdown-category">Total</span>
            <span className="breakdown-desc" />
            <span className="breakdown-cost">{formatCurrency(summary.totalCost)}</span>
            <span className="breakdown-share">
              <span>100%</span>
            </span>
          </div>
        </div>
      </div>

      <div className="wizard-nav">
        <button
          className="btn btn-secondary"
          onClick={() => dispatch({ type: 'SET_STEP', payload: 5 })}
        >
          ← Back to Overview
        </button>
        <button
          className="btn btn-primary btn-lg"
          onClick={() => {
            dispatch({ type: 'RESET_PROJECT' });
          }}
          id="new-project-btn"
        >
          🏠 Start New Project
        </button>
      </div>
    </div>
  );
}
