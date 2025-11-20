# streamlit_app.py
"""
Streamlit app — Soil Trafficability & Compaction Advisor (AgriProfessor persona)
Deterministic, rule-based assessment using the thresholds provided.
Run on Streamlit Community Cloud (or locally with `streamlit run streamlit_app.py`).
"""

import streamlit as st

st.set_page_config(page_title="Trafficability Advisor", layout="wide")
st.title("AgriProfessor — Soil Trafficability & Compaction Advisor")
st.markdown(
    "Enter field measurements (BD, CI, SMD, tire pressure, wheel load, rut depth) for a "
    "scientifically grounded assessment and clear practical recommendations."
)

# ---------- Utility functions ----------
def parse_float(x):
    try:
        return float(x)
    except Exception:
        return None

def interpret_bulk_density(bd):
    if bd is None:
        return "Unknown", "No bulk density provided."
    if bd > 1.43:
        return "High", f"BD = {bd:.2f} Mg m⁻³ — exceeds critical ~1.43 (loamy soils): high compaction risk."
    if bd > 1.30:
        return "Moderate", f"BD = {bd:.2f} Mg m⁻³ (1.30–1.43): moderate compaction risk; watch root restriction."
    return "Low", f"BD = {bd:.2f} Mg m⁻³ — within normal range (1.0–1.4)."

def interpret_cone_index(ci):
    if ci is None:
        return "Unknown", "No cone index provided."
    if ci >= 3.0:
        return "Very High", f"CI = {ci:.2f} MPa — near-zero root growth (severe mechanical impedance)."
    if ci >= 1.5:
        return "High", f"CI = {ci:.2f} MPa — ~50% root growth reduction expected."
    if ci >= 0.8:
        return "Moderate", f"CI = {ci:.2f} MPa — approaching common trafficability limits (0.8–1.43 MPa)."
    return "Low", f"CI = {ci:.2f} MPa — generally permissive for root penetration."

def interpret_moisture(smd, moisture_cat):
    # Prefer numeric SMD if provided
    if smd is not None:
        if smd >= 10:
            return "Favourable", f"SMD = +{smd:.1f} mm: drier conditions favourable for traffic."
        if smd >= 0:
            return "Marginal", f"SMD = +{smd:.1f} mm: marginal trafficability."
        return "Poor", f"SMD = {smd:.1f} mm: soil likely wet or near field capacity — high compaction risk."
    # Categorical fallback
    if moisture_cat in ("dry", "moderate"):
        return "Favourable", f"Moisture: {moisture_cat} — relatively safe for operations."
    if moisture_cat in ("near_field_capacity", "wet"):
        return "Poor", f"Moisture: {moisture_cat} — avoid traffic; high compaction risk."
    return "Unknown", "No moisture data provided."

def interpret_tire_and_load(tp_kpa, wheel_load_kg):
    reasons = []
    if tp_kpa is not None and tp_kpa > 50:
        reasons.append(f"Tire pressure {tp_kpa:.0f} kPa > 50 kPa (increases contact stress).")
    if wheel_load_kg is not None and wheel_load_kg >= 5000:
        reasons.append(f"Wheel load {wheel_load_kg:.0f} kg ≥ 5000 kg (increases subsoil compaction risk).")
    if not reasons:
        return "Low", "Tire pressure and wheel load within low-risk bounds."
    # decide level
    if any("≥ 5000" in r for r in reasons):
        return "High", " ".join(reasons)
    return "Moderate", " ".join(reasons)

def interpret_rut_depth(rut_cm):
    if rut_cm is None:
        return "Unknown", "No rut depth provided."
    if rut_cm > 10:
        return "High", f"Rut depth {rut_cm:.1f} cm > 10 cm — severe surface disturbance."
    if rut_cm > 3:
        return "Moderate", f"Rut depth {rut_cm:.1f} cm — noticeable surface deformation."
    return "Low", f"Rut depth {rut_cm:.1f} cm — negligible."

def aggregate_risk(levels):
    # Simple scoring map; tuned to prioritise any 'High' or 'Very High'
    score_map = {"Low":0, "Favourable":0, "Moderate":1, "Marginal":1, "High":2, "Very High":3, "Poor":2, "Unknown":0}
    total = sum(score_map.get(l, 0) for l in levels)
    if total >= 5:
        return "High"
    if total >= 2:
        return "Moderate"
    return "Low"

