import { useEffect, useState } from "react";
import * as api from "./api.js";

const TABS = [
  { id: "nutrition", icon: "🥗", label: "Food & Nutrition", desc: "Khane ki photo upload karo, calories aur nutrition pao.", accept: "image/*" },
  { id: "freshness", icon: "🍅", label: "Freshness Detection", desc: "Fruit/sabzi/food ki photo se freshness aur spoilage check karo.", accept: "image/*" },
  { id: "hygiene", icon: "🧼", label: "Hygiene Monitor", desc: "Kitchen/restaurant ki photo ya video se hygiene audit karo.", accept: "image/*,video/*" },
  { id: "cooking", icon: "👩‍🍳", label: "Smart Cooking" },
  { id: "mealplan", icon: "📅", label: "Meal Planner" },
  { id: "history", icon: "🕘", label: "History" },
];

const pretty = (k) => k.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

/* Generic recursive renderer for any JSON result */
function Value({ v }) {
  if (v === null || v === undefined) return <span className="muted">—</span>;
  if (typeof v === "boolean") return <span className={v ? "pill ok" : "pill bad"}>{v ? "Yes" : "No"}</span>;
  if (typeof v === "number" || typeof v === "string") return <span>{String(v)}</span>;
  if (Array.isArray(v)) {
    if (!v.length) return <span className="muted">None</span>;
    if (v.every((x) => typeof x !== "object")) return <ul>{v.map((x, i) => <li key={i}>{String(x)}</li>)}</ul>;
    return <div className="cards">{v.map((x, i) => <div className="mini" key={i}><Value v={x} /></div>)}</div>;
  }
  return (
    <dl>
      {Object.entries(v).filter(([k]) => !k.startsWith("_")).map(([k, val]) => (
        <div className="row" key={k}><dt>{pretty(k)}</dt><dd><Value v={val} /></dd></div>
      ))}
    </dl>
  );
}

function Result({ data }) {
  if (!data) return null;
  const score = data.hygiene_score ?? data.freshness_score;
  return (
    <div className="result">
      {data._demo && <div className="banner">⚠️ DEMO MODE: sample output dikh raha hai. Real AI ke liye backend/.env me GEMINI_API_KEY daalo.</div>}
      {score !== undefined && (
        <div className="score"><div className="bar"><div style={{ width: `${Math.min(100, score)}%` }} /></div><b>{score}/100</b></div>
      )}
      <Value v={data} />
    </div>
  );
}

function Preview({ file }) {
  const [url, setUrl] = useState(null);
  useEffect(() => {
    if (!file) return setUrl(null);
    const u = URL.createObjectURL(file);
    setUrl(u);
    return () => URL.revokeObjectURL(u);
  }, [file]);
  if (!file || !url) return null;
  if (file.type.startsWith("video")) return <video src={url} controls className="preview" />;
  if (file.type.startsWith("audio")) return <audio src={url} controls />;
  return <img src={url} className="preview" alt="preview" />;
}

function useAction() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);
  const run = async (fn) => {
    setLoading(true); setError(""); setData(null);
    try { setData(await fn()); } catch (e) { setError(e.message); } finally { setLoading(false); }
  };
  return { loading, error, data, run };
}

function Status({ loading, error }) {
  return (<>{loading && <div className="loading"><span className="spinner" /> AI analyze kar raha hai...</div>}
    {error && <div className="error">❌ {error}</div>}</>);
}

function UploadPanel({ tab }) {
  const [file, setFile] = useState(null);
  const { loading, error, data, run } = useAction();
  useEffect(() => setFile(null), [tab.id]);
  return (
    <section>
      <p className="desc">{tab.desc}</p>
      <label className="drop">
        <input type="file" accept={tab.accept} onChange={(e) => setFile(e.target.files[0] || null)} />
        {file ? `📎 ${file.name}` : "Click karke file choose karo"}
      </label>
      <Preview file={file} />
      <button disabled={!file || loading} onClick={() => run(() => api.uploadFile(tab.id, file))}>Analyze</button>
      <Status loading={loading} error={error} />
      <Result data={data} />
    </section>
  );
}

