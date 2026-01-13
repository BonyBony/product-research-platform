# UserSim Demo - Cab Aggregator Example

This document shows an example simulation for a cab aggregator app.

---

## Input

**Problem Statement:**
```
Users need to find the cheapest cab option across multiple apps (Uber, Ola, Rapido)
without manually checking each one. They want to save money on daily commute.
```

**Target Users:**
```
Daily commuters in Bangalore who are price-sensitive and tech-savvy
```

**Product Flow:**
```
1. User opens aggregator app
2. User enters destination
3. System shows price comparison across apps
4. User selects cheapest option
5. App redirects to selected cab app
6. User books cab and completes ride
```

**Number of Scenarios:** 5

---

## Output

### 1. Virtual User Profile

**Generated Virtual User:**

```
👤 Priya Sharma
28 years old, Software Engineer
Bangalore, Karnataka

Problem Context: "Spends ₹6000/month on cabs for office commute.
Looking for ways to reduce transportation costs."

Primary Goal: Save at least ₹50 per day on cab bookings

Patience Level: MEDIUM

Sensitivities:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRICE SENSITIVITY      ████████░░ 8/10
TIME SENSITIVITY       ██████░░░░ 6/10
QUALITY SENSITIVITY    ████░░░░░░ 4/10

Behavioral Traits:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TECH SAVVY            █████████░ 9/10
PATIENCE              █████░░░░░ 5/10
BRAND LOYALTY         ███░░░░░░░ 3/10
```

---

### 2. Scenario Simulations

#### Scenario 1: Happy Path ✅

**Type:** HAPPY_PATH
**Description:** User successfully finds cheapest cab and completes booking

**Journey:**

```
┌─ Step 1: ACTION (0s)
│  User opens aggregator app
│  Emotion: HOPEFUL | Churn Risk: 10% [LOW]
│
├─ Step 2: ACTION (5s)
│  User enters destination: "Koramangala to Whitefield (12km)"
│  Emotion: NEUTRAL | Churn Risk: 10% [LOW]
│
├─ Step 3: SYSTEM_RESPONSE (7s)
│  System displays price comparison:
│  • Uber: ₹180
│  • Ola: ₹165
│  • Rapido: ₹140
│  Emotion: SATISFIED | Churn Risk: 10% [LOW]
│
├─ Step 4: ACTION (12s)
│  User selects Rapido (saves ₹40 vs Uber!)
│  Emotion: DELIGHTED | Churn Risk: 8% [LOW]
│
├─ Step 5: SYSTEM_RESPONSE (14s)
│  Redirecting to Rapido app...
│  Emotion: HOPEFUL | Churn Risk: 12% [LOW]
│
├─ Step 6: SYSTEM_RESPONSE (136s - 2m 16s)
│  Rapido: Searching for driver... (2 minutes)
│  Driver found and accepted!
│  Emotion: SATISFIED | Churn Risk: 15% [LOW]
│
└─ Step 7: SUCCESS (320s - 5m 20s)
   Ride completed successfully
   Emotion: DELIGHTED | Churn Risk: 5% [LOW]

   Churn Analysis:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Base Risk:        10%
   + Frustration:     0%
   × Patience (1.5x): 15%
   - AI Adjustment:  -10% (successful experience)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Final Risk:        5% [LOW ✓]
```

**Outcome:** ✅ Success - User achieved goal
**Final Churn Probability:** 5%

**Key Insights:**
- User saved ₹40 compared to most expensive option
- Total journey time: 5 minutes 20 seconds
- Zero friction points
- High satisfaction due to meeting primary goal (save money)

---

#### Scenario 2: Redirected App Shows "No Cabs Available" ⚠️

**Type:** EDGE_CASE
**Description:** After redirect, Rapido shows no cabs available in area

**Journey:**