def recommendations(overall_level):
    if overall_level == "High":
        return [
            "Avoid field traffic until soil dries (aim SMD ≥ +10 mm) or BD/CI improve.",
            "Reduce tire pressure and/or reduce axle/wheel loads; use wide tires or tracks.",
            "Use Controlled Traffic Farming (confine compaction to fixed lanes).",
            "If persistent subsoil compaction is confirmed, consider deep ripping where agronomically appropriate."
        ]
    if overall_level == "Moderate":
        return [
            "Lower tire pressures and reduce loads where feasible.",
            "Schedule operations for drier windows; avoid repeated passes.",
            "Monitor BD and CI after operations; adjust tactics accordingly."
        ]
    return [
        "Field conditions acceptable for operations; continue routine monitoring of BD and CI.",
        "Practice best traffic management to avoid long-term compaction (CTF, wide tires)."
    ]

# ---------- UI: Measurement form ----------
st.header("Field assessment — provide measurements")
with st.form("measurement_form"):
    left, right = st.columns(2)
    with left:
        bd_input = st.text_input("Bulk density (Mg m⁻³) — e.g., 1.35", "")
        ci_input = st.text_input("Cone index (CI, MPa) — e.g., 1.2", "")
        smd_input = st.text_input("Soil Moisture Deficit (SMD, mm) — e.g., 12 (optional)", "")
    with right:
        moist_cat = st.selectbox("Moisture category (if SMD unknown)", ["", "dry", "moderate", "near_field_capacity", "wet"])
        tp_input = st.text_input("Tire pressure (kPa) — e.g., 60 (optional)", "")
        wl_input = st.text_input("Representative wheel load (kg) — e.g., 3000 (optional)", "")
        rut_input = st.text_input("Observed rut depth (cm) — e.g., 0 or 12", "")
    submitted = st.form_submit_button("Run assessment")

if submitted:
    # parse
    bd = parse_float(bd_input)
    ci = parse_float(ci_input)
    smd = parse_float(smd_input)
    tp = parse_float(tp_input)
    wl = parse_float(wl_input)
    rut = parse_float(rut_input)

    bd_level, bd_note = interpret_bulk_density(bd)
    ci_level, ci_note = interpret_cone_index(ci)
    moist_level, moist_note = interpret_moisture(smd, moist_cat)
    tire_level, tire_note = interpret_tire_and_load(tp, wl)
    rut_level, rut_note = interpret_rut_depth(rut)

    overall = aggregate_risk([bd_level, ci_level, moist_level, tire_level, rut_level])

    st.subheader(f"Overall compaction & trafficability risk: {overall}")
    st.markdown("**Contributing indicators and notes:**")
    st.write(f"- **Bulk density:** {bd_level} — {bd_note}")
    st.write(f"- **Cone index (CI):** {ci_level} — {ci_note}")
    st.write(f"- **Moisture/SMD:** {moist_level} — {moist_note}")
    st.write(f"- **Tire pressure & wheel load:** {tire_level} — {tire_note}")
    st.write(f"- **Rut depth:** {rut_level} — {rut_note}")

    st.markdown("**Recommended actions:**")
    for r in recommendations(overall):
        st.write("- " + r)

    st.info(
        "Thresholds used: BD normal 1.0–1.4 Mg m⁻³; critical ~1.43 Mg m⁻³ (loamy soils). "
        "CI approx. 0.8–1.43 MPa used for trafficability; 1.5 MPa ~50% root reduction; 3.0 MPa approximates near-zero root growth. "
        "Tire pressure >50 kPa and wheel loads ≥5000 kg increase compaction risk; rut depth >10 cm is severe."
    )

# ---------- Quick Q/A ----------
st.header("Quick definitions & thresholds (text input)")
query = st.text_input("Ask a short question (e.g., 'What BD is critical?', 'When is trafficability good?')", "")
if query:
    q = query.lower()
    if "trafficability" in q:
        st.write("Trafficability: capacity of land to support vehicle operations without causing significant soil degradation (compaction, rutting). Influenced by moisture, texture, and load.")
    elif "compaction" in q:
        st.write("Soil compaction: increase in bulk density and soil strength caused by applied stresses, reducing porosity, aeration and infiltration. Measured with bulk density and cone index.")
    elif "bulk density" in q or "bd" in q:
        st.write("Bulk density typical normal range: 1.0–1.4 Mg m⁻³. BD > 1.4 Mg m⁻³ indicates compaction; critical ~1.43 Mg m⁻³ for loam.")
    elif "cone index" in q or "ci" in q:
        st.write("Cone index (CI): 0.8–1.43 MPa used for critical trafficability; 1.5 MPa ≈ 50% root growth reduction; 3.0 MPa ≈ near-zero root penetration.")
    elif "smd" in q or "soil moisture deficit" in q:
        st.write("SMD: positive values (e.g., +10 mm) indicate drier conditions favourable for traffic. Wet soil at or above field capacity is high risk for compaction.")
    else:
        st.write("I provide definitions, thresholds, and deterministic assessments. For an assessment use the measurement form above.")
