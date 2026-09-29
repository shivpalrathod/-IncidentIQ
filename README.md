# 🧠 IncidentIQ

## AI Incident Response Agent with Persistent Institutional Memory

IncidentIQ is an AI-powered production incident response agent that helps engineers investigate production incidents using persistent institutional memory.

Instead of treating every incident as a completely new problem, IncidentIQ recalls relevant historical incidents from **Hindsight**, provides that historical context to **Groq**, and generates an incident analysis containing historical facts, current hypotheses, investigation steps, historical resolutions, and recommended next actions.

IncidentIQ also includes a **memory-quality gate** that prevents unverified AI hypotheses from automatically becoming long-term institutional knowledge.

---

## 🚀 Live Demo

### Frontend

https://incident-iq-lilac-phi.vercel.app

### Backend API

https://incidentiq-backend-ftab.onrender.com

### API Documentation

https://incidentiq-backend-ftab.onrender.com/docs

### GitHub Repository

https://github.com/shivpalrathod/-IncidentIQ

---

# 🎯 Problem

Production incidents frequently repeat.

An engineering team may have already experienced the same:

- API failure
- infrastructure problem
- database timeout
- memory issue
- service outage
- configuration problem
- deployment-related failure

and may already know how the problem was resolved.

However, engineers often need to search through:

- previous incident reports
- monitoring dashboards
- logs
- tickets
- documentation
- team conversations

to rediscover that knowledge.

A traditional stateless AI assistant has another limitation: it can analyze the current incident, but it does not automatically maintain reliable institutional memory from previous incidents.

This creates a recurring problem:

```text
Incident happens
      ↓
Engineers investigate
      ↓
Incident gets resolved
      ↓
Knowledge becomes documentation
      ↓
Similar incident happens later
      ↓
Engineers investigate again
```

IncidentIQ is designed to close this loop.

---

# 💡 Solution

IncidentIQ provides an AI incident-response workflow with persistent memory.

The system follows:

```text
Report
   ↓
Recall
   ↓
Reason
   ↓
Respond
   ↓
Remember
```

When an engineer reports an incident:

1. IncidentIQ receives the incident description.
2. Hindsight searches for relevant historical memories.
3. Historical context is passed into the AI reasoning process.
4. Groq analyzes the current incident using the recalled context.
5. The system separates historical facts from current hypotheses and recommendations.
6. A memory-quality gate determines whether new knowledge is reliable enough to retain.
7. Verified knowledge can be stored in Hindsight for future incidents.
8. Unverified conclusions are rejected from long-term memory.

---

# ✨ Key Features

## 🧠 Persistent Institutional Memory

IncidentIQ uses Hindsight as its persistent memory layer.

Historical incident knowledge can be recalled during future incidents.

---

## 🔎 Historical Incident Recall

When an incident is reported, IncidentIQ searches Hindsight for relevant historical context.

For example:

```text
Payment API is returning 503 errors again.
Redis memory is around 96%.
```

The system can recall a previous incident involving:

```text
INC-001
Payment API 503 errors
Redis memory around 96%
Resolved by increasing Redis memory
Added Redis memory monitoring
```

---

## 🤖 AI Incident Analysis

Groq analyzes the current incident together with historical context.

The generated analysis contains sections such as:

- Related Previous Incident
- Likely Cause
- Investigation Steps
- Historical Resolution
- Recommended Next Action

---

## 🧩 Historical Facts vs Current Hypotheses

IncidentIQ distinguishes between information that is already documented and information that is only a current hypothesis.

### Historical Fact

Example:

```text
A previous Payment API 503 incident was resolved
by increasing Redis memory and adding monitoring.
```

### Current Hypothesis

Example:

```text
The current 503 errors may be caused by Redis
operating near its memory capacity.
```

### Recommendation

Example:

```text
Check Redis memory and eviction metrics before
applying infrastructure changes.
```

This distinction helps prevent assumptions from being presented as confirmed historical knowledge.

---

# 🛡️ Memory Quality Gate

One of the key features of IncidentIQ is that it does not blindly save every AI-generated conclusion.

The system requires verified incident knowledge before allowing new information to become institutional memory.

The memory decision has two possible outcomes:

```text
SAVE
```

or:

```text
DO_NOT_SAVE
```

---

# ✅ SAVE

A memory can be retained when:

1. A valid memory summary is generated.
2. Groq determines that the knowledge is sufficiently useful.
3. Hindsight contains a documented completed resolution for the incident.

Example:

```text
Payment API 503 errors were previously linked
to Redis memory usage around 96%.

The incident was resolved by increasing Redis
memory and adding Redis memory monitoring.
```

The system can then produce:

```text
MEMORY_DECISION: SAVE
```

and retain the verified incident knowledge in Hindsight.

---

# 🚫 DO_NOT_SAVE

IncidentIQ does not save an incident as institutional memory when the available information contains only hypotheses without a documented resolution.

For example:

```text
Order API is returning 502 errors and database
connections are timing out.
```

Hindsight may contain possible explanations such as:

```text
Redis memory pressure
Database connection-pool saturation
Upstream resource exhaustion
```

However, if there is no documented completed resolution, the system prevents those assumptions from becoming institutional memory.

The result is:

```text
MEMORY_DECISION: DO_NOT_SAVE
```

The frontend displays:

```text
Memory Not Saved
Memory Quality: Not verified
```

This protects the long-term memory from accumulating unsupported conclusions.

---

# 🔄 IncidentIQ Memory Loop

IncidentIQ is designed around a continuous memory loop.

```text
┌──────────────────────┐
│  01. REPORT          │
│  Engineer reports    │
│  production incident │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  02. RECALL          │
│  Hindsight searches  │
│  historical memory   │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  03. REASON          │
│  Groq analyzes       │
│  historical context  │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  04. RESPOND         │
│  Engineers receive   │
│  actionable guidance │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  05. REMEMBER        │
│  Verified knowledge  │
│  is retained         │
└──────────────────────┘
```

---

# 🏗️ System Architecture

```text
                         ┌─────────────────┐
                         │     Engineer    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ React Frontend  │
                         │     Vercel      │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ FastAPI Backend │
                         │     Render      │
                         └──────┬─────┬────┘
                                │     │
                   ┌────────────┘     └────────────┐
                   ▼                               ▼
          ┌─────────────────┐             ┌─────────────────┐
          │    Hindsight    │             │      Groq       │
          │                 │             │                 │
          │ Recall / Retain │             │  AI Reasoning   │
          └────────┬────────┘             └────────┬────────┘
                   │                               │
                   └───────────────┬───────────────┘
                                   ▼
                         ┌────────────────────┐
                         │  Memory Quality    │
                         │       Gate         │
                         └─────────┬──────────┘
                              ┌────┴────┐
                              ▼         ▼
                           ┌──────┐ ┌─────────────┐
                           │ SAVE │ │ DO_NOT_SAVE │
                           └──┬───┘ └─────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Hindsight Retain│
                       └─────────────────┘
```

---

# 🔁 Request Flow

A typical request flows through the system as follows:

```text
1. Engineer enters incident
              ↓
2. React frontend sends POST request
              ↓
3. FastAPI receives incident
              ↓
4. Hindsight recalls relevant memories
              ↓
5. Backend prepares historical context
              ↓
6. Groq analyzes current + historical context
              ↓
7. Backend extracts memory decision
              ↓
8. Server-side memory-quality validation
              ↓
        ┌─────┴─────┐
        ↓           ↓
      SAVE      DO_NOT_SAVE
        ↓           ↓
 Hindsight Retain   Stop
        ↓
 Future Recall
```

---

# 🧠 How Hindsight Is Used

Hindsight is a central component of IncidentIQ.

It is responsible for persistent memory operations.

## 1. Recall

IncidentIQ sends the current incident to Hindsight with instructions to retrieve relevant historical incidents, documented causes, completed resolutions, and prevention actions.

The returned memories can include different memory types such as:

```text
World Fact
Observation
Previous Experience
```

The recalled memories are displayed in the IncidentIQ interface.

---

## 2. Reasoning with Memory

The recalled historical context is provided to Groq.

Groq uses this information to analyze the current incident.

The system instructs the AI to distinguish:

```text
Historical Fact
Current Hypothesis
Recommendation
Historical Resolution
```

This prevents the AI from automatically treating historical observations as confirmed current causes.

---