```
┌─ Steps 1-4: Same as Happy Path
│  (User selects Rapido - cheapest at ₹140)
│  Churn Risk: 12% [LOW]
│
├─ Step 5: SYSTEM_RESPONSE (14s)
│  Redirecting to Rapido app...
│  Emotion: HOPEFUL | Churn Risk: 15% [LOW]
│
├─ Step 6: ERROR (16s) 🚨
│  Rapido: "No cabs available in your area"
│  Emotion: FRUSTRATED | Churn Risk: 45% [MEDIUM]
│
│  Churn Analysis:
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│  Base Risk:          10%
│  + No availability:  +30%
│  + Time wasted:      +5%
│  × Patience (1.5x):  67.5%
│  - Sunk cost (16s):  -5%
│  + Easy alternative: +10%
│  - First failure:    -5%
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│  Final Risk:         62.5% [HIGH ⚠️]
│
└─ Step 7: DECISION POINT (26s) ❓

   What should Priya do?

   OPTIONS:
   ○ Retry Rapido immediately
   ○ Go back to aggregator and select Ola (₹165)
   ● Give up and book Uber directly (₹180)

   ✓ CHOSEN: Go back to aggregator, select Ola

   REASONING:
   "Priya's high price sensitivity (8/10) prevents her from going
   straight to the most expensive option (Uber ₹180). She's willing
   to try Ola (₹165) which still saves ₹15 vs Uber. The sunk cost
   of 26 seconds is minimal, and her medium patience level allows
   for one more attempt before giving up completely."

   Emotion: ANNOYED | Churn Risk: 50% [MEDIUM]

Step 8: SYSTEM_RESPONSE (28s)
│  Back in aggregator, selecting Ola (₹165)
│  Redirecting to Ola app...
│  Emotion: HOPEFUL | Churn Risk: 48% [MEDIUM]
│
└─ Step 9: SUCCESS (208s - 3m 28s)
   Ola driver found and accepted!
   Ride completed
   Emotion: SATISFIED | Churn Risk: 30% [LOW]
```

**Outcome:** 🟡 Partial Success - User frustrated but completed
**Final Churn Probability:** 30%

**Key Insights:**
- Highest churn risk at Step 6 when Rapido showed no cabs (62.5%)
- User faced 1 decision point
- Total journey time: 3 minutes 28 seconds
- User still saved ₹15 vs Uber (acceptable to price-sensitive user)
- Risk of churn on next failure: High

---

#### Scenario 3: 5 Minute Wait - No Cab Found 🚨

**Type:** FAILURE
**Description:** User waits 5 minutes but no cab is assigned

**Journey:**

```
┌─ Steps 1-5: Same as previous scenarios
│  User redirected to Rapido
│  Churn Risk: 15% [LOW]
│
├─ Step 6: SYSTEM_RESPONSE (316s - 5m 16s)
│  Rapido: "Searching for driver..." (5 minutes elapsed)
│  Still searching... no cab found
│  Emotion: FRUSTRATED | Churn Risk: 75% [HIGH]
│
│  Churn Analysis:
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│  Base Risk:          10%
│  + Long wait:        +30%
│  + No progress:      +15%
│  × Patience (1.5x):  82.5%
│  - Sunk cost (5min): -15%
│  - High urgency:     -5% (needs to reach office)
│  + Easy alternative: +12%
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│  Final Risk:         74.5% [HIGH 🚨]
│
└─ Step 7: DECISION POINT (326s - 5m 26s) ❓

   What should Priya do?

   OPTIONS:
   ○ Wait another 5 minutes
   ○ Cancel and try Ola
   ● Give up on aggregator, book Uber directly

   ✓ CHOSEN: Cancel and try Ola immediately

   REASONING:
   "After waiting 5 minutes with no result, Priya's patience
   threshold (medium = 5 minutes) is reached. However, her high
   urgency to reach office (work starts in 20 mins) combined with
   price sensitivity prevents complete abandonment. She'll give
   ONE more attempt with Ola before resorting to expensive Uber.

   Context factors:
   • Time lost: 5 minutes (significant sunk cost)
   • Urgency: HIGH (can't risk being late)
   • Trust in Rapido: DAMAGED (unlikely to retry)
   • Willingness to pay extra: LOW but increasing"

   Emotion: ANGRY | Churn Risk: 65% [HIGH]

Step 8: SYSTEM_RESPONSE (328s - 5m 28s)
│  Canceling Rapido, switching to Ola...
│  Emotion: ANNOYED | Churn Risk: 60% [HIGH]
│
└─ Step 9: DECISION RESULT
   User tries Ola as last resort
   If this fails → Complete churn (will use Uber app directly next time)
```

