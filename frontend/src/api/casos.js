const apiUrl = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

async function request(path, options = {}) {
  const response = await fetch(`${apiUrl}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const body = await response.json().catch(() => ({ detail: "Ocurrió un error." }));
  if (!response.ok) throw new Error(body.detail || "No se pudo completar la operación.");
  return body;
}

export const casosApi = {
  generar: (dificultad, seed) => {
    const params = new URLSearchParams({ dificultad });
    if (seed) params.set("seed", seed);
    return request(`/api/casos/generar?${params}`);
  },
  verificar: (payload) => request("/api/casos/verificar-prueba", { method: "POST", body: JSON.stringify(payload) }),
  pista: (params) => request(`/api/casos/pista?${new URLSearchParams(params)}`),
  acusar: (payload) => request("/api/casos/acusar", { method: "POST", body: JSON.stringify(payload) }),
};
