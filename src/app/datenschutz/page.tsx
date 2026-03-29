import LegalPage, { Section, SubSection } from "@/components/LegalPage";

export default function DatenschutzPage() {
  return (
    <LegalPage title="Datenschutzerklärung" lastUpdated="25. März 2026">
      <Section title="1. Datenschutz auf einen Blick">
        <SubSection title="Allgemeine Hinweise">
          <p>
            Die folgenden Hinweise geben einen einfachen Überblick darüber, was
            mit deinen personenbezogenen Daten passiert, wenn du diese Website
            besuchst. Personenbezogene Daten sind alle Daten, mit denen du
            persönlich identifiziert werden kannst. Ausführliche Informationen
            zum Thema Datenschutz entnimmst du unserer unter diesem Text
            aufgeführten Datenschutzerklärung.
          </p>
        </SubSection>

        <SubSection title="Datenerfassung auf dieser Website">
          <p>
            <strong>Wer ist verantwortlich für die Datenerfassung auf dieser Website?</strong>
            <br />
            Die Datenverarbeitung auf dieser Website erfolgt durch den
            Websitebetreiber. Dessen Kontaktdaten kannst du dem Abschnitt
            „Hinweis zur verantwortlichen Stelle" in dieser Datenschutzerklärung
            entnehmen.
          </p>
          <p className="mt-2">
            <strong>Wie erfassen wir deine Daten?</strong>
            <br />
            Deine Daten werden zum einen dadurch erhoben, dass du uns diese
            mitteilst. Hierbei kann es sich z.B. um Daten handeln, die du in
            ein Kontaktformular eingibst. Andere Daten werden automatisch oder
            nach deiner Einwilligung beim Besuch der Website durch unsere
            IT-Systeme erfasst. Das sind vor allem technische Daten (z.B.
            Internetbrowser, Betriebssystem oder Uhrzeit des Seitenaufrufs).
            Die Erfassung dieser Daten erfolgt automatisch, sobald du diese
            Website betrittst.
          </p>
          <p className="mt-2">
            <strong>Wofür nutzen wir deine Daten?</strong>
            <br />
            Ein Teil der Daten wird erhoben, um eine fehlerfreie Bereitstellung
            der Website zu gewährleisten. Andere Daten können zur Analyse
            deines Nutzerverhaltens verwendet werden.
          </p>
          <p className="mt-2">
            <strong>Welche Rechte hast du bezüglich deiner Daten?</strong>
            <br />
            Du hast jederzeit das Recht, unentgeltlich Auskunft über Herkunft,
            Empfänger und Zweck deiner gespeicherten personenbezogenen Daten
            zu erhalten. Du hast außerdem ein Recht, die Berichtigung oder
            Löschung dieser Daten zu verlangen. Wenn du eine Einwilligung zur
            Datenverarbeitung erteilt hast, kannst du diese Einwilligung
            jederzeit für die Zukunft widerrufen. Außerdem hast du das Recht,
            unter bestimmten Umständen die Einschränkung der Verarbeitung
            deiner personenbezogenen Daten zu verlangen. Des Weiteren steht
            dir ein Beschwerderecht bei der zuständigen Aufsichtsbehörde zu.
          </p>
        </SubSection>
      </Section>

      <Section title="2. Verantwortliche Stelle">
        <p>
          Die verantwortliche Stelle für die Datenverarbeitung auf dieser
          Website ist:
        </p>
        <p className="mt-2">
          Kengo GmbH
          <br />
          Phil Hie (Geschäftsführer)
          <br />
          Ridlerstraße 39
          <br />
          80339 München
          <br />
          Deutschland
        </p>
        <p className="mt-2">
          E-Mail: datenschutz@kengo.de
        </p>
        <p className="mt-2">
          Verantwortliche Stelle ist die natürliche oder juristische Person,
          die allein oder gemeinsam mit anderen über die Zwecke und Mittel
          der Verarbeitung von personenbezogenen Daten (z.B. Namen,
          E-Mail-Adressen o.Ä.) entscheidet.
        </p>
      </Section>

      <Section title="3. Hosting">
        <p>
          Wir hosten die Inhalte unserer Website bei Vercel Inc. (Edge
          Network) und bei Hetzner Online GmbH (Applikationsdaten).
        </p>
        <SubSection title="Vercel">
          <p>
            Anbieter ist die Vercel Inc., 340 S Lemon Ave #4133, Walnut, CA
            91789, USA. Details entnimmst du der Datenschutzerklärung von
            Vercel:{" "}
            <a href="https://vercel.com/legal/privacy-policy" target="_blank" rel="noopener noreferrer" className="text-kengo hover:text-kengo-light underline">
              https://vercel.com/legal/privacy-policy
            </a>
            . Die Datenübertragung in die USA wird auf Basis der
            Standardvertragsklauseln der EU-Kommission durchgeführt.
          </p>
        </SubSection>
        <SubSection title="Hetzner">
          <p>
            Applikationsdaten werden auf Servern der Hetzner Online GmbH,
            Industriestr. 25, 91710 Gunzenhausen, Deutschland gehostet. Alle
            Daten verbleiben in Deutschland. Auftragsverarbeitungsvertrag liegt
            vor.
          </p>
        </SubSection>
      </Section>

      <Section title="4. Allgemeine Hinweise und Pflichtinformationen">
        <SubSection title="Datenschutz">
          <p>
            Die Betreiber dieser Seiten nehmen den Schutz deiner persönlichen
            Daten sehr ernst. Wir behandeln deine personenbezogenen Daten
            vertraulich und entsprechend der gesetzlichen
            Datenschutzvorschriften sowie dieser Datenschutzerklärung.
          </p>
        </SubSection>

        <SubSection title="Speicherdauer">
          <p>
            Soweit innerhalb dieser Datenschutzerklärung keine speziellere
            Speicherdauer genannt wurde, verbleiben deine personenbezogenen
            Daten bei uns, bis der Zweck für die Datenverarbeitung entfällt.
            Wenn du ein berechtigtes Löschersuchen geltend machst oder eine
            Einwilligung zur Datenverarbeitung widerrufst, werden deine Daten
            gelöscht, sofern wir keine anderen rechtlich zulässigen Gründe für
            die Speicherung deiner personenbezogenen Daten haben.
          </p>
        </SubSection>

        <SubSection title="Widerruf deiner Einwilligung zur Datenverarbeitung">
          <p>
            Viele Datenverarbeitungsvorgänge sind nur mit deiner ausdrücklichen
            Einwilligung möglich. Du kannst eine bereits erteilte Einwilligung
            jederzeit widerrufen. Die Rechtmäßigkeit der bis zum Widerruf
            erfolgten Datenverarbeitung bleibt vom Widerruf unberührt.
          </p>
        </SubSection>

        <SubSection title="Beschwerderecht bei der zuständigen Aufsichtsbehörde">
          <p>
            Im Falle von Verstößen gegen die DSGVO steht den Betroffenen ein
            Beschwerderecht bei einer Aufsichtsbehörde zu, insbesondere in dem
            Mitgliedstaat ihres gewöhnlichen Aufenthalts, ihres Arbeitsplatzes
            oder des Orts des mutmaßlichen Verstoßes.
          </p>
        </SubSection>

        <SubSection title="Recht auf Datenübertragbarkeit">
          <p>
            Du hast das Recht, Daten, die wir auf Grundlage deiner
            Einwilligung oder in Erfüllung eines Vertrags automatisiert
            verarbeiten, an dich oder an einen Dritten in einem gängigen,
            maschinenlesbaren Format aushändigen zu lassen. Sofern du die
            direkte Übertragung der Daten an einen anderen Verantwortlichen
            verlangst, erfolgt dies nur, soweit es technisch machbar ist.
          </p>
        </SubSection>

        <SubSection title="Auskunft, Löschung und Berichtigung">
          <p>
            Du hast im Rahmen der geltenden gesetzlichen Bestimmungen
            jederzeit das Recht auf unentgeltliche Auskunft über deine
            gespeicherten personenbezogenen Daten, deren Herkunft und
            Empfänger und den Zweck der Datenverarbeitung und ggf. ein Recht
            auf Berichtigung oder Löschung dieser Daten. Hierzu sowie zu
            weiteren Fragen zum Thema personenbezogene Daten kannst du dich
            jederzeit an uns wenden: datenschutz@kengo.de.
          </p>
        </SubSection>
      </Section>

      <Section title="5. Datenerfassung auf dieser Website">
        <SubSection title="Server-Log-Dateien">
          <p>
            Der Provider der Seiten erhebt und speichert automatisch
            Informationen in so genannten Server-Log-Dateien, die dein Browser
            automatisch an uns übermittelt. Dies sind: Browsertyp und
            Browserversion, verwendetes Betriebssystem, Referrer URL,
            Hostname des zugreifenden Rechners, Uhrzeit der Serveranfrage,
            IP-Adresse.
          </p>
          <p className="mt-2">
            Eine Zusammenführung dieser Daten mit anderen Datenquellen wird
            nicht vorgenommen. Die Erfassung dieser Daten erfolgt auf
            Grundlage von Art. 6 Abs. 1 lit. f DSGVO.
          </p>
        </SubSection>

        <SubSection title="Cookies">
          <p>
            Diese Website verwendet keine Tracking-Cookies. Es werden
            ausschließlich technisch notwendige Cookies eingesetzt, die für
            den Betrieb der Website erforderlich sind.
          </p>
        </SubSection>

        <SubSection title="Webanalyse (Plausible)">
          <p>
            Wir nutzen Plausible Analytics, einen datenschutzfreundlichen
            Webanalysedienst der Plausible Insights OÜ (EU/Estland). Plausible
            verwendet keine Cookies, speichert keine personenbezogenen Daten
            und ist vollständig DSGVO-konform. Es werden ausschließlich
            aggregierte, anonyme Nutzungsdaten erhoben (Seitenaufrufe,
            Referrer, Gerätetyp, Land). Eine Identifikation einzelner
            Besucher ist nicht möglich. Die Daten werden auf EU-Servern
            verarbeitet.
          </p>
          <p className="mt-2">
            Rechtsgrundlage: Art. 6 Abs. 1 lit. f DSGVO (berechtigtes
            Interesse an der anonymen Analyse der Website-Nutzung zur
            Verbesserung unseres Angebots).
          </p>
          <p className="mt-2">
            Weitere Informationen:{" "}
            <a href="https://plausible.io/data-policy" target="_blank" rel="noopener noreferrer" className="text-kengo hover:text-kengo-light underline">
              plausible.io/data-policy
            </a>
          </p>
        </SubSection>

        <SubSection title="Kontaktformular und Demo-Buchung">
          <p>
            Wenn du uns per Kontaktformular oder Demo-Buchung (Cal.com)
            Anfragen zukommen lässt, werden deine Angaben aus dem
            Anfrageformular inklusive der von dir dort angegebenen
            Kontaktdaten zwecks Bearbeitung der Anfrage und für den Fall von
            Anschlussfragen bei uns gespeichert. Diese Daten geben wir nicht
            ohne deine Einwilligung weiter.
          </p>
          <p className="mt-2">
            Die Verarbeitung dieser Daten erfolgt auf Grundlage von Art. 6
            Abs. 1 lit. b DSGVO, sofern deine Anfrage mit der Erfüllung eines
            Vertrags zusammenhängt oder zur Durchführung vorvertraglicher
            Maßnahmen erforderlich ist.
          </p>
        </SubSection>
      </Section>

      <Section title="6. Auftragsverarbeitung">
        <p>
          Wir haben Auftragsverarbeitungsverträge (AVV) mit folgenden
          Dienstleistern geschlossen:
        </p>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Hetzner Online GmbH (Hosting, Deutschland)</li>
          <li>Vercel Inc. (Website-Hosting, USA — Standardvertragsklauseln)</li>
          <li>Cal.com Inc. (Terminbuchung — Standardvertragsklauseln)</li>
        </ul>
      </Section>

      <Section title="7. Änderungen">
        <p>
          Wir behalten uns vor, diese Datenschutzerklärung anzupassen, damit
          sie stets den aktuellen rechtlichen Anforderungen entspricht oder um
          Änderungen unserer Leistungen in der Datenschutzerklärung umzusetzen.
          Für deinen erneuten Besuch gilt dann die neue Datenschutzerklärung.
        </p>
      </Section>
    </LegalPage>
  );
}
