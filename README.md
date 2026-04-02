# Secure Idea Verifier

A Streamlit app to verify and analyze idea novelty using similarity detection, domain classification, and simple local user authentication.

## Files included
- `app.py` - main Streamlit application
- `ideas_dataset.csv` - example idea dataset used for similarity and domain modeling
- `requirements.txt` - Python dependencies
- `.gitignore` - files to ignore when pushing to GitHub

## Setup locally

1. Install Python 3.10+.
2. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Windows cmd
.\.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
streamlit run app.py
```

## Push to GitHub

1. Create a new GitHub repository on github.com.
2. In this project folder, initialize Git and push:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## Deploy on Streamlit

1. Go to https://share.streamlit.io/
2. Sign in with GitHub.
3. Click **New app**.
4. Choose your repository, branch `main`, and set the file path to `app.py`.
5. Click **Deploy**.

## Notes

- `users.json` is excluded from GitHub so user accounts remain local and are created automatically.
- Keep `ideas_dataset.csv` in the repository because the app needs it to run.
- If you want, you can rename `app.py` to `streamlit_app.py` and update the Streamlit app path during deployment.
