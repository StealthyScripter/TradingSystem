import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Investment Portfolio Dashboard",
  description: "Real-time portfolio management with AI-powered insights",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
