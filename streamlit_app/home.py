"""
Home page — clean, professional login / signup interface.
"""

import logging

import streamlit as st

from utils.api_client import create_user, login_user, get_api_token


st.set_page_config(
    page_title="Adaptive RAG — Login",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="a",
)
logger = logging.getLogger(__name__)


st.markdown("""
<style>
/* Hide default navigation and footer */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarNav"],
[data-testid="collapsedControl"] { display: none; }

/* Form container */
div[data-testid="stForm"] {
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.5rem;
}

/* Tab bar */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-radius: 8px;
    overflow: hidden;
}
.stTabs [data-baseweb="tab"] {
    padding: 0.6rem 1.2rem;
    font-weight: 500;
}

/* Primary button glow */
.stFormSubmitButton > button {
    width: 100%;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 0.55rem !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown("")  # top spacing

col_l, col_c, col_r = st.columns([1, 4, 1])
with col_c:
    st.markdown(
        "<h1 style='text-align:center; margin-bottom:0; max-width: 100%;'>🧠 Adaptive RAG</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#8b95a5; margin-top:0.25rem; font-size:0.95rem;'>"
        "Intelligent document assistant powered by LangGraph</p>",
        unsafe_allow_html=True,
    )

st.divider()


if "session_id" not in st.session_state:
    with st.spinner("Connecting to backend…"):
        token = get_api_token()
    if token:
        st.session_state["session_id"] = token
    else:
        st.error(
            "Could not connect to the backend. Is the FastAPI server running on port 8000?")
        st.stop()


tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])


with tab_login:
    with st.form("login_form", clear_on_submit=False, border=True):
        st.markdown("##### Welcome back")
        username = st.text_input(
            "Username", placeholder="your username", key="login_user")
        password = st.text_input(
            "Password", type="password", placeholder="your password", key="login_pass")
        submitted = st.form_submit_button(
            "Sign In", type="primary", use_container_width=True)

    if submitted:
        if not username or not password:
            st.warning("Please fill in both fields.")
        else:
            with st.spinner("Authenticating…"):
                response = login_user(username, password,
                                      st.session_state["session_id"])
            if response and response.get("jwt"):
                st.session_state["jwt_token"] = response["jwt"]
                st.session_state["username"] = username
                st.success(f"Welcome back, **{username}**!")
                st.switch_page("pages/chat.py")
            else:
                st.error("Invalid credentials. Please try again.")


with tab_signup:
    with st.form("signup_form", clear_on_submit=True, border=True):
        st.markdown("##### Create a new account")
        new_user = st.text_input(
            "Username", placeholder="choose a username", key="signup_user")
        new_pass = st.text_input(
            "Password", type="password", placeholder="min. 6 characters", key="signup_pass")
        new_pass2 = st.text_input("Confirm Password", type="password",
                                  placeholder="re-enter password", key="signup_pass2")
        signup_submitted = st.form_submit_button(
            "Create Account", type="primary", use_container_width=True)

    if signup_submitted:
        if not new_user or not new_pass or not new_pass2:
            st.warning("All fields are required.")
        elif len(new_pass) < 6:
            st.warning("Password must be at least 6 characters.")
        elif new_pass != new_pass2:
            st.error("Passwords do not match.")
        else:
            with st.spinner("Creating account…"):
                success = create_user(new_user, new_pass,
                                      st.session_state["session_id"])
            if success:
                st.success("Account created! Switch to **Sign In** to log in.")
            else:
                st.error("Username already taken or registration failed.")


st.markdown("")
st.divider()
st.caption("Adaptive RAG · Built with FastAPI & LangGraph")
