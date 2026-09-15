# Themis Speaks — Setup Guide

A chatbot that answers questions about the FIA regulations, using Claude. Follow these
steps in order — no coding experience needed.

## Step 1 — Get an Anthropic API key

1. Go to https://console.anthropic.com and sign up / log in.
2. Go to **Settings → API Keys** and click **Create Key**.
3. Copy the key (starts with `sk-ant-...`) and save it somewhere safe — you won't be able to see it again.
4. Add a small amount of credit under **Settings → Billing** (a few dollars covers a lot of questions).

## Step 2 — Add your FIA PDF files

1. Put your FIA regulation PDFs (Sporting Regs, Technical Regs, etc.) into the `docs/` folder
   in this project.
2. Delete the `PUT_YOUR_FIA_PDFS_HERE.txt` placeholder file once you've added them.

## Step 3 — Put this project on GitHub

1. Go to https://github.com and sign up / log in (free).
2. Click the **+** icon (top right) → **New repository**.
3. Name it `themis-speaks`, keep it **Public** or **Private** (either works), click **Create repository**.
4. On the new repo page, click **uploading an existing file**.
5. Drag in every file and folder from this project (`app.py`, `requirements.txt`, `.gitignore`,
   the `docs/` folder with your PDFs, and the `.streamlit` folder — but NOT the `secrets.toml.example`
   file, you don't need it on GitHub).
6. Click **Commit changes**.

## Step 4 — Deploy to Streamlit Community Cloud (free)

1. Go to https://share.streamlit.io and sign up / log in with your GitHub account.
2. Click **Create app** → **From existing repo**.
3. Choose your `themis-speaks` repo, branch `main`, and set the main file path to `app.py`.
4. Before clicking Deploy, click **Advanced settings** and paste this into the **Secrets** box:
   ```
   ANTHROPIC_API_KEY = "sk-ant-your-real-key-here"
   ```
   (use the real key you copied in Step 1)
5. Click **Deploy**. Wait 1–2 minutes.
6. You'll get a public URL like `https://themis-speaks.streamlit.app` — this is your live chatbot.
   Share this link with anyone you want to have access.

## Updating the regulations later

Whenever the FIA publishes updated regs: go to your GitHub repo, open the `docs/` folder,
delete the old PDF and upload the new one (or just add a new PDF alongside it), commit the
change — Streamlit will automatically redeploy with the new documents.

## Notes & limits

- This app currently gives Claude the **full text** of your PDFs as context for every question.
  This works great for a reasonable set of regulations (a few hundred pages). If you load in
  *everything* FIA has ever published across every series, you may hit context limits — the app
  will warn you in the sidebar if a file gets skipped for space.
- Anyone with the app link can use it and each question costs a small amount of API credit
  (a few cents at most). If you're sharing it widely, keep an eye on usage in the Anthropic
  console.
- If you ever want to make it private, Streamlit Community Cloud has a viewer-access option
  under app settings.
