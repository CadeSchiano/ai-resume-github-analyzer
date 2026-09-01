import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Northstar: Resume and GitHub Analyzer for Software Developers",
  description: "Analyze your resume and public GitHub projects to understand your developer readiness, strengths, weaknesses, and next steps.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
