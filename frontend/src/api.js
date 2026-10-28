async function handle(res) {
  if (!res.ok) {
    let msg = res.statusText;
    try { msg = (await res.json()).detail || msg; } catch {}
    throw new Error(msg);
  }
  return res.json();
}

export const getHealth = () => fetch("/api/health").then(handle);

export const uploadFile = (kind, file) => {
  const fd = new FormData();
  fd.append("file", file);
  return fetch(`/api/analyze/${kind}`, { method: "POST", body: fd }).then(handle);
};

export const cook = ({ query, ingredients, file }) => {
  const fd = new FormData();
  fd.append("query", query || "");
  fd.append("ingredients", ingredients || "");
  if (file) fd.append("file", file);
  return fetch("/api/cooking", { method: "POST", body: fd }).then(handle);
};

export const mealPlan = (profile) =>
  fetch("/api/meal-plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  }).then(handle);

export const getHistory = () => fetch("/api/history").then(handle);
export const deleteHistory = (id) => fetch(`/api/history/${id}`, { method: "DELETE" }).then(handle);
