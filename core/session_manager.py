import streamlit as st

class SessionManager:
    @staticmethod
    def initialize_session_state():
        """Initialize all session state variables"""
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {}
        
        # Initialize calculator session state
        if 'calculator_sample_size' not in st.session_state:
            st.session_state.calculator_sample_size = None
        if 'calculator_test_type' not in st.session_state:
            st.session_state.calculator_test_type = None
    
    @staticmethod
    def get_form_data(key, default=None):
        """Get value from form_data session state"""
        return st.session_state.form_data.get(key, default)
    
    @staticmethod
    def set_form_data(key, value):
        """Set value in form_data session state"""
        st.session_state.form_data[key] = value
    
    @staticmethod
    def update_form_data(data_dict):
        """Update multiple values in form_data session state"""
        st.session_state.form_data.update(data_dict)
    
    @staticmethod
    def get_calculator_sample_size():
        """Get calculator sample size from session state"""
        return st.session_state.calculator_sample_size
    
    @staticmethod
    def set_calculator_sample_size(value):
        """Set calculator sample size in session state"""
        st.session_state.calculator_sample_size = value
    
    @staticmethod
    def get_calculator_test_type():
        """Get calculator test type from session state"""
        return st.session_state.calculator_test_type
    
    @staticmethod
    def set_calculator_test_type(value):
        """Set calculator test type in session state"""
        st.session_state.calculator_test_type = value
    
    @staticmethod
    def reset_calculator_sample_size():
        """Reset calculator sample size"""
        st.session_state.calculator_sample_size = None 