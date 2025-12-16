// App.js
import { useMemo, useState } from "react";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("groups");
  const [sectorsOpen, setSectorsOpen] = useState(true);
  const [activeGroup, setActiveGroup] = useState({ type: "watchlist", id: "1" });
  const [promptText, setPromptText] = useState(
    "Title: Q2 FY26 IT watchlist summary\n\nSummarise key management guidance, risks, and any change in tone versus the last two quarters. Highlight major surprises and numbers that investors should care about."
  );
  const [showPromptEditor, setShowPromptEditor] = useState(false);
  const [promptEditorContext, setPromptEditorContext] = useState({
    scope: "group",
    targetName: "Watchlist 1",
  });

  // Ask tab state
  const [askScope, setAskScope] = useState("company"); // "company" or "group"
  const [askNumTranscripts, setAskNumTranscripts] = useState(4); // 1–10
  const [askIncludeSectorOutputs, setAskIncludeSectorOutputs] = useState(true);

  const topTabs = useMemo(
    () => [
      { id: "groups", icon: "📂", label: "Groups" },
      { id: "ask", icon: "💬", label: "Ask" },
      { id: "settings", icon: "⚙️", label: "Settings" },
    ],
    []
  );

  const watchlists = useMemo(
    () => [
      { id: "1", name: "Watchlist 1", count: 32 },
      { id: "2", name: "Watchlist 2", count: 18 },
    ],
    []
  );

  const sectors = useMemo(
    () => [
      { id: "it", name: "IT Sector", count: 10 },
      { id: "ind", name: "Industrial", count: 14 },
      { id: "auto", name: "Auto", count: 7 },
      { id: "banks", name: "Banks", count: 9 },
    ],
    []
  );

  const isGroupActive = (type, id) => activeGroup.type === type && activeGroup.id === id;

  // Only show first line of prompt
  const promptPreview = promptText.split("\n")[0];

  const openGroupPromptEditor = () => {
    setPromptEditorContext({ scope: "group", targetName: "Watchlist 1" });
    setShowPromptEditor(true);
  };

  const openCompanyPromptEditor = (companyName) => {
    setPromptEditorContext({ scope: "company", targetName: companyName });
    setShowPromptEditor(true);
  };

  const isGroupEditor = promptEditorContext.scope === "group";

  return (
    <div className="app-root">
      {/* Top bar */}
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <div className="brand-logo">RA</div>
            <div>
              <div className="brand-text-main">RAIO</div>
              <div className="brand-text-sub">Research Automation AI</div>
            </div>
          </div>

          <nav className="top-tabs">
            {topTabs.map((tab) => (
              <button
                key={tab.id}
                className={`top-tab ${activeTab === tab.id ? "active" : ""}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <span className="top-tab-icon">{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>

          <div className="top-right">
            <span className="plan-pill">Trial · 10 transcripts/day</span>
            <div className="user-chip">
              <div className="user-avatar">VG</div>
              <div>
                <div style={{ fontSize: "12px", fontWeight: 500 }}>Vipin Goel</div>
                <div style={{ fontSize: "11px", color: "var(--text-softer)" }}>
                  Mirabilis Invest · Org admin
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main shell */}
      <div className="app-shell">
        {/* Sidebar is only shown on Groups tab */}
        {activeTab === "groups" && (
          <aside className="sidebar">
            <div className="sidebar-header">
              <div className="sidebar-title">Groups</div>
              <div className="sidebar-actions">
                <button className="badge-btn secondary">+ Watchlist</button>
                <button className="badge-btn">+ Sector</button>
              </div>
            </div>

            {/* Watchlists */}
            <div className="sidebar-section">
              <div className="sidebar-section-header">Watchlists</div>
              <div className="sidebar-list">
                {watchlists.map((wl) => (
                  <div
                    key={wl.id}
                    className={`sidebar-item ${
                      isGroupActive("watchlist", wl.id) ? "active" : ""
                    }`}
                    onClick={() => setActiveGroup({ type: "watchlist", id: wl.id })}
                  >
                    <span>{wl.name}</span>
                    <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                      <span
                        className={`sidebar-item-badge ${
                          isGroupActive("watchlist", wl.id) ? "primary" : ""
                        }`}
                      >
                        {wl.count}
                      </span>
                      <button
                        className="sidebar-delete-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          // future: delete watchlist API
                        }}
                      >
                        🗑
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Sectors */}
            <div className="sidebar-section">
              <div
                className="sidebar-collapse-header"
                onClick={() => setSectorsOpen((prev) => !prev)}
              >
                <span>Sectors</span>
                <span className="sidebar-collapse-icon">
                  {sectorsOpen ? "▾" : "▸"}
                </span>
              </div>
              <div
                className="sidebar-list"
                style={{ display: sectorsOpen ? "flex" : "none" }}
              >
                {sectors.map((sector) => (
                  <div
                    key={sector.id}
                    className={`sidebar-item ${
                      isGroupActive("sector", sector.id) ? "active" : ""
                    }`}
                    onClick={() => setActiveGroup({ type: "sector", id: sector.id })}
                  >
                    <span>{sector.name}</span>
                    <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                      <span className="sidebar-item-badge">{sector.count}</span>
                      <button
                        className="sidebar-delete-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          // future: delete sector API
                        }}
                      >
                        🗑
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="sidebar-footer">
              <div style={{ fontSize: "11px" }}>ValueWise LLP</div>
            </div>
          </aside>
        )}

        {/* Right main area */}
        <main className="main">
          {/* GROUPS TAB */}
          <section className={`tab-panel ${activeTab === "groups" ? "active" : ""}`}>
            <div className="main-card">
              {/* Group header */}
              <div className="groups-header-row">
                <div className="groups-header-meta">
                  <div className="main-card-title">
                    Watchlist 1
                    <span className="tag-pill">32 companies</span>
                  </div>
                  <div className="main-card-subtitle">
                    Last updated · 2 minutes ago · Timezone: IST
                  </div>
                </div>
                <div className="groups-header-actions">
                  <span className="main-card-subtitle">
                    Group prompt will auto-run when all companies have reported.
                  </span>
                </div>
              </div>

              {/* Group-level prompt summary */}
              <div className="prompt-card">
                <div className="prompt-card-header">
                  <div>
                    <div className="prompt-card-title">Group-level prompt</div>
                    <div className="main-card-subtitle">
                      Applies on transcripts for all companies in this watchlist.
                    </div>
                  </div>

                  {/* Right side: buttons + current prompt under them */}
                  <div className="prompt-card-header-right">
                    <div className="prompt-card-actions">
                      <button className="btn-primary btn-sm">Run prompt now</button>
                      <button
                        className="btn-outline btn-sm"
                        onClick={openGroupPromptEditor}
                      >
                        Edit prompt
                      </button>
                    </div>

                    <div className="prompt-card-body">
                      <span className="prompt-card-body-label">Current prompt:</span>{" "}
                      <span title={promptText}>
                        {promptPreview.length > 90
                          ? `${promptPreview.slice(0, 90)}…`
                          : promptPreview}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="prompt-card-footer">
                  <div className="prompt-card-footer-left">
                    <div className="badge-status success">
                      <span className="badge-status-dot"></span>
                      <span>Last run: Completed · 24 Oct 10:31 AM</span>
                    </div>
                    <span className="pill-small">Latest coverage: Q2 FY26</span>
                    <span className="pill-small">Progress: 7 / 8 companies reported</span>
                  </div>
                  <div className="prompt-card-footer-right">
                    <span
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        fontSize: "12px",
                      }}
                    >
                      Auto emails
                      <div className="toggle on">
                        <div className="toggle-knob"></div>
                      </div>
                    </span>
                    <span style={{ fontSize: "11px", color: "var(--text-softer)" }}>
                      Emails: research@firm.com, team@firm.com, &amp; 4 more
                    </span>
                  </div>
                </div>
              </div>

              {/* Company search / add */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "8px",
                  marginTop: "10px",
                }}
              >
                <div
                  style={{
                    flex: 1,
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  <input
                    type="text"
                    className="input"
                    placeholder="Search companies to add (name / ticker / ISIN). Click a suggestion to add to this group."
                  />
                  {/* Future: dropdown suggestions; click = add to watchlist */}
                </div>
              </div>

              {/* Company table */}
              <div className="table-wrapper" style={{ marginTop: "10px" }}>
                <table>
                  <thead>
                    <tr>
                      <th>Company</th>
                      <th>Last concall</th>
                      <th>Analysis</th>
                      <th>Auto email</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {/* Row 1 – transcript available, analysis completed */}
                    <tr>
                      <td>
                        <div className="table-company-cell">
                          <span className="table-company-name">Infosys Ltd.</span>
                          <span className="table-company-sub">
                            INFY · IT Services · ISIN: INE009A01021
                          </span>
                        </div>
                      </td>
                      <td>
                        <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                          <span style={{ fontSize: "13px" }}>Q2 FY26 · 24 Oct 2025</span>
                          <span
                            style={{
                              fontSize: "12px",
                              color: "var(--text-soft)",
                            }}
                          >
                            Transcript available ·{" "}
                            <a href="#" className="link">
                              View
                            </a>{" "}
                            ·{" "}
                            <a href="#" className="link">
                              Download
                            </a>
                          </span>
                          <span
                            style={{
                              fontSize: "11px",
                              color: "var(--text-softer)",
                              marginTop: "2px",
                            }}
                          >
                            Available transcripts: Q2 FY26 · Q1 FY25 · Q4 FY24
                          </span>
                        </div>
                      </td>
                      <td>
                        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                          <span className="badge-status success">
                            <span className="badge-status-dot"></span>
                            Completed (10:31 AM)
                          </span>
                          <a href="#" className="link">
                            Open latest output
                          </a>
                        </div>
                      </td>
                      <td>
                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "8px",
                          }}
                        >
                          <div className="toggle on">
                            <div className="toggle-knob"></div>
                          </div>
                          <span
                            style={{
                              fontSize: "11px",
                              color: "var(--text-softer)",
                            }}
                          >
                            To: research@firm.com
                          </span>
                        </div>
                      </td>
                      <td>
                        <div className="table-actions">
                          <button className="btn-outline btn-sm">Run</button>
                          <button
                            className="btn-outline btn-sm"
                            onClick={() => openCompanyPromptEditor("Infosys Ltd.")}
                          >
                            Edit prompt
                          </button>
                          <button className="btn-outline btn-sm">Remove</button>
                        </div>
                      </td>
                    </tr>

                    {/* Row 2 – latest concall, transcript not yet available */}
                    <tr>
                      <td>
                        <div className="table-company-cell">
                          <span className="table-company-name">
                            Tata Consultancy Services
                          </span>
                          <span className="table-company-sub">
                            TCS · IT Services · ISIN: INE467B01029
                          </span>
                        </div>
                      </td>
                      <td>
                        <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                          <span style={{ fontSize: "13px" }}>Q2 FY26 · 23 Oct 2025</span>
                          <span
                            style={{
                              fontSize: "12px",
                              color: "var(--text-soft)",
                            }}
                          >
                            Transcript not yet available
                          </span>
                          <span
                            style={{
                              fontSize: "11px",
                              color: "var(--text-softer)",
                              marginTop: "2px",
                            }}
                          >
                            Available transcripts: Q1 FY25 · Q4 FY24
                          </span>
                        </div>
                      </td>
                      <td>
                        <span className="badge-status pending">
                          <span className="badge-status-dot"></span>
                          Will auto-run when transcript arrives
                        </span>
                      </td>
                      <td>
                        <div className="toggle">
                          <div className="toggle-knob"></div>
                        </div>
                      </td>
                      <td>
                        <div className="table-actions">
                          <button className="btn-outline btn-sm" disabled>
                            Run
                          </button>
                          <button
                            className="btn-outline btn-sm"
                            onClick={() =>
                              openCompanyPromptEditor("Tata Consultancy Services")
                            }
                          >
                            Edit prompt
                          </button>
                          <button className="btn-outline btn-sm">Remove</button>
                        </div>
                      </td>
                    </tr>

                    {/* Row 3 – no concall this quarter yet */}
                    <tr>
                      <td>
                        <div className="table-company-cell">
                          <span className="table-company-name">HCL Technologies</span>
                          <span className="table-company-sub">
                            HCLT · IT Services · ISIN: INE860A01027
                          </span>
                        </div>
                      </td>
                      <td>
                        <span
                          style={{
                            fontSize: "13px",
                            color: "var(--text-softer)",
                          }}
                        >
                          No concall transcript available yet this quarter
                        </span>
                      </td>
                      <td>
                        <span className="badge-status pending">
                          <span className="badge-status-dot"></span>
                          Will auto-run when transcript arrives
                        </span>
                      </td>
                      <td>
                        <div className="toggle on">
                          <div className="toggle-knob"></div>
                        </div>
                      </td>
                      <td>
                        <div className="table-actions">
                          <button
                            className="btn-outline btn-sm"
                            onClick={() => openCompanyPromptEditor("HCL Technologies")}
                          >
                            Edit prompt
                          </button>
                          <button className="btn-outline btn-sm">Remove</button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          {/* ASK TAB */}
          <section className={`tab-panel ${activeTab === "ask" ? "active" : ""}`}>
            <div className="ask-layout">
              {/* LEFT: setup (scope + entity + data) */}
              <div className="ask-card">
                <div>
                  <div className="ask-section-title">What do you want to ask about?</div>
                  <div className="ask-section-sub"></div>
                </div>

                {/* Scope toggle */}
                <div className="radio-row" style={{ marginTop: "8px" }}>
                  <label className="radio-item">
                    <input
                      type="radio"
                      className="radio-input"
                      name="ask-scope"
                      checked={askScope === "company"}
                      onChange={() => setAskScope("company")}
                    />
                    <span>Single company</span>
                  </label>
                  <label className="radio-item">
                    <input
                      type="radio"
                      className="radio-input"
                      name="ask-scope"
                      checked={askScope === "group"}
                      onChange={() => setAskScope("group")}
                    />
                    <span>Existing group (watchlist / sector)</span>
                  </label>
                </div>

                {/* Company / group search */}
                <div style={{ marginTop: "14px" }}>
                  <label className="field">
                    <span>Search Company / Group</span>
                    <input
                      type="text"
                      className="input"
                      placeholder="Example: Infosys, TCS, HDFC Bank, IT Sector, Banks, Auto"
                    />
                  </label>
                  <div className="field-hint"></div>
                </div>

                {/* Data selection – slider */}
                <div style={{ marginTop: "16px" }}>
                  <div className="ask-section-title">
                    Include last <strong>{askNumTranscripts}</strong> of 10 transcripts for this{" "}
                    {askScope === "company" ? "Company" : "Group"}
                  </div>

                  <div className="ask-section-sub"></div>
                  <div className="slider-row">
                    <input
                      type="range"
                      min={1}
                      max={10}
                      value={askNumTranscripts}
                      onChange={(e) => setAskNumTranscripts(Number(e.target.value))}
                    />
                    <span className="slider-value">
                      RAIO uses these when generating answer.
                    </span>
                  </div>
                </div>

                {/* Additional context – company vs group */}
                {askScope === "company" ? (
                  <div style={{ marginTop: "14px" }}>
                    <label className="field">
                      <span>Additional context</span>
                      <div className="input-chip-row" style={{ alignItems: "center" }}>
                        <button
                          type="button"
                          className={`input-chip-toggle-pill ${
                            askIncludeSectorOutputs ? "on" : ""
                          }`}
                          onClick={() =>
                            setAskIncludeSectorOutputs((prev) => !prev)
                          }
                        >
                          <div className="input-chip-toggle-knob" />
                        </button>
                        <span className="field-hint">
                          Also include sector-level outputs that mention this name.
                        </span>
                      </div>
                    </label>
                  </div>
                ) : (
                  <div style={{ marginTop: "14px" }}>
                    <div className="field">
                      <span style={{ fontSize: "12px", color: "var(--text-soft)" }}>
                        Additional context
                      </span>
                      <div className="field-hint">
                        RAIO also retains the history of earlier group-level conversations
                        <br />
                        and includes them as context automatically.
                      </div>
                    </div>
                  </div>
                )}

                <div
                  style={{
                    marginTop: "auto",
                    fontSize: "11px",
                    color: "var(--text-softer)",
                  }}
                >
                  Note: LLM model and Email settings are controlled from Settings.
                </div>
              </div>

              {/* RIGHT: conversation + bottom question bar */}
              <div className="ask-card ask-card-conversation">
                <div className="ask-results">
                  <div className="ask-results-title">Conversation</div>
                  <div className="ask-results-msg">
                    <strong>You:</strong> What changed in management tone this quarter vs
                    the last two quarters for IT Sector?
                  </div>
                  <div className="ask-results-msg">
                    <strong>Assistant:</strong>
                    <div style={{ marginTop: "4px" }}>
                      - Management tone is slightly more cautious on discretionary
                      spending, especially from US/Europe banking clients.
                      <br />
                      - Guidance bands have narrowed, with most companies emphasising
                      back-end loaded growth in H2.
                      <br />
                      - Multiple CEOs referenced slower decision cycles but stable
                      long-term demand in cloud and AI-related projects.
                      <br />
                      - Hiring and utilisation commentary indicates a focus on margin
                      protection rather than aggressive growth.
                    </div>
                  </div>
                  <div className="ask-results-msg">
                    <strong>You:</strong> Which management team sounds most confident on
                    AI-driven opportunities?
                  </div>
                  <div className="ask-results-msg">
                    <strong>Assistant:</strong>
                    <div style={{ marginTop: "4px" }}>
                      Based on the transcripts analysed (Infosys, TCS, HCL Tech), Infosys
                      management sounds the most confident. They:
                      <ul
                        style={{
                          margin: "4px 0 0 16px",
                          padding: 0,
                        }}
                      >
                        <li>
                          Mentioned a growing pipeline of GenAI projects with specific
                          client wins.
                        </li>
                        <li>
                          Discussed internal productivity gains and margin upside from AI
                          tooling.
                        </li>
                        <li>
                          Provided more concrete numbers on AI-related revenue than peers.
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Bottom question bar (ChatGPT-style) */}
                <div className="ask-bottom-bar">
                  <textarea
                    className="textarea ask-bottom-input"
                    placeholder="Type your question here..."
                  ></textarea>
                  <button className="btn-primary ask-bottom-button">Ask</button>
                </div>
              </div>
            </div>
          </section>

          {/* SETTINGS TAB */}
          <section
            className={`tab-panel ${activeTab === "settings" ? "active" : ""}`}
          >
            <div className="settings-layout">
              {/* LEFT COLUMN */}
              <div>
                {/* Account */}
                <div className="settings-section">
                  <div className="settings-title-row">
                    <div>
                      <div className="settings-title">Account</div>
                      <div className="settings-subtitle">
                        Manage your profile and organisation.
                      </div>
                    </div>
                    <button className="btn-outline btn-sm">Sign out</button>
                  </div>

                  <div className="settings-grid-2">
                    <div className="field">
                      <label>Name</label>
                      <input
                        type="text"
                        className="input"
                        defaultValue="Vipin Goel"
                      />
                    </div>
                    <div className="field">
                      <label>Email</label>
                      <input
                        type="email"
                        className="input"
                        defaultValue="vipin@mirabilisinvest.com"
                      />
                    </div>
                    <div className="field">
                      <label>Organisation</label>
                      <input
                        type="text"
                        className="input"
                        defaultValue="Mirabilis Invest"
                      />
                    </div>
                  </div>

                  <div className="field" style={{ marginTop: "8px" }}>
                    <label>Password</label>
                    <button
                      className="btn-outline btn-sm"
                      style={{ width: "max-content" }}
                    >
                      Change password
                    </button>
                  </div>
                </div>

                {/* Plan & usage – transcripts only */}
                <div className="settings-section">
                  <div className="settings-title-row">
                    <div>
                      <div className="settings-title">Plan &amp; usage</div>
                      <div className="settings-subtitle">
                        Manage your plan and see how many transcripts RAIO has processed.
                      </div>
                    </div>
                    <span className="pill-plan">Trial</span>
                  </div>

                  <div className="settings-grid-2">
                    <div className="field">
                      <label>Current plan</label>
                      <select className="select">
                        <option>Trial (10 transcripts/day)</option>
                        <option>Silver (1000 transcripts/month)</option>
                        <option>Gold (3000 transcripts/month)</option>
                      </select>
                    </div>
                    <div className="field">
                      <label>Plan description</label>
                      <div className="field-hint">
                        Trial: 10 transcripts/day · Silver: 1000/month · Gold: 3000/month.
                      </div>
                    </div>
                  </div>

                  <div style={{ marginTop: "10px" }}>
                    <div
                      style={{
                        fontSize: "12px",
                        color: "var(--text-soft)",
                        marginBottom: "4px",
                      }}
                    >
                      Usage this month
                    </div>

                    <div className="usage-bar">
                      <div className="usage-bar-fill"></div>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        fontSize: "11px",
                        marginTop: "4px",
                        color: "var(--text-softer)",
                      }}
                    >
                      <span>123 transcripts processed</span>
                      <span>Plan limit: 1000 transcripts/month · 12.3% used</span>
                    </div>

                    <div
                      style={{
                        marginTop: "4px",
                        fontSize: "11px",
                        color: "var(--text-softer)",
                      }}
                    >
                      Each time RAIO analyses a transcript, it counts towards this limit.
                    </div>
                  </div>
                </div>
              </div>

              {/* RIGHT COLUMN */}
              <div>
                {/* LLM defaults */}
                <div className="settings-section">
                  <div className="settings-title-row">
                    <div>
                      <div className="settings-title">LLM defaults</div>
                      <div className="settings-subtitle">
                        Default models for each workflow.
                      </div>
                    </div>
                  </div>

                  <div className="settings-grid-2">
                    <div className="field">
                      <label>Company auto-analysis</label>
                      <select className="select">
                        <option>Gemini 3 Pro</option>
                        <option>Gemini 3 Flash</option>
                        <option>GPT-4.1</option>
                        <option>Claude 3.5 Sonnet</option>
                      </select>
                    </div>

                    <div className="field">
                      <label>Sector / watchlist prompt</label>
                      <select className="select">
                        <option>Claude 3.5 Sonnet</option>
                        <option>Gemini 3 Pro</option>
                        <option>GPT-4.1</option>
                      </select>
                    </div>

                    <div className="field">
                      <label>Ask tab Q&amp;A</label>
                      <select className="select">
                        <option>Gemini 3 Flash</option>
                        <option>Gemini 3 Pro</option>
                        <option>GPT-4.1</option>
                        <option>Claude 3.5 Sonnet</option>
                      </select>
                    </div>

                    <div className="field">
                      <label>Default max tokens</label>
                      <input type="number" className="input" defaultValue={3000} />
                      <div className="field-hint">
                        Advanced setting. You can leave this as default.
                      </div>
                    </div>
                  </div>
                </div>

                {/* Email & notifications */}
                <div className="settings-section">
                  <div className="settings-title-row">
                    <div>
                      <div className="settings-title">Email &amp; notifications</div>
                      <div className="settings-subtitle">
                        Configure how auto-mails are sent to your team.
                      </div>
                    </div>
                  </div>

                  <div className="settings-grid-2">
                    <div className="field">
                      <label>From name</label>
                      <input
                        type="text"
                        className="input"
                        defaultValue="Research Desk · Mirabilis"
                      />
                      <div className="field-hint">
                        Appears as the sender name in recipients&apos; inbox.
                      </div>
                    </div>

                    <div className="field">
                      <label>Delivery style</label>
                      <select className="select">
                        <option>On behalf of you via app</option>
                        <option>System alerts only</option>
                      </select>
                    </div>
                  </div>

                  <div className="field" style={{ marginTop: "8px" }}>
                    <label>Default recipient list (max 100)</label>
                    <table className="table-mini">
                      <thead>
                        <tr>
                          <th>Name</th>
                          <th>Email</th>
                          <th>Active</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>Research Team</td>
                          <td>research@firm.com</td>
                          <td>
                            <div className="toggle on">
                              <div className="toggle-knob"></div>
                            </div>
                          </td>
                        </tr>
                        <tr>
                          <td>PM Desk</td>
                          <td>pm-desk@firm.com</td>
                          <td>
                            <div className="toggle on">
                              <div className="toggle-knob"></div>
                            </div>
                          </td>
                        </tr>
                        <tr>
                          <td>Risk</td>
                          <td>risk@firm.com</td>
                          <td>
                            <div className="toggle">
                              <div className="toggle-knob"></div>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>

                    <button
                      className="btn-outline btn-sm"
                      style={{ marginTop: "6px" }}
                    >
                      + Add recipient
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>

      {/* Prompt drawer (group + company) */}
      {showPromptEditor && (
        <div
          className="drawer-overlay"
          onClick={() => setShowPromptEditor(false)}
        >
          <div
            className="drawer"
            onClick={(e) => {
              e.stopPropagation();
            }}
          >
            <div className="drawer-header">
              <div>
                <div className="drawer-title">
                  {isGroupEditor
                    ? "Edit group prompt"
                    : `Edit prompt for ${promptEditorContext.targetName}`}
                </div>
                <div className="drawer-subtitle">
                  {isGroupEditor
                    ? "This prompt applies to all companies in the selected group."
                    : "This prompt will override the group prompt for this company."}
                </div>
              </div>
              <button
                className="btn-icon"
                onClick={() => setShowPromptEditor(false)}
              >
                ×
              </button>
            </div>
            <label className="field" style={{ marginTop: "8px" }}>
              <span>Prompt</span>
              <textarea
                className="textarea"
                style={{ minHeight: "160px" }}
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
              />
            </label>
            <div className="drawer-actions">
              <button
                className="btn-outline"
                onClick={() => setShowPromptEditor(false)}
              >
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={() => {
                  // future: save prompt via API
                  setShowPromptEditor(false);
                }}
              >
                Save prompt
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
