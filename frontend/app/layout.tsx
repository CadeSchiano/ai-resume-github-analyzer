import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Northstar: Developer Readiness",
  description: "See the developer evidence your resume and GitHub already communicate.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
