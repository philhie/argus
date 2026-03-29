// Requires ANTHROPIC_API_KEY in .env.local
// Get your key at console.anthropic.com

import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { companyName, industry, employeeCount } = await req.json();

  // If no API key, return fallback immediately
  if (!process.env.ANTHROPIC_API_KEY) {
    return NextResponse.json(getFallback(companyName, industry, employeeCount), {
      headers: { "Cache-Control": "no-store" },
    });
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        "x-api-key": process.env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 1500,
        messages: [
          {
            role: "user",
            content: `Du bist ein Kengo KI-Mitarbeiter-Berater. Ein potenzieller Kunde möchte sehen, was ein KI-Mitarbeiter für sein Unternehmen tun kann.

Unternehmen: ${companyName}
Branche: ${industry || "Nicht angegeben"}
Mitarbeiterzahl: ${employeeCount || "Nicht angegeben"}

Analysiere dieses Unternehmen und generiere EXAKT 3 konkrete Aufgaben, die ein KI-Mitarbeiter sofort übernehmen kann. Sei SEHR spezifisch — nenne konkrete Beispiele die zu dieser Branche und Unternehmensgröße passen.

Antworte AUSSCHLIESSLICH in diesem JSON-Format, ohne Markdown, ohne Backticks:

{
  "companyProfile": {
    "name": "${companyName}",
    "industry": "erkannte Branche",
    "size": "Unternehmensgröße",
    "summary": "Ein Satz über typische Herausforderungen dieses Unternehmenstyps"
  },
  "tasks": [
    {
      "icon": "passender Emoji",
      "title": "Aufgabentitel",
      "description": "2-3 Sätze die GENAU beschreiben was der KI-Mitarbeiter tut. Sehr konkret und branchenspezifisch.",
      "impact": "Konkrete Zeitersparnis oder Kostenersparnis",
      "demo": [
        "Schritt 1: Was der Agent tut",
        "Schritt 2: Was als nächstes passiert",
        "Schritt 3: Das Ergebnis"
      ]
    }
  ],
  "totalImpact": {
    "hoursPerWeek": Zahl,
    "costPerMonth": Zahl
  }
}`,
          },
        ],
      }),
    });

    clearTimeout(timeout);
    const data = await response.json();
    const text = data.content?.[0]?.text || "";

    const cleanText = text.replace(/```json|```/g, "").trim();
    const result = JSON.parse(cleanText);

    return NextResponse.json(result, {
      headers: { "Cache-Control": "no-store" },
    });
  } catch (error) {
    clearTimeout(timeout);
    console.error("Demo API error:", error);
    return NextResponse.json(getFallback(companyName, industry, employeeCount), {
      headers: { "Cache-Control": "no-store" },
    });
  }
}

function getFallback(
  companyName: string,
  industry?: string,
  employeeCount?: string
) {
  return {
    companyProfile: {
      name: companyName,
      industry: industry || "Mittelstand",
      size: employeeCount || "30-100",
      summary: `${companyName} verliert vermutlich 30+ Stunden pro Woche an administrative Routinearbeit.`,
    },
    tasks: [
      {
        icon: "📧",
        title: "E-Mail-Triage & Antworten",
        description: `Der KI-Mitarbeiter liest alle eingehenden E-Mails von ${companyName}, kategorisiert sie automatisch (Kundenanfrage, Rechnung, intern, Spam), und beantwortet Routineanfragen sofort. Komplexe E-Mails werden mit Kontext an den richtigen Kollegen weitergeleitet.`,
        impact: "Spart ca. 12 Stunden/Woche",
        demo: [
          "📨 Neue E-Mail: 'Können Sie mir ein Angebot für 500 Stück senden?'",
          "🔍 Kengo: Prüft CRM → Bestandskunde, letzte Bestellung: 200 Stück, Rabatt: 8%",
          "✉️ Kengo: Entwirft Angebot mit personalisierten Konditionen und sendet zur Freigabe",
        ],
      },
      {
        icon: "📄",
        title: "Rechnungsverarbeitung & DATEV-Sync",
        description: `Eingehende Rechnungen werden automatisch erkannt, ausgelesen und mit den Bestellungen von ${companyName} abgeglichen. Die Buchungsdaten werden direkt an DATEV übertragen.`,
        impact: "Reduziert Bearbeitungszeit um 80%",
        demo: [
          "📄 Rechnung eingegangen: Lieferant GmbH, €4.350,00",
          "🔍 Kengo: Gleicht ab mit PO #2024-0847 → Betrag korrekt, Lieferdatum bestätigt",
          "✅ Kengo: Buchungssatz erstellt, an DATEV übermittelt, Zahlung zur Freigabe",
        ],
      },
      {
        icon: "📅",
        title: "Termin- & Aufgabenmanagement",
        description: `Der KI-Mitarbeiter koordiniert Termine für das Team von ${companyName}, erinnert an Deadlines, bereitet Meeting-Unterlagen vor und erstellt automatisch Protokolle nach jedem Gespräch.`,
        impact: "Spart ca. 8 Stunden/Woche",
        demo: [
          "📅 Meeting morgen: Quartals-Review mit Kunde Müller",
          "🔍 Kengo: Erstellt Agenda basierend auf letztem Meeting + aktuellem CRM-Status",
          "📋 Kengo: Sendet Agenda an alle Teilnehmer, bereitet Umsatzdaten vor",
        ],
      },
    ],
    totalImpact: {
      hoursPerWeek: 25,
      costPerMonth: 3200,
    },
  };
}
