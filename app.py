import streamlit as st
import pandas as pd
import json
import os
import hashlib
from cryptography.fernet import Fernet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Secure Idea Verification Tool", page_icon="🛡️", layout="wide")

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
/* App background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b, #312e81);
    color: white;
}

/* Headings and text */
h1, h2, h3, h4, h5, h6, p, label, div, span {
    color: white !important;
}

/* Titles */
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: white !important;
}
.sub-title {
    text-align: center;
    font-size: 18px;
    color: #cbd5e1 !important;
    margin-bottom: 25px;
}

/* Cards */
.result-box {
    background-color: rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 18px;
    margin-bottom: 18px;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0px 4px 20px rgba(0,0,0,0.15);
}
.small-note {
    color: #cbd5e1 !important;
    font-size: 14px;
}
.example-box {
    background-color: rgba(255,255,255,0.06);
    padding: 12px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 8px;
}

/* TEXT INPUTS - BLACK */
input, textarea {
    background-color: #000000 !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid #444 !important;
    caret-color: white !important;
}

.stTextInput > div > div > input,
.stTextArea textarea,
.stPasswordInput > div > div > input {
    background-color: #000000 !important;
    color: white !important;
    border: 1px solid #444 !important;
    border-radius: 12px !important;
    caret-color: white !important;
}

