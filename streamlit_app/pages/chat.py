"""
Chat page — clean, professional chat interface with loading states.
"""

import streamlit as st

from utils.api_client import query_backend, document_upload_rag


st.set_page_config(
    page_title="Adaptive RAG — Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get help": None, "Report a Bug": None, "About": None},
)


if "session_id" not in st.session_state or "jwt_token" not in st.session_state:
    st.warning("Session expired — please log in again.")
    st.page_link("home.py", label="← Back to Login", icon="🔑")
    st.stop()


st.markdown("""
<style>
#MainMenu, footer { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none; }

/* chat messages */
[data-testid="stChatMessage"] {
    border-radius: 10px;
    margin-bottom: 0.35rem;
}
</style>
""", unsafe_allow_html=True)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}
if "show_logout_confirm" not in st.session_state:
    st.session_state.show_logout_confirm = False

username = st.session_state.get("username", "User")


col_title, col_spacer, col_user, col_logout = st.columns([5, 2, 2, 2])
with col_title:
    st.markdown("### 🧠 Adaptive RAG Chat")
# with col_user:
with col_logout:
    st.markdown(f"👤 Logged in as **{username}**")
    if st.button("Logout", use_container_width=True):
        st.session_state.show_logout_confirm = True

# Logout confirmation
if st.session_state.show_logout_confirm:
    st.warning("Are you sure you want to logout?")
    c1, c2, c3 = st.columns([1, 1, 5])
    with c1:
        if st.button("Yes, logout", type="primary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("home.py")
    with c2:
        if st.button("Cancel"):
            st.session_state.show_logout_confirm = False
            st.rerun()

st.divider()


with st.sidebar:
    st.markdown("### 📂 Document Upload")
    st.caption("Upload a PDF or TXT to get document-grounded answers.")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "txt"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        file_description = st.text_input(
            "Describe this document",
            max_chars=300,
            placeholder="e.g. Python tutorial with code examples",
        )

        file_key = f"{uploaded_file.name}_{file_description}"

        if file_description:
            if file_key not in st.session_state.uploaded_files:
                upload_btn = st.button(
                    "Upload & Process", type="primary", use_container_width=True)
                if upload_btn:
                    with st.spinner(f"Processing {uploaded_file.name}… this may take a moment."):
                        success = document_upload_rag(
                            uploaded_file, file_description)
                    if success:
                        st.session_state.uploaded_files[file_key] = uploaded_file.name
                        st.success(f"✅ {uploaded_file.name} uploaded!")
                        st.rerun()
                    else:
                        st.error(f"Upload failed for {uploaded_file.name}.")
            else:
                st.info("Already uploaded.")
        else:
            st.info("Add a description to enable upload.")

    # Show uploaded files
    if st.session_state.uploaded_files:
        st.divider()
        st.markdown("**Uploaded files**")
        for name in sorted(set(st.session_state.uploaded_files.values())):
            st.markdown(f"📄 `{name}`")

    st.divider()
    with st.expander("💡 Tips"):
        st.markdown(
            "- Upload a **PDF** or **TXT** and describe it.\n"
            "- The assistant uses your document for relevant queries.\n"
            "- General questions work without uploads."
        )


# Empty state
if not st.session_state.chat_history:
    st.markdown("")
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown(
            "<div style='text-align:center; padding:3rem 0; color:#6b7280;'>"
            "<div style='font-size:3rem; margin-bottom:0.5rem;'>💬</div>"
            "<h4 style='color:#9ca3af; margin:0;'>Start a conversation</h4>"
            "<p style='font-size:0.9rem;'>Ask a question or upload a document first.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
else:
    # Render history
    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(text)

# Chat input
user_input = st.chat_input("Ask anything…")

if user_input:
    # Show user message immediately
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # Show thinking indicator then response
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            response = query_backend(user_input, st.session_state["jwt_token"])
        st.markdown(response)

    st.session_state.chat_history.append(("assistant", response))
