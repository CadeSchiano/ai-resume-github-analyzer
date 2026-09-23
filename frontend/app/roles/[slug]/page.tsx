import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { roleGuideBySlug, roleGuides } from "../../role-guides";
import styles from "./role-guide.module.css";

type PageProps = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return roleGuides.map(({ slug }) => ({ slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const guide = roleGuideBySlug[slug];
  if (!guide) return {};
  return {
    title: `${guide.title} Guide | Repolume`,
    description: `Core skills, differentiators, and project evidence for aspiring ${guide.title.toLowerCase()} candidates.`,
  };
}

export default async function RoleGuidePage({ params }: PageProps) {
  const { slug } = await params;
  const guide = roleGuideBySlug[slug];
  if (!guide) notFound();

  return (
    <main className={styles.page}>
      <nav className={styles.nav} aria-label="Main navigation"><Link className={`wordmark ${styles.wordmark}`} href="/"><span>repolume</span><i>developer readiness</i></Link><Link href="/#analyze">Analyze your profile</Link></nav>
      <section className={styles.hero}>
        <p className="eyebrow">ROLE GUIDE</p>
        <h1>{guide.title}</h1>
        <p>{guide.summary}</p>
        <a href="/#analyze">Analyze for this role <span>→</span></a>
      </section>
      <section className={styles.content}>
        <div className={styles.intro}><p className="eyebrow">CORE SKILLS</p><h2>What to build first.</h2><p>These are practical foundations to develop, not a universal hiring checklist. Job descriptions and teams vary.</p></div>
        <ol className={styles.skillList}>{guide.coreSkills.map((skill, index) => <li key={skill}><span>0{index + 1}</span>{skill}</li>)}</ol>
        <div className={styles.intro}><p className="eyebrow">WHAT DIFFERENTIATES YOU</p><h2>Make the evidence easy to evaluate.</h2><p>Strong candidates make their work legible. They show the problem, their decisions, and how the result holds up.</p></div>
        <div className={styles.differentiatorGrid}>{guide.differentiators.map((item) => <article key={item}><span>+</span><p>{item}</p></article>)}</div>
        <aside className={styles.proof}><p className="eyebrow">PROJECT PROOF</p><p>{guide.projectProof}</p></aside>
        <p className={styles.disclaimer}>Repolume compares your resume and public GitHub evidence. It does not replace interview preparation or evaluate every factor used by a hiring team.</p>
      </section>
      <footer className={styles.footer}><span>Repolume beta</span><div><Link href="/privacy">Privacy</Link><Link href="/terms">Terms</Link><a href="mailto:cadeschiano8@yahoo.com" target="_blank" rel="noreferrer">cadeschiano8@yahoo.com</a></div></footer>
    </main>
  );
}