/* Placeholder text */
input::placeholder, textarea::placeholder {
    color: #cbd5e1 !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95) !important;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* BLACK BUTTONS */
div.stButton > button {
    background: #000000 !important;
    color: white !important;
    border: 1px solid #444 !important;
    border-radius: 12px !important;
    padding: 0.6rem 1rem !important;
    font-weight: bold !important;
    font-size: 15px !important;
    width: 100% !important;
    opacity: 1 !important;
    visibility: visible !important;
}

div.stButton > button p,
div.stButton > button span,
div.stButton > button div {
    color: white !important;
    font-weight: bold !important;
}

div.stButton > button:hover {
    background: #1a1a1a !important;
    color: white !important;
    border: 1px solid #666 !important;
    transform: scale(1.03);
}

/* Radio buttons */
div[role="radiogroup"] label {
    color: white !important;
    font-weight: bold !important;
}

/* Tabs / misc */
[data-baseweb="tab"] {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATASET
# -----------------------------
df = pd.read_csv("ideas_dataset.csv")
df["combined_text"] = df["idea_title"] + " " + df["description"] + " " + df["domain"]

# -----------------------------
# TF-IDF FOR IDEA SIMILARITY
# -----------------------------
vectorizer = TfidfVectorizer(stop_words="english")
idea_vectors = vectorizer.fit_transform(df["combined_text"])

# -----------------------------
# DOMAIN CLASSIFICATION MODEL
# -----------------------------
X_domain = vectorizer.transform(df["combined_text"])
label_encoder = LabelEncoder()
y_domain = label_encoder.fit_transform(df["domain"])

domain_model = MultinomialNB()
domain_model.fit(X_domain, y_domain)

# -----------------------------
# ENCRYPTION SETUP
# -----------------------------
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

# -----------------------------
# USERS FILE CHECK
# -----------------------------
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

with open("users.json", "r") as f:
    users = json.load(f)

# -----------------------------
# HASH PASSWORD FUNCTION
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -----------------------------
# SAVE USERS FUNCTION
# -----------------------------
def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# -----------------------------
# LOGIN FUNCTION
# -----------------------------
def login(username, password):
    hashed = hash_password(password)
    return username in users and users[username] == hashed

# -----------------------------
# REGISTER FUNCTION
# -----------------------------
def register(username, password):
    if username in users:
        return False, "Username already exists!"
    users[username] = hash_password(password)
    save_users()
    return True, "Account created successfully!"

# -----------------------------
# ENCRYPT IDEA FUNCTION
# -----------------------------
def encrypt_idea(text):
    encrypted = cipher.encrypt(text.encode())
    return encrypted.decode()

# -----------------------------
# IDEA SUMMARY FUNCTION
# -----------------------------
def generate_summary(user_idea, predicted_domain):
    user_idea_lower = user_idea.lower()

    if "kids" in user_idea_lower or "children" in user_idea_lower or "cartoon" in user_idea_lower:
        return f"This idea appears to be a child-focused AI learning assistant in the domain of {predicted_domain}, designed to improve engagement and concept understanding in a fun and personalized way."
    elif "detect" in user_idea_lower or "security" in user_idea_lower or "phishing" in user_idea_lower or "scam" in user_idea_lower:
        return f"This idea appears to be a security-oriented intelligent system in the domain of {predicted_domain}, aimed at identifying risks, threats, or suspicious digital behavior."
    elif "chatbot" in user_idea_lower or "assistant" in user_idea_lower:
        return f"This idea appears to be an AI-based assistant in the domain of {predicted_domain}, designed to help users through conversational interaction and intelligent responses."
    elif "health" in user_idea_lower or "disease" in user_idea_lower or "symptom" in user_idea_lower:
        return f"This idea appears to be a healthcare-support AI solution in the domain of {predicted_domain}, intended to assist users in health-related understanding or monitoring."
    else:
        return f"This idea appears to be an innovative project concept related to {predicted_domain}, with practical application potential based on its described functionality."

# -----------------------------
# IDEA ANALYSIS FUNCTION
# -----------------------------
def analyze_idea(user_idea):
    user_vector = vectorizer.transform([user_idea])
    similarity_scores = cosine_similarity(user_vector, idea_vectors).flatten()

    top_indices = similarity_scores.argsort()[-3:][::-1]
    top_matches = df.iloc[top_indices][["idea_title", "description", "domain"]].copy()
    top_matches["similarity_score"] = similarity_scores[top_indices] * 100

    predicted_domain_encoded = domain_model.predict(user_vector)[0]
    predicted_domain = label_encoder.inverse_transform([predicted_domain_encoded])[0]

    max_score = similarity_scores.max() * 100
    novelty_score = 100 - max_score

    if max_score >= 70:
        uniqueness = "⚠️ Strong Similarity Found"
        interpretation = "A very similar idea already exists in the dataset."
    elif max_score >= 40:
        uniqueness = "🟡 Related Idea Exists"
        interpretation = "Your idea is related to existing ideas but may still have some uniqueness."
    else:
        uniqueness = "🟢 No Strong Match Found"
        interpretation = "Your idea appears relatively unique within the current dataset."

    summary = generate_summary(user_idea, predicted_domain)

    return top_matches, predicted_domain, max_score, novelty_score, uniqueness, interpretation, summary

# -----------------------------
# SESSION STATE
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "idea_text" not in st.session_state:
    st.session_state.idea_text = ""

if "show_encrypted" not in st.session_state:
    st.session_state.show_encrypted = False

# -----------------------------
# LOGIN / SIGNUP PAGE
# -----------------------------
if not st.session_state.logged_in:
    st.markdown('<div class="main-title">🛡️ Secure Idea Verification Tool</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Check whether your idea is common, related, or relatively unique ✨</div>', unsafe_allow_html=True)

    menu = st.radio("Choose Option", ["Login", "Sign Up"], horizontal=True)

    if menu == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    elif menu == "Sign Up":
        new_username = st.text_input("Create Username")
        new_password = st.text_input("Create Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Create Account"):
            if new_username.strip() == "" or new_password.strip() == "":
                st.warning("Username and password cannot be empty.")
            elif new_password != confirm_password:
                st.error("Passwords do not match!")
            else:
                success, message = register(new_username, new_password)
                if success:
                    st.success(message)
                    st.info("Now go to Login and sign in with your new account.")
                else:
                    st.error(message)

# -----------------------------
# MAIN APP
# -----------------------------
else:
    st.markdown('<div class="main-title">🛡️ Secure Idea Verification Tool</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">Welcome, <b>{st.session_state.username}</b> 👋</div>', unsafe_allow_html=True)

    st.sidebar.title("🔐 Security + ML Features")
    st.sidebar.success("✔ User Authentication")
    st.sidebar.success("✔ Password Hashing")
    st.sidebar.success("✔ Idea Encryption")
    st.sidebar.success("✔ Similarity Detection")
    st.sidebar.success("✔ Domain Classification")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown("## 💡 Enter Your Idea")
    st.caption("Example: AI tutor for kids using cartoon characters to explain doubts")

    # Example buttons
    st.markdown("### ✨ Try Example Ideas")
    col1, col2, col3 = st.columns(3)

    if col1.button("Kids AI Tutor"):
        st.session_state.idea_text = "An AI made for children where doubt clarification is given using their favorite cartoon or goal character."
    if col2.button("Phishing Detector"):
        st.session_state.idea_text = "A machine learning system to detect phishing websites and scam links."
    if col3.button("Career Assistant"):
        st.session_state.idea_text = "An AI tool that suggests career paths based on student interests and skills."

    user_idea = st.text_area("Type your project or startup idea here...", value=st.session_state.idea_text, height=180)

    if st.button("🚀 Verify Idea"):
        if user_idea.strip() == "":
            st.warning("Please enter an idea first.")
        else:
            top_matches, predicted_domain, max_score, novelty_score, uniqueness, interpretation, summary = analyze_idea(user_idea)
            encrypted_text = encrypt_idea(user_idea)

            # reset hidden state whenever new result comes
            st.session_state.show_encrypted = False
            st.session_state.current_encrypted_text = encrypted_text

            st.markdown("## 📊 Analysis Result")

            colA, colB = st.columns(2)

            with colA:
                st.markdown(f"""
                <div class="result-box">
                    <h3>🔍 Predicted Domain</h3>
                    <p>{predicted_domain}</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="result-box">
                    <h3>📈 Highest Similarity Score</h3>
                    <p>{max_score:.2f}%</p>
                </div>
                """, unsafe_allow_html=True)

            with colB:
                st.markdown(f"""
                <div class="result-box">
                    <h3>🌟 Novelty Score</h3>
                    <p>{novelty_score:.2f}%</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="result-box">
                    <h3>🧠 Novelty Result</h3>
                    <p><b>{uniqueness}</b></p>
                    <p>{interpretation}</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("### 🌡️ Novelty Meter")
            st.progress(int(novelty_score))

            st.markdown(f"""
            <div class="result-box">
                <h3>📝 Idea Understanding</h3>
                <p>{summary}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 📌 Top Similar Existing Ideas")
            for _, row in top_matches.iterrows():
                st.markdown(f"""
                <div class="result-box">
                    <h4>{row['idea_title']}</h4>
                    <p><b>Description:</b> {row['description']}</p>
                    <p><b>Domain:</b> {row['domain']}</p>
                    <p><b>Similarity:</b> {row['similarity_score']:.2f}%</p>
                </div>
                """, unsafe_allow_html=True)

    # -----------------------------
    # ENCRYPTED TEXT TOGGLE SECTION
    # -----------------------------
    if "current_encrypted_text" in st.session_state:
        st.markdown("### 🔐 Encrypted Stored Version of Your Idea")

        if st.button("👁️ Show / Hide Encrypted Text"):
            st.session_state.show_encrypted = not st.session_state.show_encrypted

        if st.session_state.show_encrypted:
            st.markdown(f"""
            <div class="result-box">
                <h3>🔐 Encrypted Idea Content</h3>
                <p style="background:black; color:#00ff99; padding:12px; border-radius:12px; font-family:monospace; word-wrap:break-word;">
                    {st.session_state.current_encrypted_text}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="result-box">
                <h3>🔒 Encrypted Idea Content</h3>
                <p style="color:#cbd5e1;">Encrypted text is currently hidden for security purposes.</p>
            </div>
            """, unsafe_allow_html=True)

        st.info("Your idea has been securely processed and represented in encrypted form.")

        st.markdown("""
        <div class="small-note">
        ⚠️ Note: This tool estimates idea similarity based on the available dataset and does not guarantee legal originality or copyright ownership.
        </div>
        """, unsafe_allow_html=True)