## 3. Retain

After analysis, IncidentIQ determines whether the incident contains sufficiently verified knowledge.

If the incident has a documented completed resolution and passes the memory-quality gate, the system retains a concise incident memory in Hindsight.

---

# 🔐 Why Memory Quality Matters

Persistent memory is useful only when the stored knowledge is reliable.

If every AI hypothesis were automatically stored, the memory system could gradually accumulate:

- incorrect assumptions
- unverified root causes
- temporary observations
- speculative recommendations

IncidentIQ therefore uses a memory-quality gate.

The important principle is:

```text
Not every AI conclusion should become institutional knowledge.
```

Only verified incident knowledge should become persistent memory.

---

# 🧪 Demonstrated Test Cases

## Test Case 1 — Known Payment API Incident

Input:

```text
Payment API is returning 503 errors again.
Redis memory is around 96%.
```

Hindsight recalled previous Payment API incidents.

The historical context included:

```text
INC-001
Payment API 503 errors
Redis memory around 96%
```

and the documented resolution:

```text
Increase Redis memory
Add Redis memory monitoring
```

Result:

```text
Memory Saved
AI Decision: SAVE
Memory Quality: Verified
```

The AI correctly identified the historical resolution while treating the current root cause as a hypothesis that should still be investigated.

---

# 🧪 Test Case 2 — Unverified Order API Incident

Input:

```text
Order API is returning 502 errors and database
connections are timing out.
```

Hindsight recalled historical information involving:

```text
Redis memory pressure
Database connection-pool saturation
Upstream resource exhaustion
```

However, there was no documented completed resolution.

Therefore:

```text
Memory Not Saved
AI Decision: DO_NOT_SAVE
Memory Quality: Not verified
```

The AI correctly reported:

```text
No documented previous resolution was found in Hindsight.
```

This demonstrates that IncidentIQ does not blindly promote hypotheses into persistent institutional memory.

---

# 📊 Example AI Analysis

A typical analysis can contain:

```text
1. Related Previous Incident

Historical facts and experiences recalled from Hindsight.

2. Likely Cause

Current hypothesis based on current evidence and
historical context.

3. Investigation Steps

Actions engineers can perform to validate the hypothesis.

4. Historical Resolution

Previously documented resolution, when available.

5. Recommended Next Action

The next investigation or operational action.
```

---

# 🛠️ Technology Stack

## Frontend

- React
- Vite
- JavaScript
- CSS
- Lucide React

## Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- Python-dotenv

## AI

- Groq API
- Configured Groq language model

## Persistent Memory

- Hindsight

## Deployment

- Vercel
- Render

## Version Control

- Git
- GitHub

## Development Environment

- Visual Studio Code
- Python virtual environment
- Node.js
- npm

---

# 📁 Project Structure

```text
IncidentIQ/
│
├── backend/
│   ├── main.py
│   └── config.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   │
│   ├── package.json
│   └── vite.config.js
│
├── data/
│
├── tests/
│
├── docs/
│   └── architecture.png
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# ⚙️ Local Development

## Prerequisites

Install:

- Python 3.11+
- Node.js
- npm
- Git

You also need:

- Hindsight API access
- Groq API access

---

## 1. Clone Repository

```bash
git clone https://github.com/shivpalrathod/-IncidentIQ.git
cd -IncidentIQ
```

---

## 2. Create Python Virtual Environment

Windows:

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\Scripts\Activate.ps1
```

---

## 3. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
HINDSIGHT_API_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=your_hindsight_api_key
HINDSIGHT_BANK_ID=incidentiq

GROQ_API_KEY=your_groq_api_key
```

Do not commit `.env`.

The repository contains `.env.example` as a template.

---

# ▶️ Run Backend

From the project root:

```powershell
python -m uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# ▶️ Run Frontend

Open another terminal.

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL displayed in the terminal.

During local development, the frontend communicates with the local FastAPI backend.

---

# 🌐 Production Deployment

## Frontend — Vercel

The React frontend is deployed on Vercel.

Production URL:

https://incident-iq-lilac-phi.vercel.app

The frontend sends API requests to the deployed Render backend.

---

## Backend — Render

The FastAPI backend is deployed on Render.

Backend URL:

https://incidentiq-backend-ftab.onrender.com

