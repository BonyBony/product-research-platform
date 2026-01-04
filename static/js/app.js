// DOM Elements
const form = document.getElementById('researchForm');
const generateBtn = document.getElementById('generateBtn');
const loadingState = document.getElementById('loadingState');
const loadingText = document.getElementById('loadingText');
const errorState = document.getElementById('errorState');
const errorText = document.getElementById('errorText');
const painPointsSection = document.getElementById('painPointsSection');
const painPointsList = document.getElementById('painPointsList');
const personasSection = document.getElementById('personasSection');
const personasGrid = document.getElementById('personasGrid');
const personasCount = document.getElementById('personasCount');

// State
let currentPainPoints = [];
let currentPersonas = [];
let currentFormData = {};

// Event Listeners
form.addEventListener('submit', handleFormSubmit);

// Main Form Handler
async function handleFormSubmit(e) {
    e.preventDefault();

    const formData = {
        problem_statement: document.getElementById('problemStatement').value,
        target_users: document.getElementById('targetUsers').value,
        data_source: document.getElementById('dataSource').value,
        num_personas: parseInt(document.getElementById('numPersonas').value)
    };

    // Reset UI
    hideError();
    hidePainPoints();
    hidePersonas();

    // Dynamic loading message based on source
    const sourceNames = {
        'auto': 'the best available source',
        'hackernews': 'Hacker News',
        'youtube': 'YouTube',
        'reddit': 'Reddit',
        'producthunt': 'Product Hunt',
        'demo': 'demo data'
    };
    showLoading(`Analyzing user research from ${sourceNames[formData.data_source]}...`);
    disableForm();

    try {
        // Step 1: Get pain points from research
        const painPoints = await fetchPainPoints(
            formData.problem_statement,
            formData.target_users,
            formData.data_source
        );

        if (!painPoints || painPoints.length === 0) {
            throw new Error('No pain points found. Try refining your query with specific app names or use cases.');
        }

        currentPainPoints = painPoints;
        currentFormData = formData;
        displayPainPoints(painPoints);

        // Step 2: Generate personas
        showLoading('Generating user personas with AI...');
        const personas = await generatePersonas(painPoints, formData);

        if (!personas || personas.length === 0) {
            throw new Error('Failed to generate personas. Please try again.');
        }

        currentPersonas = personas;
        displayPersonas(personas);
        hideLoading();

        // Step 3: Show prioritization option
        showPrioritizeButton();

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred. Please try again.');
        hideLoading();
    } finally {
        enableForm();
    }
}

// API Calls
async function fetchPainPoints(problemStatement, targetUsers, dataSource) {
    const response = await fetch('http://localhost:8000/api/research', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            problem_statement: problemStatement,
            target_users: targetUsers,
            source: dataSource
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch pain points');
    }

    const data = await response.json();
    return data.pain_points;
}

async function generatePersonas(painPoints, formData) {
    const response = await fetch('http://localhost:8000/api/personas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            pain_points: painPoints,
            problem_statement: formData.problem_statement,
            target_users: formData.target_users,
            num_personas: formData.num_personas
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to generate personas');
    }

    const data = await response.json();
    return data.personas;
}

// Display Functions
function displayPainPoints(painPoints) {
    painPointsList.innerHTML = '';

    painPoints.forEach((pp, index) => {
        const card = document.createElement('div');
        card.className = `pain-point-card severity-${pp.severity.toLowerCase()}`;

        card.innerHTML = `
            <div class="pain-point-description">${pp.description}</div>
            <div class="pain-point-quote">"${pp.quote}"</div>
            <div class="pain-point-meta">
                <span class="severity-badge ${pp.severity.toLowerCase()}">${pp.severity}</span>
                <span>Frequency: ${pp.frequency}</span>
            </div>
        `;

        painPointsList.appendChild(card);
    });

    painPointsSection.style.display = 'block';
}

