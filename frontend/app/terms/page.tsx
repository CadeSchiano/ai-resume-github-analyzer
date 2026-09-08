import type { Metadata } from "next";
import styles from "../legal.module.css";

export const metadata: Metadata = {
  title: "Terms of Use | DevProof",
  description: "Terms of use for the DevProof developer-readiness beta.",
};

export default function TermsPage() {
  return (
    <main className={styles.page}>
      <nav className={styles.nav}><a className={`wordmark ${styles.wordmark}`} href="/"><span>devproof</span><i>developer readiness</i></a><a href="/">Back to DevProof</a></nav>
      <article className={styles.content}>
        <p className="eyebrow">TERMS OF USE</p>
        <h1>Use DevProof thoughtfully.</h1>
        <p className={styles.lede}>Effective September 8, 2026. These terms govern use of the DevProof beta.</p>
        <h2>Beta service</h2><p>DevProof is an experimental developer-readiness tool. Features, availability, and the analysis may change as the beta develops.</p>
        <h2>Your submissions</h2><p>You may submit only a resume you are authorized to use and a GitHub username you are authorized to analyze. Do not submit unlawful, harmful, malicious, or infringing content, and do not attempt to disrupt, probe, or abuse the service.</p>
        <h2>Public GitHub data</h2><p>DevProof evaluates public GitHub information only. You are responsible for confirming that the username you enter is correct and for respecting GitHub’s terms when using information returned by the service.</p>
        <h2>No hiring or professional guarantee</h2><p>Reports and optional AI explanations are informational feedback, not a hiring decision, professional advice, or a guarantee of interview, employment, compensation, or outcome. Review the results critically before acting on them.</p>
        <h2>Availability and acceptable use</h2><p>We may limit, suspend, or discontinue access to protect the service, comply with law, or address misuse. Do not bypass rate limits, attempt unauthorized access, or use automated traffic that interferes with normal operation.</p>
        <h2>Changes and contact</h2><p>We may update these terms as the beta evolves. The effective date above will be updated when changes are posted. For questions, contact <a href="mailto:cade73328@gmail.com">cade73328@gmail.com</a>.</p>
      </article>
      <footer className={styles.footer}><span>DevProof beta</span><div><a href="/privacy">Privacy</a><a href="/terms">Terms</a><a href="mailto:cade73328@gmail.com">Contact</a></div></footer>
    </main>
  );
}
