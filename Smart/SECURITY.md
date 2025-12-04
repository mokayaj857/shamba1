# Security and Secrets Management for SACP (Smart Agricultural Connectivity Planner)

This document explains how to securely manage API keys and other secrets for the `Smart/` Streamlit app.

## 1) Immediate actions (REQUIRED)
- **Rotate the exposed key now.** The key that was previously stored in `Smart/.env` has been removed from the workspace. You must revoke it from your API provider dashboard (OpenAI / AIMLAPI) and create a new key.

## 2) Local development
1. Copy the example file and add your real key locally (never commit it):

```bash
cp Smart/.env.example Smart/.env
# then edit Smart/.env and set AIMLAPI_KEY
```

2. The app uses `python-dotenv` (see `Smart/utils/aiml_integration.py`) to load `AIMLAPI_KEY` from the environment when present.

3. To run locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r Smart/requirements.txt
cd Smart
streamlit run app.py
```

## 3) Streamlit Community Cloud (recommended for hosting)
- Do NOT add `.env` to the repo. Use Streamlit Cloud's Secrets manager:
  1. Open your app on Streamlit Cloud.
  2. Go to **Settings → Secrets**.
  3. Add a secret with the key `AIMLAPI_KEY` and the new API key as the value.
  4. Deploy — the app will access the secret via `os.getenv("AIMLAPI_KEY")`.

## 4) GitHub Actions / CI
- Store secrets in the repository or organization Secrets (Settings → Secrets → Actions).
- Example: set `AIMLAPI_KEY` in repo secrets, then reference in workflow:

```yaml
env:
  AIMLAPI_KEY: ${{ secrets.AIMLAPI_KEY }}

steps:
  - name: Run app tests or deploy
    run: |
      echo "Using AIMLAPI_KEY: $AIMLAPI_KEY"
```

## 5) Why rotate keys and best practices
- If a secret is ever posted publicly (even briefly), rotate/revoke it immediately and create a new one.
- Use short-lived keys when supported and limit scopes/permissions.
- Use platform secret stores (Streamlit Secrets, GitHub Secrets, AWS Secrets Manager, Azure Key Vault) for production.

## 6) Keep secrets out of Git history
- If you accidentally committed a secret, simply deleting the file is not enough — you'll need to purge it from git history (e.g., `git filter-branch` or [BFG Repo-Cleaner]). After purging, rotate the secret.

## 7) Contact
- If you want, I can add a GitHub Actions snippet to automatically fail PRs that include `.env` or secrets (pre-commit / CI) — tell me and I will add it.
