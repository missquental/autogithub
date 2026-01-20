import streamlit as st
import requests
import os
import base64

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="GitHub → Streamlit Deployer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# STYLES
# ===============================
st.markdown("""
<style>
.main-header {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-radius: 12px;
    margin-bottom: 2rem;
}
.card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0,0,0,.1);
    margin-bottom: 1rem;
}
.success {
    background: linear-gradient(135deg, #4CAF50, #2e7d32);
    color: white;
    padding: 1rem;
    border-radius: 10px;
}
.error {
    background: linear-gradient(135deg, #f44336, #c62828);
    color: white;
    padding: 1rem;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# UTILITIES
# ===============================
def get_available_templates():
    """Auto-detect template-app*.py files"""
    return sorted([
        f for f in os.listdir(".")
        if f.startswith("template-app") and f.endswith(".py")
    ])

def read_template(template_file):
    try:
        with open(template_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        st.error(f"❌ Failed to read {template_file}: {e}")
        return None

def read_file(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def create_repo(token, name, desc, private):
    r = requests.post(
        "https://api.github.com/user/repos",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        },
        json={
            "name": name,
            "description": desc,
            "private": private,
            "auto_init": True
        }
    )
    return r

def upload_file(token, owner, repo, path, content, msg):
    return requests.put(
        f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        },
        json={
            "message": msg,
            "content": base64.b64encode(content.encode()).decode()
        }
    )

# ===============================
# MAIN APP
# ===============================
def main():
    st.markdown("""
    <div class="main-header">
        <h1>🚀 GitHub → Streamlit Deployer</h1>
        <p>Auto Create Repo + Auto Deploy Template</p>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.title("⚙️ Configuration")

    token = st.sidebar.text_input("GitHub Token", type="password")
    repo_name = st.sidebar.text_input("Repository Name", "streamlit-app")
    repo_desc = st.sidebar.text_area("Description", "Auto deployed Streamlit app")
    private = st.sidebar.checkbox("Private Repository", False)

    st.sidebar.subheader("📦 Template")
    templates = get_available_templates()

    if not templates:
        st.sidebar.error("No template-app*.py found")
        st.stop()

    default_index = templates.index("template-app4.py") if "template-app4.py" in templates else 0

    selected_template = st.sidebar.selectbox(
        "Select Template",
        templates,
        index=default_index
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
        <div class="card">
            <h3>Selected Template</h3>
            <code>{selected_template}</code>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Create Repo & Deploy", type="primary"):
            if not token:
                st.markdown("<div class='error'>GitHub token required</div>", unsafe_allow_html=True)
                return

            with st.spinner("Creating repository..."):
                res = create_repo(token, repo_name, repo_desc, private)

            if res.status_code != 201:
                st.markdown(f"<div class='error'>{res.json().get('message')}</div>", unsafe_allow_html=True)
                return

            data = res.json()
            owner = data["owner"]["login"]

            st.markdown("<div class='success'>Repository Created</div>", unsafe_allow_html=True)

            files = [
                ("app.py", read_template(selected_template)),
                ("requirements.txt", read_file("requirements.txt")),
                ("packages.txt", read_file("packages.txt")),
            ]

            for f, c in files:
                upload_file(token, owner, repo_name, f, c, f"Add {f}")

            st.success("All files uploaded")
            st.markdown(f"[Open Repository]({data['html_url']})")

    with col2:
        st.markdown("""
        <div class="card">
            <h4>Next Step</h4>
            <ol>
                <li>Open share.streamlit.io</li>
                <li>New App</li>
                <li>Select repo</li>
                <li>Main file: app.py</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
