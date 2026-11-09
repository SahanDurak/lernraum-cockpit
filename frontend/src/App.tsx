import { useEffect, useState } from "react";

type ApiStatus = "loading" | "ok" | "error";

export default function App() {
  const [status, setStatus] = useState<ApiStatus>("loading");

  useEffect(() => {
    fetch("/api/health")
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then((body: { status: string }) =>
        setStatus(body.status === "ok" ? "ok" : "error"),
      )
      .catch(() => setStatus("error"));
  }, []);

  return (
    <main className="mx-auto max-w-xl p-6">
      <h1 className="text-2xl font-bold">Lernraum Cockpit</h1>
      <p className="mt-2 text-gray-600">API: {status}</p>
    </main>
  );
}
