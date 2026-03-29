import LegalPage, { Section } from "@/components/LegalPage";

export default function ImpressumPage() {
  return (
    <LegalPage title="Impressum" lastUpdated="25. März 2026">
      <Section title="Angaben gemäß § 5 TMG">
        <p>
          Kengo GmbH
          <br />
          Ridlerstraße 39
          <br />
          80339 München
          <br />
          Deutschland
        </p>
      </Section>

      <Section title="Vertreten durch">
        <p>Geschäftsführer: Phil Hie</p>
      </Section>

      <Section title="Kontakt">
        <p>
          E-Mail: hello@kengo.de
          <br />
          Telefon: +49 178 681 3898
        </p>
      </Section>

      <Section title="Registereintrag">
        <p>
          Handelsregister: HRB 290841
          <br />
          Registergericht: Amtsgericht München
        </p>
      </Section>

      <Section title="Umsatzsteuer-ID">
        <p>
          Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:
          <br />
          USt-IdNr.: DE365248719
        </p>
      </Section>

      <Section title="Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV">
        <p>
          Phil Hie
          <br />
          Kengo GmbH
          <br />
          Ridlerstraße 39
          <br />
          80339 München
        </p>
      </Section>

      <Section title="EU-Streitschlichtung">
        <p>
          Die Europäische Kommission stellt eine Plattform zur
          Online-Streitbeilegung (OS) bereit. Diese Plattform finden Sie unter{" "}
          <a
            href="https://ec.europa.eu/consumers/odr/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-kengo hover:text-kengo-light transition-colors underline"
          >
            https://ec.europa.eu/consumers/odr/
          </a>
          .
        </p>
        <p className="mt-2">
          Wir sind nicht bereit oder verpflichtet, an
          Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle
          teilzunehmen.
        </p>
      </Section>

      <Section title="Haftung für Inhalte">
        <p>
          Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte
          auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach
          §§ 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht
          verpflichtet, übermittelte oder gespeicherte fremde Informationen zu
          überwachen oder nach Umständen zu forschen, die auf eine
          rechtswidrige Tätigkeit hinweisen.
        </p>
        <p className="mt-2">
          Verpflichtungen zur Entfernung oder Sperrung der Nutzung von
          Informationen nach den allgemeinen Gesetzen bleiben hiervon
          unberührt. Eine diesbezügliche Haftung ist jedoch erst ab dem
          Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei
          Bekanntwerden von entsprechenden Rechtsverletzungen werden wir diese
          Inhalte umgehend entfernen.
        </p>
      </Section>

      <Section title="Haftung für Links">
        <p>
          Unser Angebot enthält Links zu externen Websites Dritter, auf deren
          Inhalte wir keinen Einfluss haben. Deshalb können wir für diese
          fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der
          verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber
          der Seiten verantwortlich. Die verlinkten Seiten wurden zum
          Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft.
          Rechtswidrige Inhalte waren zum Zeitpunkt der Verlinkung nicht
          erkennbar.
        </p>
      </Section>

      <Section title="Urheberrecht">
        <p>
          Die durch die Seitenbetreiber erstellten Inhalte und Werke auf
          diesen Seiten unterliegen dem deutschen Urheberrecht. Die
          Vervielfältigung, Bearbeitung, Verbreitung und jede Art der
          Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der
          schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.
          Downloads und Kopien dieser Seite sind nur für den privaten, nicht
          kommerziellen Gebrauch gestattet.
        </p>
      </Section>
    </LegalPage>
  );
}
