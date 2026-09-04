import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Arbiter",
  description: "AI-powered payment failure recovery dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
      <body>{children}</body>
    </html>
  );
}
