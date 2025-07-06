#!/usr/bin/env python3
"""
GitHub Repository Creator and Streamlit Cloud Auto-Deploy Script
===============================================================

This script automates the process of creating GitHub repositories
and setting them up for automatic deployment to Streamlit Cloud.

Usage:
    python deploy_script.py

Author: GitHub → Streamlit Deployer
Version: 1.0.0
"""

import requests
import json
import os
import base64
import argparse
from datetime import datetime
from typing import Optional, Dict, Any

class GitHubStreamlitDeployer:
    """Main class for handling GitHub repository creation and Streamlit deployment setup."""
    
    def __init__(self, github_token: str):
        """Initialize the deployer with GitHub token."""
        self.github_token = github_token
        self.github_headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """
        Create a new GitHub repository.
        
        Args:
            name: Repository name
            description: Repository description
            private: Whether the repository should be private
            
        Returns:
            Dictionary containing repository information
        """
        url = "https://api.github.com/user/repos"
        
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True
        }
        
        response = requests.post(url, headers=self.github_headers, json=data)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create repository: {response.json()}")
    
    def upload_file(self, owner: str, repo: str, file_path: str, content: str, message: str = "Add file") -> bool:
        """
        Upload a file to the GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            file_path: Path where the file should be created
            content: File content
            message: Commit message
            
        Returns:
            True if successful, False otherwise
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        
        content_b64 = base64.b64encode(content.encode()).decode()
        
        data = {
            "message": message,
            "content": content_b64
        }
        
        response = requests.put(url, headers=self.github_headers, json=data)
        return response.status_code in [201, 200]
    
    def get_streamlit_app_template(self) -> str:
        """Generate a comprehensive Streamlit app template."""
        """Read template from template-app.py file"""
        try:
            with open('template-app.py', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print("❌ template-app.py file not found!")
            return None
        except Exception as e:
            print(f"❌ Error reading template-app.py: {e}")
            return None
    
    def get_requirements_txt(self) -> str:
        """Generate requirements.txt content."""
        try:
            with open('requirements.txt', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print("❌ requirements.txt file not found!")
            return None
        except Exception as e:
            print(f"❌ Error reading requirements.txt: {e}")
            return None
    
    def get_packages_txt(self) -> str:
        """Generate packages.txt content for system dependencies"""
        return """ffmpeg
"""
    
    def get_readme_content(self, repo_name: str) -> str:
        """Generate README.md content."""
        return f"""# {repo_name}

🚀 **Auto-deployed Streamlit Application**

This beautiful Streamlit application was automatically created and deployed using the GitHub → Streamlit Cloud integration tool.

## 🌟 Features

- **Interactive Dashboard**: Real-time data visualization and analytics
- **Advanced Analytics**: Statistical analysis, correlations, and time series
- **Business Tools**: Calculators, data generators, and plotting tools
- **Responsive Design**: Mobile-friendly interface with modern styling
- **Auto-Deployment**: Automatic updates when pushing to GitHub

## 🚀 Live Demo

Visit the live application: [Your App URL will be here after deployment]

## 🛠️ Local Development

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/{repo_name}.git
cd {repo_name}
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
streamlit run app.py
```

## 📊 Application Structure

```
{repo_name}/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🎯 Pages & Features

### 🏠 Home
- Welcome message and app overview
- Key metrics and statistics
- Feature highlights

### 📊 Dashboard
- Interactive data visualization
- Filtering and date range selection
- Real-time charts and graphs

### 📈 Analytics
- Advanced statistical analysis
- Correlation matrices
- Time series analysis
- Distribution plots

### 🔧 Tools
- Data generator for sample datasets
- Business calculator for metrics
- Custom function plotter

### ℹ️ About
- Application information
- Technical stack details
- Customization guide

## 🚀 Deployment

This application is automatically deployed to Streamlit Cloud whenever changes are pushed to the main branch.

### Manual Deployment Steps:

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click "New app"
3. Select this repository
4. Set main file path: `app.py`
5. Click "Deploy!"

