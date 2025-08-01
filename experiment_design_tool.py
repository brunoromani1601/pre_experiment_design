import streamlit as st
from core.calculator import SampleSizeCalculator
from core.pdf_generator import PDFGenerator
from core.session_manager import SessionManager
from ui.styling import get_custom_css
from components.sample_calculator import sample_size_calculator
from components.experiment_designer import experiment_designer
from components.post_experiment_analysis import post_experiment_analysis
import time
import traceback

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

# Initialize performance tracking
if 'performance_initialized' not in st.session_state:
    st.session_state.performance_initialized = True
    st.session_state.last_interaction = None
    st.session_state.error_count = 0

# Global error handler
def handle_errors(func):
    """Decorator to handle errors gracefully"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.session_state.error_count += 1
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 **Tip:** Try refreshing the page or check your Notion configuration.")
            
            # Show detailed error in debug mode
            if st.session_state.error_count <= 3:  # Only show first 3 errors
                with st.expander("🔍 Debug Information", expanded=False):
                    st.code(traceback.format_exc())
            
            return None
    return wrapper

# ===== MAIN APPLICATION =====
@handle_errors
def main():
    st.title("🧪 SCS Experiment Design")
    st.markdown("Design and standardize your experiments with proper statistical rigor")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox("Navigate", ["🎯 Pre-Experiment Design Tool", "📊 Sample Size Calculator", "📈 Post-Experiment Analysis"])
    
    # Performance indicator
    if st.session_state.error_count > 0:
        st.sidebar.warning(f"⚠️ {st.session_state.error_count} error(s) encountered")
    
    if page == "🎯 Pre-Experiment Design Tool":
        experiment_designer()
    elif page == "📊 Sample Size Calculator":
        sample_size_calculator()
    else:
        post_experiment_analysis()

if __name__ == "__main__":
    main()