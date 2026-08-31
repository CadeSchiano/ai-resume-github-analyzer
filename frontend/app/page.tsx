"use client";

import { ChangeEvent, FormEvent, useMemo, useState } from "react";

const roles = [
  "Software Engineer Intern",
  "Software Engineer",
  "Backend Developer",
  "Frontend Developer",
  "Full-Stack Developer",
  "Mobile Developer",
  "AI/ML",
];

type CategoryMap = Record<string, number | null>;
type Repository = {
  name: string;
  primary_language?: string | null;
  technologies_detected?: string[];
  scores?: CategoryMap;
};
type Analysis = {
  github_analysis: { github_score: number | null; categories: CategoryMap; strongest_projects: Repository[] };
  resume_analysis: { resume_score: number; categories: CategoryMap; strengths: string[]; improvements: string[] };
  resume_github_evidence: Array<{ skill: string; evidence_level: string; evidence_repositories: string[] }>;
  role_readiness?: { target_role: string; role_readiness_score: number; categories: CategoryMap };
  ai_explanation?: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

function prettyLabel(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function Score({ value }: { value: number | null | undefined }) {
  return <span className="score-value">{value ?? "N/A"}<small>{value !== null && value !== undefined ? "/100" : ""}</small></span>;
}

function EvidenceTag({ level }: { level: string }) {
  const label = level === "strong_public_evidence" ? "Strong evidence" : level === "some_public_evidence" ? "Some evidence" : "No public evidence";
  return <span className={`evidence-tag ${level}`}>{label}</span>;
}

export default function Home() {
  const [username, setUsername] = useState("");
  const [resume, setResume] = useState<File | null>(null);
  const [role, setRole] = useState(roles[0]);
  const [includeAi, setIncludeAi] = useState(false);
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");
  const [error, setError] = useState("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);

  const evidenceCount = useMemo(
    () => analysis?.resume_github_evidence.filter((item) => item.evidence_level !== "no_public_github_evidence_found").length ?? 0,
    [analysis],
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!resume || !username.trim()) {
      setError("Add a public GitHub username and a PDF resume to continue.");
      return;
    }

    setStatus("loading");
    setError("");
    setAnalysis(null);
    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("target_role", role);
    formData.append("include_ai_explanation", String(includeAi));

    try {
      const response = await fetch(`${apiBaseUrl}/analysis/${encodeURIComponent(username.trim())}/resume`, {
        method: "POST",
        body: formData,
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "The analysis could not be completed.");
      setAnalysis(payload);
      setStatus("idle");
    } catch (requestError) {
      setStatus("error");
      setError(requestError instanceof Error ? requestError.message : "The analysis could not be completed.");
    }
  }

  function handleResumeChange(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null;
    setResume(selected);
    if (selected && selected.type !== "application/pdf") setError("Please choose a PDF resume.");
    else setError("");
  }

  return (
    <main>
      <nav className="nav-shell" aria-label="Main navigation">
        <a className="wordmark" href="#top"><span>northstar</span><i>developer readiness</i></a>
        <a className="quiet-link" href="#how-it-works">How it works <span>↘</span></a>
      </nav>

      <section className="hero" id="top">
        <p className="eyebrow">PUBLIC EVIDENCE, CLEARER NEXT STEPS</p>
        <h1>Turn your work into a more <em>legible</em> developer story.</h1>
        <p className="hero-copy">A grounded review of your resume and public GitHub work, built for early-career software engineers.</p>
      </section>

      <section className="analyze-grid" aria-label="Developer analysis form">
        <form className="analysis-form" onSubmit={handleSubmit}>
          <div className="form-heading"><span className="form-index">01</span><h2>Start an analysis</h2></div>
          <label>
            <span>GitHub username</span>
            <input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="e.g. octocat" autoComplete="off" />
            <small>Any GitHub username is supported. We analyze public repositories only, never private repositories.</small>
          </label>
          <label>
            <span>Resume</span>
            <input className="file-input" type="file" accept="application/pdf" onChange={handleResumeChange} />
            <small>{resume ? resume.name : "PDF only · processed in memory"}</small>
          </label>
          <label>
            <span>Target role</span>
            <select value={role} onChange={(event) => setRole(event.target.value)}>
              {roles.map((option) => <option key={option}>{option}</option>)}
            </select>
          </label>
          <label className="ai-toggle">
            <input type="checkbox" checked={includeAi} onChange={(event) => setIncludeAi(event.target.checked)} />
            <span><b>Add an AI explanation</b><small>Scores stay deterministic. AI only explains the evidence.</small></span>
          </label>
          {error && <p className="form-error" role="alert">{error}</p>}
          <button disabled={status === "loading"} type="submit">{status === "loading" ? "Reviewing your evidence…" : "Analyze my readiness"}<span>→</span></button>
        </form>

        <aside className="confidence-panel" id="how-it-works">
          <p className="eyebrow">WHAT WE LOOK AT</p>
          <div><strong>01</strong><p><b>Resume evidence</b><br />Skills, project detail, experience bullets, and structure.</p></div>
          <div><strong>02</strong><p><b>GitHub evidence</b><br />Documentation, testing, engineering practice, and visible technology choices.</p></div>
          <div><strong>03</strong><p><b>Role context</b><br />What your evidence supports for the role you are aiming toward.</p></div>
          <p className="privacy-note">Any public GitHub username can be analyzed. Private repositories are never accessed. Your PDF is analyzed in memory and is not saved.</p>
        </aside>
      </section>

      {analysis && <section className="results" aria-live="polite">
        <div className="results-intro"><p className="eyebrow">YOUR READINESS SNAPSHOT</p><h2>Evidence, not guesswork.</h2><p>Here is what your public work and resume currently communicate.</p></div>
        <div className="score-row">
          <article className="hero-score"><p>Developer evidence</p><Score value={analysis.github_analysis.github_score} /><small>GitHub analysis</small></article>
          <article className="hero-score"><p>Resume evidence</p><Score value={analysis.resume_analysis.resume_score} /><small>Resume analysis</small></article>
          <article className="hero-score accent-score"><p>{analysis.role_readiness?.target_role ?? role}</p><Score value={analysis.role_readiness?.role_readiness_score} /><small>Role readiness</small></article>
        </div>
        <div className="results-grid">
          <article className="result-card"><div className="card-title"><p className="eyebrow">GITHUB</p><span>{analysis.github_analysis.strongest_projects.length} projects surfaced</span></div>
            <div className="category-list">{Object.entries(analysis.github_analysis.categories).map(([name, value]) => <div key={name}><span>{prettyLabel(name)}</span><Score value={value} /></div>)}</div>
          </article>
          <article className="result-card"><div className="card-title"><p className="eyebrow">RESUME</p><span>{analysis.resume_analysis.strengths.length} strengths found</span></div>
            <ul className="finding-list">{analysis.resume_analysis.strengths.map((item) => <li key={item}>{item}</li>)}{analysis.resume_analysis.improvements.slice(0, 3).map((item) => <li className="improvement" key={item}>{item}</li>)}</ul>
          </article>
        </div>
        <article className="evidence-card"><div className="card-title"><p className="eyebrow">RESUME × GITHUB</p><span>{evidenceCount} skills with public project evidence</span></div>
          <div className="evidence-list">{analysis.resume_github_evidence.map((item) => <div key={item.skill}><b>{item.skill}</b><EvidenceTag level={item.evidence_level} /><small>{item.evidence_repositories.length ? item.evidence_repositories.join(", ") : "No matching public repository detected"}</small></div>)}</div>
        </article>
        {analysis.ai_explanation && <article className="ai-note"><p className="eyebrow">AI EXPLANATION</p><p>{analysis.ai_explanation}</p></article>}
      </section>}
    </main>
  );
}