**Outcome:** 🔴 High Churn Risk - User close to abandoning product
**Final Churn Probability:** 65%

**Key Insights:**
- Waiting 5+ minutes is a critical churn hotspot
- User patience threshold exceeded
- One more failure = complete product abandonment
- Need to show estimated wait time upfront
- Consider showing "Ola available now" while searching in Rapido

---

#### Scenario 4: Driver Cancels After 2 Minutes 💥

**Type:** EDGE_CASE
**Description:** Driver accepts but cancels 2 minutes later

**Journey:**

```
┌─ Steps 1-5: User redirected to Rapido
│
├─ Step 6: SYSTEM_RESPONSE (136s - 2m 16s)
│  Rapido: "Searching for driver..." (2 minutes)
│  Driver found and accepted!
│  Emotion: RELIEVED | Churn Risk: 20% [LOW]
│
├─ Step 7: SYSTEM_RESPONSE (256s - 4m 16s) 🚨
│  Driver is on the way...
│  🚨 DRIVER CANCELLED 🚨
│  Emotion: ANGRY | Churn Risk: 70% [HIGH]
│
│  Churn Analysis:
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│  Base Risk:             10%
│  + Driver cancellation: +25%
│  + Time wasted (4min):  +10%
│  + Emotional impact:    +15%
│  × Patience (1.5x):     90%
│  - Sunk cost (4min):    -12%
│  - High urgency:        -5%
│  + Easy alternatives:   +10%
│  - First failure:       -5%
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│  Final Risk:            68% [HIGH 🚨]
│
└─ Step 8: DECISION POINT (266s - 4m 26s) ❓

   What should Priya do?

   OPTIONS:
   ○ Retry Rapido (same app that just failed)
   ○ Go back to aggregator, select Ola
   ● Abandon aggregator, book Uber directly

   ✓ CHOSEN: Go back to aggregator, select Ola

   REASONING:
   "Driver cancellation after 4 minutes is highly frustrating.
   Priya has lost trust in Rapido for today. However, she hasn't
   lost trust in the aggregator concept itself - the price
   comparison was still valuable.

   Decision factors:
   • Trust in Rapido: BROKEN (won't retry same app)
   • Trust in aggregator: DAMAGED but not destroyed
   • Time pressure: HIGH (already lost 4 minutes)
   • Price sensitivity: Still strong (8/10)
   • Last chance: If Ola fails, will abandon aggregator permanently

   Next failure = 95% churn probability"

   Emotion: FRUSTRATED | Churn Risk: 60% [HIGH]
```

**Outcome:** 🟡 User gives aggregator ONE more chance
**Final Churn Probability:** 60%

**Key Insights:**
- Driver cancellation is the MOST frustrating event
- User lost 4 minutes (2 min search + 2 min waiting)
- Trust in specific app (Rapido) broken
- Trust in aggregator damaged but salvageable
- Recommendation: Show driver reliability score before selection

---

#### Scenario 5: Price Increased After Redirect ⚠️

**Type:** EDGE_CASE
**Description:** Price shown in aggregator doesn't match price in Rapido app

**Journey:**

```
┌─ Steps 1-4: User sees Rapido at ₹140, selects it
│  Emotion: DELIGHTED | Churn Risk: 8% [LOW]
│
├─ Step 5: SYSTEM_RESPONSE (14s)
│  Redirecting to Rapido app...
│  Emotion: HOPEFUL | Churn Risk: 12% [LOW]
│
├─ Step 6: ERROR (16s) 🚨
│  Rapido app shows price: ₹165 (₹25 higher!)
│  "Prices may vary based on demand"
│  Emotion: BETRAYED | Churn Risk: 55% [MEDIUM]
│
│  Churn Analysis:
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│  Base Risk:            10%
│  + Unexpected cost:    +15%
│  + Misleading info:    +20%
│  × Patience (1.5x):    67.5%
│  - Sunk cost (16s):    -5%
│  + Easy alternative:   +10%
│  - First time issue:   -5%
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│  Final Risk:           57.5% [MEDIUM ⚠️]
│
└─ Step 7: DECISION POINT (26s) ❓

   What should Priya do?

   OPTIONS:
   ○ Accept higher price (₹165) in Rapido
   ○ Go back and try Ola (originally ₹165)
   ● Go back and try Uber (originally ₹180)

   ✓ CHOSEN: Go back to aggregator, reevaluate options

   REASONING:
   "This is a CRITICAL trust-breaking moment. The aggregator
   showed ₹140 but Rapido shows ₹165 - a bait-and-switch.

   Priya's reaction:
   • Feels misled by aggregator
   • Questions accuracy of ALL prices shown
   • If Ola also shows different price → Complete churn
   • Aggregator lost its core value proposition (accurate comparison)

   Psychological impact:
   • Price sensitivity (8/10) makes this deeply frustrating
   • Trust in aggregator: SEVERELY DAMAGED
   • Likely to abandon aggregator after this experience
   • Will share negative review about 'misleading prices'

   One-time forgiveness: User will check if it's systematic issue
   If happens again → 100% churn + negative word-of-mouth"

   Emotion: BETRAYED | Churn Risk: 75% [HIGH]
```

