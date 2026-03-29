import type { CascadeScenario } from "@/components/SpecialistCascade";

export const supportScenarios: CascadeScenario[] = [
  {
    trigger: {
      icon: "💬",
      line1: "Neues Ticket von Kunde Weber",
      line2: "\"Wo ist meine Bestellung #4821? Wurde vor 5 Tagen verschickt.\"",
    },
    steps: [
      { icon: "🔍", system: "CRM", action: "Kundenhistorie geladen", detail: "Weber GmbH · Stammkunde seit 2019 · 47 Bestellungen · NPS 8/10" },
      { icon: "📦", system: "ERP", action: "Sendungsstatus geprüft", detail: "DHL #4821 · Zugestellt am 21.03. · Unterschrift: M. Weber" },
      { icon: "💬", system: "Antwort", action: "Ticket beantwortet", detail: "\"Ihre Bestellung wurde am 21.03. zugestellt. Sendungsnachweis anbei.\"" },
      { icon: "📋", system: "FAQ", action: "Wissensdatenbank aktualisiert", detail: "Neuer Eintrag: Sendungsverfolgung — häufig gefragt, autonom lösbar" },
      { icon: "✅", system: "Ticket", action: "Geschlossen · CSAT abgefragt", detail: "Antwortzeit: 28 Sekunden · Autonom gelöst · Keine Eskalation" },
    ],
    kicker: "Gelöst in 28 Sekunden. Ohne menschliches Eingreifen.",
  },
];

export const hrScenarios: CascadeScenario[] = [
  {
    trigger: {
      icon: "📄",
      line1: "Neue Bewerbung eingegangen",
      line2: "Senior Entwickler · Julia Hartmann · München",
    },
    steps: [
      { icon: "📄", system: "CV", action: "Lebenslauf analysiert", detail: "8 Jahre Erfahrung · Python, TypeScript, AWS · Ex-Siemens, Ex-BMW" },
      { icon: "📊", system: "Matching", action: "Score berechnet", detail: "Match: 91/100 · Übertrifft Anforderungen in 4/5 Kategorien" },
      { icon: "📅", system: "Kalender", action: "Interview geplant", detail: "Mi 14:00 mit CTO · Teams-Link erstellt · Erinnerungen gesetzt" },
      { icon: "📧", system: "E-Mail", action: "Einladung versendet", detail: "Personalisiert: Bezug auf Siemens-Projekt, Team-Vorstellung, Anfahrt" },
      { icon: "👥", system: "Hiring", action: "Team benachrichtigt", detail: "CTO + VP Engineering informiert · Interview-Guide mit Fragen vorbereitet" },
    ],
    kicker: "Vom Eingang zum Interview in 3 Minuten.",
  },
];

export const salesScenarios: CascadeScenario[] = [
  {
    trigger: {
      icon: "🔔",
      line1: "Neuer Lead über Website",
      line2: "Dr. Maria Schulz · CFO · Hoffmann Maschinenbau GmbH",
    },
    steps: [
      { icon: "🔍", system: "Enrichment", action: "Kontakt angereichert", detail: "280 Mitarbeiter · €45M Umsatz · Branche: Maschinenbau · Standort: Stuttgart" },
      { icon: "📊", system: "Scoring", action: "Lead qualifiziert", detail: "Score: 87/100 · ICP-Match: Mittelstand, Finance-Pain, DATEV-Nutzer" },
      { icon: "💾", system: "CRM", action: "Kontakt angelegt", detail: "Firma + Kontakt in CRM · Tags: Hot Lead, CFO, Finance-Interest" },
      { icon: "📧", system: "E-Mail", action: "Personalisierte E-Mail drafted", detail: "Bezug: Maschinenbau + Finance-Pain · Case Study Müller GmbH angehängt" },
      { icon: "🔧", system: "Follow-up", action: "Sequenz gestartet", detail: "Tag 1: E-Mail · Tag 3: LinkedIn · Tag 7: Nachfass · Auto-Stop bei Antwort" },
    ],
    kicker: "Vom Lead zum qualifizierten Kontakt in 45 Sekunden.",
  },
];

export const marketingScenarios: CascadeScenario[] = [
  {
    trigger: {
      icon: "📣",
      line1: "Kampagnen-Auftrag",
      line2: "\"Erstell eine Q2-Kampagne für unsere DATEV-Integration.\"",
    },
    steps: [
      { icon: "🎯", system: "Zielgruppe", action: "Audience definiert", detail: "CFOs + Buchhalter · Mittelstand 50-500 MA · DATEV-Nutzer · DACH-Region" },
      { icon: "✍️", system: "Content", action: "3 Assets erstellt", detail: "Blog-Artikel (1.800 Wörter) · LinkedIn-Post · Newsletter-Segment" },
      { icon: "📅", system: "Planung", action: "Publishing geplant", detail: "Blog: Montag 09:00 · LinkedIn: Dienstag 11:30 · Newsletter: Donnerstag" },
      { icon: "💰", system: "Budget", action: "Spend allokiert", detail: "€500 LinkedIn Ads · Targeting: DATEV-Hashtag + Finance-Interesse" },
      { icon: "📊", system: "Tracking", action: "KPI-Dashboard live", detail: "Impressions, Clicks, Signups · Auto-Report jeden Freitag an Marketing-Lead" },
    ],
    kicker: "Von Briefing zu Live-Kampagne in 5 Minuten.",
  },
];

