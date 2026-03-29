import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Integrations from "@/components/Integrations";

// Mock framer-motion to avoid animation issues in tests
vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    p: ({ children, ...props }: any) => <p {...props}>{children}</p>,
  },
}));

describe("Integrations", () => {
  it("renders all 16 integration cards", () => {
    render(<Integrations />);
    expect(screen.getByText("E-Mail (IMAP/SMTP)")).toBeInTheDocument();
    expect(screen.getByText("Slack")).toBeInTheDocument();
    expect(screen.getByText("Microsoft Teams")).toBeInTheDocument();
    expect(screen.getByText("WhatsApp")).toBeInTheDocument();
    expect(screen.getByText("Google Workspace")).toBeInTheDocument();
    expect(screen.getByText("Microsoft 365")).toBeInTheDocument();
    expect(screen.getByText("Notion")).toBeInTheDocument();
    expect(screen.getByText("n8n / Make")).toBeInTheDocument();
    expect(screen.getByText("DATEV")).toBeInTheDocument();
    expect(screen.getByText("sevDesk")).toBeInTheDocument();
    expect(screen.getByText("lexoffice")).toBeInTheDocument();
    expect(screen.getByText("Personio")).toBeInTheDocument();
    expect(screen.getByText("HubSpot")).toBeInTheDocument();
    expect(screen.getByText("Salesforce")).toBeInTheDocument();
    expect(screen.getByText("Zendesk")).toBeInTheDocument();
    expect(screen.getByText("Und 20+ weitere")).toBeInTheDocument();
  });

  it("renders the section headline and subtitle", () => {
    render(<Integrations />);
    expect(screen.getByText("Funktioniert mit deinen bestehenden Tools.")).toBeInTheDocument();
    expect(screen.getByText(/Kengo verbindet sich mit den Systemen/)).toBeInTheDocument();
  });

  it("renders the 48h integration note", () => {
    render(<Integrations />);
    expect(screen.getByText(/wir bauen sie in 48 Stunden/)).toBeInTheDocument();
  });
});
