"""GF-language template library for translating findings to sales copy.

Each template has:
    short: 3-6 words, used as {{finding_1_short}} in subject lines (<=50 chars)
    what:  1 sentence in GF-language for {{finding_X_what}} body placeholders

Placeholders resolved at render time (see translator.fill_placeholders):
    {domain}, {ip}, {cve_count}, {cve_example}, {count},
    {breach_count}, {pwd_count}, {port}, {path}, {version}, {bytes}, {email}
"""

from __future__ import annotations

TEMPLATES: dict[str, dict[str, str]] = {

    # ─── OPEN SERVICES (Shodan) ──────────────────────────────────────

    "shodan:mysql": {
        "short": "Datenbank offen im Internet",
        "what": "Ihr MySQL-Server antwortet auf Port 3306 aus dem offenen Internet — jede IP weltweit kann Verbindungs- und Login-Versuche starten, rund um die Uhr, ohne Vorwarnung.",
    },
    "shodan:ftp": {
        "short": "FTP offen aus dem Internet",
        "what": "Ihr FTP-Dienst auf Port 21 ist öffentlich erreichbar — FTP überträgt Zugangsdaten unverschlüsselt und ist eines der häufigsten Brute-Force-Ziele.",
    },
    "shodan:postgresql": {
        "short": "PostgreSQL offen im Internet",
        "what": "Ihre PostgreSQL-Datenbank antwortet auf Port 5432 aus dem offenen Internet — direktes Angriffsziel für Brute-Force und Datendiebstahl.",
    },
    "shodan:redis": {
        "short": "Redis öffentlich erreichbar",
        "what": "Ihr Redis-Server ist öffentlich erreichbar und akzeptiert in Standardkonfiguration Verbindungen ohne Passwort — Lese- und Schreibzugriff für jeden.",
    },
    "shodan:mongodb": {
        "short": "MongoDB offen im Internet",
        "what": "Ihre MongoDB-Datenbank ist öffentlich erreichbar — in Standardkonfiguration ohne Authentifizierung, d.h. vollständiger Lese- und Schreibzugriff für jeden.",
    },
    "shodan:rdp": {
        "short": "Remote-Desktop offen im Internet",
        "what": "Ihr RDP-Dienst (Port 3389) ist öffentlich erreichbar — Remote-Desktop ist das häufigste Einfallstor bei Ransomware-Angriffen auf Mittelständler.",
    },
    "shodan:ssh": {
        "short": "SSH offen im Internet",
        "what": "Ihr SSH-Dienst ist aus dem offenen Internet erreichbar — SSH ohne IP-Beschränkung ist ein permanentes Brute-Force-Ziel.",
    },
    "shodan:telnet": {
        "short": "Telnet offen im Internet",
        "what": "Ihr Telnet-Dienst ist öffentlich erreichbar — Telnet überträgt Zugangsdaten unverschlüsselt und gilt seit über einem Jahrzehnt als nicht mehr einsetzbar.",
    },
    "shodan:cve": {
        "short": "Ungepatchte Schwachstellen aktiv",
        "what": "Auf Ihrer Server-IP sind {cve_count} bekannte Schwachstellen mit verfügbaren Patches aktiv (z.B. {cve_example}) — alle haben Security-Updates, die nicht eingespielt wurden.",
    },
    "shodan:many_ports": {
        "short": "Große Angriffsfläche",
        "what": "{count} Ports sind auf Ihrem Server öffentlich erreichbar — eine unzureichende Firewall-Konfiguration, die die Angriffsfläche unnötig vergrößert.",
    },

    # ─── EXCHANGE ────────────────────────────────────────────────────

    "exchange:ecp_powershell": {
        "short": "Exchange Admin-Panel offen",
        "what": "Ihr Exchange-Server hat /ecp und /PowerShell ohne Beschränkung exposed — die zwei häufigsten Einstiegspunkte bei Exchange-Ransomware (ProxyShell, ProxyLogon, ProxyNotShell).",
    },
    "exchange:multiple_endpoints": {
        "short": "Exchange-Schnittstellen offen",
        "what": "{count} Exchange-Endpoints sind öffentlich erreichbar (/owa, /ecp, /ews, /mapi, /PowerShell, /autodiscover) — die Angriffsfläche ist maximal.",
    },
    "exchange:basic_auth": {
        "short": "Exchange Basic Auth aktiv",
        "what": "Auf Ihrem Exchange-Endpoint ist Basic Authentication aktiviert — Zugangsdaten werden Base64-kodiert übertragen, leicht abfangbar bei jeder MitM-Schwäche.",
    },
    "exchange:eol": {
        "short": "Exchange End-of-Life",
        "what": "Ihr Exchange-Server ist eine Version, die keine Sicherheitsupdates mehr erhält — jede neue Schwachstelle bleibt dauerhaft offen.",
    },
    "exchange:hostname_leak": {
        "short": "Interner Hostname geleakt",
        "what": "Ihr Exchange-Server verrät über den X-FEServer-Header den internen Hostnamen — Angreifer können damit Rückschlüsse auf Ihre interne Netzwerkstruktur ziehen.",
    },

    # ─── FILE EXPOSURE ───────────────────────────────────────────────

    "file:webconfig": {
        "short": "Konfigurationsdatei öffentlich",
        "what": "Ihre /web.config liegt öffentlich im Internet (HTTP 200 abrufbar) — diese Datei enthält bei IIS-Servern typischerweise Datenbank-Connection-Strings im Klartext.",
    },
    "file:env": {
        "short": ".env-Datei exponiert",
        "what": "Ihre /.env-Datei ist öffentlich abrufbar — diese Datei enthält in der Regel API-Keys, Datenbank-Passwörter und Secret-Keys im Klartext.",
    },
    "file:htpasswd": {
        "short": "Passwort-Datei exponiert",
        "what": "Ihre /.htpasswd-Datei ist öffentlich abrufbar — sie enthält gehashte Passwörter, die offline geknackt werden können.",
    },
    "file:htaccess": {
        "short": "Apache-Config exponiert",
        "what": "Ihre /.htaccess-Datei ist öffentlich abrufbar — sie verrät Pfad-Schutzregeln und damit gezielt, wo Angreifer ansetzen müssen.",
    },
    "file:git": {
        "short": "Git-Repository exponiert",
        "what": "Ihr /.git-Verzeichnis ist öffentlich abrufbar — Angreifer können darüber den vollständigen Quellcode Ihrer Anwendung rekonstruieren, inklusive aller Passwörter in der Commit-Historie.",
    },
    "file:composer": {
        "short": "Dependency-Manifest öffentlich",
        "what": "Ihre /composer.json ist öffentlich — Angreifer können daraus Ihre PHP-Library-Versionen ablesen und gezielt nach passenden Exploits suchen.",
    },
    "file:package_json": {
        "short": "Package-Manifest öffentlich",
        "what": "Ihre /package.json ist öffentlich — sie verrät alle Node.js-Dependencies und deren Versionen, was gezielte Supply-Chain-Angriffe erleichtert.",
    },
    "file:phpinfo": {
        "short": "PHP-Info öffentlich",
        "what": "Ihre /phpinfo.php ist öffentlich — sie zeigt die komplette Server-Konfiguration, PHP-Version, geladene Module und Umgebungsvariablen.",
    },
    "file:docker": {
        "short": "Docker-Config exponiert",
        "what": "Ihre Docker-Konfiguration (docker-compose.yml oder Dockerfile) ist öffentlich abrufbar — sie kann Credentials, interne Netzwerk-Topologie und Service-Abhängigkeiten verraten.",
    },
    "file:backup": {
        "short": "Backup-Datei exponiert",
        "what": "Eine Backup-Datei ist öffentlich abrufbar — sie kann eine vollständige Kopie Ihrer Datenbank oder Anwendung enthalten.",
    },
    "file:sqldump": {
        "short": "Datenbank-Dump exponiert",
        "what": "Ein SQL-Dump ist öffentlich abrufbar — er enthält potenziell Ihren gesamten Datenbestand im Klartext.",
    },

    # ─── EMAIL AUTHENTICATION ────────────────────────────────────────

    "email:no_dmarc": {
        "short": "Kein DMARC-Eintrag",
        "what": "Ihre Domain hat keinen DMARC-Eintrag — der internationale Standardschutz gegen E-Mail-Spoofing fehlt komplett. Jede Person weltweit kann eine E-Mail in Ihrem Namen versenden.",
    },
    "email:dmarc_none": {
        "short": "DMARC nur auf Beobachten",
        "what": "Ihre DMARC-Policy steht auf 'none' — der Schutz existiert nur auf dem Papier. Empfangende Server ergreifen keinerlei Maßnahmen gegen gefälschte E-Mails in Ihrem Namen.",
    },
    "email:no_spf": {
        "short": "Kein SPF-Eintrag",
        "what": "Für Ihre Domain existiert kein SPF-Record — ohne SPF kann jeder Server im Internet E-Mails in Ihrem Namen versenden, ohne dass Spam-Filter eingreifen.",
    },
    "email:spf_weak": {
        "short": "SPF zu schwach",
        "what": "Ihr SPF-Record steht auf 'softfail' — fremde Server können in Ihrem Namen versenden und werden lediglich als 'verdächtig' markiert, nicht abgelehnt.",
    },
    "email:no_dkim": {
        "short": "Kein DKIM-Schlüssel",
        "what": "Sie haben keinen DKIM-Schlüssel für Ihre Domain konfiguriert — empfangende Server können nicht kryptografisch verifizieren, ob eine E-Mail wirklich von Ihnen stammt.",
    },
    "email:dmarc_subdomain_none": {
        "short": "Subdomain-Spoofing möglich",
        "what": "Ihre DMARC-Subdomain-Policy steht auf 'none' — Angreifer können mail.{domain} oder rechnung.{domain} für Spoofing verwenden, auch wenn die Hauptdomain geschützt ist.",
    },

    # ─── CREDENTIALS / BREACHES ──────────────────────────────────────

    "cred:hibp_password": {
        "short": "Passwort in Datenleck",
        "what": "Ihre {email} erscheint in einem Datenleck mit Klartext-Passwort. Wenn dieselbe Person dieses Passwort heute noch nutzt, sind die zugehörigen Konten kompromittiert.",
    },
    "cred:hibp_multiple": {
        "short": "Mail-Adresse in {breach_count} Lecks",
        "what": "Ihre {email} erscheint in {breach_count} Datenlecks — davon {pwd_count} mit Klartext-Passwort. Das ist ein offenes Tor für Credential-Stuffing-Angriffe auf Ihre Unternehmenskonten.",
    },
    "cred:hibp_metadata": {
        "short": "Mail-Adresse in Datenlecks",
        "what": "Ihre {email} ist in {breach_count} Datenlecks gefunden. Auch ohne Klartext-Passwort liefert das Angreifern wertvolles Material für gezieltes Phishing.",
    },

    # ─── ADMIN PANELS ────────────────────────────────────────────────

    "admin:phpmyadmin": {
        "short": "phpMyAdmin offen im Web",
        "what": "Ihr Datenbank-Verwaltungstool phpMyAdmin ist ohne IP-Beschränkung aus dem Internet erreichbar — ein erfolgreicher Login bedeutet sofortigen Vollzugriff auf Ihre Geschäftsdaten.",
    },
    "admin:adminer": {
        "short": "Adminer offen im Web",
        "what": "Ihr Adminer-Datenbankzugang ist öffentlich erreichbar — direkter Brute-Force-Pfad zu Ihren Datenbanken.",
    },
    "admin:cpanel": {
        "short": "cPanel offen im Web",
        "what": "Ihr cPanel-Server-Management ist ohne IP-Beschränkung aus dem Internet aufrufbar — Brute-Force gegen Ihren Admin-Account läuft vermutlich bereits.",
    },
    "admin:plesk": {
        "short": "Plesk offen im Web",
        "what": "Ihr Plesk-Server-Management ist öffentlich erreichbar — Angreifer können versuchen, Zugangsdaten zu erraten oder bekannte Schwachstellen auszunutzen.",
    },
    "admin:webmail": {
        "short": "Webmail offen im Web",
        "what": "Ihr Webmail-Login ist ohne IP-Beschränkung über das Internet erreichbar — bei sensiblen Geschäfts-E-Mails ein priorisiertes Brute-Force-Ziel.",
    },
    "admin:wordpress": {
        "short": "WordPress-Login öffentlich",
        "what": "Ihre WordPress-Login-Seite ist ohne IP-Beschränkung erreichbar — priorisiertes Brute-Force-Ziel mit täglich tausenden automatisierten Angriffsversuchen.",
    },
    "admin:typo3": {
        "short": "TYPO3-Admin offen im Web",
        "what": "Ihr TYPO3-Backend ist ohne IP-Beschränkung aus dem Internet erreichbar — bei nicht aktueller Version ein priorisiertes Ziel für automatisierte Brute-Force-Angriffe.",
    },
    "admin:joomla": {
        "short": "Joomla-Admin offen im Web",
        "what": "Ihr Joomla-Administrationsbereich ist öffentlich erreichbar — historisch eines der meistattackierten CMS-Backends.",
    },
    "admin:drupal": {
        "short": "Drupal-Admin offen im Web",
        "what": "Ihr Drupal-Administrationsbereich ist öffentlich erreichbar — ohne IP-Beschränkung ein dauerhaft aktives Brute-Force-Ziel.",
    },

    # ─── TLS ─────────────────────────────────────────────────────────

    "tls:tls10": {
        "short": "Verschlüsselung TLS 1.0 aktiv",
        "what": "Ihr Webserver akzeptiert noch TLS 1.0 — eine Verschlüsselung, die seit 2020 als gebrochen klassifiziert ist (POODLE- und BEAST-Angriffe). Eine Cyber-Versicherung kann an dieser Stelle die Schadensregulierung verweigern.",
    },
    "tls:tls11": {
        "short": "Veraltete TLS 1.1 aktiv",
        "what": "Ihr Server unterstützt TLS 1.1, das seit 2020 offiziell veraltet ist — alle modernen Browser haben es bereits deaktiviert.",
    },

    # ─── SOURCE MAPS ─────────────────────────────────────────────────

    "srcmap:exposed": {
        "short": "Quellcode öffentlich abrufbar",
        "what": "Eine JavaScript-Source-Map ist öffentlich abrufbar ({bytes} Bytes Original-Quellcode) — Angreifer haben Ihren ungekürzten Code zum gezielten Schwachstellen-Suchen.",
    },

    # ─── GOOGLE DORKING ──────────────────────────────────────────────

    "dork:confidential_pdfs": {
        "short": "Vertrauliche PDFs indexiert",
        "what": "{count} als 'vertraulich', 'intern' oder 'confidential' markierte PDFs sind in Google-Suchergebnissen abrufbar — bei Mandantenvertraulichkeit ein direkter Reputationsschaden.",
    },
    "dork:excel": {
        "short": "Excel-Dateien indexiert",
        "what": "Excel-Dateien Ihres Unternehmens sind in Google-Suchergebnissen abrufbar — Tabellenkalkulationen enthalten häufig interne Zahlen und Kundendaten.",
    },
    "dork:admin_indexed": {
        "short": "Admin-Panel in Google",
        "what": "Ihr Admin-Bereich ist in Google indexiert — Angreifer finden ihn nicht durch Raten, sondern durch eine einfache Google-Suche.",
    },
    "dork:cicd_indexed": {
        "short": "CI/CD-Pfade in Google",
        "what": "Ihre CI/CD-Oberfläche ist in Google-Suchergebnissen abrufbar — Angreifer müssen sie nicht finden, nur nachschlagen.",
    },
    "dork:devtools_indexed": {
        "short": "Entwicklungstools in Google",
        "what": "Interne Entwicklungstools sind in Google-Suchergebnissen abrufbar — das verrät Systemarchitektur und zieht gezielte Angriffe an.",
    },

    # ─── SUBDOMAINS ──────────────────────────────────────────────────

    "sub:database": {
        "short": "Datenbank-Subdomains exponiert",
        "what": "Mehrere Subdomains weisen auf öffentlich erreichbare Datenbankdienste hin (db, mysql, postgres, mongo, redis) — jede davon ist ein eigenständiges Angriffsziel.",
    },
    "sub:admin": {
        "short": "Admin-Subdomains exponiert",
        "what": "Mehrere Admin-Panel-Subdomains sind öffentlich auflösbar (admin, administrator, panel, plesk, cpanel) — Brute-Force-Ziele mit erweitertem Privilegien-Kontext.",
    },
    "sub:staging": {
        "short": "Staging-Umgebung exponiert",
        "what": "Ihre Staging-Umgebung ist öffentlich auflösbar und damit angreifbar — Staging-Systeme enthalten häufig schwächere Zugangsdaten und Debug-Informationen.",
    },

    # ─── TECH FINGERPRINT ────────────────────────────────────────────

    "tech:outdated": {
        "short": "Veraltete Software erkannt",
        "what": "Auf Ihrem Server läuft {version} — eine Version, die keine Sicherheitsupdates mehr erhält. Angreifer nutzen bekannte Schwachstellen in alten Versionen aktiv aus.",
    },

    # ─── GITHUB (only real, post-filter findings) ────────────────────

    "github:private_key": {
        "short": "Private Key auf GitHub",
        "what": "Ein privater Schlüssel mit Bezug zu Ihrem Unternehmen liegt in einem öffentlichen GitHub-Repository — Private Keys ermöglichen die vollständige Übernahme der betroffenen Systeme.",
    },
    "github:api_key": {
        "short": "API-Key auf GitHub exponiert",
        "what": "Ein API-Schlüssel mit Bezug zu Ihrem Unternehmen liegt in einem öffentlichen GitHub-Repository — er ermöglicht unbefugten Zugriff auf die verbundenen Dienste.",
    },
    "github:db_creds": {
        "short": "Datenbank-Passwort auf GitHub",
        "what": "Datenbank-Zugangsdaten mit Bezug zu Ihrem Unternehmen liegen in einem öffentlichen GitHub-Repository — direkter Datenbankzugriff für jeden.",
    },
    "github:aws_key": {
        "short": "AWS-Zugangsdaten auf GitHub",
        "what": "AWS-Zugangsdaten mit Bezug zu Ihrem Unternehmen liegen in einem öffentlichen GitHub-Repository — AWS-Keys ermöglichen vollen Zugriff auf Cloud-Ressourcen.",
    },
    "github:password": {
        "short": "Passwort auf GitHub exponiert",
        "what": "Ein Passwort mit Bezug zu Ihrem Unternehmen liegt in einem öffentlichen GitHub-Repository — direkter Einstiegspunkt für jeden, der die Referenz findet.",
    },
}
