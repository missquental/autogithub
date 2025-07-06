# GitHub → Streamlit Deployer

A beautiful Python application that automatically creates GitHub repositories and sets up auto-deployment to Streamlit Cloud.

## Features

- 🚀 **Auto Repository Creation**: Creates GitHub repositories with a single click
- 📱 **Beautiful Templates**: Includes pre-built Streamlit app templates
- 🔧 **Auto File Upload**: Automatically uploads app.py, requirements.txt, and README.md
- 🌟 **Streamlit Cloud Integration**: Step-by-step deployment guidance
- 🎨 **Modern UI**: Beautiful, responsive interface with custom styling
- 📊 **Data Visualization**: Pre-configured with Plotly and Pandas
- 🔒 **Secure**: Uses GitHub Personal Access Tokens for authentication

## Live Demo

Run this application locally or deploy it to Streamlit Cloud to start creating repositories!

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd github-streamlit-deployer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Get GitHub Token**:
   - Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
   - Generate a new token (classic)
   - Select the `repo` scope
   - Copy the token

2. **Configure Repository**:
   - Enter your GitHub token
   - Provide repository name and description
   - Choose visibility (public/private)

3. **Create & Deploy**:
   - Click "Create Repository & Deploy"
   - Wait for files to be uploaded
   - Follow Streamlit Cloud deployment instructions

## Generated Repository Structure

```
your-repo/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # Repository documentation
```

## Generated App Features

The automatically created Streamlit app includes:

- **Multi-page Navigation**: Home, Data Analysis, Charts
- **Interactive Visualizations**: Plotly charts and graphs
- **Data Analysis Tools**: Pandas DataFrames and statistics
- **Responsive Design**: Mobile-friendly interface
- **Custom Styling**: Beautiful CSS with gradients and animations
- **Metrics Dashboard**: Key performance indicators
- **Sample Data**: Pre-populated datasets for demonstration

## Streamlit Cloud Deployment

After repository creation, deploy to Streamlit Cloud:

1. Visit [share.streamlit.io](https://share.streamlit.io/)
2. Click "New app"
3. Select your newly created repository
4. Set main file path: `app.py`
5. Click "Deploy!"

Your app will be live within minutes and automatically update when you push changes to GitHub!

## Security Features

- 🔐 Secure token handling (password input type)
- 🛡️ No token storage or logging
- 🔒 GitHub API authentication
- 🚫 Input validation and error handling

## Technical Details

- **Framework**: Streamlit
- **API Integration**: GitHub REST API v3
- **Authentication**: GitHub Personal Access Tokens
- **File Upload**: Base64 encoded content upload
- **Styling**: Custom CSS with modern design principles

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License.

## Support

If you encounter any issues:
1. Check your GitHub token permissions
2. Ensure repository name is unique
3. Verify internet connection
4. Check GitHub API rate limits

Happy deploying! 🚀