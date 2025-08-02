# 🧪 SCS Experiment Design Tool

A comprehensive Streamlit-based application for designing and standardizing A/B tests with proper statistical rigor. This tool helps you calculate sample sizes, estimate runtimes, and manage experiments through Notion integration.

## ✨ Features

### 🎯 Pre-Experiment Design Tool
- **Step-by-step experiment planning** with guided form inputs
- **Real-time sample size calculations** for superiority and non-inferiority tests
- **Automatic runtime estimation** based on traffic volume (Daily/Weekly/Monthly)
- **Live preview** of experiment design before final submission
- **Notion integration** for automatic experiment creation in your database
- **Searchable dropdowns** for EPCVIP Campaigns, Affiliates, and Initiatives
- **Auto-save functionality** to preserve form data across sessions
- **Owner and stakeholder tracking** for experiment accountability
- **JIRA link integration** for project management

### 📊 Sample Size Calculator
- **Multiple test types**: Two-proportion Z-test, Continuous metric T-test, Non-inferiority test
- **Statistical parameter customization**: Significance level (α) and statistical power
- **Traffic allocation planning** with detailed breakdowns
- **Runtime estimation** with daily/weekly/monthly traffic options

### 📈 Post-Experiment Analysis
- **Automatic data retrieval** from Notion experiment pages
- **Statistical analysis** for both superiority and non-inferiority tests
- **Sample size validation** against pre-experiment requirements
- **Concise results display** with practical significance assessment
- **One-tailed statistical tests** for proper hypothesis testing

### 📋 Notion Integration Features
- **Automatic experiment creation** in Notion Experiments database
- **Rich content formatting** with complete experiment details
- **Database relations** for Campaigns, Affiliates, and Initiatives
- **Two-step validation** process with preview before creation
- **Environment-based configuration** for secure database access
- **Post-experiment results template** for easy data input
- **Dynamic data parsing** from Notion page content

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd pre_experiment_design
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt):**
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables** (for Notion integration)
   Create a `.env` file in the project root with your Notion configuration:
   
   ```bash
   # Notion API Configuration
   NOTION_TOKEN=your_notion_integration_token_here
   
   # Notion Database IDs (get these from your Notion database URLs)
   NOTION_EXPERIMENTS_DB_ID=your_experiments_database_id_here
   NOTION_CAMPAIGNS_DB_ID=your_campaigns_database_id_here
   NOTION_AFFILIATES_DB_ID=your_affiliates_database_id_here
   NOTION_INITIATIVES_DB_ID=your_initiatives_database_id_here
   ```
   
   **🔍 How to find database IDs:**
   - Open your Notion database
   - Copy the ID from the URL: `https://notion.so/workspace/DATABASE_ID?v=...`
   - Or use the Notion API to list your databases

6. **Run the application**
   ```bash
   streamlit run experiment_design_tool.py
   ```

7. **Open your browser**
   Navigate to `http://localhost:8501`

## 📖 Usage Guide

### Creating an Experiment Design

1. **Navigate to "Pre-Experiment Design Tool"** in the sidebar
2. **Fill out Step 1**: Basic experiment information (name, owner, stakeholders, feature, hypothesis)
3. **Configure Step 2**: Select metrics, test type, and expected lift/margin
4. **Review real-time calculations**: Sample size and runtime are calculated automatically
5. **Complete Steps 3-5**: Campaign configuration, target audience, and priority
6. **Create in Notion**: Click "Review Notion Data" then "Create in Notion" to add to your database

### Analyzing Post-Experiment Results

1. **Navigate to "Post-Experiment Analysis"** in the sidebar
2. **Select experiment**: Choose from active experiments (not marked as "Complete")
3. **Filter by campaign**: Select the relevant campaign for your experiment
4. **Review results**: The tool automatically retrieves and analyzes your experiment data
5. **Interpret findings**: Get statistical significance and practical significance assessments

### Using the Sample Size Calculator

1. **Navigate to "Sample Size Calculator"** in the sidebar
2. **Select test type**: Choose the appropriate statistical test
3. **Set parameters**: Configure significance level, power, and test-specific values
4. **Calculate**: Click "Calculate Sample Size" to see results
5. **Plan traffic**: Use the runtime estimation to plan your experiment timeline

## 🔧 Configuration

### Statistical Parameters
- **Significance Level (α)**: Default 0.05 (5% chance of Type I error)
- **Statistical Power**: Default 0.80 (80% chance of detecting true effect)
- **Test Types**: Superiority tests, Non-inferiority tests

### Traffic Options
- **Daily/Weekly/Monthly** traffic volume inputs
- **Automatic conversion** between time periods
- **Runtime estimation** based on sample size and traffic

## 🔗 Notion Integration

The application integrates with Notion databases for seamless experiment management:

### Features
- **Automatic experiment creation** in Notion Experiments database
- **Searchable dropdowns** for EPCVIP Campaigns, Affiliates, and Initiatives
- **Integrated search functionality** for initiatives with 100+ options
- **Two-step validation** process with preview before creation
- **Rich content formatting** in Notion page body
- **Environment-based configuration** for secure database access

### Required Notion Setup
1. **Create a Notion integration** in your workspace
2. **Share databases** with your integration:
   - Experiments database
   - EPCVIP Campaigns database  
   - EPCVIP Affiliates database
   - Initiatives database
3. **Get database IDs** from the Notion URL or API
4. **Configure environment variables** in `.env` file

### Database Mappings
- **Experiments DB**: Main experiment records with relations
- **Campaigns DB**: EPCVIP Campaign options (relation)
- **Affiliates DB**: EPCVIP Affiliate options (summary only)
- **Initiatives DB**: Feature/Initiative options (relation)

## 📁 Project Structure

```
pre_experiment_design/
├── experiment_design_tool.py    # Main application entry point
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
├── .env                         # Environment variables (not in repo)
├── backup/                      # Backup files from migration
├── components/                  # Streamlit page components
│   ├── experiment_designer.py   # Pre-experiment design tool
│   ├── post_experiment_analysis.py  # Post-experiment analysis
│   └── sample_calculator.py     # Standalone sample size calculator
├── core/                        # Core functionality modules
│   ├── calculator.py            # Statistical calculations
│   ├── notion_integration.py    # Notion API integration
│   ├── session_manager.py       # Session state management
│   └── pdf_generator.py         # PDF generation (legacy)
└── ui/                         # UI styling and components
    └── styling.py               # Custom CSS and styling
```

## 🛠️ Dependencies

Key packages used:
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations
- **SciPy**: Statistical functions
- **Notion Client**: Notion API integration
- **Python-dotenv**: Environment variable management
- **ReportLab**: PDF generation (legacy)
- **Altair**: Data visualization (legacy)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the documentation above
2. Review the error messages in the Streamlit interface
3. Open an issue on GitHub with detailed information about the problem

## 🔄 Version History

- **v2.0.0**: Complete redesign with Notion integration and modular architecture
  - Features: Notion database integration, post-experiment analysis, modular components, auto-save, real-time calculations
  - New: EPCVIP Campaigns, Affiliates, and Initiatives integration
  - New: Post-experiment results template and analysis
  - New: One-tailed statistical tests for proper hypothesis testing
  - Improved: Traffic period handling (Daily/Weekly/Monthly)
  - Improved: Sample size calculator with better runtime estimation
- **v1.0.0**: Initial release with experiment design tool and sample size calculator
  - Features: PDF generation, auto-save, real-time calculations, comprehensive form validation 