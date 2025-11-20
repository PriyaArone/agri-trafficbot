# agri-trafficbot
# Persona Agri Trafficability Chatbot — Streamlit Cloud deployment

This repository contains a deterministic, rule-based Streamlit app that assesses soil trafficability and compaction risk using field measurements (bulk density, cone index, SMD, tire pressure, wheel load, rut depth).

## Files
- `streamlit_app.py` — Streamlit application (entrypoint).
- `requirements.txt` — dependencies for Streamlit Cloud.

## Deploy to Streamlit Community Cloud (steps)
1. Create a new GitHub repository and push these files to the `main` branch.
   ```bash
   git init
   git add .
   git commit -m "Initial commit — trafficability advisor"
   git branch -M main
   git remote add origin git@github.com:<your-username>/persona-agri-trafficbot.git
   git push -u origin main