**Outcome:** 🔴 Critical Churn Risk - Trust broken
**Final Churn Probability:** 75%

**Key Insights:**
- Price mismatch is a TRUST-DESTROYING event
- Undermines core value proposition (accurate comparison)
- User questions ALL information from aggregator
- High risk of negative reviews and word-of-mouth
- Recommendation: Real-time price sync or show "estimated" disclaimer

---

### 3. Summary & Recommendations

**Summary Insights:**
- Average churn probability across scenarios: 47%
- Outcomes: 1 successful, 4 with churn risk (20% success rate)
- Critical insight: Even small friction points compound quickly

**Churn Hotspots:**
1. 🔥 Driver cancellation after user wait (occurred in 1 scenario, 70% churn)
2. 🔥 5+ minute wait with no progress (occurred in 1 scenario, 75% churn)
3. 🔥 Price mismatch between aggregator and app (occurred in 1 scenario, 75% churn)
4. ⚠️ No cabs available after redirect (occurred in 1 scenario, 62% churn)

**Recommendations:**

1. **Show estimated wait time BEFORE redirect**
   - Helps users make informed decisions
   - Reduces frustration from unexpected delays
   - Priority: HIGH

2. **Real-time price sync**
   - Display "estimated" if prices may vary
   - Show last updated timestamp
   - Priority: CRITICAL (trust issue)

3. **Fallback options while searching**
   - "Rapido searching... Ola available now for ₹165"
   - Let users switch without going back
   - Priority: MEDIUM

4. **Driver reliability indicator**
   - Show cancellation rate per app
   - "Rapido: 15% cancellation rate vs Ola: 8%"
   - Priority: HIGH

5. **Maximum wait time setting**
   - "Alert me if no cab in X minutes"
   - Auto-suggest alternatives after threshold
   - Priority: MEDIUM

---

## Key Learnings

### What We Discovered About Priya:

1. **Price Sensitivity is Strong** (8/10)
   - Will tolerate moderate friction to save money
   - Won't immediately jump to expensive option
   - Gives multiple chances to cheaper alternatives

2. **Patience Threshold: ~5 Minutes**
   - Can wait 2-3 minutes without major frustration
   - 5+ minutes = critical churn risk
   - After 7-8 minutes = complete abandonment

3. **Trust is Fragile**
   - One price mismatch = 75% churn
   - One driver cancel = trust in specific app broken
   - Two consecutive failures = trust in product broken

4. **Context Matters**
   - High urgency (work) = more tolerance for trying alternatives
   - Low urgency (leisure) = would give up faster
   - Time of day affects decision-making

### How This Informs Product Design:

**Before UserSim:**
- "Users want cheapest cab" ← Vague requirement
- "Add price comparison" ← Simple feature spec

**After UserSim:**
- "Users will tolerate ONE failure but need clear alternatives"
- "Price accuracy is MORE important than lowest price"
- "Wait time expectations must be set upfront"
- "After 5 minutes, automatically suggest alternatives"

**Result:** Build a product that matches ACTUAL user behavior, not assumed behavior.

---

## Try It Yourself

```bash
cd usersim
uvicorn app.main:app --reload
```

Open http://localhost:8000 and run this simulation with your own product!
