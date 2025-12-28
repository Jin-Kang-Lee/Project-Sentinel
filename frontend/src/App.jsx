import { useMemo, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/analyze";

const TIMELINE = [
  "PDF intake and validation",
  "Statement extraction and schema checks",
  "Risk engine scoring",
  "Compliance or wealth path response",
];

const ADVISORY_LABELS = ["Recommendation"];
const COMPLIANCE_LABELS = ["Reason", "Regulation"];

function Badge({ label }) {
  return <span className="badge">{label}</span>;
}

function parseSections(text, kind) {
  if (!text) {
    return [];
  }

  const normalized = text.replace(/\r\n/g, "\n");
  const regex = /(Reason|Regulation|Recommendation)\s*[:\-]/gi;
  const sections = [];

  let match;
  let lastLabel = null;
  let lastIndex = 0;

  while ((match = regex.exec(normalized)) !== null) {
    if (lastLabel) {
      const content = normalized.slice(lastIndex, match.index).trim();
      if (content) {
        sections.push({ label: lastLabel, content });
      }
    }
    lastLabel = match[1].charAt(0).toUpperCase() + match[1].slice(1).toLowerCase();
    lastIndex = match.index + match[0].length;
  }

  if (lastLabel) {
    const content = normalized.slice(lastIndex).trim();
    if (content) {
      sections.push({ label: lastLabel, content });
    }
  }

  if (sections.length) {
    return sections;
  }

  const sentences = normalized.split(/(?<=[.!?])\s+/).filter(Boolean);

  if (normalized.includes("Wealth Product")) {
    return [
      { label: "Recommendation", content: normalized },
    ];
  }

  if (sentences.length >= 2) {
    if (kind === "compliance") {
      return [
        { label: "Reason", content: sentences.slice(0, 2).join(" ") },
        { label: "Regulation", content: sentences.slice(1).join(" ") },
      ];
    }
    return [
      { label: "Recommendation", content: sentences.join(" ") },
    ];
  }

  if (kind === "compliance") {
    return [
      { label: "Reason", content: normalized },
      { label: "Regulation", content: "Not specified in the response." },
    ];
  }

  return [
    { label: "Recommendation", content: normalized },
  ];
}

function MemoSections({ sections, emptyText, labels, bulletRecommendations }) {
  if (!sections.length) {
    return <p className="card-body">{emptyText}</p>;
  }

  const ordered = labels.map((label) =>
    sections.find((section) => section.label === label)
  ).filter(Boolean);

  return (
    <div className="memo-list">
      {ordered.map((section) => (
        <div key={section.label} className="memo-section">
          <span className="memo-label">{section.label}:</span>
          {bulletRecommendations && section.label === "Recommendation" ? (
            <ul className="memo-bullets">
              {section.content
                .split(/\n+/)
                .map((line) => line.trim())
                .filter(Boolean)
                .map((line, index) => (
                  <li key={`${section.label}-${index}`}>{line}</li>
                ))}
            </ul>
          ) : (
            <span className="memo-text">{section.content}</span>
          )}
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const output = useMemo(() => {
    if (!result) {
      return {
        verdict: "Awaiting Analysis",
        tone: "",
        headline: "Upload a statement to run Sentinel.",
        detail: "Decision details will appear after processing.",
      };
    }

    if (result.final_decision === "REJECT") {
      return {
        verdict: "High Risk",
        tone: "alert",
        headline: "Escalate to compliance review.",
        detail:
          "Multiple risk indicators were detected. Review MAS guideline references below.",
      };
    }

    if (result.final_decision === "APPROVE") {
      return {
        verdict: "Low Risk",
        tone: "safe",
        headline: "Onboard with advisory handoff.",
        detail:
          "Affordability metrics pass and no AML flags triggered. Review wealth product suggestions below.",
      };
    }

    return {
      verdict: "Analysis Error",
      tone: "alert",
      headline: "Unable to process the statement.",
      detail: "Please try another PDF or check the backend logs.",
    };
  }, [result]);

  const handleUpload = (event) => {
    const selected = event.target.files?.[0];
    setFile(selected || null);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setStatus("running");
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail || "Backend error");
      }

      const payload = await response.json();
      setResult(payload);
      setStatus("done");
    } catch (err) {
      setStatus("error");
      setError(err.message || "Unexpected error");
    }
  };

  return (
    <div className="page">
      <div className="glow" aria-hidden="true" />
      <header className="nav">
        <div className="logo">
          <span className="logo-dot" />
          Sentinel Portal
        </div>
        <div className="nav-actions">
          <Badge label="Mock UI" />
          <button className="ghost">View Audit Log</button>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-text">
            <p className="eyebrow">KYC and AML Decisioning</p>
            <h1>
              Bank onboarding with <span>machine-backed</span> compliance clarity.
            </h1>
            <p className="lede">
              Upload a statement, get a deterministic risk verdict, and see the
              MAS guideline references or wealth products immediately.
            </p>
            <div className="hero-meta">
              <div>
                <p className="meta-label">Decision SLA</p>
                <p className="meta-value">Under 2 minutes</p>
              </div>
              <div>
                <p className="meta-label">Coverage</p>
                <p className="meta-value">MAS Notice 626</p>
              </div>
              <div>
                <p className="meta-label">Risk Engine</p>
                <p className="meta-value">Deterministic checks</p>
              </div>
            </div>
          </div>
          <div className="hero-panel">
            <div className="panel-header">
              <h2>Statement Intake</h2>
              <p>Upload PDF statements and run the Sentinel workflow.</p>
            </div>
            <label className="upload" htmlFor="pdfUpload">
              <input
                id="pdfUpload"
                type="file"
                accept="application/pdf"
                onChange={handleUpload}
              />
              <div>
                <p className="upload-title">Drop a PDF or browse files</p>
                <p className="upload-sub">
                  {file ? file.name : "Supported: PDF statements"}
                </p>
              </div>
              <span className="upload-pill">Statement PDF</span>
            </label>
            <div className="panel-actions">
              <div className="select">
                <span>Backend</span>
                <span>{API_URL}</span>
              </div>
              <button
                className="primary"
                onClick={handleAnalyze}
                disabled={!file || status === "running"}
              >
                {status === "running" ? "Analyzing..." : "Run Sentinel"}
              </button>
            </div>
            <ul className="timeline">
              {TIMELINE.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ul>
          </div>
        </section>

        <section className="results">
          <div className={`result-card ${output.tone}`}>
            <div className="result-header">
              <div>
                <p className="eyebrow">Decision Output</p>
                <h3>{output.verdict}</h3>
                <p className="result-detail">{output.headline}</p>
              </div>
              <Badge
                label={
                  status === "running"
                    ? "Processing"
                    : status === "done"
                    ? "Ready"
                    : "Waiting"
                }
              />
            </div>
            {status === "running" && (
              <div className="loading-row" role="status" aria-live="polite">
                <span className="spinner" aria-hidden="true" />
                Processing document...
              </div>
            )}
            <p className="result-body">{output.detail}</p>
            {status === "error" && (
              <p className="result-body">{error}</p>
            )}
            <div className="signal">
              <div>
                <p className="meta-label">Affordability</p>
                <p className="meta-value">
                  {result?.risk_analysis?.math_analysis?.ratio
                    ? `${Math.round(
                        result.risk_analysis.math_analysis.ratio * 100
                      )}%`
                    : "Pending"}
                </p>
              </div>
              <div>
                <p className="meta-label">Structuring</p>
                <p className="meta-value">
                  {result?.risk_analysis?.compliance_analysis?.category ||
                    "Pending"}
                </p>
              </div>
              <div>
                <p className="meta-label">Source of Wealth</p>
                <p className="meta-value">
                  {result?.client_data?.source_of_wealth || "Pending"}
                </p>
              </div>
            </div>
          </div>

          <div className="result-grid">
            <div className="detail-card">
              <h4>MAS Guideline References</h4>
              <p className="card-subtitle">
                Displayed when the client is classified as high risk.
              </p>
              <div className="card-list">
                <div className="card-item">
                  <p className="card-title">Compliance memo</p>
                  <MemoSections
                    sections={
                      result?.final_decision === "REJECT"
                        ? parseSections(result?.legal_opinion, "compliance")
                        : []
                    }
                    emptyText="Run Sentinel on a high risk client to view MAS references."
                    labels={COMPLIANCE_LABELS}
                  />
                </div>
              </div>
            </div>
            <div className="detail-card">
              <h4>Wealth Product Suggestions</h4>
              <p className="card-subtitle">
                Displayed when the client is classified as low risk.
              </p>
              <div className="card-list">
                <div className="card-item">
                  <p className="card-title">Advisory memo</p>
                  <MemoSections
                    sections={
                      result?.final_decision === "APPROVE"
                        ? parseSections(result?.wealth_plan, "advisory")
                        : []
                    }
                    emptyText="Run Sentinel on a low risk client to view products."
                    labels={ADVISORY_LABELS}
                    bulletRecommendations
                  />
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
