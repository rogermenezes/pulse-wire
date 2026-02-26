import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PulseWire",
  description: "Curated cross-source story clusters and summaries"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header style={{ borderBottom: "1px solid #e2e8f0", background: "white" }}>
          <main style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: "1rem", paddingBottom: "1rem" }}>
            <strong>PulseWire</strong>
            <span className="badge">MVP Scaffold</span>
          </main>
        </header>
        {children}
      </body>
    </html>
  );
}
