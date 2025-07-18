def get_custom_css():
    """Return custom CSS for the application"""
    return """
<style>
    .main > div {
        padding: 1.5rem 1rem;
    }
    .step-header {
        background: linear-gradient(90deg, #6c757d, #5a6268);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin: 1.5rem 0 1rem 0;
        font-weight: 600;
    }
    .subsection-header {
        background: #adb5bd;
        color: white;
        padding: 0.5rem 0.75rem;
        border-radius: 4px;
        margin: 1rem 0 0.75rem 0;
        font-weight: 500;
        font-size: 0.95rem;
    }
    .info-box {
        background-color: #f5f5f5;
        padding: 0.75rem;
        border-radius: 4px;
        border-left: 3px solid #2196F3;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    .warning-box {
        background-color: #fff8e1;
        padding: 0.75rem;
        border-radius: 4px;
        border-left: 3px solid #ff9800;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    .success-box {
        background-color: #f1f8e9;
        padding: 0.75rem;
        border-radius: 4px;
        border-left: 3px solid #4CAF50;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    
    /* Hide only the main menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide the deploy button */
    .stDeployButton {display: none;}
</style>
""" 