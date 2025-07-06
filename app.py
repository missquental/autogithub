import streamlit as st
import requests
import json
import os
from datetime import datetime
import base64

# Set page config
st.set_page_config(
    page_title="GitHub → Streamlit Deployer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .success-message {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def create_github_repo(token, repo_name, description, private=False):
    """Create a GitHub repository"""
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": True
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response

def upload_file_to_repo(token, owner, repo, file_path, content, message="Add file"):
    """Upload a file to GitHub repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Encode content to base64
    content_b64 = base64.b64encode(content.encode()).decode()
    
    data = {
        "message": message,
        "content": content_b64
    }
    
    response = requests.put(url, headers=headers, json=data)
    return response

def get_streamlit_app_template():
    """Get a template Streamlit app"""
    """Read template from template-app.py file"""
    try:
        with open('template-app.py', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error("❌ template-app.py file not found!")
        return None
    except Exception as e:
        st.error(f"❌ Error reading template-app.py: {e}")
        return None

def get_requirements_txt():
    """Get requirements.txt content"""
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error("❌ requirements.txt file not found!")
        return None
    except Exception as e:
        st.error(f"❌ Error reading requirements.txt: {e}")
        return None

def get_packages_txt():
    """Get packages.txt content for system dependencies"""
    return """ffmpeg
"""
def get_readme_content(repo_name):
    """Get README.md content"""
    return f"""# {repo_name}

A beautiful Streamlit application automatically deployed from GitHub.

## Features

- 🚀 Auto-deployment to Streamlit Cloud
- 📊 Interactive data visualizations
- 📱 Responsive design
- 🎨 Beautiful UI with custom styling

## Live Demo

Visit the live application: [Your App URL]

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/{repo_name}.git
cd {repo_name}
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Deployment

This app is automatically deployed to Streamlit Cloud whenever changes are pushed to the main branch.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License.
"""

# Main app
def main():
    st.markdown("""
    <div class="main-header">
        <h1>🚀 GitHub → Streamlit Deployer</h1>
        <p>Create GitHub repositories and auto-deploy to Streamlit Cloud</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Configuration")
    
    # GitHub token input
    github_token = st.sidebar.text_input(
        "GitHub Personal Access Token",
        type="password",
        help="Create a token at https://github.com/settings/tokens"
    )
    
    # Repository details
    st.sidebar.subheader("Repository Details")
    repo_name = st.sidebar.text_input("Repository Name", "my-streamlit-app")
    repo_description = st.sidebar.text_area(
        "Description", 
        "A beautiful Streamlit application with auto-deployment"
    )
    private_repo = st.sidebar.checkbox("Private Repository", False)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>✨ Features</h3>
            <ul>
                <li>🔧 Automatically creates GitHub repository</li>
                <li>📱 Includes beautiful Streamlit app template</li>
                <li>🚀 Sets up auto-deployment to Streamlit Cloud</li>
                <li>📊 Pre-configured with data visualization tools</li>
                <li>🎨 Modern, responsive design</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Create Repository & Deploy", type="primary"):
            if not github_token:
                st.markdown("""
                <div class="error-message">
                    ❌ Please provide a GitHub Personal Access Token
                </div>
                """, unsafe_allow_html=True)
                return
            
            if not repo_name:
                st.markdown("""
                <div class="error-message">
                    ❌ Please provide a repository name
                </div>
                """, unsafe_allow_html=True)
                return
            
            with st.spinner("Creating repository..."):
                # Create repository
                response = create_github_repo(
                    github_token, 
                    repo_name, 
                    repo_description, 
                    private_repo
                )
                
                if response.status_code == 201:
                    repo_data = response.json()
                    owner = repo_data['owner']['login']
                    
                    st.markdown("""
                    <div class="success-message">
                        ✅ Repository created successfully!
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Upload files
                    files_to_upload = [
                        ("app.py", get_streamlit_app_template(), "Add YouTube Live Streaming app"),
                        ("requirements.txt", get_requirements_txt(), "Add requirements"),
                        ("packages.txt", get_packages_txt(), "Add system packages"),
                        ("README.md", get_readme_content(repo_name), "Add README")
                    ]
                    
                    progress_bar = st.progress(0)
                    
                    for i, (file_path, content, message) in enumerate(files_to_upload):
                        upload_response = upload_file_to_repo(
                            github_token, owner, repo_name, file_path, content, message
                        )
                        
                        if upload_response.status_code in [201, 200]:
                            st.success(f"✅ {file_path} uploaded successfully")
                        else:
                            st.error(f"❌ Failed to upload {file_path}")
                        
                        progress_bar.progress((i + 1) / len(files_to_upload))
                    
                    # Display repository info
                    st.markdown(f"""
                    <div class="info-box">
                        <h3>🎉 Repository Created!</h3>
                        <p><strong>Repository URL:</strong> <a href="{repo_data['html_url']}" target="_blank">{repo_data['html_url']}</a></p>
                        <p><strong>Clone URL:</strong> {repo_data['clone_url']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Streamlit Cloud deployment instructions
                    st.markdown("""
                    <div class="feature-card">
                        <h3>🚀 Deploy to Streamlit Cloud</h3>
                        <p>Follow these steps to deploy your app:</p>
                        <ol>
                            <li>Go to <a href="https://share.streamlit.io/" target="_blank">share.streamlit.io</a></li>
                            <li>Click "New app"</li>
                            <li>Select your repository</li>
                            <li>Set main file path: <code>app.py</code></li>
                            <li>Click "Deploy!"</li>
                        </ol>
                        <p>Your app will be automatically deployed and updated whenever you push to GitHub!</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    error_message = response.json().get('message', 'Unknown error')
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ Failed to create repository: {error_message}
                    </div>
                    """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📋 Setup Instructions</h3>
            <p><strong>1. Get GitHub Token:</strong></p>
            <ol>
                <li>Go to GitHub Settings</li>
                <li>Developer settings → Personal access tokens</li>
                <li>Generate new token (classic)</li>
                <li>Select 'repo' scope</li>
                <li>Copy the token</li>
            </ol>
            
            <p><strong>2. Repository Setup:</strong></p>
            <ul>
                <li>Choose a unique name</li>
                <li>Add description</li>
                <li>Select visibility</li>
            </ul>
            
            <p><strong>3. Deployment:</strong></p>
            <ul>
                <li>Automatic file upload</li>
                <li>Streamlit Cloud integration</li>
                <li>Live URL generation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
