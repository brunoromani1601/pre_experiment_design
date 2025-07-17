import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import math
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

# Configure page
st.set_page_config(
    page_title="Experiment Design Tool",
    page_icon="🧪",
    layout="wide"
)

# Custom CSS for cleaner styling
st.markdown("""
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

# ===== SAMPLE SIZE CALCULATION MODULE =====
class SampleSizeCalculator:
    @staticmethod
    def calculate_proportions(p1, p2, alpha=0.05, power=0.8):
        """Calculate sample size for two-proportion z-test"""
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        p_pooled = (p1 + p2) / 2
        
        numerator = (z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled)) + 
                    z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2)))**2
        denominator = (p1 - p2)**2
        
        n = numerator / denominator
        return math.ceil(n)
    
    @staticmethod
    def calculate_continuous(mean1, mean2, std, alpha=0.05, power=0.8):
        """Calculate sample size for continuous metrics (t-test)"""
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        effect_size = abs(mean1 - mean2) / std
        n = 2 * ((z_alpha + z_beta) / effect_size)**2
        return math.ceil(n)
    
    @staticmethod
    def calculate_non_inferiority(p1, delta, alpha=0.05, power=0.8):
        """Calculate sample size for non-inferiority test"""
        z_alpha = stats.norm.ppf(1 - alpha)  # One-sided test
        z_beta = stats.norm.ppf(power)
        
        p2 = p1 - delta  # Non-inferiority margin
        p_pooled = (p1 + p2) / 2
        
        numerator = (z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled)) + 
                    z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2)))**2
        denominator = delta**2
        
        n = numerator / denominator
        return math.ceil(n)
    
    @staticmethod
    def estimate_runtime(sample_size, daily_users):
        """Estimate experiment runtime in days"""
        if daily_users > 0:
            return math.ceil(sample_size / daily_users)
        return 0

# ===== PDF GENERATION MODULE =====
class PDFGenerator:
    @staticmethod
    def create_experiment_pdf(form_data):
        """Generate PDF document from form data"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor=colors.black
        )
        story.append(Paragraph(f"Experiment: {form_data.get('experiment_name', 'N/A')}", title_style))
        
        # Experiment Configuration Section
        story.append(Paragraph("<b>Experiment Configuration:</b>", styles['Heading2']))
        
        # Main sections
        sections = [
            ("Feature Being Tested", form_data.get('feature_description', 'N/A')),
            ("Hypothesis", form_data.get('hypothesis', 'N/A')),
            ("Test Type", form_data.get('test_type', 'N/A')),
            ("Target Metric", f"{form_data.get('primary_metric', 'N/A')} (Baseline = {form_data.get('baseline_value', 'N/A')}%)"),
        ]
        
        # Add test-specific parameters
        if form_data.get('test_type') == 'Superiority Test' and form_data.get('expected_lift'):
            sections.append(("Expected Lift", f"{form_data.get('expected_lift', 'N/A')}%"))
        elif form_data.get('test_type') == 'Non-Inferiority Test' and form_data.get('non_inferiority_margin'):
            sections.append(("Non-Inferiority Margin", f"{form_data.get('non_inferiority_margin', 'N/A')}%"))
        
        # Add remaining sections
        sections.extend([
            ("Secondary Metrics", ", ".join(form_data.get('secondary_metrics', []))),
            ("Required Sample Size Per Variation", f"{form_data.get('calculated_sample_size', 'N/A'):,} users" if form_data.get('calculated_sample_size') else 'N/A'),
            ("Total Sample Size Required", f"{form_data.get('calculated_sample_size', 0) * 2:,} users" if form_data.get('calculated_sample_size') else 'N/A'),
            ("Estimated Runtime", f"{form_data.get('estimated_runtime', 'N/A')} days at {form_data.get('daily_users', 'N/A'):,}/day" if form_data.get('daily_users') else 'N/A')
        ])
        
        for section_title, content in sections:
            story.append(Paragraph(f"<b>{section_title}:</b> {content}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        # SCS Configuration
        story.append(Paragraph("<b>SCS Configuration:</b>", styles['Heading2']))
        scs_data = [
            ("Campaign", form_data.get('campaign', 'N/A')),
            ("Traffic Type", form_data.get('traffic_type', 'N/A')),
            ("Control", form_data.get('control_variant', 'N/A')),
            ("Treatment", form_data.get('treatment_variant', 'N/A'))
        ]
        
        for label, value in scs_data:
            story.append(Paragraph(f"<b>{label}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Target Audience
        story.append(Paragraph("<b>Target Audience:</b>", styles['Heading2']))
        audience_data = [
            ("User Segment", form_data.get('user_segment', 'N/A')),
            ("Traffic Type", form_data.get('traffic_type', 'N/A')),
            ("Device Type", form_data.get('device_type', 'N/A'))
        ]
        
        for label, value in audience_data:
            story.append(Paragraph(f"<b>{label}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 12))
        
        # Priority Section
        story.append(Paragraph("<b>Priority:</b>", styles['Heading2']))
        priority_color = colors.red if form_data.get('priority') == 'High' else colors.orange if form_data.get('priority') == 'Medium' else colors.green
        story.append(Paragraph(f"<font color='{priority_color}'>● {form_data.get('priority', 'N/A')}</font>", styles['Normal']))
        if form_data.get('business_goal'):
            story.append(Paragraph(f"<b>Business goal:</b> {form_data['business_goal']}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer

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

def experiment_designer():
    st.markdown('<div class="step-header"><h2>🎯 Pre-Experiment Design Tool</h2></div>', unsafe_allow_html=True)
    

    


    # ===== STEP 1: BASIC INFORMATION =====
    st.markdown('<div class="step-header"><h3>Step 1: Basic Information</h3></div>', unsafe_allow_html=True)
    
    experiment_name = st.text_input(
        "🏷️ Experiment Name",
        value=st.session_state.form_data.get('experiment_name', ''),
        placeholder="e.g., Test Dynamic CTA Text on PPC Ad Chain",
        help="Give your experiment a descriptive name that clearly identifies what you're testing. Include the specific feature, component, or change you're testing.",
        key="experiment_name_input"
    )
    
    # Auto-save to session state
    if experiment_name != st.session_state.form_data.get('experiment_name', ''):
        st.session_state.form_data['experiment_name'] = experiment_name
    
    feature_description = st.text_area(
        "⚙️ Feature Being Tested",
        value=st.session_state.form_data.get('feature_description', ''),
        placeholder="e.g., CTA text change from 'Apply Now' to 'Get Approved Fast'",
        help="Describe what you're testing in detail. Include any data analysis or insights that led to this experiment idea. Be specific about the change and why you think it will work.",
        key="feature_description_input"
    )
    
    # Auto-save to session state
    if feature_description != st.session_state.form_data.get('feature_description', ''):
        st.session_state.form_data['feature_description'] = feature_description
    
    hypothesis = st.text_area(
        "🔬 Hypothesis",
        value=st.session_state.form_data.get('hypothesis', ''),
        placeholder="e.g., Changing CTA will increase App Rate by 1.2% because...",
        help="State your hypothesis clearly. For superiority tests: 'Changing X will increase Y by Z% because...' For non-inferiority tests: 'The new X will not decrease Y by more than Z% while improving...'",
        key="hypothesis_input"
    )
    
    # Auto-save to session state
    if hypothesis != st.session_state.form_data.get('hypothesis', ''):
        st.session_state.form_data['hypothesis'] = hypothesis
    
    # ===== STEP 2: METRICS & TEST CONFIGURATION =====
    st.markdown('<div class="step-header"><h3>Step 2: Metrics & Test Configuration</h3></div>', unsafe_allow_html=True)
    
    # First, get the metrics
    primary_metric = st.selectbox(
        "📈 Primary Metric",
        ["App Rate", "Revenue", "EPL", "Sold Rate", "Fund Rate", "EPS"],
        help="The main metric you're trying to move. This will be used for sample size calculations.",
        key="primary_metric_input"
    )
    
    # Auto-save to session state
    if primary_metric != st.session_state.form_data.get('primary_metric', ''):
        st.session_state.form_data['primary_metric'] = primary_metric
    
    baseline_value = st.number_input(
        "📊 Current Baseline Value (%)" if primary_metric in ["App Rate", "Sold Rate", "Fund Rate"] else "📊 Current Baseline Value",
        value=st.session_state.form_data.get('baseline_value', 75.0 if primary_metric == "App Rate" else 0.0),
        help="Current performance of your primary metric. Make sure this reflects the specific user segment you're targeting.",
        key="baseline_value_input"
    )
    
    # Auto-save to session state
    if baseline_value != st.session_state.form_data.get('baseline_value', 0.0):
        st.session_state.form_data['baseline_value'] = baseline_value
    
    secondary_metrics = st.multiselect(
        "📊 Secondary Metrics",
        ["App Rate", "Revenue", "EPL", "Sold Rate", "Fund Rate", "EPS"],
        default=st.session_state.form_data.get('secondary_metrics', []),
        help="Additional metrics to monitor for any unexpected effects",
        key="secondary_metrics_input"
    )
    
    # Auto-save to session state
    if secondary_metrics != st.session_state.form_data.get('secondary_metrics', []):
        st.session_state.form_data['secondary_metrics'] = secondary_metrics
    
    # Then, get the test type
    test_type = st.selectbox(
        "🎯 Test Type",
        ["Superiority Test", "Non-Inferiority Test"],
        index=0 if st.session_state.form_data.get('test_type') == 'Superiority Test' else 1,
        help="Superiority Test: Testing if the new version performs better than the current version. Non-Inferiority Test: Testing if the new version is not worse than the current version by more than a specified margin.",
        key="test_type_input"
    )
    
    # Auto-save to session state
    if test_type != st.session_state.form_data.get('test_type', ''):
        st.session_state.form_data['test_type'] = test_type
    
    # Initialize variables to avoid None issues
    expected_lift = None
    non_inferiority_margin = None
    
    # Dynamic lift input based on test type - NOW UPDATES IN REAL-TIME!
    if test_type == "Superiority Test":
        expected_lift = st.number_input(
            "📈 Expected Lift (%)",
            value=st.session_state.form_data.get('expected_lift', 1.2),
            help="How much improvement do you expect? (in percentage points). This directly impacts sample size - smaller lifts require larger sample sizes.",
            key="expected_lift_input"
        )
        
        # Auto-save to session state
        if expected_lift != st.session_state.form_data.get('expected_lift', 0.0):
            st.session_state.form_data['expected_lift'] = expected_lift
            st.session_state.form_data['non_inferiority_margin'] = None
        
    else:
        non_inferiority_margin = st.number_input(
            "📉 Non-Inferiority Margin (% absolute)",
            value=st.session_state.form_data.get('non_inferiority_margin', 1.0),
            help="Maximum acceptable decrease in absolute percentage points. E.g., if baseline is 75% and margin is 1%, you're testing that treatment ≥ 74%.",
            key="non_inferiority_margin_input"
        )
        
        # Auto-save to session state
        if non_inferiority_margin != st.session_state.form_data.get('non_inferiority_margin', 0.0):
            st.session_state.form_data['non_inferiority_margin'] = non_inferiority_margin
            st.session_state.form_data['expected_lift'] = None
    
    # ===== SAMPLE SIZE & RUNTIME CALCULATION =====
    st.markdown('<div class="step-header"><h4>📊 Sample Size & Runtime Calculator</h4></div>', unsafe_allow_html=True)
    
    # Statistical parameters and traffic input in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🔬 Statistical Parameters")
        alpha = st.number_input(
            "Significance Level (α)", 
            value=st.session_state.form_data.get('alpha', 0.05), 
            min_value=0.01, 
            max_value=0.10, 
            help="Probability of Type I error (false positive)",
            key="alpha_input"
        )
        
        # Auto-save to session state
        if alpha != st.session_state.form_data.get('alpha', 0.05):
            st.session_state.form_data['alpha'] = alpha
        
        power = st.number_input(
            "Statistical Power", 
            value=st.session_state.form_data.get('power', 0.80), 
            min_value=0.70, 
            max_value=0.99, 
            help="Probability of detecting a true effect (1 - Type II error)",
            key="power_input"
        )
        
        # Auto-save to session state
        if power != st.session_state.form_data.get('power', 0.80):
            st.session_state.form_data['power'] = power
    
    with col2:
        st.subheader("👥 Traffic Volume")
        traffic_period = st.radio(
            "📅 Traffic Period",
            ["Daily", "Weekly", "Monthly"],
            index=["Daily", "Weekly", "Monthly"].index(st.session_state.form_data.get('traffic_period', 'Daily')),
            help="Select the time period for your traffic volume",
            key="traffic_period_input"
        )
        
        # Auto-save to session state
        if traffic_period != st.session_state.form_data.get('traffic_period', 'Daily'):
            st.session_state.form_data['traffic_period'] = traffic_period
        
        if traffic_period == "Daily":
            traffic_volume = st.number_input(
                "👥 Daily Users",
                value=st.session_state.form_data.get('daily_users', 12000),
                help="How many users per day will enter this experiment?",
                key="daily_users_input"
            )
            
            # Auto-save to session state
            if traffic_volume != st.session_state.form_data.get('daily_users', 12000):
                st.session_state.form_data['daily_users'] = traffic_volume
            
            daily_users = traffic_volume
        elif traffic_period == "Weekly":
            weekly_users = st.number_input(
                "👥 Weekly Users",
                value=st.session_state.form_data.get('weekly_users', 84000),
                help="How many users per week will enter this experiment?",
                key="weekly_users_input"
            )
            
            # Auto-save to session state
            if weekly_users != st.session_state.form_data.get('weekly_users', 84000):
                st.session_state.form_data['weekly_users'] = weekly_users
            
            daily_users = weekly_users / 7
        else:  # Monthly
            monthly_users = st.number_input(
                "👥 Monthly Users",
                value=st.session_state.form_data.get('monthly_users', 360000),
                help="How many users per month will enter this experiment?",
                key="monthly_users_input"
            )
            
            # Auto-save to session state
            if monthly_users != st.session_state.form_data.get('monthly_users', 360000):
                st.session_state.form_data['monthly_users'] = monthly_users
            
            daily_users = monthly_users / 30
    
    with col3:
        st.subheader("📊 Results")
        # Calculate sample size based on test type and parameters - NOW LIVE!
        calc = SampleSizeCalculator()
        
        if test_type == "Superiority Test" and expected_lift is not None:
            if primary_metric in ["App Rate", "Sold Rate", "Fund Rate"]:
                p1 = baseline_value / 100
                p2 = (baseline_value + expected_lift) / 100
                sample_size = calc.calculate_proportions(p1, p2, alpha, power)
                
                # Auto-save calculated values to session state
                st.session_state.form_data['calculated_sample_size'] = sample_size
                st.session_state.form_data['treatment_rate'] = baseline_value + expected_lift
                
                st.metric("📊 Sample Size (per group)", f"{sample_size:,}")
                st.metric("👥 Total Sample Size", f"{sample_size*2:,}")
                st.metric("📈 Treatment Rate", f"{baseline_value + expected_lift:.1f}%")
            else:
                # For continuous metrics, provide guidance
                st.markdown('<div class="warning-box">⚠️ <b>Continuous Metrics:</b> Use sidebar calculator for detailed calculations.</div>', unsafe_allow_html=True)
                sample_size = 10000  # Placeholder
        elif test_type == "Non-Inferiority Test" and non_inferiority_margin is not None:
            p1 = baseline_value / 100
            sample_size = calc.calculate_non_inferiority(p1, non_inferiority_margin / 100, alpha, power)
            
            # Auto-save calculated values to session state
            st.session_state.form_data['calculated_sample_size'] = sample_size
            st.session_state.form_data['min_acceptable_rate'] = baseline_value - non_inferiority_margin
            
            st.metric("📊 Sample Size (per group)", f"{sample_size:,}")
            st.metric("👥 Total Sample Size", f"{sample_size*2:,}")
            st.metric("📉 Min Acceptable Rate", f"{baseline_value - non_inferiority_margin:.1f}%")
        else:
            # Show placeholder when parameters are not set
            sample_size = None
            st.markdown('<div class="warning-box">⚠️ <b>Set test parameters above</b></div>', unsafe_allow_html=True)
        
        # Runtime calculation
        if 'sample_size' in locals() and sample_size is not None:
            runtime = calc.estimate_runtime(sample_size * 2, daily_users)
            
            # Auto-save runtime to session state
            st.session_state.form_data['estimated_runtime'] = runtime
            st.session_state.form_data['daily_users_calculated'] = daily_users
            st.metric("⏱️ Estimated Runtime", f"{runtime} days")
            st.metric("👥 Daily Users per Group", f"{daily_users//2:,.0f}")
        else:
            st.markdown('<div class="warning-box">⚠️ <b>Runtime not available</b></div>', unsafe_allow_html=True)
    
    # Validation and warnings
    if sample_size is not None:
        if sample_size > 50000:
            st.warning("⚠️ Large sample size required. Consider increasing your expected lift or non-inferiority margin.")
        elif sample_size < 1000:
            st.success("✅ Sample size is reasonable and achievable.")
        
        if 'runtime' in locals() and runtime > 30:
            st.warning("⚠️ Long runtime (>30 days). Consider increasing daily traffic or adjusting test parameters.")
        elif 'runtime' in locals() and runtime < 7:
            st.success("✅ Quick experiment - will complete in less than a week.")
    
    # ===== STEP 3: CAMPAIGN & CONFIGURATION =====
    st.markdown('<div class="step-header"><h3>Step 3: Campaign & Configuration</h3></div>', unsafe_allow_html=True)
    
    campaign = st.selectbox(
        "🎯 Campaign",
        ["FastLoanAdvance-Google", "GraceLoanAdvance-Google", "5k Dupes"],
        index=["FastLoanAdvance-Google", "GraceLoanAdvance-Google", "5k Dupes"].index(st.session_state.form_data.get('campaign', 'FastLoanAdvance-Google')),
        help="Which campaign will this experiment run in?",
        key="campaign_input"
    )
    
    # Auto-save to session state
    if campaign != st.session_state.form_data.get('campaign', ''):
        st.session_state.form_data['campaign'] = campaign
    
    traffic_type = st.selectbox(
        "🚦 Traffic Type",
        ["PPC", "RESID", "RAQID", "Prepop", "Affiliate"],
        index=["PPC", "RESID", "RAQID", "Prepop", "Affiliate"].index(st.session_state.form_data.get('traffic_type', 'PPC')),
        help="What type of traffic will be included in this experiment?",
        key="traffic_type_input"
    )
    
    # Auto-save to session state
    if traffic_type != st.session_state.form_data.get('traffic_type', ''):
        st.session_state.form_data['traffic_type'] = traffic_type
    
    control_variant = st.text_input(
        "🎛️ Control Variant ID",
        value=st.session_state.form_data.get('control_variant', ''),
        placeholder="e.g., 8980",
        help="ID for the control (current) version",
        key="control_variant_input"
    )
    
    # Auto-save to session state
    if control_variant != st.session_state.form_data.get('control_variant', ''):
        st.session_state.form_data['control_variant'] = control_variant
    
    treatment_variant = st.text_input(
        "🎛️ Treatment Variant ID",
        value=st.session_state.form_data.get('treatment_variant', ''),
        placeholder="e.g., 9255",
        help="ID for the treatment (new) version",
        key="treatment_variant_input"
    )
    
    # Auto-save to session state
    if treatment_variant != st.session_state.form_data.get('treatment_variant', ''):
        st.session_state.form_data['treatment_variant'] = treatment_variant
    
    # ===== STEP 4: TARGET AUDIENCE =====
    st.markdown('<div class="step-header"><h3>Step 4: Target Audience</h3></div>', unsafe_allow_html=True)
    
    user_segment = st.selectbox(
        "👥 User Segment",
        ["All Users", "New Users", "Lookup Users"],
        index=["All Users", "New Users", "Lookup Users"].index(st.session_state.form_data.get('user_segment', 'All Users')),
        help="Which user segment will see this experiment? This affects your baseline rates.",
        key="user_segment_input"
    )
    
    # Auto-save to session state
    if user_segment != st.session_state.form_data.get('user_segment', ''):
        st.session_state.form_data['user_segment'] = user_segment
    
    device_type = st.selectbox(
        "📱 Device Type",
        ["All Devices", "Mobile", "Desktop"],
        index=["All Devices", "Mobile", "Desktop"].index(st.session_state.form_data.get('device_type', 'All Devices')),
        help="Which devices will be included in the experiment?",
        key="device_type_input"
    )
    
    # Auto-save to session state
    if device_type != st.session_state.form_data.get('device_type', ''):
        st.session_state.form_data['device_type'] = device_type
    
    # ===== STEP 5: PRIORITY & BUSINESS CONTEXT =====
    st.markdown('<div class="step-header"><h3>Step 5: Priority & Business Context</h3></div>', unsafe_allow_html=True)
    
    priority = st.selectbox(
        "🚨 Priority",
        ["High", "Medium", "Low"],
        index=["High", "Medium", "Low"].index(st.session_state.form_data.get('priority', 'Medium')),
        help="How important is this experiment to current business objectives?",
        key="priority_input"
    )
    
    # Auto-save to session state
    if priority != st.session_state.form_data.get('priority', ''):
        st.session_state.form_data['priority'] = priority
    
    business_goal = st.text_area(
        "🎯 Business Goal",
        value=st.session_state.form_data.get('business_goal', ''),
        placeholder="e.g., Test messaging shift before major campaign push in August",
        help="Explain why this experiment is important to the business and how it fits into broader goals.",
        key="business_goal_input"
    )
    
    # Auto-save to session state
    if business_goal != st.session_state.form_data.get('business_goal', ''):
        st.session_state.form_data['business_goal'] = business_goal
    
    # ===== LIVE PREVIEW SECTION =====
    st.markdown("---")
    st.markdown('<div class="step-header"><h3>📋 Pre-Experiment Design Preview</h3></div>', unsafe_allow_html=True)
    
    # Create a live preview of the experiment
    if experiment_name or feature_description or hypothesis:
        
        # Create preview data
        preview_data = {
            'experiment_name': experiment_name or "Untitled Experiment",
            'feature_description': feature_description or "Not specified",
            'hypothesis': hypothesis or "Not specified",
            'test_type': test_type,
            'primary_metric': primary_metric,
            'baseline_value': baseline_value,
            'expected_lift': expected_lift if test_type == "Superiority Test" else None,
            'non_inferiority_margin': non_inferiority_margin if test_type == "Non-Inferiority Test" else None,
            'secondary_metrics': secondary_metrics,
            'campaign': campaign,
            'traffic_type': traffic_type,
            'user_segment': user_segment,
            'control_variant': control_variant,
            'treatment_variant': treatment_variant,
            'device_type': device_type,
            'traffic_period': st.session_state.form_data.get('traffic_period', 'Daily'),
            'daily_users': st.session_state.form_data.get('daily_users_calculated', 0),
            'calculated_sample_size': st.session_state.form_data.get('calculated_sample_size'),
            'estimated_runtime': st.session_state.form_data.get('estimated_runtime'),
            'priority': priority,
            'business_goal': business_goal
        }
        
        # Display live preview
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Experiment Details")
            st.write(f"**Name:** {preview_data['experiment_name']}")
            st.write(f"**Test Type:** {preview_data['test_type']}")
            st.write(f"**Primary Metric:** {preview_data['primary_metric']} (Baseline: {preview_data['baseline_value']}%)")
            
            if preview_data['test_type'] == "Superiority Test" and preview_data['expected_lift']:
                st.write(f"**Expected Lift:** {preview_data['expected_lift']}%")
            elif preview_data['test_type'] == "Non-Inferiority Test" and preview_data['non_inferiority_margin']:
                st.write(f"**Non-Inferiority Margin:** {preview_data['non_inferiority_margin']}%")
            
            st.write(f"**Campaign:** {preview_data['campaign']}")
            st.write(f"**Traffic Type:** {preview_data['traffic_type']}")
            st.write(f"**User Segment:** {preview_data['user_segment']}")
            st.write(f"**Device Type:** {preview_data['device_type']}")
        
        with col2:
            st.subheader("📈 Sample Size & Runtime")
            if preview_data['calculated_sample_size']:
                st.write(f"**Sample Size:** {preview_data['calculated_sample_size']:,} users per group")
                st.write(f"**Total Sample Size:** {preview_data['calculated_sample_size']*2:,} users")
            else:
                st.write("**Sample Size:** Not calculated yet")
            
            if preview_data['estimated_runtime']:
                st.write(f"**Runtime:** {preview_data['estimated_runtime']} days")
            else:
                st.write("**Runtime:** Not calculated yet")
            
            # Display traffic information based on period
            if preview_data['traffic_period'] == "Daily":
                st.write(f"**Traffic:** {preview_data['daily_users']:,.0f} users/day")
            elif preview_data['traffic_period'] == "Weekly":
                weekly_traffic = preview_data['daily_users'] * 7
                st.write(f"**Traffic:** {weekly_traffic:,.0f} users/week ({preview_data['daily_users']:,.0f}/day)")
            else:  # Monthly
                monthly_traffic = preview_data['daily_users'] * 30
                st.write(f"**Traffic:** {monthly_traffic:,.0f} users/month ({preview_data['daily_users']:,.0f}/day)")
            
            st.write(f"**Priority:** {preview_data['priority']}")
            
            if preview_data['secondary_metrics']:
                st.write(f"**Secondary Metrics:** {', '.join(preview_data['secondary_metrics'])}")
        
        # Validation status
        st.subheader("✅ Validation Status")
        validation_issues = []
        
        if not experiment_name:
            validation_issues.append("❌ Experiment name is required")
        else:
            validation_issues.append("✅ Experiment name provided")
            
        if not feature_description:
            validation_issues.append("❌ Feature description is required")
        else:
            validation_issues.append("✅ Feature description provided")
            
        if not hypothesis:
            validation_issues.append("❌ Hypothesis is required")
        else:
            validation_issues.append("✅ Hypothesis provided")
            
        if not control_variant:
            validation_issues.append("⚠️ Control variant ID recommended")
        else:
            validation_issues.append("✅ Control variant ID provided")
            
        if not treatment_variant:
            validation_issues.append("⚠️ Treatment variant ID recommended")
        else:
            validation_issues.append("✅ Treatment variant ID provided")
        
        for issue in validation_issues:
            st.write(issue)
    
    # ===== FINAL SUBMISSION SECTION =====
    st.markdown("---")
    st.markdown('<div class="step-header"><h3>🚀 Generate Final Experiment Design</h3></div>', unsafe_allow_html=True)
    
    # Generate final design button
    if st.button("🚀 Generate Final Design", type="primary"):
            # Validate required fields
            if not experiment_name or not feature_description or not hypothesis:
                st.error("❌ Please fill in all required fields: Experiment Name, Feature Being Tested, and Hypothesis")
                return
            
            saved_sample_size = st.session_state.form_data.get('calculated_sample_size')
            if not saved_sample_size:
                st.error("❌ Sample size calculation failed. Please check your test parameters.")
                return
            
            # Get saved values from session state
            saved_runtime = st.session_state.form_data.get('estimated_runtime')
            saved_daily_users = st.session_state.form_data.get('daily_users_calculated')
            
            # Create final form data
            final_form_data = {
                'experiment_name': experiment_name,
                'feature_description': feature_description,
                'hypothesis': hypothesis,
                'test_type': test_type,
                'primary_metric': primary_metric,
                'baseline_value': baseline_value,
                'expected_lift': expected_lift if test_type == "Superiority Test" else None,
                'non_inferiority_margin': non_inferiority_margin if test_type == "Non-Inferiority Test" else None,
                'secondary_metrics': secondary_metrics,
                'campaign': campaign,
                'traffic_type': traffic_type,
                'user_segment': user_segment,
                'control_variant': control_variant,
                'treatment_variant': treatment_variant,
                'device_type': device_type,
                'traffic_period': st.session_state.form_data.get('traffic_period', 'Daily'),
                'daily_users': saved_daily_users or 0,
                'calculated_sample_size': saved_sample_size,
                'estimated_runtime': saved_runtime,
                'priority': priority,
                'business_goal': business_goal
            }
            
            # Save to session state
            st.session_state.form_data.update(final_form_data)
            
            # Generate PDF
            pdf_generator = PDFGenerator()
            pdf_buffer = pdf_generator.create_experiment_pdf(final_form_data)
            
            st.success("✅ Experiment design generated successfully!")
            
            # Display final summary
            st.subheader("📋 Final Experiment Summary")
            st.write(f"**Experiment:** {experiment_name}")
            st.write(f"**Test Type:** {test_type}")
            st.write(f"**Primary Metric:** {primary_metric} (Baseline: {baseline_value}%)")
            if test_type == "Superiority Test":
                st.write(f"**Expected Lift:** {expected_lift}%")
            else:
                st.write(f"**Non-Inferiority Margin:** {non_inferiority_margin}%")
            st.write(f"**Sample Size:** {saved_sample_size:,} users per group ({saved_sample_size*2:,} total)")
            st.write(f"**Runtime:** {saved_runtime} days")
            st.write(f"**Priority:** {priority}")
            
            # Download button
            st.download_button(
                label="📥 Download Experiment Design (PDF)",
                data=pdf_buffer,
                file_name=f"experiment_design_{experiment_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                type="primary"
            )

def sample_size_calculator():
    st.markdown('<div class="step-header"><h2>📊 Sample Size Calculator</h2></div>', unsafe_allow_html=True)
    st.markdown("Calculate required sample sizes for different test types with detailed explanations")
    
    test_type = st.selectbox(
        "🎯 Test Type",
        ["Two-Proportion Z-Test", "Continuous Metric T-Test", "Non-Inferiority Test"],
        help="Choose the appropriate test type based on your metric and hypothesis"
    )
    
    # Test explanations
    if test_type == "Two-Proportion Z-Test":
        st.info("📊 Use for percentage-based metrics like App Rate, Conversion Rate, etc. Tests if two proportions are significantly different.")
    elif test_type == "Continuous Metric T-Test":
        st.info("📊 Use for continuous metrics like Revenue, EPL, etc. Tests if two means are significantly different.")
    else:
        st.info("📊 Use when you want to show that a new version is not worse than the current version by more than a specified margin.")
    
    # Test parameters
    st.subheader("🔬 Test Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        alpha = st.number_input("Significance Level (α)", value=0.05, min_value=0.01, max_value=0.10, help="Probability of Type I error (false positive)")
    with col2:
        power = st.number_input("Statistical Power", value=0.80, min_value=0.70, max_value=0.99, help="Probability of detecting a true effect (1 - Type II error)")
    
    calc = SampleSizeCalculator()
    
    if test_type == "Two-Proportion Z-Test":
        st.subheader("📊 Proportion Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            p1 = st.number_input("Control Rate (%)", value=75.0, help="Current conversion rate") / 100
        with col2:
            p2 = st.number_input("Treatment Rate (%)", value=76.2, help="Expected treatment conversion rate") / 100
        
        if st.button("🔢 Calculate Sample Size", type="primary"):
            n = calc.calculate_proportions(p1, p2, alpha, power)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 Sample Size (per group)", f"{n:,}")
            with col2:
                st.metric("👥 Total Sample Size", f"{n*2:,}")
            
            st.success("✅ Calculation complete! Each group needs at least this many users to detect the difference with the specified power and significance level.")
            
    elif test_type == "Continuous Metric T-Test":
        st.subheader("📊 Continuous Metric Parameters")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            mean1 = st.number_input("Control Mean", value=100.0, help="Average value in control group")
        with col2:
            mean2 = st.number_input("Treatment Mean", value=105.0, help="Expected average value in treatment group")
        with col3:
            std = st.number_input("Standard Deviation", value=20.0, help="Standard deviation of the metric")
        
        if st.button("🔢 Calculate Sample Size", type="primary"):
            n = calc.calculate_continuous(mean1, mean2, std, alpha, power)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 Sample Size (per group)", f"{n:,}")
            with col2:
                st.metric("👥 Total Sample Size", f"{n*2:,}")
            
            effect_size = abs(mean1 - mean2) / std
            st.write(f"**Effect Size (Cohen's d):** {effect_size:.3f}")
            
    else:  # Non-Inferiority Test
        st.subheader("📊 Non-Inferiority Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            p1 = st.number_input("Control Rate (%)", value=75.0, help="Current conversion rate") / 100
        with col2:
            delta = st.number_input("Non-Inferiority Margin (% absolute)", value=1.0, help="Maximum acceptable decrease (absolute)") / 100
        
        st.info(f"📊 Testing if treatment rate ≥ {(p1-delta)*100:.1f}% (i.e., not worse than {delta*100:.1f}% absolute decrease)")
        
        if st.button("🔢 Calculate Sample Size", type="primary"):
            n = calc.calculate_non_inferiority(p1, delta, alpha, power)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 Sample Size (per group)", f"{n:,}")
            with col2:
                st.metric("👥 Total Sample Size", f"{n*2:,}")
    
    # Runtime estimation
    if 'n' in locals():
        st.subheader("⏱️ Runtime Estimation")
        
        daily_traffic = st.number_input("Daily Users", value=12000, help="Total daily users entering the experiment")
        
        runtime = calc.estimate_runtime(n*2, daily_traffic)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("⏱️ Estimated Runtime", f"{runtime} days")
        with col2:
            st.metric("👥 Daily Users per Group", f"{daily_traffic//2:,}")
        
        # Traffic allocation details
        st.subheader("🚦 Traffic Allocation")
        allocation_df = pd.DataFrame({
            'Group': ['Control', 'Treatment', 'Total'],
            'Daily Users': [f"{daily_traffic//2:,}", f"{daily_traffic//2:,}", f"{daily_traffic:,}"],
            'Total Users Needed': [f"{n:,}", f"{n:,}", f"{n*2:,}"],
            'Days to Complete': [f"{runtime}", f"{runtime}", f"{runtime}"]
        })
        st.dataframe(allocation_df, use_container_width=True)

if __name__ == "__main__":
    main()