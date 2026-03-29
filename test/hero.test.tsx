import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";

// Mock framer-motion
vi.mock("framer-motion", () => ({
  motion: {
    h1: ({ children, ...props }: any) => <h1>{children}</h1>,
    p: ({ children, ...props }: any) => <p>{children}</p>,
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    span: ({ children, ...props }: any) => <span>{children}</span>,
  },
}));

// Mock CascadeDemo
vi.mock("@/components/CascadeDemo", () => ({
  default: () => <div data-testid="cascade-demo">CascadeDemo</div>,
}));

import Hero from "@/components/Hero";

describe("Hero", () => {
  it("renders the headline text", () => {
    render(<Hero />);
    expect(screen.getByText("KI-Mitarbeiter.")).toBeInTheDocument();
    expect(screen.getByText("Abteilung.")).toBeInTheDocument();
  });

  it("renders both CTA buttons", () => {
    render(<Hero />);
    expect(screen.getByText("Demo vereinbaren")).toBeInTheDocument();
    expect(screen.getByText("Produkte entdecken")).toBeInTheDocument();
  });

  it("renders CascadeDemo in the right column", () => {
    render(<Hero />);
    expect(screen.getByTestId("cascade-demo")).toBeInTheDocument();
  });

  it("renders all trust bar items", () => {
    render(<Hero />);
    expect(screen.getByText("Gehostet in Deutschland")).toBeInTheDocument();
    expect(screen.getByText("DSGVO-konform")).toBeInTheDocument();
    expect(screen.getByText("5 Tage Einarbeitung")).toBeInTheDocument();
    expect(screen.getByText("Monatlich kündbar")).toBeInTheDocument();
  });
});
