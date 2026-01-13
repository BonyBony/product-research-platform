// State
let simulationData = null;

// DOM Elements
const form = document.getElementById('simulationForm');
const loadingState = document.getElementById('loadingState');
const inputSection = document.getElementById('inputSection');
const userProfileSection = document.getElementById('userProfileSection');
const scenariosSection = document.getElementById('scenariosSection');
const summarySection = document.getElementById('summarySection');

// Form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        problem_statement: document.getElementById('problemStatement').value,
        target_users: document.getElementById('targetUsers').value,
        product_flow: document.getElementById('productFlow').value,
        num_scenarios: parseInt(document.getElementById('numScenarios').value)
    };

    await runSimulation(formData);
});

async function runSimulation(data) {
    try {
        // Show loading
        loadingState.style.display = 'block';
        inputSection.style.display = 'none';
        userProfileSection.style.display = 'none';
        scenariosSection.style.display = 'none';
        summarySection.style.display = 'none';

        // Call API
        const response = await fetch('http://localhost:8001/api/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        simulationData = await response.json();

        // Hide loading
        loadingState.style.display = 'none';

        // Display results
        displayUserProfile(simulationData.virtual_user);
        displayScenarios(simulationData.scenarios);
        displaySummary(simulationData);

        // Show sections
        inputSection.style.display = 'block';
        userProfileSection.style.display = 'block';
        scenariosSection.style.display = 'block';
        summarySection.style.display = 'block';

        // Scroll to results
        userProfileSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Simulation error:', error);
        alert('Error running simulation: ' + error.message);
        loadingState.style.display = 'none';
        inputSection.style.display = 'block';
    }
}

function displayUserProfile(user) {
    const container = document.getElementById('userProfileCard');

    const sensitivitiesHTML = user.sensitivities.map(s => `
        <div class="attribute-bar">
            <div class="attribute-label">
                <span>${s.name.replace(/_/g, ' ').toUpperCase()}</span>
                <span>${s.level}/10</span>
            </div>
            <div class="attribute-progress">
                <div class="attribute-fill" style="width: ${s.level * 10}%"></div>
            </div>
        </div>
    `).join('');

    const traitsHTML = user.traits.map(t => `
        <div class="attribute-bar">
            <div class="attribute-label">
                <span>${t.name.replace(/_/g, ' ').toUpperCase()}</span>
                <span>${t.value}/10</span>
            </div>
            <div class="attribute-progress">
                <div class="attribute-fill" style="width: ${t.value * 10}%"></div>
            </div>
        </div>
    `).join('');

    container.innerHTML = `
        <div class="user-basic-info">
            <h3>${user.name}</h3>
            <p>${user.age} years old, ${user.occupation}</p>
            <p>${user.location}</p>
            <p style="margin-top: 1rem; font-style: italic;">"${user.problem_context}"</p>
            <p style="margin-top: 0.5rem; font-weight: 600;">Goal: ${user.primary_goal}</p>
            <p style="margin-top: 0.5rem;">Patience: ${user.patience_level.toUpperCase()}</p>
        </div>
        <div class="user-attributes">
            <h4>Sensitivities</h4>
            ${sensitivitiesHTML}
            <h4 style="margin-top: 1.5rem;">Behavioral Traits</h4>
            ${traitsHTML}
        </div>
    `;
}

function displayScenarios(scenarios) {
    const container = document.getElementById('scenariosContainer');

    const scenariosHTML = scenarios.map(scenario => {
        const outcomeClass = scenario.outcome.toLowerCase().includes('churn') ? 'churned' :
                           scenario.outcome.toLowerCase().includes('partial') ? 'partial' : 'success';

        const churnClass = scenario.final_churn_probability < 30 ? 'low' :
                          scenario.final_churn_probability < 50 ? 'medium' :
                          scenario.final_churn_probability < 75 ? 'high' : 'critical';

        const stepsHTML = scenario.steps.map(step => createStepHTML(step)).join('');

        const insightsHTML = scenario.key_insights.map(insight => `<li>${insight}</li>`).join('');

        return `
            <div class="scenario-card ${scenario.scenario_type}">
                <div class="scenario-header">
                    <div class="scenario-title">
                        <h3>${scenario.scenario_name}</h3>
                        <span class="scenario-type ${scenario.scenario_type}">${scenario.scenario_type.replace(/_/g, ' ')}</span>
                    </div>
                    <div class="scenario-outcome">
                        <span class="outcome-badge ${outcomeClass}">${scenario.outcome}</span>
                        <div class="churn-meter">
                            <span>Churn Risk:</span>
                            <div class="churn-bar">
                                <div class="churn-fill ${churnClass}" style="width: ${scenario.final_churn_probability}%"></div>
                            </div>
                            <span style="font-weight: 700;">${scenario.final_churn_probability.toFixed(0)}%</span>
                        </div>
                    </div>
                </div>

                <p style="color: var(--text-light); margin-bottom: 1.5rem;">${scenario.description}</p>

                <div class="journey-timeline">
                    ${stepsHTML}
                </div>

                <div style="margin-top: 2rem; padding: 1rem; background: var(--bg); border-radius: 0.5rem;">
                    <h4 style="margin-bottom: 0.5rem;">Key Insights:</h4>
                    <ul style="margin-left: 1.5rem;">
                        ${insightsHTML}
                    </ul>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = scenariosHTML;
}

function createStepHTML(step) {
    const emotionBadge = `<span class="emotion-badge ${step.emotional_state}">${step.emotional_state}</span>`;
    const timeBadge = `<span>${formatTime(step.time_elapsed)}</span>`;

    let stepContent = `
        <div class="journey-step">
            <div class="step-marker ${step.step_type}">${step.step_number}</div>
            <div class="step-content ${step.is_decision_point ? 'decision-point' : ''}">
                <div class="step-header">
                    <div class="step-description">${step.description}</div>
                    <div class="step-meta">
                        ${emotionBadge}
                        ${timeBadge}
                    </div>
                </div>
    `;

    // Decision point
    if (step.is_decision_point && step.decision_options.length > 0) {
        const optionsHTML = step.decision_options.map(opt => `
            <li class="decision-option ${opt.option_id === step.chosen_option ? 'chosen' : ''}">
                ${opt.description}
                ${opt.option_id === step.chosen_option ? ' ✓' : ''}
            </li>
        `).join('');

        stepContent += `
            <div class="decision-section">
                <h4>DECISION POINT</h4>
                <ul class="decision-options">
                    ${optionsHTML}
                </ul>
                <div class="decision-reasoning">
                    <strong>Why this choice?</strong><br>
                    ${step.decision_reasoning}
                </div>
            </div>
        `;
    }

    // Churn analysis
    if (step.churn_analysis) {
        const analysis = step.churn_analysis;
        const frustrationHTML = analysis.frustration_events.map(e => `
            <div class="frustration-event">
                <span class="event-name">${e.event.replace(/_/g, ' ')}</span>
                <span class="event-risk">+${e.risk_added.toFixed(0)}%</span>
            </div>
        `).join('');

        stepContent += `
            <div class="churn-analysis">
                <h4>
                    Churn Probability: <span class="churn-risk-badge ${analysis.risk_level}">${analysis.risk_level}</span>
                    <span style="font-size: 1.5rem; margin-left: 0.5rem;">${analysis.final_churn_probability.toFixed(0)}%</span>
                </h4>

                <div class="churn-breakdown">
                    <div class="churn-stat">
                        <div class="churn-stat-value">${analysis.base_risk}%</div>
                        <div class="churn-stat-label">Base</div>
                    </div>
                    <div class="churn-stat">
                        <div class="churn-stat-value">${analysis.formula_risk.toFixed(0)}%</div>
                        <div class="churn-stat-label">+ Frustration</div>
                    </div>
                    <div class="churn-stat">
                        <div class="churn-stat-value">${analysis.patience_multiplier}x</div>
                        <div class="churn-stat-label">× Patience</div>
                    </div>
                    <div class="churn-stat">
                        <div class="churn-stat-value">${analysis.calculated_risk.toFixed(0)}%</div>
                        <div class="churn-stat-label">= Calculated</div>
                    </div>
                </div>

                <div class="churn-reasoning">
                    ${analysis.reasoning}
                </div>

                ${analysis.frustration_events.length > 0 ? `
                    <div class="frustration-events">
                        <strong style="font-size: 0.75rem; color: var(--text-light);">Frustration Events:</strong>
                        ${frustrationHTML}
                    </div>
                ` : ''}
            </div>
        `;
    }

    stepContent += `
            </div>
        </div>
    `;

    return stepContent;
}

function displaySummary(data) {
    // Summary insights
    const insightsHTML = data.summary_insights.map(insight => `<li>${insight}</li>`).join('');
    document.getElementById('summaryInsights').innerHTML = insightsHTML;

    // Churn hotspots
    const hotspotsHTML = data.churn_hotspots.length > 0
        ? data.churn_hotspots.map(hotspot => `<li>${hotspot}</li>`).join('')
        : '<li>No critical churn hotspots identified</li>';
    document.getElementById('churnHotspots').innerHTML = hotspotsHTML;

    // Recommendations
    const recommendationsHTML = data.recommendations.length > 0
        ? data.recommendations.map(rec => `<li>${rec}</li>`).join('')
        : '<li>Continue monitoring user behavior patterns</li>';
    document.getElementById('recommendations').innerHTML = recommendationsHTML;
}

function formatTime(seconds) {
    if (seconds < 60) {
        return `${seconds.toFixed(0)}s`;
    }
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
}