function CookingPanel() {
  const [query, setQuery] = useState("");
  const [ingredients, setIngredients] = useState("");
  const [file, setFile] = useState(null);
  const { loading, error, data, run } = useAction();
  return (
    <section>
      <p className="desc">Ingredients likho, fridge ki photo do, ya apni awaaz (audio) upload karo. AI recipe aur steps dega.</p>
      <input placeholder="Kya banana hai? (e.g. quick dinner, high protein)" value={query} onChange={(e) => setQuery(e.target.value)} />
      <input placeholder="Ingredients (e.g. paneer, onion, tomato)" value={ingredients} onChange={(e) => setIngredients(e.target.value)} />
      <label className="drop">
        <input type="file" accept="image/*,audio/*" onChange={(e) => setFile(e.target.files[0] || null)} />
        {file ? `📎 ${file.name}` : "Optional: fridge photo ya audio query upload karo"}
      </label>
      <Preview file={file} />
      <button disabled={loading || (!query && !ingredients && !file)} onClick={() => run(() => api.cook({ query, ingredients, file }))}>Get Recipe</button>
      <Status loading={loading} error={error} />
      <Result data={data} />
    </section>
  );
}

function MealPlanPanel() {
  const [p, setP] = useState({ age: 22, gender: "male", weight: 65, height: 170, goal: "maintain weight", diet: "vegetarian", allergies: "", cuisine: "Indian", days: 3 });
  const { loading, error, data, run } = useAction();
  const set = (k) => (e) => setP({ ...p, [k]: e.target.value });
  const num = (k) => (e) => setP({ ...p, [k]: Number(e.target.value) });
  return (
    <section>
      <p className="desc">Apni details bharo, personalised meal plan milega.</p>
      <div className="grid">
        <label>Age<input type="number" value={p.age} onChange={num("age")} /></label>
        <label>Gender<select value={p.gender} onChange={set("gender")}><option>male</option><option>female</option><option>other</option></select></label>
        <label>Weight (kg)<input type="number" value={p.weight} onChange={num("weight")} /></label>
        <label>Height (cm)<input type="number" value={p.height} onChange={num("height")} /></label>
        <label>Goal<select value={p.goal} onChange={set("goal")}><option>lose weight</option><option>maintain weight</option><option>gain muscle</option></select></label>
        <label>Diet<select value={p.diet} onChange={set("diet")}><option>vegetarian</option><option>vegan</option><option>non-vegetarian</option><option>eggetarian</option></select></label>
        <label>Allergies<input value={p.allergies} onChange={set("allergies")} placeholder="peanuts, dairy..." /></label>
        <label>Cuisine<input value={p.cuisine} onChange={set("cuisine")} /></label>
        <label>Days<input type="number" min="1" max="7" value={p.days} onChange={num("days")} /></label>
      </div>
      <button disabled={loading} onClick={() => run(() => api.mealPlan(p))}>Generate Plan</button>
      <Status loading={loading} error={error} />
      <Result data={data} />
    </section>
  );
}

function HistoryPanel() {
  const [items, setItems] = useState([]);
  const load = () => api.getHistory().then(setItems).catch(() => {});
  useEffect(() => { load(); }, []);
  return (
    <section>
      <p className="desc">Aapke saare pichhle analysis (SQLite database me store).</p>
      {!items.length && <p className="muted">Abhi koi history nahi hai.</p>}
      {items.map((h) => (
        <details key={h.id} className="hist">
          <summary>
            <b>{h.kind}</b> · {h.input_name} <span className="muted">· {h.created_at}</span>
            <button className="small" onClick={(e) => { e.preventDefault(); api.deleteHistory(h.id).then(load); }}>Delete</button>
          </summary>
          <Result data={h.result} />
        </details>
      ))}
    </section>
  );
}

export default function App() {
  const [tabId, setTabId] = useState("nutrition");
  const [health, setHealth] = useState(null);
  useEffect(() => { api.getHealth().then(setHealth).catch(() => setHealth({ offline: true })); }, []);
  const tab = TABS.find((t) => t.id === tabId);
  return (
    <div className="app">
      <header>
        <h1>🍽️ FoodVerse AI</h1>
        <p>Multimodal Food Intelligence Agent</p>
        {health?.offline && <div className="error">Backend chalu nahi hai. backend folder me `uvicorn main:app --reload` run karo.</div>}
        {health?.demo_mode && <span className="pill bad">DEMO MODE</span>}
        {health && !health.demo_mode && !health.offline && <span className="pill ok">Gemini connected</span>}
      </header>
      <nav>{TABS.map((t) => (
        <button key={t.id} className={t.id === tabId ? "tab active" : "tab"} onClick={() => setTabId(t.id)}>{t.icon} {t.label}</button>
      ))}</nav>
      <main>
        {["nutrition", "freshness", "hygiene"].includes(tabId) && <UploadPanel tab={tab} key={tabId} />}
        {tabId === "cooking" && <CookingPanel />}
        {tabId === "mealplan" && <MealPlanPanel />}
        {tabId === "history" && <HistoryPanel />}
      </main>
    </div>
  );
}
