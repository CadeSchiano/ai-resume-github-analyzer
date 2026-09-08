import type { Metadata } from "next";
import styles from "../legal.module.css";

export const metadata: Metadata = {
  title: "Privacy Policy | DevProof",
  description: "How DevProof handles resume uploads, public GitHub data, and optional AI explanations.",
};

export default function PrivacyPage() {
  return (
    <main className={styles.page}>
      <nav className={styles.nav}><a className={`wordmark ${styles.wordmark}`} href="/"><span>devproof</span><i>developer readiness</i></a><a href="/">Back to DevProof</a></nav>
      <article className={styles.content}>
        <p className="eyebrow">PRIVACY POLICY</p>
        <h1>Clear about the data used for your analysis.</h1>
        <p className={styles.lede}>Effective September 8, 2026. This policy explains how DevProof handles information submitted through this beta application.</p>
        <h2>Information used to provide the service</h2><p>DevProof receives the GitHub username, PDF resume, selected target role, and AI-explanation preference that you submit. It uses these inputs to generate your developer-readiness report.</p>
        <h2>Public GitHub information</h2><p>DevProof analyzes repositories and related information that are publicly available through GitHub’s API. It does not access private repositories.</p>
        <h2>Resume processing and retention</h2><p>Your resume is processed during the request to extract text and generate the report. DevProof’s application code does not save resumes or extracted resume text to a database or other persistent application storage after processing.</p>
        <h2>Optional AI explanations</h2><p>If you choose “Add an AI explanation,” DevProof sends the completed report to OpenAI to generate an explanation. It does not send the raw PDF file, and DevProof sets <code>store=false</code> for the request. OpenAI may retain abuse-monitoring logs under its API data policies. Do not select this option if you do not want the completed report used to create an AI explanation.</p>
        <h2>How information is used</h2><p>Information is used to provide the requested report, operate and troubleshoot the beta, protect the service from abuse, and comply with applicable law. DevProof does not sell resume information.</p>
        <h2>Third parties</h2><p>DevProof uses GitHub’s public API to retrieve public repository information. When you opt in to an AI explanation, it uses OpenAI’s API to generate that explanation. Those providers handle information under their own terms and privacy practices.</p>
        <h2>Changes and contact</h2><p>We may update this policy as the beta evolves. The effective date above will be updated when changes are posted. For privacy questions, contact <a href="mailto:cade73328@gmail.com">cade73328@gmail.com</a>.</p>
      </article>
      <footer className={styles.footer}><span>DevProof beta</span><div><a href="/privacy">Privacy</a><a href="/terms">Terms</a><a href="mailto:cade73328@gmail.com">Contact</a></div></footer>
    </main>
  );
}
