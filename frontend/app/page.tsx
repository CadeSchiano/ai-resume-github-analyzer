"use client";

import { ChangeEvent, FormEvent, useMemo, useState } from "react";

const roles = ["Software Engineer Intern", "Software Engineer", "Backend Developer", "Frontend Developer", "Full-Stack Developer", "Mobile Developer", "AI/ML"];
const exampleCategories = [["Repository quality", 76], ["Documentation", 58], ["Engineering practices", 64], ["Project complexity", 72], ["Technical breadth", 92], ["Project presentation", 67], ["Activity", 80]];

type CategoryMap = Record<string, number | null>;
type Repository = { name: string; primary_language?: string | null; technologies_detected?: string[]; scores?: CategoryMap };
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

  const evidenceCount = useMemo(() => analysis?.resume_github_evidence.filter((item) => item.evidence_level !== "no_public_github_evidence_found").length ?? 0, [analysis]);

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
      const response = await fetch(`${apiBaseUrl}/analysis/${encodeURIComponent(username.trim())}/resume`, { method: "POST", body: formData });
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
    setError(selected && selected.type !== "application/pdf" ? "Please choose a PDF resume." : "");
  }

  return (
    <main>
      <nav className="nav-shell" aria-label="Main navigation">
        <a className="wordmark" href="#top"><span>devproof</span><i>developer readiness</i></a>
        <div className="nav-links"><a href="#how-it-works">How it works</a><a href="#analyze">Analyze <span>↘</span></a></div>
      </nav>

      <section className="hero" id="top">
        <p className="eyebrow">PUBLIC EVIDENCE, CLEARER NEXT STEPS</p>
        <h1>See how job-ready your developer profile <em>actually</em> is.</h1>
        <p className="hero-copy">Get an evidence-based review of your resume and public GitHub, with clear scores and specific ways to improve.</p>
        <a className="hero-cta" href="#analyze">Analyze my profile <span>→</span></a>
        <ul className="trust-list" aria-label="DevProof trust commitments"><li>No account required</li><li>Public GitHub repositories only</li><li>Resume processed in memory</li></ul>
      </section>

      <section className="example-section" id="example-report" aria-labelledby="example-title">
        <div className="section-intro"><p className="eyebrow">A CLEARER PICTURE</p><h2 id="example-title">Know what the report will tell you.</h2><p>DevProof turns the work you already have into a focused review, not an arbitrary score.</p></div>
        <article className="example-report">
          <div className="example-score"><div><p className="eyebrow">EXAMPLE REPORT</p><h3>Developer readiness</h3><Score value={76} /></div><p>Based on resume evidence, public GitHub projects, and a selected role.</p></div>
          <div className="example-categories">{exampleCategories.map(([label, score]) => <div key={label as string}><span>{label}</span><b>{score}</b></div>)}</div>
          <p className="example-insight">Your projects show strong technical breadth, but several repositories make it difficult to quickly understand what you built and how the work is structured.</p>
        </article>
        <a className="text-cta" href="#analyze">View the real analysis flow <span>→</span></a>
      </section>

      <section className="how-section" id="how-it-works" aria-labelledby="how-title">
        <div className="section-intro"><p className="eyebrow">HOW IT WORKS</p><h2 id="how-title">One practical report, built from your real evidence.</h2></div>
        <div className="steps"><article><strong>01</strong><h3>Upload your resume</h3><p>We extract visible skills, project detail, experience evidence, and resume structure.</p></article><article><strong>02</strong><h3>Enter your GitHub username</h3><p>We review original public repositories and the engineering evidence they make visible.</p></article><article><strong>03</strong><h3>Get your readiness report</h3><p>See scores, supporting evidence, role context, and next steps you can act on.</p></article></div>
      </section>

      <section className="sources-section" aria-labelledby="sources-title">
        <div className="section-intro"><p className="eyebrow">WHAT DEVPROOF ANALYZES</p><h2 id="sources-title">Two perspectives. One more useful developer story.</h2></div>
        <div className="source-grid"><article><p className="eyebrow">RESUME</p><h3>What your application says on paper.</h3><ul><li>Explicit technical skills</li><li>Experience and action-oriented language</li><li>Project detail and technologies</li><li>Resume sections and structure</li></ul></article><article><p className="eyebrow">PUBLIC GITHUB</p><h3>What your work shows in practice.</h3><ul><li>Repository quality and documentation</li><li>Testing and visible engineering practices</li><li>Technical breadth and project complexity</li><li>Project presentation and recent activity</li></ul></article></div>
      </section>

      <section className="audience-section" aria-labelledby="audience-title">
        <p className="eyebrow">BUILT FOR EARLY-CAREER DEVELOPERS</p><h2 id="audience-title">Choose the direction you are working toward.</h2><p>DevProof supports role-specific context for the paths where early projects and a clear resume can make the biggest difference.</p><div className="role-list">{roles.map((item) => <span key={item}>{item}</span>)}</div>
      </section>

      <section className="feedback-section" aria-labelledby="feedback-title">
        <div><p className="eyebrow">ACTIONABLE, NOT GENERIC</p><h2 id="feedback-title">A score should point somewhere useful.</h2></div><blockquote>“Your public projects show useful technical range. Make the work easier to evaluate by adding setup, usage, and architecture guidance to your strongest repositories.”</blockquote><a className="text-cta" href="#example-report">View example report <span>↗</span></a>
      </section>

      <section className="analysis-wrap" id="analyze" aria-labelledby="analysis-title">
        <div className="analysis-heading"><p className="eyebrow">START YOUR ANALYSIS</p><h2 id="analysis-title">Ready to see yours?</h2><p>No account required. Your resume is processed in memory and not saved.</p></div>
        <div className="analyze-grid" aria-label="Developer analysis form">
          <form className="analysis-form" onSubmit={handleSubmit}>
            <div className="form-heading"><span className="form-index">01</span><h3>Start an analysis</h3></div>
            <label><span>GitHub username</span><input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="e.g. octocat" autoComplete="off" required /><small>Any GitHub username is supported. We analyze public repositories only, never private repositories.</small></label>
            <label><span>Resume</span><input className="file-input" type="file" accept="application/pdf" onChange={handleResumeChange} required /><small>{resume ? resume.name : "PDF only · processed in memory"}</small></label>
            <label><span>Target role</span><select value={role} onChange={(event) => setRole(event.target.value)}>{roles.map((option) => <option key={option}>{option}</option>)}</select></label>
            <label className="ai-toggle"><input type="checkbox" checked={includeAi} onChange={(event) => setIncludeAi(event.target.checked)} /><span><b>Add an AI explanation</b><small>Scores stay deterministic. AI only explains the evidence.</small></span></label>
            {error && <p className="form-error" role="alert">{error}</p>}
            <button disabled={status === "loading"} type="submit">{status === "loading" ? "Reviewing your evidence…" : "Analyze my readiness"}<span>→</span></button>
          </form>
          <aside className="confidence-panel"><p className="eyebrow">WHAT YOU RECEIVE</p><div><strong>01</strong><p><b>Evidence-based scores</b><br />Resume, GitHub, and role-readiness results stay deterministic.</p></div><div><strong>02</strong><p><b>Specific feedback</b><br />See the strongest evidence and the most valuable places to improve.</p></div><div><strong>03</strong><p><b>Public evidence mapping</b><br />Find which resume skills have visible support in your public projects.</p></div><p className="privacy-note">Private repositories are never accessed. Your PDF is processed in memory and is not saved.</p></aside>
        </div>
      </section>

      {analysis && <section className="results" aria-live="polite">
        <div className="results-intro"><p className="eyebrow">YOUR READINESS SNAPSHOT</p><h2>Evidence, not guesswork.</h2><p>Here is what your public work and resume currently communicate.</p></div>
        <div className="score-row"><article className="hero-score"><p>Developer evidence</p><Score value={analysis.github_analysis.github_score} /><small>GitHub analysis</small></article><article className="hero-score"><p>Resume evidence</p><Score value={analysis.resume_analysis.resume_score} /><small>Resume analysis</small></article><article className="hero-score accent-score"><p>{analysis.role_readiness?.target_role ?? role}</p><Score value={analysis.role_readiness?.role_readiness_score} /><small>Role readiness</small></article></div>
        <div className="results-grid"><article className="result-card"><div className="card-title"><p className="eyebrow">GITHUB</p><span>{analysis.github_analysis.strongest_projects.length} projects surfaced</span></div><div className="category-list">{Object.entries(analysis.github_analysis.categories).map(([name, value]) => <div key={name}><span>{prettyLabel(name)}</span><Score value={value} /></div>)}</div></article><article className="result-card"><div className="card-title"><p className="eyebrow">RESUME</p><span>{analysis.resume_analysis.strengths.length} strengths found</span></div><ul className="finding-list">{analysis.resume_analysis.strengths.map((item) => <li key={item}>{item}</li>)}{analysis.resume_analysis.improvements.slice(0, 3).map((item) => <li className="improvement" key={item}>{item}</li>)}</ul></article></div>
        <article className="evidence-card"><div className="card-title"><p className="eyebrow">RESUME × GITHUB</p><span>{evidenceCount} skills with public project evidence</span></div><div className="evidence-list">{analysis.resume_github_evidence.map((item) => <div key={item.skill}><b>{item.skill}</b><EvidenceTag level={item.evidence_level} /><small>{item.evidence_repositories.length ? item.evidence_repositories.join(", ") : "No matching public repository detected"}</small></div>)}</div></article>
        {analysis.ai_explanation && <article className="ai-note"><p className="eyebrow">AI EXPLANATION</p><p>{analysis.ai_explanation}</p></article>}
      </section>}

    </main>
  );
}
