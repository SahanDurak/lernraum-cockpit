import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import App from "./App.tsx";

describe("App", () => {
  it("shows ok when the API is healthy", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(Response.json({ status: "ok" })),
    );
    render(<App />);
    expect(await screen.findByText("API: ok")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith("/api/health");
  });

  it("shows error when the API is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("network")));
    render(<App />);
    expect(await screen.findByText("API: error")).toBeInTheDocument();
  });

  it("shows error when the API answers with an HTTP error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(null, { status: 500 })),
    );
    render(<App />);
    expect(await screen.findByText("API: error")).toBeInTheDocument();
  });
});
