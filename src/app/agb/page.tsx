import LegalPage, { Section, SubSection } from "@/components/LegalPage";

export default function AGBPage() {
  return (
    <LegalPage title="Allgemeine Geschäftsbedingungen" lastUpdated="25. März 2026">
      <Section title="§ 1 Geltungsbereich">
        <p>
          (1) Diese Allgemeinen Geschäftsbedingungen (nachfolgend „AGB") gelten
          für alle Verträge zwischen der Kengo GmbH, [Adresse], Deutschland
          (nachfolgend „Kengo" oder „wir") und dem Kunden (nachfolgend „Kunde"
          oder „du") über die Nutzung der KI-Mitarbeiter-Plattform und
          zugehöriger Dienstleistungen.
        </p>
        <p className="mt-2">
          (2) Abweichende, entgegenstehende oder ergänzende AGB des Kunden
          werden nicht Vertragsbestandteil, es sei denn, Kengo stimmt ihrer
          Geltung ausdrücklich schriftlich zu.
        </p>
        <p className="mt-2">
          (3) Diese AGB gelten sowohl gegenüber Verbrauchern als auch gegenüber
          Unternehmern, es sei denn, in der jeweiligen Klausel wird eine
          Differenzierung vorgenommen.
        </p>
      </Section>

      <Section title="§ 2 Vertragsgegenstand">
        <p>
          (1) Kengo stellt dem Kunden KI-basierte Mitarbeiter (nachfolgend
          „KI-Mitarbeiter") zur Verfügung, die autonome Aufgaben in den
          Bereichen Finance, Customer Support, HR, Sales, Marketing, IT Ops,
          Procurement, Compliance und Cybersecurity übernehmen.
        </p>
        <p className="mt-2">
          (2) Der genaue Leistungsumfang ergibt sich aus der jeweils gewählten
          Leistungsstufe (KI-Assistent, KI-Fachkraft oder KI-Abteilung) und
          den zum Zeitpunkt des Vertragsschlusses auf kengo.de veröffentlichten
          Produktbeschreibungen.
        </p>
        <p className="mt-2">
          (3) Kengo schuldet eine Dienstleistung, keinen bestimmten Erfolg. Die
          KI-Mitarbeiter arbeiten nach bestem technischem Stand, eine
          Fehlerfreiheit wird nicht garantiert.
        </p>
      </Section>

      <Section title="§ 3 Vertragsschluss">
        <p>
          (1) Die Darstellung der Leistungen auf kengo.de stellt kein
          verbindliches Angebot dar, sondern eine Aufforderung zur Abgabe
          eines Angebots.
        </p>
        <p className="mt-2">
          (2) Der Vertrag kommt zustande, wenn Kengo die Bestellung des Kunden
          durch eine Auftragsbestätigung per E-Mail annimmt oder die
          Leistungserbringung aufnimmt.
        </p>
      </Section>

      <Section title="§ 4 Preise und Zahlung">
        <p>
          (1) Es gelten die zum Zeitpunkt des Vertragsschlusses auf kengo.de
          veröffentlichten Preise. Alle Preise verstehen sich zuzüglich der
          gesetzlichen Umsatzsteuer.
        </p>
        <p className="mt-2">
          (2) Die monatliche Grundgebühr wird im Voraus zum Monatsbeginn
          fällig. Ergebnis-basierte Kosten für Spezialisten werden am
          Monatsende nach tatsächlichem Verbrauch abgerechnet.
        </p>
        <p className="mt-2">
          (3) Die Zahlung erfolgt per Lastschrift, Kreditkarte oder
          Überweisung. Bei Zahlungsverzug gelten die gesetzlichen
          Verzugsregelungen.
        </p>
      </Section>

      <Section title="§ 5 Einarbeitung und Laufzeit">
        <SubSection title="Einarbeitung">
          <p>
            Die Einarbeitung des KI-Mitarbeiters dauert in der Regel 5
            Arbeitstage. Während dieser Zeit lernt der KI-Mitarbeiter die
            Prozesse, Systeme und Ziele des Kunden kennen. Die Einarbeitung
            ist im Vertragspreis enthalten.
          </p>
        </SubSection>
        <SubSection title="Laufzeit und Kündigung">
          <p>
            (1) Der Vertrag hat eine Mindestlaufzeit von einem Monat und
            verlängert sich automatisch um jeweils einen weiteren Monat, sofern
            er nicht mit einer Frist von 14 Tagen zum Ende des jeweiligen
            Vertragsmonats gekündigt wird.
          </p>
          <p className="mt-2">
            (2) Das Recht zur außerordentlichen Kündigung aus wichtigem Grund
            bleibt unberührt.
          </p>
          <p className="mt-2">
            (3) Die Kündigung bedarf der Textform (E-Mail genügt).
          </p>
        </SubSection>
      </Section>

      <Section title="§ 6 Pflichten des Kunden">
        <p>
          (1) Der Kunde stellt Kengo die für die Erbringung der Leistungen
          erforderlichen Informationen, Zugänge und Daten rechtzeitig und
          vollständig zur Verfügung.
        </p>
        <p className="mt-2">
          (2) Der Kunde ist für die Richtigkeit und Rechtmäßigkeit der von
          ihm bereitgestellten Daten verantwortlich.
        </p>
        <p className="mt-2">
          (3) Der Kunde konfiguriert die Freigabe-Schwellenwerte und
          Eskalationsregeln für seinen KI-Mitarbeiter. Kengo haftet nicht für
          Ergebnisse, die auf fehlerhafter Konfiguration durch den Kunden
          beruhen.
        </p>
      </Section>

      <Section title="§ 7 Datenschutz und Datensicherheit">
        <p>
          (1) Die Verarbeitung personenbezogener Daten erfolgt gemäß der
          DSGVO. Details regelt unsere Datenschutzerklärung unter{" "}
          <a href="/datenschutz" className="text-kengo hover:text-kengo-light underline">
            kengo.de/datenschutz
          </a>
          .
        </p>
        <p className="mt-2">
          (2) Soweit Kengo im Auftrag des Kunden personenbezogene Daten
          verarbeitet, schließen die Parteien einen separaten
          Auftragsverarbeitungsvertrag (AVV).
        </p>
        <p className="mt-2">
          (3) Alle Kundendaten werden auf Servern in Deutschland (Hetzner
          Online GmbH) gehostet. Ein Transfer in Drittländer findet nur mit
          ausdrücklicher Zustimmung des Kunden statt.
        </p>
      </Section>

      <Section title="§ 8 Haftung">
        <p>
          (1) Kengo haftet unbeschränkt für Schäden aus der Verletzung des
          Lebens, des Körpers oder der Gesundheit sowie für Vorsatz und grobe
          Fahrlässigkeit.
        </p>
        <p className="mt-2">
          (2) Bei leichter Fahrlässigkeit haftet Kengo nur bei Verletzung
          wesentlicher Vertragspflichten (Kardinalpflichten). Die Haftung ist
          in diesem Fall auf den vertragstypischen, vorhersehbaren Schaden
          begrenzt.
        </p>
        <p className="mt-2">
          (3) Die Haftung für mittelbare Schäden, Folgeschäden und entgangenen
          Gewinn ist bei leichter Fahrlässigkeit ausgeschlossen.
        </p>
        <p className="mt-2">
          (4) Die vorstehenden Haftungsbeschränkungen gelten nicht für Ansprüche
          nach dem Produkthaftungsgesetz.
        </p>
      </Section>

      <Section title="§ 9 Verfügbarkeit">
        <p>
          (1) Kengo strebt eine Verfügbarkeit der KI-Mitarbeiter von 99,5% im
          Monatsmittel an (gemessen an der Gesamtzeit abzüglich geplanter
          Wartungsfenster).
        </p>
        <p className="mt-2">
          (2) Geplante Wartungsarbeiten werden dem Kunden mindestens 48 Stunden
          im Voraus per E-Mail mitgeteilt und finden nach Möglichkeit außerhalb
          der üblichen Geschäftszeiten statt.
        </p>
      </Section>

      <Section title="§ 10 Vertraulichkeit">
        <p>
          Beide Parteien verpflichten sich, alle im Rahmen der
          Vertragsbeziehung erhaltenen vertraulichen Informationen vertraulich
          zu behandeln und nicht an Dritte weiterzugeben, es sei denn, dies
          ist zur Vertragserfüllung erforderlich oder gesetzlich vorgeschrieben.
        </p>
      </Section>

      <Section title="§ 11 Änderungen der AGB">
        <p>
          (1) Kengo behält sich vor, diese AGB mit Wirkung für die Zukunft zu
          ändern. Kengo wird den Kunden über Änderungen mindestens 30 Tage
          vor Inkrafttreten per E-Mail informieren.
        </p>
        <p className="mt-2">
          (2) Widerspricht der Kunde nicht innerhalb von 30 Tagen nach
          Zugang der Änderungsmitteilung, gelten die geänderten AGB als
          angenommen. Kengo wird den Kunden in der Änderungsmitteilung auf
          die Widerspruchsmöglichkeit und die Folgen hinweisen.
        </p>
      </Section>

      <Section title="§ 12 Schlussbestimmungen">
        <p>
          (1) Es gilt das Recht der Bundesrepublik Deutschland unter
          Ausschluss des UN-Kaufrechts.
        </p>
        <p className="mt-2">
          (2) Ist der Kunde Kaufmann, juristische Person des öffentlichen
          Rechts oder öffentlich-rechtliches Sondervermögen, ist
          ausschließlicher Gerichtsstand für alle Streitigkeiten aus diesem
          Vertrag der Sitz von Kengo.
        </p>
        <p className="mt-2">
          (3) Sollten einzelne Bestimmungen dieser AGB unwirksam sein oder
          werden, bleibt die Wirksamkeit der übrigen Bestimmungen unberührt.
        </p>
      </Section>
    </LegalPage>
  );
}
