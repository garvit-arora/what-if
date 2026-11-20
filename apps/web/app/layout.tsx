import type { Metadata } from "next";
import "../index.css";

export const metadata: Metadata = {
  title: "Aurora Sign Up",
  description: "Create your Aurora profile.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