## 🎨 Customization

### Adding New Features:

1. **Edit `app.py`**: Add new pages or modify existing ones
2. **Update dependencies**: Add new packages to `requirements.txt`
3. **Commit changes**: Push to GitHub for automatic deployment

### Styling:

The application uses custom CSS for beautiful styling. Modify the CSS in the `st.markdown()` sections to customize the appearance.

## 📋 Technical Details

- **Framework**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Plotly Express & Graph Objects
- **Deployment**: Streamlit Cloud
- **Version Control**: GitHub
- **Python Version**: 3.8+

## 🔧 Dependencies

All dependencies are automatically managed through `requirements.txt`:

- `streamlit>=1.28.0`: Web framework
- `pandas>=1.5.0`: Data manipulation
- `numpy>=1.24.0`: Numerical computing
- `plotly>=5.15.0`: Interactive visualizations
- `requests>=2.31.0`: HTTP requests

## 🌍 Contributing

Feel free to submit issues and enhancement requests!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For questions or issues:
- Check the application's About page
- Review Streamlit documentation
- Create an issue in this repository

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Created with the GitHub → Streamlit Deployer tool
- Built with Streamlit and Plotly
- Deployed on Streamlit Cloud

---

**Happy analyzing!** 🎉

*Auto-generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    def deploy_complete_app(self, repo_name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """
        Deploy a complete Streamlit application to GitHub.
        
        Args:
            repo_name: Name of the repository
            description: Repository description
            private: Whether the repository should be private
            
        Returns:
            Dictionary containing deployment information
        """
        print(f"🚀 Creating repository: {repo_name}")
        
        # Create repository
        repo_info = self.create_repository(repo_name, description, private)
        owner = repo_info['owner']['login']
        
        print(f"✅ Repository created: {repo_info['html_url']}")
        
        # Files to upload
        files = [
            ("app.py", self.get_streamlit_app_template(), "Add YouTube Live Streaming application"),
            ("requirements.txt", self.get_requirements_txt(), "Add Python dependencies"),
            ("packages.txt", self.get_packages_txt(), "Add system packages"),
            ("README.md", self.get_readme_content(repo_name), "Add detailed documentation")
        ]
        
        # Upload files
        for file_path, content, message in files:
            print(f"📤 Uploading {file_path}...")
            success = self.upload_file(owner, repo_name, file_path, content, message)
            if success:
                print(f"✅ {file_path} uploaded successfully")
            else:
                print(f"❌ Failed to upload {file_path}")
        
        deployment_info = {
            'repository': repo_info,
            'owner': owner,
            'repo_name': repo_name,
            'clone_url': repo_info['clone_url'],
            'html_url': repo_info['html_url'],
            'streamlit_instructions': {
                'url': 'https://share.streamlit.io/',
                'steps': [
                    'Go to share.streamlit.io',
                    'Click "New app"',
                    'Select your repository',
                    'Set main file path: app.py',
                    'Click "Deploy!"'
                ]
            }
        }
        
        return deployment_info

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="GitHub → Streamlit Cloud Auto-Deployer")
    parser.add_argument("--token", required=True, help="GitHub Personal Access Token")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--description", default="Auto-deployed Streamlit application", help="Repository description")
    parser.add_argument("--private", action="store_true", help="Create private repository")
    
    args = parser.parse_args()
    
    try:
        deployer = GitHubStreamlitDeployer(args.token)
        result = deployer.deploy_complete_app(args.repo, args.description, args.private)
        
        print("\n🎉 Deployment Complete!")
        print(f"📁 Repository: {result['html_url']}")
        print(f"🔗 Clone URL: {result['clone_url']}")
        print("\n🚀 Next Steps:")
        print("1. Go to https://share.streamlit.io/")
        print("2. Click 'New app'")
        print("3. Select your repository")
        print("4. Set main file path: app.py")
        print("5. Click 'Deploy!'")
        print("\n✨ Your app will be live in minutes!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
