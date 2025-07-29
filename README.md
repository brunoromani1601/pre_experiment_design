# 🧪 SCS Experiment Design Tool

A comprehensive Streamlit-based application for designing and standardizing A/B tests with proper statistical rigor. This tool helps you calculate sample sizes, estimate runtimes, and generate professional experiment design documents.

## ✨ Features

### 🎯 Pre-Experiment Design Tool
- **Step-by-step experiment planning** with guided form inputs
- **Real-time sample size calculations** for superiority and non-inferiority tests
- **Automatic runtime estimation** based on traffic volume
- **Live preview** of experiment design before final submission
- **Professional PDF generation** with complete experiment documentation
- **Auto-save functionality** to preserve form data across sessions

### 📊 Sample Size Calculator
- **Multiple test types**: Two-proportion Z-test, Continuous metric T-test, Non-inferiority test
- **Statistical parameter customization**: Significance level (α) and statistical power
- **Traffic allocation planning** with detailed breakdowns
- **Runtime estimation** with daily/weekly/monthly traffic options

### 📋 Generated PDF Includes
- **Experiment Configuration**: Feature description, hypothesis, test type, metrics
- **Statistical Details**: Sample size per variation, total sample size, runtime
- **SCS Configuration**: Campaign, traffic type, control/treatment variants
- **Target Audience**: User segments, device types, traffic sources
- **Priority & Business Context**: Priority level with color coding, business goals

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
   
   **Option A: Use the helper script**
   ```bash
   python setup_env.py
   ```
   
   **Option B: Create manually**
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
   - Or run `python find_notion_databases.py` to list all accessible databases

6. **Run the application**
   ```bash
   streamlit run experiment_design_tool.py
   ```

7. **Open your browser**
   Navigate to `http://localhost:8501`

## 📖 Usage Guide

### Creating an Experiment Design

1. **Navigate to "Pre-Experiment Design Tool"** in the sidebar
2. **Fill out Step 1**: Basic experiment information (name, feature, hypothesis)
3. **Configure Step 2**: Select metrics, test type, and expected lift/margin
4. **Review real-time calculations**: Sample size and runtime are calculated automatically
5. **Complete Steps 3-5**: Campaign configuration, target audience, and priority
6. **Generate PDF**: Click "Generate Final Design" to create and download the PDF

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
- **Dynamic dropdowns** for EPCVIP Campaigns, Affiliates, and Initiatives
- **Search functionality** for initiatives with 100+ options
- **Two-step validation** process with preview before creation
- **Rich content formatting** in Notion page body

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
├── experiment_design_tool.py    # Main application file
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
└── venv/                        # Virtual environment (not in repo)
```

## 🛠️ Dependencies

Key packages used:
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations
- **SciPy**: Statistical functions
- **ReportLab**: PDF generation
- **Altair**: Data visualization

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

- **v1.0.0**: Initial release with experiment design tool and sample size calculator
- Features: PDF generation, auto-save, real-time calculations, comprehensive form validation 