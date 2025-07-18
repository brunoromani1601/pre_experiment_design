import streamlit as st
from core.calculator import SampleSizeCalculator
from core.pdf_generator import PDFGenerator
from core.session_manager import SessionManager
from ui.styling import get_custom_css
from components.sample_calculator import sample_size_calculator
from components.experiment_designer import experiment_designer

# Configure page
st.set_page_config(
    page_title="Experiment Design Tool",
    page_icon="🧪",
    layout="wide"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize session state
SessionManager.initialize_session_state()

# ===== MAIN APPLICATION =====
def main():
    st.title("🧪 SCS Experiment Design")
    st.markdown("Design and standardize your experiments with proper statistical rigor")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox("Navigate", ["🎯 Pre-Experiment Design Tool", "📊 Sample Size Calculator"])
    
    if page == "🎯 Pre-Experiment Design Tool":
        experiment_designer()
    else:
        sample_size_calculator()

if __name__ == "__main__":
    main() 