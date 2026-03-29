import type { Metadata } from "next";
import localFont from "next/font/local";
import Script from "next/script";
import "./globals.css";

const calSans = localFont({
  src: "../fonts/CalSans-SemiBold.woff2",
  variable: "--font-display",
  weight: "600",
  display: "swap",
});

const generalSans = localFont({
  src: "../fonts/GeneralSans-Variable.woff2",
  variable: "--font-sans",
  weight: "400 700",
  display: "swap",
});

const jetbrainsMono = localFont({
  src: [
    { path: "../fonts/JetBrainsMono-Regular.woff2", weight: "400" },
    { path: "../fonts/JetBrainsMono-Bold.woff2", weight: "700" },
  ],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://kengo.de"),
  title: "Kengo | KI-Mitarbeiter für den Mittelstand",
  description:
    "Kengo stellt deinem Unternehmen KI-Mitarbeiter ein — für Finance, Sales, HR, IT und mehr. Ab €1.999/Monat. Einarbeitung in 5 Tagen. Gehostet in Deutschland.",
  keywords: [
    "KI Mitarbeiter",
    "KI Agent Unternehmen",
    "KI Sachbearbeiter",
    "KI Buchhaltung",
    "KI Kundenservice",
    "OpenClaw Deutschland",
    "Fachkräftemangel Lösung",
    "Verwaltung automatisieren",
    "DATEV KI Integration",
    "autonome Rechnungsverarbeitung",
    "KI für Mittelstand",
  ],
  openGraph: {
    title: "Kengo | KI-Mitarbeiter für den Mittelstand",
    description:
      "Kengo stellt deinem Unternehmen KI-Mitarbeiter ein — für Finance, Sales, HR, IT und mehr. Ab €1.999/Monat. Gehostet in Deutschland.",
    url: "https://kengo.de",
    siteName: "Kengo",
    locale: "de_DE",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Kengo | KI-Mitarbeiter für den Mittelstand",
    description:
      "KI-Mitarbeiter für jede Abteilung. Sofort einsatzbereit.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="de"
      className={`${calSans.variable} ${generalSans.variable} ${jetbrainsMono.variable}`}
    >
      <head>
        <Script
          defer
          data-domain="kengo.de"
          src="https://plausible.io/js/script.js"
          strategy="afterInteractive"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
