import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  AlertTriangle,
  BarChart3,
  Brain,
  FileUp,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function Stat({ icon: Icon, label, value, tone }) {
  return (
    <section className={`stat ${tone || ""}`}>
      <div className="statIcon">
        <Icon size={20} />
      </div>
      <p>{label}</p>
      <strong>{value}</strong>
    </section>
  );
}

function Heatmap({ labels, matrix }) {
  return (
    <div className="heatmap">
      {matrix.map((row, rowIndex) =>
        row.map((value, colIndex) => (
          <div
            className="heatCell"
            key={`${rowIndex}-${colIndex}`}
            title={`${labels[rowIndex]} / ${labels[colIndex]}: ${value}`}
            style={{ backgroundColor: `rgba(15, 118, 110, ${Math.max(0.12, Math.abs(value))})` }}
          >
            {value}
          </div>
        )),
      )}
    </div>
  );
}

function App() {
  const [analysis, setAnalysis] = useState(null);
  const [market, setMarket] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("Upload your bankruptcy dataset or a company CSV to begin.");

  const ratioBars = useMemo(() => {
    if (!analysis) return [];
    return Object.entries(analysis.ratios).map(([name, value]) => ({
      name: name.replaceAll("_", " "),
      value,
    }));
  }, [analysis]);

  async function uploadCsv(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setMessage("Analyzing financial risk...");
    const form = new FormData();
    form.append("file", file);
    try {
      const response = await fetch(`${API_BASE}/upload_csv`, { method: "POST", body: form });
      if (!response.ok) throw new Error(await response.text());
      setAnalysis(await response.json());
      setMessage("Analysis complete.");
    } catch (error) {
      setMessage(`Upload failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function trainModel() {
    setLoading(true);
    setMessage("Training bankruptcy model from the dataset...");
    try {
      const response = await fetch(`${API_BASE}/train`, { method: "POST" });
      if (!response.ok) throw new Error(await response.text());
      const result = await response.json();
      setMessage(`Model trained. ROC-AUC: ${result.roc_auc}`);
    } catch (error) {
      setMessage(`Training failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function loadMarket() {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/market/correlation?symbols=AAPL,MSFT,JPM,V,MA`);
      setMarket(await response.json());
    } finally {
      setLoading(false);
    }
  }

  const risk = analysis?.bankruptcy?.risk_score ?? 0;
  const riskColor = risk >= 70 ? "#be123c" : risk >= 40 ? "#b45309" : "#047857";

  return (
    <main className="appShell">
      <aside className="sidebar">
        <div className="brand">
          <Brain size={28} />
          <div>
            <h1>Risk Intelligence</h1>
            <span>Financial AI Console</span>
          </div>
        </div>
        <label className="uploadButton">
          <FileUp size={18} />
          Upload CSV
          <input type="file" accept=".csv" onChange={uploadCsv} />
        </label>
        <button onClick={trainModel} disabled={loading}>
          <ShieldCheck size={18} />
          Train Model
        </button>
        <button onClick={loadMarket} disabled={loading}>
          <TrendingUp size={18} />
          Market Heatmap
        </button>
        <p className="statusText">{message}</p>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <h2>AI Financial Risk Intelligence Platform</h2>
            <p>Bankruptcy prediction, fraud anomalies, ratios, sentiment, and analyst-style reporting.</p>
          </div>
          <span className="liveBadge">{loading ? "Working" : "Ready"}</span>
        </header>

        <section className="statsGrid">
          <Stat icon={AlertTriangle} label="Risk Score" value={`${risk}%`} tone="danger" />
          <Stat icon={BarChart3} label="Risk Category" value={analysis?.bankruptcy?.category || "Pending"} />
          <Stat icon={ShieldCheck} label="Fraud Score" value={`${analysis?.fraud?.fraud_score ?? 0}%`} />
          <Stat icon={Brain} label="AI Source" value={analysis?.bankruptcy?.model_source || "Not run"} />
        </section>

        <section className="mainGrid">
          <div className="panel wide">
            <div className="panelHeader">
              <h3>Risk Trend</h3>
              <span style={{ color: riskColor }}>{analysis ? analysis.bankruptcy.category : "Waiting"}</span>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={analysis?.trends || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="debt_ratio" stroke="#0f766e" fill="#99f6e4" />
                <Area type="monotone" dataKey="cash_flow_health" stroke="#7c3aed" fill="#ddd6fe" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="panel">
            <div className="panelHeader">
              <h3>Ratio Engine</h3>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={ratioBars}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" hide />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value">
                  {ratioBars.map((_, index) => (
                    <Cell key={index} fill={index % 2 ? "#7c3aed" : "#0f766e"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="panel">
            <div className="panelHeader">
              <h3>Stock Correlation</h3>
              <span>{market?.source || "Load data"}</span>
            </div>
            {market ? <Heatmap labels={market.symbols} matrix={market.matrix} /> : <p className="empty">No market matrix loaded.</p>}
          </div>

          <div className="panel wide report">
            <div className="panelHeader">
              <h3>AI Analyst Report</h3>
            </div>
            <pre>{analysis?.report || "Upload a CSV to generate the analyst-style report."}</pre>
          </div>

          <div className="panel wide">
            <div className="panelHeader">
              <h3>Recommendations</h3>
            </div>
            <div className="recommendations">
              {(analysis?.recommendations || ["Train the model and upload financial data to receive recommendations."]).map((item) => (
                <div className="recommendation" key={item}>{item}</div>
              ))}
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