function displayPersonas(personas) {
    personasGrid.innerHTML = '';
    personasCount.textContent = `${personas.length} personas generated from ${currentPainPoints.length} pain points`;

    personas.forEach((persona, index) => {
        const card = createPersonaCard(persona, index);
        personasGrid.appendChild(card);
    });

    personasSection.style.display = 'block';

    // Smooth scroll to personas
    setTimeout(() => {
        personasSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

function createPersonaCard(persona, index) {
    const card = document.createElement('div');
    card.className = 'persona-card';

    // Get initials for avatar
    const initials = persona.name.split(' ').map(n => n[0]).join('').substring(0, 2);

    // Avatar colors
    const colors = [
        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
    ];

    card.innerHTML = `
        <div class="persona-header" style="background: ${colors[index % colors.length]}">
            <div class="persona-avatar">${initials}</div>
            <div class="persona-name">${persona.name}</div>
            <div class="persona-title">${persona.age} years • ${persona.occupation}</div>
            <div class="persona-location">📍 ${persona.location}</div>
        </div>

        <div class="persona-body">
            ${persona.quote ? `
                <div class="persona-quote">
                    "${persona.quote}"
                </div>
            ` : ''}

            <div class="persona-section">
                <div class="section-title">Background</div>
                <p class="persona-background">${persona.background}</p>
            </div>

            <div class="persona-section">
                <div class="section-title">Goals</div>
                <ul class="persona-list">
                    ${persona.goals.map(goal => `<li>${goal}</li>`).join('')}
                </ul>
            </div>

            <div class="persona-section">
                <div class="section-title">Pain Points</div>
                <ul class="persona-list">
                    ${persona.pain_points.map(pp => `<li>${pp}</li>`).join('')}
                </ul>
            </div>

            <div class="persona-section">
                <div class="section-title">Behaviors</div>
                <ul class="persona-list">
                    ${persona.behaviors.map(behavior => `<li>${behavior}</li>`).join('')}
                </ul>
            </div>

            ${persona.motivations && persona.motivations.length > 0 ? `
                <div class="persona-section">
                    <div class="section-title">Motivations</div>
                    <ul class="persona-list">
                        ${persona.motivations.map(motivation => `<li>${motivation}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}

            ${persona.frustrations && persona.frustrations.length > 0 ? `
                <div class="persona-section">
                    <div class="section-title">Frustrations</div>
                    <ul class="persona-list">
                        ${persona.frustrations.map(frustration => `<li>${frustration}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}

            <div class="persona-section">
                <div class="section-title">User Profile</div>
                <div class="persona-stats">
                    ${persona.shopping_frequency ? `
                        <div class="stat-item">
                            <div class="stat-label">Frequency</div>
                            <div class="stat-value">${persona.shopping_frequency}</div>
                        </div>
                    ` : ''}
                    ${persona.avg_spend ? `
                        <div class="stat-item">
                            <div class="stat-label">Avg Spend</div>
                            <div class="stat-value">${persona.avg_spend}</div>
                        </div>
                    ` : ''}
                </div>
                <div class="tech-badge ${persona.tech_savviness.toLowerCase()}">
                    ${persona.tech_savviness} Tech Savviness
                </div>
            </div>
        </div>
    `;

    return card;
}

// UI State Functions
function showLoading(message) {
    loadingText.textContent = message;
    loadingState.style.display = 'block';
}

function hideLoading() {
    loadingState.style.display = 'none';
}

function showError(message) {
    errorText.textContent = message;
    errorState.style.display = 'block';
}

function hideError() {
    errorState.style.display = 'none';
}

function hidePainPoints() {
    painPointsSection.style.display = 'none';
}

function hidePersonas() {
    personasSection.style.display = 'none';
}

function disableForm() {
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';
}

function enableForm() {
    generateBtn.disabled = false;
    generateBtn.textContent = 'Generate Personas';
}

// Prioritization Functions
function showPrioritizeButton() {
    const prioritizeSection = document.getElementById('prioritizeSection');
    if (prioritizeSection) {
        prioritizeSection.style.display = 'block';
    }
}

async function prioritizePainPoints() {
    const prioritizeBtn = document.getElementById('prioritizeBtn');
    const prioritizationResults = document.getElementById('prioritizationResults');

    try {
        // Show loading
        prioritizeBtn.disabled = true;
        prioritizeBtn.textContent = 'Prioritizing...';
        showLoading('Analyzing pain points with JTBD + RICE framework...');

        // Call prioritization API
        const response = await fetch('http://localhost:8000/api/prioritize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                pain_points: currentPainPoints,
                personas: currentPersonas,
                problem_statement: currentFormData.problem_statement,
                target_users: currentFormData.target_users,
                market_context: {}
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to prioritize pain points');
        }

        const data = await response.json();

        // Display results
        displayPrioritization(data);
        hideLoading();

        // Scroll to results
        setTimeout(() => {
            prioritizationResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to prioritize. Please try again.');
        hideLoading();
    } finally {
        prioritizeBtn.disabled = false;
        prioritizeBtn.textContent = 'Prioritize Pain Points';
    }
}

function displayPrioritization(data) {
    const resultsDiv = document.getElementById('prioritizationResults');
    const resultsGrid = document.getElementById('prioritizationGrid');

    resultsGrid.innerHTML = '';

    data.prioritized_pain_points.forEach((pp, index) => {
        const card = createPriorityCard(pp, index);
        resultsGrid.appendChild(card);
    });

    resultsDiv.style.display = 'block';
}

function createPriorityCard(pp, index) {
    const card = document.createElement('div');
    card.className = 'priority-card';

    // Rank badge color
    const rankColors = ['#ffd700', '#c0c0c0', '#cd7f32', '#6366f1', '#8b5cf6'];
    const rankColor = rankColors[Math.min(index, 4)];

    // Score color
    const scorePercent = (pp.final_score / 200) * 100;
    let scoreClass = 'score-low';
    if (scorePercent >= 70) scoreClass = 'score-high';
    else if (scorePercent >= 40) scoreClass = 'score-medium';

    // JTBD category badge
    const categoryBadges = {
        'underserved': { text: 'Underserved', class: 'category-underserved' },
        'wellserved': { text: 'Well Served', class: 'category-wellserved' },
        'overserved': { text: 'Overserved', class: 'category-overserved' }
    };
    const categoryBadge = categoryBadges[pp.jtbd.category] || categoryBadges['wellserved'];

    card.innerHTML = `
        <div class="priority-header">
            <div class="priority-rank" style="background: ${rankColor}">
                #${pp.priority_rank}
            </div>
            <div class="priority-score ${scoreClass}">
                ${pp.final_score.toFixed(0)}/200
            </div>
        </div>

        <div class="priority-body">
            <h3 class="priority-title">${pp.description}</h3>

            <div class="priority-badges">
                <span class="badge ${categoryBadge.class}">${categoryBadge.text}</span>
                <span class="badge severity-${pp.original_severity.toLowerCase()}">${pp.original_severity} Severity</span>
            </div>

            <!-- JTBD Section -->
            <div class="analysis-section">
                <h4>🎯 Jobs-to-be-Done Analysis</h4>
                <p class="jtbd-statement">${pp.jtbd.job_statement}</p>
                <div class="jtbd-scores">
                    <div class="metric">
                        <span class="metric-label">Opportunity Score</span>
                        <span class="metric-value">${pp.jtbd.opportunity_score.toFixed(1)}/20</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Importance</span>
                        <span class="metric-value">${pp.jtbd.importance.toFixed(1)}/10</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Satisfaction</span>
                        <span class="metric-value">${pp.jtbd.satisfaction.toFixed(1)}/10</span>
                    </div>
                </div>
                <p class="reasoning">${pp.jtbd.reasoning}</p>
            </div>

            <!-- RICE Section -->
            <div class="analysis-section">
                <h4>📊 RICE Breakdown</h4>
                <div class="rice-grid">
                    <div class="rice-metric">
                        <div class="rice-label">Reach</div>
                        <div class="rice-value">${pp.rice.reach.toLocaleString()}</div>
                        <div class="rice-detail">users affected</div>
                    </div>
                    <div class="rice-metric">
                        <div class="rice-label">Impact</div>
                        <div class="rice-value">${pp.rice.impact.toFixed(1)}x</div>
                        <div class="rice-detail">multiplier</div>
                    </div>
                    <div class="rice-metric">
                        <div class="rice-label">Confidence</div>
                        <div class="rice-value">${(pp.rice.confidence * 100).toFixed(0)}%</div>
                        <div class="rice-detail">certainty</div>
                    </div>
                    <div class="rice-metric">
                        <div class="rice-label">Effort</div>
                        <div class="rice-value">${pp.rice.effort.toFixed(1)}</div>
                        <div class="rice-detail">person-months</div>
                    </div>
                </div>
                <div class="rice-score-display">
                    <strong>RICE Score:</strong> ${pp.rice.rice_score.toLocaleString()}
                </div>
            </div>

            <!-- Persona Alignment -->
            <div class="analysis-section">
                <h4>👥 Persona Impact</h4>
                <div class="persona-tags">
                    ${pp.persona_alignment.affected_personas.map(name =>
                        `<span class="persona-tag affinity-${pp.persona_alignment.affinities[name].toLowerCase().replace(' ', '-')}">${name}</span>`
                    ).join('')}
                </div>
                <p class="persona-coverage">Affects ${pp.persona_alignment.affected_personas.length} of ${Object.keys(pp.persona_alignment.affinities).length} personas (${(pp.persona_alignment.coverage * 100).toFixed(0)}% coverage)</p>
            </div>

            <!-- Market Validation -->
            ${pp.justification.market_data ? `
                <div class="analysis-section">
                    <h4>📈 Market Validation</h4>
                    <div class="market-data">
                        <p><strong>TAM:</strong> ${pp.justification.market_data.tam}</p>
                        <p><strong>Market Size:</strong> $${(pp.justification.market_data.market_size_usd / 1_000_000_000).toFixed(2)}B</p>
                        <p><strong>Growth:</strong> ${pp.justification.market_data.growth_rate}</p>
                    </div>
                </div>
            ` : ''}

            <!-- Why Top Priority -->
            <div class="analysis-section justification-section">
                <h4>✨ Why This Matters</h4>
                <p class="justification-text">${pp.justification.why_top_priority}</p>

                <details class="evidence-details">
                    <summary>Show Evidence</summary>
                    <ul class="evidence-list">
                        ${pp.justification.evidence.map(ev => `<li>${ev}</li>`).join('')}
                    </ul>
                </details>
            </div>

            <button class="expand-btn" onclick="toggleDetails(this)">
                Show Full Analysis ▼
            </button>
        </div>
    `;

    return card;
}

function toggleDetails(btn) {
    const card = btn.closest('.priority-card');
    card.classList.toggle('expanded');
    btn.textContent = card.classList.contains('expanded') ? 'Show Less ▲' : 'Show Full Analysis ▼';
}
