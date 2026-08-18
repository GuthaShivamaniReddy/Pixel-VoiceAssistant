import type { ReactNode } from "react";
import type { Metadata } from "next";
import { assertNoSecretShapedPublicEnv } from "@/lib/env";
import "./globals.css";

assertNoSecretShapedPublicEnv();

export const metadata: Metadata = {
  title: "Pixel — Cyber Florida",
  description: "Cyber Florida AI voice assistant for public information and defensive guidance",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