export const itOpsScenarios: CascadeScenario[] = [
  {
    trigger: {
      icon: "🎫",
      line1: "IT-Ticket #2847",
      line2: "\"Kann mich nicht mehr einloggen. Dringend — Kundentermin in 30 Min.\"",
    },
    steps: [
      { icon: "🔍", system: "Identität", action: "Benutzer verifiziert", detail: "Thomas Schmidt · Vertrieb · Letzter Login: Gestern 18:42 · 3 Fehlversuche" },
      { icon: "🔑", system: "AD", action: "Passwort zurückgesetzt", detail: "Neues temporäres Passwort generiert · MFA-Token bestätigt" },
      { icon: "📧", system: "E-Mail", action: "Zugangsdaten gesendet", detail: "Verschlüsselt an T. Schmidt · Aufforderung: Passwort sofort ändern" },
      { icon: "📋", system: "Log", action: "Vorfall dokumentiert", detail: "Ursache: Passwort abgelaufen · Kategorie: Routine · Keine Sicherheitsbedrohung" },
      { icon: "✅", system: "Ticket", action: "Gelöst und geschlossen", detail: "Lösungszeit: 47 Sekunden · Vor dem Kundentermin erledigt" },
    ],
    kicker: "47 Sekunden. Der Kundentermin fand statt.",
  },
];

export const procurementScenarios: CascadeScenario[] = [
  {
    trigger: {
      icon: "📦",
      line1: "3 neue Angebote eingegangen",
      line2: "Büromaterial Q2 · Weber, Fischer & Braun Lieferanten",
    },
    steps: [
      { icon: "📄", system: "Extraktion", action: "Angebote analysiert", detail: "Weber: €3.420 · Fischer: €3.180 · Braun: €3.650 · Alle 47 Positionen verglichen" },
      { icon: "📊", system: "Vergleich", action: "Ranking erstellt", detail: "1. Fischer (günstigster + 98% Liefertreue) · 2. Weber · 3. Braun" },
      { icon: "⚠️", system: "Prüfung", action: "Anomalie erkannt", detail: "Braun: Papier 23% teurer als Marktdurchschnitt · Druckerpatronen: Auslaufmodell" },
      { icon: "📝", system: "Bestellung", action: "Bestellung vorbereitet", detail: "Fischer Logistik · 47 Positionen · €3.180 · Lieferung: 5 Werktage" },
      { icon: "📧", system: "Freigabe", action: "Zur Genehmigung gesendet", detail: "An M. Schmidt (GF) · Vergleichsübersicht + Empfehlung angehängt" },
    ],
    kicker: "3 Angebote verglichen. Beste Option identifiziert. 2 Minuten.",
  },
];

export const complianceScenarios: CascadeScenario[] = [
  {
    trigger: {
      icon: "⚖️",
      line1: "Regulatorisches Update erkannt",
      line2: "NIS2-Richtlinie: Neue Meldepflichten ab 01.04.2026",
    },
    steps: [
      { icon: "📄", system: "Analyse", action: "Änderungen identifiziert", detail: "3 neue Anforderungen · 2 verschärfte Meldepflichten · Frist: 30 Tage" },
      { icon: "🔍", system: "Gap-Check", action: "Lücken geprüft", detail: "Anforderung 1: ✓ erfüllt · Anforderung 2: ⚠ teilweise · Anforderung 3: ✗ fehlend" },
      { icon: "📋", system: "Maßnahmen", action: "Aktionsplan erstellt", detail: "5 Maßnahmen · 2 Verantwortliche · Deadline: 25.03.2026 (5 Tage Puffer)" },
      { icon: "📊", system: "Report", action: "Compliance-Report generiert", detail: "Status: 67% konform · Risiko: Mittel · Prognose: 100% bis Frist" },
      { icon: "📧", system: "Benachrichtigung", action: "GF + Rechtsabteilung informiert", detail: "Report + Aktionsplan + Fristwarnung per E-Mail versendet" },
    ],
    kicker: "Regulierung erkannt. Lücken geprüft. Plan erstellt. 90 Sekunden.",
  },
];

export const cybersecurityScenarios: CascadeScenario[] = [
  {
    trigger: {
      icon: "🚨",
      line1: "Anomalie erkannt",
      line2: "Ungewöhnlicher Login: admin@kengo.de aus Bukarest, Rumänien · 03:47 Uhr",
    },
    steps: [
      { icon: "🔍", system: "Analyse", action: "Bedrohung bewertet", detail: "IP: 185.XX.XX.XX · Bekannter VPN-Anbieter · Kein vorheriger Zugriff aus RO" },
      { icon: "🛡️", system: "Response", action: "Session blockiert", detail: "Login-Session terminiert · Account temporär gesperrt · MFA erzwungen" },
      { icon: "📧", system: "Alert", action: "IT-Leiter benachrichtigt", detail: "Severity: Hoch · Sofort-Maßnahmen bereits ergriffen · Bestätigung angefordert" },
      { icon: "📋", system: "Forensik", action: "Incident dokumentiert", detail: "Audit-Trail erstellt · Alle Zugriffe der letzten 24h geprüft · Keine Datenverluste" },
      { icon: "🔧", system: "Härtung", action: "Regeln aktualisiert", detail: "Geo-Blocking: RO/UA auf Watchlist · Login-Alerts verschärft · NIS2-konform" },
    ],
    kicker: "Bedrohung erkannt, blockiert und dokumentiert. 12 Sekunden.",
  },
];
