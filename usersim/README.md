# UserSim - Virtual User Behavior Simulator

> **Build Users Before Building Software**

AI-powered tool to create virtual users, simulate realistic behavior patterns, and calculate churn probability at every step of the user journey.

Inspired by: [Build Software, Build Users](https://dima.day/blog/build-software-build-users/)

---

## 🎯 What is UserSim?

UserSim reverses traditional software development by helping you **understand and model your users BEFORE writing code**. Instead of static personas or user stories, UserSim creates AI-powered virtual users that make realistic decisions in different scenarios.

### Traditional Approach
```
Write User Stories → Build Software → Test → Get Feedback → Iterate
```

### UserSim Approach
```
Define Problem → Create Virtual User → Simulate Behavior → Design Software → Build
```

---

## ✨ Features

### 1. **AI-Powered Virtual Users**
- Generated from your problem statement and target audience
- Realistic personalities with sensitivities, traits, and patience levels
- Based on ResearchAI personas (optional integration)

### 2. **Scenario Simulation**
- **Happy Path**: Everything works perfectly
- **Edge Cases**: Things that can go wrong
- **Failures**: System errors, unavailability, external factors

### 3. **Behavioral Decision Engine**
- Uses Claude Sonnet 4.5 to make realistic user decisions
- Considers context (urgency, alternatives, time invested, etc.)
- Tracks emotional states (frustrated, hopeful, satisfied, etc.)

### 4. **Churn Probability Calculation**
- **Two-Layer System**:
  - Layer 1: Formula-based (frustration events × patience multiplier)
  - Layer 2: AI context adjustment (sunk cost, urgency, alternatives)
- Real-time churn tracking at every step
- Risk levels: LOW, MEDIUM, HIGH, CRITICAL

### 5. **Visual Journey Maps**
- Step-by-step user flow visualization
- Decision points with reasoning
- Churn probability breakdown
- Emotional state tracking
- Time tracking

---

## 🚀 Quick Start

### Installation

```bash
cd usersim

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### Run the Server

```bash
uvicorn app.main:app --reload
```

Open http://localhost:8000 in your browser.

---

## 📖 How to Use

### 1. Define Your Problem

**Example: Cab Aggregator App**

**Problem Statement:**
```
Users need to find the cheapest cab option across multiple apps
without manually checking each one
```

**Target Users:**
```
Daily commuters in Bangalore who are price-sensitive
```

**Product Flow:**
```
1. User enters destination
2. System compares prices across Uber, Ola, Rapido
3. User selects cheapest option
4. Redirects to selected app
5. User books cab
```

### 2. Generate Virtual User

UserSim creates a realistic virtual user:

```json
{
  "name": "Priya",
  "age": 28,
  "occupation": "Software Engineer",
  "problem_context": "Spends ₹300/day on cabs, wants to save money",
  "primary_goal": "Save ₹50+ on daily commute",
  "sensitivities": [
    {"name": "price_sensitivity", "level": 8},
    {"name": "time_sensitivity", "level": 6}
  ],
  "patience_level": "medium"
}
```

### 3. Simulate Scenarios

UserSim generates 5 scenarios (configurable):

**Scenario 1: Happy Path** ✅
- User finds cheapest cab → Books successfully

**Scenario 2: Redirected App - No Cabs Available** ⚠️
- Decision Point: What does Priya do?
- AI Decision: "Go back to aggregator, select Ola (second cheapest)"
- Churn Risk: 50% (MEDIUM)

**Scenario 3: 5 Min Wait - No Cab Found** 🚨
- Decision Point: Continue waiting or switch?
- AI Decision: "Cancel and try Ola immediately"
- Churn Risk: 65% (HIGH)

**Scenario 4: Driver Cancels After 2 Mins** 💥
- Decision Point: Retry or give up?
- AI Decision: "Go back to aggregator, select Ola"
- Churn Risk: 60% (HIGH)

### 4. Analyze Results

**Churn Hotspots:**
- Driver cancellation (occurred in 2 scenarios)
- No cabs available (occurred in 2 scenarios)

**Recommendations:**
- Reduce "Driver Cancellation" events
- Add "Show alternative while searching" feature
- Display "Estimated wait time" upfront

---

## 🧮 Churn Probability Formula

```
Churn Risk = Base Risk + Σ(Frustration Events) × Patience Multiplier + AI Adjustment

Base Risk: 10%

Frustration Events:
- Driver cancellation: +25%
- No cabs found (5+ mins): +30%
- App redirect failure: +20%
- Long wait (3-5 mins): +10%
- Price higher than expected: +15%

Patience Multiplier:
- Low patience: 2.0x
- Medium patience: 1.5x
- High patience: 1.0x

AI Context Adjustment (-50 to +50):
- Sunk cost (time invested): -5 to -15%
- High urgency: -5%
- Alternatives available: +10 to +15%
- Repeated failures: +10 to +20%
```

**Example Calculation:**

```
Step: Driver cancels after 2 mins

Base Risk: 10%
+ Driver Cancellation: +25%
+ Time Wasted (2 mins): +5%
= 40% base risk

× Patience Multiplier (Medium = 1.5x)
= 60% calculated risk

AI Adjustments:
- Sunk cost (2 mins invested): -10%
- High urgency (getting to work): -5%
+ Easy alternatives (Ola available): +10%
- First failure today: -5%
= -10% net adjustment

Final Churn Risk: 60% - 10% = 50% (MEDIUM)
```

---

## 🎨 Visual Output Examples

### User Profile Card
![User Profile](docs/user-profile-example.png)

Shows:
- Demographics and context
- Sensitivities (price, time, quality)
- Behavioral traits (tech savvy, patience)
- Frustration triggers

### Scenario Journey
![Scenario Journey](docs/scenario-journey-example.png)

Shows:
- Step-by-step timeline
- Decision points with reasoning
- Churn probability at each step
- Emotional states
- Time tracking

### Churn Analysis
![Churn Analysis](docs/churn-analysis-example.png)

Shows:
- Base → Frustration → Patience → Final calculation
- Frustration events breakdown
- AI context adjustments
- Risk level (LOW/MEDIUM/HIGH/CRITICAL)

---

## 🔧 Generic for Any Problem

UserSim works for **any product or service**:

### E-commerce
```
Problem: Users abandon carts before checkout
Scenarios: Price increases, out of stock, payment fails
```

### SaaS Product
```
Problem: Users struggle with onboarding
Scenarios: Complex UI, missing features, slow loading
```

### Food Delivery
```
Problem: Users frustrated by delivery delays
Scenarios: Restaurant delay, driver cancels, cold food
```

### Fintech
```
Problem: Users drop off during KYC
Scenarios: Upload fails, rejection, too many steps
```

---

## 🧪 API Reference

### POST `/api/simulate`

**Request:**
```json
{
  "problem_statement": "Users need to find cheapest cab",
  "target_users": "Price-sensitive commuters",
  "product_flow": "1. Enter destination\n2. Compare prices...",
  "num_scenarios": 5
}
```

**Response:**
```json
{
  "virtual_user": { /* VirtualUser object */ },
  "scenarios": [ /* Array of Scenario objects */ ],
  "summary_insights": [ /* Key findings */ ],
  "churn_hotspots": [ /* High-risk steps */ ],
  "recommendations": [ /* Product improvements */ ]
}
```

---

## 🔗 Integration with ResearchAI

UserSim can import personas from ResearchAI:

```python
# In ResearchAI, generate personas
personas = await generate_personas(pain_points)

# Import into UserSim
virtual_user = decision_engine.generate_virtual_user(
    problem_statement="...",
    target_users="...",
    persona_data=personas[0]  # Use first persona
)
```

---

## 📊 Use Cases

### 1. **Product Design**
- Identify drop-off points before building
- Validate feature priority
- Design friction-reducing UX

### 2. **Stakeholder Communication**
- Evidence-based decision justification
- Visual journey maps for alignment
- Churn risk quantification

### 3. **Testing Strategy**
- Define edge case test scenarios
- Prioritize test coverage
- Realistic user behavior patterns

### 4. **Market Validation**
- Test product-market fit hypothetically
- Identify deal-breakers early
- Refine value proposition

---

## 🛠 Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **AI Engine**: Anthropic Claude Sonnet 4.5
- **Data Validation**: Pydantic
- **Frontend**: Vanilla JS, HTML5, CSS3

---

## 📝 Future Enhancements

- [ ] Multi-user simulation (test different personas simultaneously)
- [ ] A/B testing scenarios (compare different product flows)
- [ ] Integration with actual UI prototypes (Figma, etc.)
- [ ] Export to PDF/PPTX for stakeholders
- [ ] Historical tracking (compare simulations over time)
- [ ] Custom frustration weights per domain

---

## 📄 License

MIT

---

## 🙏 Acknowledgments

Inspired by Dmitrii's article: [Build Software, Build Users](https://dima.day/blog/build-software-build-users/)

Built with Claude Code 🤖

---

## 💡 Philosophy

> "Quality software looks simple to its users. But achieving that simplicity requires deep understanding."

UserSim helps you gain that deep understanding **before** you write a single line of production code.
