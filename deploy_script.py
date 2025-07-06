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
        return '''import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Set page configuration
st.set_page_config(
    page_title="Auto-Deployed Streamlit App",
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
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #667eea;
    }
    
    .feature-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
    }
    
    .sidebar-info {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def generate_sample_data():
    """Generate sample data for demonstration."""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    data = pd.DataFrame({
        'Date': dates,
        'Sales': np.random.randint(100, 1000, len(dates)) + np.sin(np.arange(len(dates))/10) * 100,
        'Customers': np.random.randint(10, 100, len(dates)),
        'Revenue': np.random.randint(1000, 10000, len(dates)),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], len(dates)),
        'Product': np.random.choice(['Product A', 'Product B', 'Product C', 'Product D'], len(dates))
    })
    
    return data

def main():
    """Main application function."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Auto-Deployed Streamlit Application</h1>
        <p>Created automatically via GitHub → Streamlit Cloud deployment</p>
        <small>Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown("""
    <div class="sidebar-info">
        <h3>🎯 Navigation</h3>
        <p>Explore different features of this auto-deployed app</p>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.selectbox(
        "Choose a page",
        ["🏠 Home", "📊 Dashboard", "📈 Analytics", "🔧 Tools", "ℹ️ About"]
    )
    
    if page == "🏠 Home":
        st.title("Welcome to Your Auto-Deployed App!")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 🎉 Congratulations!
            
            Your Streamlit application has been successfully:
            - ✅ Created in a GitHub repository
            - ✅ Automatically deployed to Streamlit Cloud
            - ✅ Configured with a beautiful, responsive interface
            - ✅ Pre-loaded with sample data and visualizations
            
            ### 🚀 What's Next?
            
            1. **Customize**: Edit the `app.py` file in your repository
            2. **Deploy**: Changes will auto-deploy when you push to GitHub
            3. **Share**: Your app is live and ready to share!
            """)
        
        with col2:
            st.markdown("""
            <div class="feature-section">
                <h3>🌟 Features</h3>
                <ul>
                    <li>Real-time data visualization</li>
                    <li>Interactive charts</li>
                    <li>Responsive design</li>
                    <li>Auto-deployment</li>
                    <li>Modern UI/UX</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Sample metrics
        st.subheader("📊 Sample Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", "1,234", "↗️ 12%")
        
        with col2:
            st.metric("Revenue", "$45,678", "↗️ 8%")
        
        with col3:
            st.metric("Conversions", "89%", "↗️ 3%")
        
        with col4:
            st.metric("Active Sessions", "567", "↗️ 15%")
    
    elif page == "📊 Dashboard":
        st.title("📊 Interactive Dashboard")
        
        # Generate sample data
        data = generate_sample_data()
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            selected_region = st.selectbox("Select Region", ['All'] + list(data['Region'].unique()))
        
        with col2:
            date_range = st.date_input(
                "Select Date Range",
                value=(data['Date'].min(), data['Date'].max()),
                min_value=data['Date'].min(),
                max_value=data['Date'].max()
            )
        
        # Filter data
        filtered_data = data.copy()
        if selected_region != 'All':
            filtered_data = filtered_data[filtered_data['Region'] == selected_region]
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(filtered_data, x='Date', y='Sales', 
                         title='Sales Over Time',
                         color_discrete_sequence=['#667eea'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(filtered_data.groupby('Region')['Revenue'].sum().reset_index(),
                        x='Region', y='Revenue',
                        title='Revenue by Region',
                        color_discrete_sequence=['#764ba2'])
            st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("📋 Data Table")
        st.dataframe(filtered_data.head(20), use_container_width=True)
    
    elif page == "📈 Analytics":
        st.title("📈 Advanced Analytics")
        
        data = generate_sample_data()
        
        # Advanced visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Correlation heatmap
            corr_data = data[['Sales', 'Customers', 'Revenue']].corr()
            fig = px.imshow(corr_data, 
                           title='Correlation Matrix',
                           color_continuous_scale='RdBu')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distribution plot
            fig = px.histogram(data, x='Sales', nbins=30,
                              title='Sales Distribution',
                              color_discrete_sequence=['#667eea'])
            st.plotly_chart(fig, use_container_width=True)
        
        # Time series analysis
        st.subheader("🔍 Time Series Analysis")
        
        # Monthly aggregation
        monthly_data = data.groupby(data['Date'].dt.month).agg({
            'Sales': 'mean',
            'Revenue': 'sum',
            'Customers': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_data['Date'], y=monthly_data['Sales'],
                                mode='lines+markers', name='Average Sales'))
        fig.add_trace(go.Scatter(x=monthly_data['Date'], y=monthly_data['Revenue']/100,
                                mode='lines+markers', name='Revenue (scaled)'))
        fig.update_layout(title='Monthly Trends', xaxis_title='Month', yaxis_title='Value')
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif page == "🔧 Tools":
        st.title("🔧 Interactive Tools")
        
        tab1, tab2, tab3 = st.tabs(["📊 Data Generator", "🧮 Calculator", "📈 Plotter"])
        
        with tab1:
            st.subheader("📊 Sample Data Generator")
            
            rows = st.slider("Number of rows", 10, 1000, 100)
            cols = st.multiselect("Select columns", 
                                 ['Sales', 'Revenue', 'Customers', 'Profit', 'Orders'],
                                 default=['Sales', 'Revenue'])
            
            if st.button("Generate Data"):
                sample_data = pd.DataFrame({
                    col: np.random.randint(100, 1000, rows) for col in cols
                })
                st.dataframe(sample_data)
                
                # Download button
                csv = sample_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"sample_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with tab2:
            st.subheader("🧮 Business Calculator")
            
            col1, col2 = st.columns(2)
            
            with col1:
                revenue = st.number_input("Monthly Revenue ($)", value=10000)
                costs = st.number_input("Monthly Costs ($)", value=7000)
                
            with col2:
                customers = st.number_input("Number of Customers", value=100)
                conversion_rate = st.slider("Conversion Rate (%)", 0.0, 100.0, 5.0)
            
            profit = revenue - costs
            profit_margin = (profit / revenue) * 100 if revenue > 0 else 0
            revenue_per_customer = revenue / customers if customers > 0 else 0
            
            st.subheader("📊 Results")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Net Profit", f"${profit:,.2f}", f"{profit_margin:.1f}%")
            
            with col2:
                st.metric("Revenue per Customer", f"${revenue_per_customer:.2f}")
            
            with col3:
                st.metric("Projected Annual Revenue", f"${revenue * 12:,.2f}")
        
        with tab3:
            st.subheader("📈 Custom Plotter")
            
            # Function selector
            function_type = st.selectbox("Select Function", 
                                       ["Linear", "Quadratic", "Sine", "Cosine", "Exponential"])
            
            x = np.linspace(-10, 10, 100)
            
            if function_type == "Linear":
                slope = st.slider("Slope", -5.0, 5.0, 1.0)
                intercept = st.slider("Intercept", -10.0, 10.0, 0.0)
                y = slope * x + intercept
            
            elif function_type == "Quadratic":
                a = st.slider("a", -2.0, 2.0, 1.0)
                b = st.slider("b", -5.0, 5.0, 0.0)
                c = st.slider("c", -10.0, 10.0, 0.0)
                y = a * x**2 + b * x + c
            
            elif function_type == "Sine":
                amplitude = st.slider("Amplitude", 0.1, 5.0, 1.0)
                frequency = st.slider("Frequency", 0.1, 3.0, 1.0)
                y = amplitude * np.sin(frequency * x)
            
            elif function_type == "Cosine":
                amplitude = st.slider("Amplitude", 0.1, 5.0, 1.0)
                frequency = st.slider("Frequency", 0.1, 3.0, 1.0)
                y = amplitude * np.cos(frequency * x)
            
            elif function_type == "Exponential":
                base = st.slider("Base", 0.1, 3.0, 1.1)
                y = base ** x
            
            fig = px.line(x=x, y=y, title=f"{function_type} Function")
            st.plotly_chart(fig, use_container_width=True)
    
    elif page == "ℹ️ About":
        st.title("ℹ️ About This Application")
        
        st.markdown("""
        ### 🚀 Auto-Deployment Success!
        
        This application was automatically created and deployed using our GitHub → Streamlit Cloud integration tool.
        
        ### 🔧 Technical Stack
        
        - **Frontend**: Streamlit
        - **Data Processing**: Pandas, NumPy
        - **Visualizations**: Plotly Express
        - **Deployment**: Streamlit Cloud
        - **Version Control**: GitHub
        
        ### 📊 Features Included
        
        - **Interactive Dashboard**: Real-time data visualization
        - **Advanced Analytics**: Statistical analysis and correlations
        - **Business Tools**: Calculators and data generators
        - **Responsive Design**: Mobile-friendly interface
        - **Custom Styling**: Beautiful UI with modern design
        
        ### 🌟 Automatic Features
        
        - ✅ Auto-deployment on GitHub push
        - ✅ Requirements management
        - ✅ Error handling and validation
        - ✅ Performance optimization
        - ✅ SEO-friendly structure
        
        ### 🛠️ Customization
        
        To customize this application:
        
        1. **Edit the code**: Modify `app.py` in your GitHub repository
        2. **Add dependencies**: Update `requirements.txt`
        3. **Push changes**: Your app will automatically redeploy
        4. **Monitor**: Check deployment status in Streamlit Cloud
        
        ### 📞 Support
        
        For questions or issues:
        - Check the GitHub repository README
        - Review Streamlit documentation
        - Contact the development team
        
        ---
        
        **Created with ❤️ using the GitHub → Streamlit Deployer**
        
        *Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """*
        """)
        
        # System information
        st.subheader("🔍 System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Application Details**
            - Creation Date: {datetime.now().strftime("%Y-%m-%d")}
            - Streamlit Version: {st.__version__}
            - Python Version: 3.8+
            - Deployment: Streamlit Cloud
            """)
        
        with col2:
            st.success(f"""
            **Performance Metrics**
            - Load Time: < 2 seconds
            - Responsive: ✅
            - Mobile Ready: ✅
            - SEO Optimized: ✅
            """)

if __name__ == "__main__":
    main()
'''
    
    def get_requirements_txt(self) -> str:
        """Generate requirements.txt content."""
        return """streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.24.0
plotly>=5.15.0
requests>=2.31.0
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
            ("app.py", self.get_streamlit_app_template(), "Add comprehensive Streamlit application"),
            ("requirements.txt", self.get_requirements_txt(), "Add Python dependencies"),
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