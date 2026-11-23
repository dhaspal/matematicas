export async function api(path, options = {}) {
  const apiUrl = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
  const respuesta = await fetch(`${apiUrl}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  if (!respuesta.ok) {
    let mensaje = "Ocurrió un error.";
    try {
      const cuerpo = await respuesta.json();
      mensaje = cuerpo.detail || cuerpo.message || mensaje;
    } catch {}
    throw new Error(typeof mensaje === "string" ? mensaje : "No se pudo completar la operación.");
  }
  return respuesta.json();
}
