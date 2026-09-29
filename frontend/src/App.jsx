import { useState } from "react";

import {
  Activity,
  Brain,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  Search,
  ShieldAlert,
  Sparkles,
  TriangleAlert,
  ArrowRight,
  Lightbulb,
  Save,
} from "lucide-react";

import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [incident, setIncident] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // =========================================
  // Analyze Incident
  // =========================================

  const analyzeIncident = async () => {
    if (!incident.trim()) {
      setError("Please describe the incident first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        `${API_URL}/api/incidents/analyze`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            incident: incident.trim(),
          }),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();

        throw new Error(
          errorText || `Server error: ${response.status}`
        );
      }

      const data = await response.json();

      setResult(data);
    } catch (err) {
      console.error("IncidentIQ error:", err);

      setError(
        "Unable to connect to IncidentIQ backend. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================
  // Example Incident
  // =========================================

  const handleExample = () => {
    setIncident(
      "Payment API is returning 503 errors again. Redis memory is around 96%."
    );

    setError("");
  };

  // =========================================
  // Clear
  // =========================================

  const handleClear = () => {
    setIncident("");
    setResult(null);
    setError("");
  };

  // =========================================
  // Memory Type Label
  // =========================================

  const getMemoryType = (type) => {
    const normalized = String(type || "").toLowerCase();

    if (normalized === "world") {
      return {
        label: "World Fact",
        className: "memory-world",
      };
    }

    if (normalized === "experience") {
      return {
        label: "Previous Experience",
        className: "memory-experience",
      };
    }

    if (normalized === "observation") {
      return {
        label: "Observation",
        className: "memory-observation",
      };
    }

    return {
      label: type || "Memory",
      className: "memory-default",
    };
  };

  // =========================================
  // Render
  // =========================================

  return (
    <div className="app">

      {/* Background */}

      <div className="glow glow-one"></div>
      <div className="glow glow-two"></div>

      {/* =====================================
          HEADER
      ====================================== */}

      <header className="header">

        <div className="brand">

          <div className="brand-icon">
            <Brain size={25} />
          </div>

          <div>
            <h1>IncidentIQ</h1>

            <p>
              AI Incident Response with Persistent Memory
            </p>
          </div>

        </div>

        <div className="system-status">

          <span className="status-dot"></span>

          System Online

        </div>

      </header>

      {/* =====================================
          MAIN
      ====================================== */}

      <main className="container">

        {/* ===================================
            HERO
        ==================================== */}

        <section className="hero">

          <div className="hero-badge">

            <Sparkles size={15} />

            HINDSIGHT-POWERED INCIDENT RESPONSE

          </div>

          <h2>

            Resolve incidents with

            <span>
              institutional memory.
            </span>

          </h2>

          <p>

            IncidentIQ remembers previous production incidents,
            their root causes and resolutions, then uses that
            historical knowledge to help engineers respond faster.

          </p>

        </section>

        {/* ===================================
            INCIDENT INPUT
        ==================================== */}

        <section className="incident-card">

          <div className="section-heading">

            <div className="heading-icon warning">
              <ShieldAlert size={20} />
            </div>

            <div>

              <h3>
                Report Production Incident
              </h3>

              <p>
                Describe what is happening in your production system.
              </p>

            </div>

          </div>

          <textarea
            value={incident}
            onChange={(event) => {
              setIncident(event.target.value);
              setError("");
            }}
            placeholder="Example: Payment API is returning 503 errors..."
            rows="5"
          />

          <div className="input-footer">

            <div className="left-actions">

              <button
                className="example-button"
                onClick={handleExample}
                type="button"
              >
                Try Example
              </button>

              {(result || incident) && (

                <button
                  className="clear-button"
                  onClick={handleClear}
                  type="button"
                >
                  Clear
                </button>

              )}

            </div>

            <button
              className="analyze-button"
              onClick={analyzeIncident}
              disabled={loading}
              type="button"
            >

              {loading ? (

                <>
                  <span className="spinner"></span>
                  Analyzing...
                </>

              ) : (

                <>
                  <Search size={18} />
                  Analyze Incident
                </>

              )}

            </button>

          </div>

          {error && (

            <div className="error-box">

              <TriangleAlert size={18} />

              <span>
                {error}
              </span>

            </div>

          )}

        </section>

        {/* ===================================
            PROCESSING
        ==================================== */}

        {loading && (

          <section className="processing-card">

            <div className="processing-icon">
              <Brain size={28} />
            </div>

            <div>

              <h3>
                IncidentIQ is thinking...
              </h3>

              <p>
                Recalling institutional memory from Hindsight
                and analyzing it with AI.
              </p>

            </div>

          </section>

        )}

        {/* ===================================
            RESULTS
        ==================================== */}

        {result && !loading && (

          <>

            {/* =================================
                STATS
            ================================== */}

            <section className="stats-grid">

              <div className="stat-card">

                <div className="stat-icon blue">
                  <Database size={19} />
                </div>

                <div>

                  <span>
                    Memories Recalled
                  </span>

                  <strong>
                    {result.related_memories?.length || 0}
                  </strong>

                </div>

              </div>

              <div className="stat-card">

                <div className="stat-icon purple">
                  <Brain size={19} />
                </div>

                <div>

                  <span>
                    Memory System
                  </span>

                  <strong>
                    Hindsight
                  </strong>

                </div>

              </div>

              <div className="stat-card">

                <div className="stat-icon green">
                  <Cpu size={19} />
                </div>

                <div>

                  <span>
                    AI Engine
                  </span>

                  <strong>
                    Groq
                  </strong>

                </div>

              </div>

              <div className="stat-card">

                <div className="stat-icon orange">
                  <Activity size={19} />
                </div>

                <div>

                  <span>
                    Status
                  </span>

                  <strong>
                    Analyzed
                  </strong>

                </div>

              </div>

            </section>

            {/* =================================
                MEMORY + AI
            ================================== */}

            <div className="results-grid">

              {/* =================================
                  INSTITUTIONAL MEMORY
              ================================== */}

              <section className="panel memory-panel">

                <div className="panel-header">

                  <div>

                    <div className="panel-title">

                      <Brain size={20} />

                      <h3>
                        Institutional Memory
                      </h3>

                    </div>

                    <p>
                      Historical context recalled from Hindsight
                    </p>

                  </div>

                  <span className="memory-badge">

                    {result.related_memories?.length || 0}

                    {" "}

                    recalled

                  </span>

                </div>

                {/* Memory introduction */}

                {result.related_memories?.length > 0 && (

                  <div className="memory-intro">

                    <div className="memory-intro-icon">
                      <Brain size={17} />
                    </div>

                    <div>

                      <strong>
                        Hindsight found relevant knowledge
                      </strong>

                      <span>
                        IncidentIQ is using previous production
                        experience to inform this response.
                      </span>

                    </div>

                  </div>

                )}

                {/* Memory cards */}

                <div className="memory-list">

                  {result.related_memories?.length > 0 ? (

                    result.related_memories.map(
                      (memory, index) => {

                        const memoryType =
                          getMemoryType(memory.type);

                        return (

                          <div
                            className="memory-item"
                            key={`${memory.type}-${index}`}
                          >

                            <div className="memory-number">
                              {String(index + 1).padStart(2, "0")}
                            </div>

                            <div className="memory-content">

                              <div className="memory-top">

                                <span
                                  className={`memory-type ${memoryType.className}`}
                                >
                                  {memoryType.label}
                                </span>

                                <span className="memory-source">
                                  Hindsight
                                </span>

                              </div>

                              <p>
                                {memory.text}
                              </p>

                            </div>

                          </div>

                        );
                      }

                    )

                  ) : (

                    <div className="empty-memory">

                      <div className="empty-memory-icon">
                        <Database size={28} />
                      </div>

                      <h4>
                        No relevant historical memory
                      </h4>

                      <p>
                        IncidentIQ is analyzing this incident
                        using the current evidence.
                      </p>

                    </div>

                  )}

                </div>

                {/* =================================
                    MEMORY STATUS
                ================================== */}

                <div
                  className={`memory-saved ${
                    result.memory_saved
                      ? "memory-saved-success"
                      : "memory-saved-not"
                  }`}
                >

                  <div className="saved-header">

                    <div className="saved-icon">

                      {result.memory_saved ? (
                        <Save size={16} />
                      ) : (
                        <TriangleAlert size={16} />
                      )}

                    </div>

                    <div>

                      <strong>
                        {result.memory_saved
                          ? "Memory Saved"
                          : "Memory Not Saved"}
                      </strong>

                      <span>
                        {result.memory_saved
                          ? "Stored in Hindsight for future incidents"
                          : "This incident was not stored as institutional memory"}
                      </span>

                    </div>

                  </div>

                  {/* Saved memory summary */}

                  {result.memory_saved &&
                    result.memory_saved_summary && (

                      <p>
                        {result.memory_saved_summary}
                      </p>

                  )}

                  {/* Not saved explanation */}

                  {!result.memory_saved && (

                    <div className="memory-status-details">

                      {result.memory_quality_reason && (

                        <p>
                          <strong>Reason:</strong>{" "}
                          {result.memory_quality_reason}
                        </p>

                      )}

                      {result.memory_decision && (

                        <p>
                          <strong>AI Decision:</strong>{" "}
                          {result.memory_decision}
                        </p>

                      )}

                      {typeof result.memory_quality !==
                        "undefined" && (

                        <p>
                          <strong>Memory Quality:</strong>{" "}
                          {result.memory_quality
                            ? "Verified"
                            : "Not verified"}
                        </p>

                      )}

                    </div>

                  )}

                </div>

              </section>

              {/* =================================
                  AI ANALYSIS
              ================================== */}

              <section className="panel ai-panel">

                <div className="panel-header">

                  <div>

                    <div className="panel-title">

                      <Sparkles size={20} />

                      <h3>
                        AI Incident Analysis
                      </h3>

                    </div>

                    <p>
                      Groq analysis using recalled historical context
                    </p>

                  </div>

                  <span className="ai-badge">
                    AI Generated
                  </span>

                </div>

                <div className="analysis-content">

                  <pre>
                    {result.ai_analysis}
                  </pre>

                </div>

              </section>

            </div>

            {/* =================================
                MEMORY LOOP
            ================================== */}

            <section className="memory-loop">

              <div className="loop-heading">

                <div className="loop-icon">
                  <Brain size={20} />
                </div>

                <div>

                  <h3>
                    IncidentIQ Memory Loop
                  </h3>

                  <p>
                    Today's incident becomes tomorrow's institutional knowledge.
                  </p>

                </div>

              </div>

              <div className="loop-steps">

                <div className="loop-step">

                  <span>
                    01
                  </span>

                  <strong>
                    Recall
                  </strong>

                  <small>
                    Hindsight retrieves relevant history.
                  </small>

                </div>

                <ArrowRight
                  className="loop-arrow"
                  size={18}
                />

                <div className="loop-step">

                  <span>
                    02
                  </span>

                  <strong>
                    Reason
                  </strong>

                  <small>
                    Groq analyzes historical context.
                  </small>

                </div>

                <ArrowRight
                  className="loop-arrow"
                  size={18}
                />

                <div className="loop-step">

                  <span>
                    03
                  </span>

                  <strong>
                    Respond
                  </strong>

                  <small>
                    Engineers receive actionable guidance.
                  </small>

                </div>

                <ArrowRight
                  className="loop-arrow"
                  size={18}
                />

                <div className="loop-step">

                  <span>
                    04
                  </span>

                  <strong>
                    Remember
                  </strong>

                  <small>
                    Useful incident knowledge is retained.
                  </small>

                </div>

              </div>

            </section>

            {/* =================================
                INCIDENT SUMMARY
            ================================== */}

            <section className="incident-summary">

              <div className="summary-icon">
                <ShieldAlert size={22} />
              </div>

              <div className="summary-text">

                <span>
                  Analyzed Incident
                </span>

                <p>
                  {result.incident}
                </p>

              </div>

              <div className="resolved-badge">

                <CheckCircle2 size={16} />

                Analysis Complete

              </div>

            </section>

          </>

        )}

        {/* ===================================
            HOW IT WORKS
        ==================================== */}

        {!result && !loading && (

          <section className="how-section">

            <div className="how-header">

              <h3>
                How IncidentIQ Works
              </h3>

              <p>
                Every incident makes the system more useful over time.
              </p>

            </div>

            <div className="flow">

              <div className="flow-card">

                <div className="flow-number">
                  01
                </div>

                <ShieldAlert size={23} />

                <h4>
                  Report
                </h4>

                <p>
                  Engineer reports a production incident.
                </p>

              </div>

              <div className="flow-line"></div>

              <div className="flow-card">

                <div className="flow-number">
                  02
                </div>

                <Brain size={23} />

                <h4>
                  Recall
                </h4>

                <p>
                  Hindsight searches previous incidents.
                </p>

              </div>

              <div className="flow-line"></div>

              <div className="flow-card">

                <div className="flow-number">
                  03
                </div>

                <Sparkles size={23} />

                <h4>
                  Reason
                </h4>

                <p>
                  Groq analyzes historical context.
                </p>

              </div>

              <div className="flow-line"></div>

              <div className="flow-card">

                <div className="flow-number">
                  04
                </div>

                <Database size={23} />

                <h4>
                  Learn
                </h4>

                <p>
                  Verified incident knowledge is retained in Hindsight.
                </p>

              </div>

            </div>

          </section>

        )}

      </main>

      {/* =====================================
          FOOTER
      ====================================== */}

      <footer>

        <div>

          <Clock size={15} />

          IncidentIQ • Persistent AI Memory

        </div>

        <span>
          Powered by Hindsight + Groq
        </span>

      </footer>

    </div>
  );
}

export default App;