Swagger:

https://incidentiq-backend-ftab.onrender.com/docs

---

# 🔗 API

## Analyze Incident

### Endpoint

```text
POST /api/incidents/analyze
```

### Request

```json
{
  "incident": "Payment API is returning 503 errors again. Redis memory is around 96%."
}
```

### Response

The API returns information including:

```text
incident
related_memories
memory_count
ai_analysis
memory_saved
memory_status
memory_quality
memory_quality_reason
memory_decision
memory_saved_summary
```

---

# 🧪 API Example

Example request:

```bash
curl -X POST \
  https://incidentiq-backend-ftab.onrender.com/api/incidents/analyze \
  -H "Content-Type: application/json" \
  -d "{\"incident\":\"Payment API is returning 503 errors again. Redis memory is around 96%.\"}"
```

---

# 🔒 Security

Sensitive credentials are stored through environment variables.

The project uses:

```text
.env
```

for local secrets.

The `.gitignore` prevents `.env` from being committed.

Never expose:

- Hindsight API keys
- Groq API keys
- other production credentials

in source code, screenshots, documentation, or public repositories.

---

# 📸 Screenshots

Add project screenshots to the `docs/` directory.

Recommended screenshots:

```text
docs/
├── dashboard.png
├── payment-memory-saved.png
├── payment-ai-analysis.png
├── order-memory-not-saved.png
└── architecture.png
```

Recommended screenshot sequence:

### 1. Dashboard

Show the IncidentIQ landing page.

### 2. Historical Memory

Show Hindsight recalling previous incident knowledge.

### 3. AI Analysis

Show Groq's analysis using historical context.

### 4. Memory Saved

Show the Payment API incident producing:

```text
Memory Saved
SAVE
Verified
```

### 5. Memory Not Saved

Show the Order API incident producing:

```text
Memory Not Saved
DO_NOT_SAVE
Not verified
```

---

# 📈 Why IncidentIQ Is Different

IncidentIQ is designed around the idea that an incident-response agent should become more useful as verified operational knowledge accumulates.

The system does not simply answer:

```text
"What should I do?"
```

It also asks:

```text
"What has happened before?"
```

and:

```text
"Was the previous knowledge actually verified?"
```

This creates a persistent feedback loop between past incidents and future incident response.

---

# 🧠 Core Design Principle

```text
Recall historical knowledge
          ↓
Use it to reason about the current incident
          ↓
Provide actionable guidance
          ↓
Retain only verified knowledge
          ↓
Use that knowledge in future incidents
```

---

# 🎯 Use Cases

IncidentIQ can support production engineering workflows involving:

- API failures
- database incidents
- infrastructure issues
- caching problems
- service outages
- resource exhaustion
- recurring operational incidents
- deployment-related failures
- performance incidents

The system is designed around a focused incident-response workflow rather than general-purpose chat.

---

# 🚀 Future Improvements

Potential future extensions include:

- Integration with monitoring platforms
- Incident timeline generation
- Slack incident notifications
- Jira/Linear incident ticket creation
- Log aggregation integrations
- Service dependency graphs
- Incident severity classification
- Automatic incident postmortem generation
- Team-specific operational memory
- Incident trend analytics
- More advanced memory evaluation

---

# 🏆 Project Highlights

IncidentIQ demonstrates:

- Persistent AI memory
- Semantic historical recall
- AI-assisted incident investigation
- Historical context-aware reasoning
- Memory-quality validation
- Verified knowledge retention
- Protection against unverified memory
- Full-stack deployment
- Production-style API architecture

---

# 📌 Project Links

| Resource | Link |
|---|---|
| Live Demo | https://incident-iq-lilac-phi.vercel.app |
| GitHub | https://github.com/shivpalrathod/-IncidentIQ |
| Backend | https://incidentiq-backend-ftab.onrender.com |
| API Docs | https://incidentiq-backend-ftab.onrender.com/docs |

---

# 👨‍💻 Project

## IncidentIQ

**AI Incident Response Agent with Persistent Institutional Memory**

Built with:

```text
React
FastAPI
Hindsight
Groq
Vercel
Render
```

IncidentIQ turns verified incident experience into persistent institutional memory so future incidents can benefit from what the system has already learned.