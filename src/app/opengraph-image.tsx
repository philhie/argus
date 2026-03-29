import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Kengo — KI-Mitarbeiter für jede Abteilung";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "80px",
          backgroundColor: "#09090B",
          fontFamily: "system-ui, sans-serif",
        }}
      >
        {/* Subtle gradient glow */}
        <div
          style={{
            position: "absolute",
            top: "-20%",
            right: "-10%",
            width: "600px",
            height: "600px",
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%)",
          }}
        />

        {/* Logo */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            marginBottom: "48px",
          }}
        >
          <div
            style={{
              width: "40px",
              height: "40px",
              borderRadius: "10px",
              backgroundColor: "#3B82F6",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontSize: "20px",
              fontWeight: 700,
            }}
          >
            K
          </div>
          <span
            style={{
              fontSize: "24px",
              fontWeight: 600,
              color: "#FAFAFA",
              letterSpacing: "-0.02em",
            }}
          >
            kengo
          </span>
        </div>

        {/* Headline */}
        <div
          style={{
            fontSize: "64px",
            fontWeight: 700,
            color: "#FAFAFA",
            lineHeight: 1.1,
            letterSpacing: "-0.03em",
            marginBottom: "24px",
          }}
        >
          KI-Mitarbeiter für
          <br />
          jede Abteilung.
        </div>

        {/* Sub-headline */}
        <div
          style={{
            fontSize: "24px",
            color: "#A1A1AA",
            lineHeight: 1.5,
          }}
        >
          Ab €1.999/Monat · Einarbeitung in 5 Tagen · Gehostet in Deutschland
        </div>
      </div>
    ),
    { ...size }
  );
}
