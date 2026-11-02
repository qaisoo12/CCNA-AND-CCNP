# 🌐 CCNA / CCNP Networking Tutor

A chat app for discussing Cisco networking. Pick your level (CCNA or CCNP Enterprise) and a mode, then ask questions.

**Modes**
- **Discuss / Explain:** clear explanations with examples
- **Quiz me:** one multiple-choice exam-style question at a time, with explanations
- **Config & CLI help:** IOS/IOS-XE commands plus the `show` commands to verify them
- **Troubleshooting:** step-by-step, layer-by-layer problem solving

It keeps the conversation context, so you can ask follow-ups, and you can download the chat as Markdown.

Built with [Streamlit](https://streamlit.io) and the Google Gemini Flash model (`google-genai` SDK).

## Files

```
.
├── app.py            # Streamlit app
├── requirements.txt  # Python dependencies
└── README.md
```

## Run locally

1. Get a free Gemini API key at <https://aistudio.google.com/apikey>.
2. Install dependencies (Python 3.10+):
   ```bash
   pip install -r requirements.txt
   ```
3. Give the app your key in one of these ways:
   - Paste it into the sidebar while the app runs, or
   - Set an environment variable: `export GEMINI_API_KEY="your-key"` (Windows PowerShell: `$env:GEMINI_API_KEY="your-key"`), or
   - Create `.streamlit/secrets.toml` with `GEMINI_API_KEY = "your-key"`
4. Run:
   ```bash
   streamlit run app.py
   ```

## Change the model

Default is `gemini-2.5-flash`. Type another Gemini Flash model name in the sidebar, or change `DEFAULT_MODEL` in `app.py`. Current names: <https://ai.google.dev/gemini-api/docs/models>.

## Push to GitHub (website only)

1. Sign in at <https://github.com>, click **+** (top right) → **New repository**.
2. Name it (for example `ccna-ccnp-tutor`), choose **Public**, click **Create repository**.
3. Click **uploading an existing file**, drag in `app.py`, `requirements.txt` and `README.md`.
4. Add a commit message such as `Initial commit` and click **Commit changes**.

> Never upload your API key or a `secrets.toml` file.

## Deploy on Streamlit Community Cloud

1. Go to <https://share.streamlit.io> and sign in with GitHub.
2. Click **Create app** → deploy from GitHub.
3. Select your repository, branch `main`, main file `app.py`.
4. Open **Advanced settings → Secrets** and add:
   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   ```
5. Click **Deploy**. After a couple of minutes you get a public `*.streamlit.app` link. Later edits on GitHub redeploy automatically.

> With your key in Secrets, anyone using the public link uses your Gemini quota. To avoid that, skip the secret and let visitors paste their own key in the sidebar.

## Limitations

- AI answers can contain mistakes, especially on exact command syntax or version-specific behaviour. Verify in the Cisco documentation or a lab (Packet Tracer, CML, GNS3).
- Exam blueprints change. Always check the current one on cisco.com.
- Only the last 20 messages are sent to the model to keep requests small.
