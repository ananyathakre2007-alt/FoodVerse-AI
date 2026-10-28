import os, json, re
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DEMO = not API_KEY

_client = None
if not DEMO:
    from google import genai
    from google.genai import types
    _client = genai.Client(api_key=API_KEY)

SYSTEM = ("You are FoodVerse AI, a careful food intelligence assistant. "
          "Be honest about uncertainty, give confidence scores, and never present estimates as medical advice. "
          "Return ONLY valid JSON, no markdown.")

def _parse(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            return json.loads(m.group(0))
        return {"raw_response": text}

def run(kind, prompt, files=None):
    """files: list of (bytes, mime_type). Returns dict."""
    if DEMO:
        return {**DEMO_DATA.get(kind, {}), "_demo": True}
    parts = [types.Part.from_bytes(data=b, mime_type=m) for b, m in (files or [])]
    parts.append(prompt)
    resp = _client.models.generate_content(
        model=MODEL, contents=parts,
        config=types.GenerateContentConfig(system_instruction=SYSTEM,
                                           response_mime_type="application/json",
                                           temperature=0.3))
    return _parse(resp.text)

# ---------- Prompts ----------
def nutrition_prompt():
    return """Analyze the food in this image. Return JSON:
{"foods":[{"name":str,"portion_estimate":str,"calories":number,"protein_g":number,"carbs_g":number,"fat_g":number,"fiber_g":number}],
"total":{"calories":number,"protein_g":number,"carbs_g":number,"fat_g":number},
"health_score":number(0-10),"healthier_swaps":[str],"confidence":number(0-1),"notes":str}"""

def freshness_prompt():
    return """Inspect the food item(s) in this image for freshness/spoilage (color, mold, texture, bruising, slime, dryness).
Return JSON:
{"item":str,"freshness_status":"Fresh|Moderately Fresh|Going Bad|Spoiled","freshness_score":number(0-100),
"visual_indicators":[str],"estimated_shelf_life":str,"storage_tips":[str],"safe_to_eat":boolean,
"confidence":number(0-1),"disclaimer":"Visual estimate only; when in doubt, throw it out."}"""

def hygiene_prompt():
    return """You are a food-safety inspector. Review this kitchen/restaurant image or video for hygiene practices:
gloves, hairnets, aprons, clean surfaces, raw/cooked separation, pests, waste handling, handwashing, uniforms.
Return JSON:
{"hygiene_score":number(0-100),"rating":"Excellent|Good|Needs Improvement|Poor",
"compliant_practices":[str],"violations":[{"issue":str,"severity":"Low|Medium|High","recommendation":str}],
"summary":str,"confidence":number(0-1)}"""

def cooking_prompt(query, ingredients):
    return f"""The user wants cooking help. Query: "{query or 'Suggest what I can cook'}". Available ingredients: "{ingredients or 'unknown - detect from attached image/audio if any'}".
If audio is attached, treat it as the spoken query. If an image is attached, identify ingredients from it.
Return JSON:
{{"detected_ingredients":[str],"dish_name":str,"cuisine":str,"prep_time_min":number,"cook_time_min":number,"servings":number,
"ingredients":[{{"item":str,"quantity":str}}],"steps":[str],"tips":[str],"missing_ingredients":[str],"substitutions":[str],
"approx_calories_per_serving":number}}"""

def mealplan_prompt(p):
    return f"""Create a {p.get('days',3)}-day personalised meal plan for: age {p.get('age')}, gender {p.get('gender')},
weight {p.get('weight')} kg, height {p.get('height')} cm, goal: {p.get('goal')}, diet: {p.get('diet')}, allergies: {p.get('allergies') or 'none'},
cuisine preference: {p.get('cuisine') or 'Indian'}. Return JSON:
{{"daily_calorie_target":number,"macro_split":{{"protein_pct":number,"carbs_pct":number,"fat_pct":number}},
"plan":[{{"day":number,"meals":[{{"meal":"Breakfast|Lunch|Snack|Dinner","dish":str,"calories":number,"protein_g":number}}],"day_total_calories":number}}],
"grocery_list":[str],"hydration_tip":str,"note":"General guidance, not medical advice."}}"""

# ---------- Demo data (API key na ho to) ----------
DEMO_DATA = {
 "nutrition": {"foods":[{"name":"Dal Tadka","portion_estimate":"1 bowl (200g)","calories":180,"protein_g":9,"carbs_g":25,"fat_g":5,"fiber_g":6},
   {"name":"Steamed Rice","portion_estimate":"1 cup","calories":205,"protein_g":4,"carbs_g":45,"fat_g":0.4,"fiber_g":0.6}],
   "total":{"calories":385,"protein_g":13,"carbs_g":70,"fat_g":5.4},"health_score":7.5,
   "healthier_swaps":["Swap white rice for brown rice","Add a side salad"],"confidence":0.8,"notes":"Demo data - add GEMINI_API_KEY for real analysis."},
 "freshness": {"item":"Tomato","freshness_status":"Moderately Fresh","freshness_score":68,"visual_indicators":["Slight wrinkling","No mold"],
   "estimated_shelf_life":"2-3 more days","storage_tips":["Keep at room temperature away from sunlight"],"safe_to_eat":True,"confidence":0.75,
   "disclaimer":"Visual estimate only; when in doubt, throw it out."},
 "hygiene": {"hygiene_score":72,"rating":"Good","compliant_practices":["Clean work surfaces","Staff wearing aprons"],
   "violations":[{"issue":"No hairnet visible","severity":"Medium","recommendation":"Mandate hair covering in prep area"}],
   "summary":"Demo result - add GEMINI_API_KEY for real inspection.","confidence":0.7},
 "cooking": {"detected_ingredients":["Paneer","Capsicum","Onion"],"dish_name":"Paneer Capsicum Sabzi","cuisine":"Indian","prep_time_min":10,"cook_time_min":15,"servings":2,
   "ingredients":[{"item":"Paneer","quantity":"200g"},{"item":"Capsicum","quantity":"1"},{"item":"Onion","quantity":"1"}],
   "steps":["Saute onion till golden","Add capsicum and spices","Add paneer cubes and cook 3 min"],"tips":["Soak paneer in warm water for softness"],
   "missing_ingredients":[],"substitutions":["Tofu for paneer"],"approx_calories_per_serving":290},
 "mealplan": {"daily_calorie_target":2000,"macro_split":{"protein_pct":25,"carbs_pct":50,"fat_pct":25},
   "plan":[{"day":1,"meals":[{"meal":"Breakfast","dish":"Moong dal chilla","calories":350,"protein_g":18},
   {"meal":"Lunch","dish":"Roti, dal, sabzi, salad","calories":600,"protein_g":25},{"meal":"Dinner","dish":"Paneer bhurji with roti","calories":550,"protein_g":28}],"day_total_calories":1500}],
   "grocery_list":["Moong dal","Paneer","Atta"],"hydration_tip":"Drink 2.5-3L water daily","note":"General guidance, not medical advice. (Demo data)"},
}
