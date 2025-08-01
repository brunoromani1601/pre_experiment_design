import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm, t
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from core.notion_integration import NotionIntegration
import time

@st.cache_data(ttl=600)  # Cache for 10 minutes (increased from 5)
def get_notion_campaigns():
    """Cached function to get Notion campaigns"""
    try:
        notion_integration = NotionIntegration()
        return notion_integration.get_campaign_options()
    except Exception as e:
        st.error(f"❌ Error loading EPCVIP Campaigns: {e}")
        return []

@st.cache_data(ttl=600)  # Cache for 10 minutes (increased from 5)
def get_campaigns_with_experiments():
    """Cached function to get campaigns that have experiments"""
    try:
        notion_integration = NotionIntegration()
        return notion_integration.get_campaigns_with_experiments()
    except Exception as e:
        st.error(f"❌ Error loading campaigns with experiments: {e}")
        return []

@st.cache_data(ttl=600)  # Cache for 10 minutes (increased from 5)
def get_notion_initiatives():
    """Cached function to get Notion initiatives"""
    try:
        notion_integration = NotionIntegration()
        return notion_integration.get_initiative_options()
    except Exception as e:
        st.error(f"❌ Error loading EPCVIP Initiatives: {e}")
        return []

@st.cache_data(ttl=600)  # Cache for 10 minutes (increased from 5)
def get_initiatives_for_campaign(campaign_name):
    """Cached function to get initiatives for a specific campaign"""
    try:
        notion_integration = NotionIntegration()
        return notion_integration.get_initiatives_for_campaign(campaign_name)
    except Exception as e:
        st.error(f"❌ Error loading initiatives for campaign: {e}")
        return []

def post_experiment_analysis():
    st.markdown('<div class="step-header"><h2>📊 Post-Experiment Analysis</h2></div>', unsafe_allow_html=True)
    st.markdown("Analyze your completed experiment results from Notion data")
    
    # Performance tracking
    start_time = time.time()
    
    # Initialize session state for performance
    if 'post_analysis_initialized' not in st.session_state:
        st.session_state.post_analysis_initialized = True
        st.session_state.last_campaign_selection = None
        st.session_state.last_initiative_selection = None
    
    # ===== STEP 1: SELECT EXPERIMENT FROM NOTION =====
    st.markdown('<div class="subsection-header"><h3>Step 1: Select Experiment from Notion</h3></div>', unsafe_allow_html=True)
    
    # Add refresh button with performance indicator
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Data", help="Refresh campaign and initiative data from Notion"):
            st.cache_data.clear()
            st.session_state.last_campaign_selection = None
            st.session_state.last_initiative_selection = None
            st.rerun()
    
    try:
        # Show loading indicator only on first load
        if 'campaigns_loaded' not in st.session_state:
            with st.spinner("Loading campaigns..."):
                notion_integration = NotionIntegration()
                
                # Get campaigns that actually have experiments
                campaigns_with_experiments = get_campaigns_with_experiments()
                st.session_state.campaigns_loaded = True
                st.session_state.campaigns_data = campaigns_with_experiments
        else:
            notion_integration = NotionIntegration()
            campaigns_with_experiments = st.session_state.campaigns_data
        
        if not campaigns_with_experiments:
            st.error("❌ No campaigns with experiments found. Please create experiments using the Experiment Design Tool first.")
            st.info("💡 **Tip:** Go to the Experiment Design Tool and create some experiments with campaigns and features.")
            return
        
        with col1:
            selected_campaign = st.selectbox(
                "🎯 Select Campaign",
                ["None"] + campaigns_with_experiments,
                help="Select a campaign that has experiments"
            )
        
        # Get initiatives for the selected campaign (only when campaign changes)
        if selected_campaign != "None":
            # Check if campaign changed
            if selected_campaign != st.session_state.last_campaign_selection:
                with st.spinner(f"Loading initiatives for {selected_campaign}..."):
                    campaign_initiatives = get_initiatives_for_campaign(selected_campaign)
                    st.session_state.last_campaign_selection = selected_campaign
                    st.session_state.campaign_initiatives = campaign_initiatives
            else:
                campaign_initiatives = st.session_state.campaign_initiatives
            
            if not campaign_initiatives:
                st.warning(f"⚠️ No experiments found for campaign '{selected_campaign}'. Please select a different campaign or create experiments for this campaign first.")
                st.info("💡 **Tip:** Make sure you have created experiments using the Experiment Design Tool for this campaign.")
                return
            
            col3, col4 = st.columns(2)
            
            with col3:
                selected_initiative = st.selectbox(
                    "🎯 Select Feature/Initiative",
                    ["None"] + campaign_initiatives,
                    help=f"Select the feature/initiative for campaign '{selected_campaign}'"
                )
            
            # Fetch experiment data (only when initiative changes)
            if selected_initiative != "None":
                with st.spinner(f"Loading experiment data..."):
                    experiment = notion_integration.get_experiment_by_campaign_and_feature(selected_campaign, selected_initiative)
                
                if experiment:
                    st.success(f"✅ Found experiment: {selected_campaign} - {selected_initiative}")
                    
                    # Get experiment content and parse design parameters (cached)
                    with st.spinner("Parsing experiment design..."):
                        experiment_content = notion_integration.get_experiment_content(experiment['id'])
                        design_data = notion_integration.parse_experiment_design(experiment_content)
                    
                    # Display experiment design summary
                    st.subheader("📋 Experiment Design Summary")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Design Parameters:**")
                        if design_data.get('test_type'):
                            st.write(f"• Test Type: {design_data['test_type']}")
                        if design_data.get('primary_metric'):
                            st.write(f"• Primary Metric: {design_data['primary_metric']}")
                        if design_data.get('baseline_value') is not None:
                            st.write(f"• Baseline Value: {design_data['baseline_value']}%")
                        if design_data.get('sample_size'):
                            st.write(f"• Required Sample Size: {design_data['sample_size']:,} per group")
                        if design_data.get('total_sample_size'):
                            st.write(f"• Total Sample Size: {design_data['total_sample_size']:,}")
                    
                    with col2:
                        st.write("**Test Parameters:**")
                        if design_data.get('expected_lift') is not None:
                            st.write(f"• Expected Lift: {design_data['expected_lift']}%")
                        if design_data.get('non_inferiority_margin') is not None:
                            st.write(f"• Non-Inferiority Margin: {design_data['non_inferiority_margin']}%")
                    
                    # Check if we have all required data
                    missing_data = []
                    if not design_data.get('test_type'):
                        missing_data.append("Test Type")
                    if not design_data.get('primary_metric'):
                        missing_data.append("Primary Metric")
                    if design_data.get('baseline_value') is None:
                        missing_data.append("Baseline Value")
                    if not design_data.get('sample_size'):
                        missing_data.append("Sample Size")
                    
                    if missing_data:
                        st.error(f"❌ Missing experiment design data: {', '.join(missing_data)}")
                        st.info("Please ensure the experiment was created using the Experiment Design Tool.")
                        return
                    
                    # Check if post-experiment results are available
                    post_experiment_data = notion_integration.parse_post_experiment_results(experiment_content)
                    
                    if not post_experiment_data:
                        st.error("❌ No post-experiment results found in Notion.")
                        st.info("💡 **Tip:** Add actual results in the Notion experiment page.")
                        return
                    
                    # Store design data in session state
                    st.session_state.experiment_design = design_data
                    st.session_state.selected_experiment = experiment
                    st.session_state.post_experiment_data = post_experiment_data
                    
                    # Display post-experiment results
                    st.subheader("📊 Post-Experiment Results (from Notion)")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Control Group:**")
                        st.write(f"• Sample Size: {post_experiment_data['control_sample_size']:,}")
                        if design_data['primary_metric'] in ["App Rate", "Sold Rate", "Fund Rate"]:
                            st.write(f"• Applications: {post_experiment_data['control_applications']:,}")
                            control_rate = post_experiment_data['control_applications'] / post_experiment_data['control_sample_size']
                            st.write(f"• Rate: {control_rate:.3f}")
                        else:
                            st.write(f"• Mean: {post_experiment_data['control_mean']:.2f}")
                    
                    with col2:
                        st.write("**Treatment Group:**")
                        st.write(f"• Sample Size: {post_experiment_data['treatment_sample_size']:,}")
                        if design_data['primary_metric'] in ["App Rate", "Sold Rate", "Fund Rate"]:
                            st.write(f"• Applications: {post_experiment_data['treatment_applications']:,}")
                            treatment_rate = post_experiment_data['treatment_applications'] / post_experiment_data['treatment_sample_size']
                            st.write(f"• Rate: {treatment_rate:.3f}")
                        else:
                            st.write(f"• Mean: {post_experiment_data['treatment_mean']:.2f}")
                    
                    # ===== STEP 2: STATISTICAL ANALYSIS =====
                    st.markdown('<div class="subsection-header"><h3>Step 2: Statistical Analysis</h3></div>', unsafe_allow_html=True)
                    
                    # Check if sample sizes meet requirements
                    required_sample_size = design_data.get('sample_size', 0)
                    total_required = required_sample_size * 2
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📊 Sample Size Check")
                        st.metric("Required per group", f"{required_sample_size:,}")
                        st.metric("Control group", f"{post_experiment_data['control_sample_size']:,}")
                        st.metric("Treatment group", f"{post_experiment_data['treatment_sample_size']:,}")
                        
                        if (post_experiment_data['control_sample_size'] >= required_sample_size and 
                            post_experiment_data['treatment_sample_size'] >= required_sample_size):
                            st.success("✅ Sample sizes meet requirements!")
                        else:
                            st.warning("⚠️ Sample sizes below requirements")
                    
                    with col2:
                        st.subheader("📊 Total Sample Size")
                        total_actual = post_experiment_data['control_sample_size'] + post_experiment_data['treatment_sample_size']
                        st.metric("Required", f"{total_required:,}")
                        st.metric("Actual", f"{total_actual:,}")
                        
                        if total_actual >= total_required:
                            st.success("✅ Total sample size sufficient!")
                        else:
                            st.warning("⚠️ Total sample size below requirement")
                    
                    # Perform statistical analysis automatically
                    with st.spinner("Performing statistical analysis..."):
                        if design_data['primary_metric'] == "App Rate":
                            # Z-test for proportions
                            perform_proportion_analysis(
                                post_experiment_data['control_sample_size'], 
                                post_experiment_data['control_applications'],
                                post_experiment_data['treatment_sample_size'], 
                                post_experiment_data['treatment_applications'],
                                design_data
                            )
                        else:
                            # T-test for means
                            perform_mean_analysis(
                                post_experiment_data['control_sample_size'], 
                                post_experiment_data['control_mean'], 
                                10.0,  # Default std dev
                                post_experiment_data['treatment_sample_size'], 
                                post_experiment_data['treatment_mean'], 
                                10.0,  # Default std dev
                                design_data
                            )
                    
                else:
                    st.error(f"❌ No experiment found for {selected_campaign} - {selected_initiative}")
                    st.info("Please ensure the experiment exists and has the correct campaign and feature associations.")
                    return
            else:
                st.info("Please select a feature/initiative to continue.")
                return
        else:
            st.info("Please select a campaign to continue.")
            return
    
    except Exception as e:
        st.error(f"❌ Error connecting to Notion: {e}")
        st.info("Please check your Notion configuration and try again.")
        return
    
    # ===== STEP 2: ENTER EXPERIMENT RESULTS =====

def perform_proportion_analysis(control_n, control_successes, treatment_n, treatment_successes, design_data):
    """Perform statistical analysis for proportion data (App Rate)"""
    
    # Calculate rates
    control_rate = control_successes / control_n
    treatment_rate = treatment_successes / treatment_n
    
    # Calculate pooled proportion
    pooled_successes = control_successes + treatment_successes
    pooled_n = control_n + treatment_n
    pooled_rate = pooled_successes / pooled_n
    
    # Calculate standard error
    se = np.sqrt(pooled_rate * (1 - pooled_rate) * (1/control_n + 1/treatment_n))
    
    # Calculate test statistic
    z_stat = (treatment_rate - control_rate) / se
    
    # Calculate observed effect
    observed_effect = treatment_rate - control_rate
    
    # Calculate p-value based on test type
    if design_data['test_type'] == 'Superiority Test':
        # One-tailed test for superiority (H1: treatment > control)
        p_value = 1 - norm.cdf(z_stat)
    else:
        # Non-inferiority test: H0: treatment_rate - control_rate <= -margin
        # H1: treatment_rate - control_rate > -margin
        margin = design_data.get('non_inferiority_margin', 0) / 100
        # Test statistic for non-inferiority: (observed_effect - (-margin)) / se
        non_inferiority_z = (observed_effect - (-margin)) / se
        p_value = 1 - norm.cdf(non_inferiority_z)  # One-tailed test
    
    # Calculate confidence interval
    ci_lower = (treatment_rate - control_rate) - 1.96 * se
    ci_upper = (treatment_rate - control_rate) + 1.96 * se
    
    # Display results - Clean and concise
    st.subheader("📊 Statistical Results")
    
    # Key metrics in a clean format
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Control Rate", f"{control_rate:.3f}", f"{control_successes}/{control_n}")
        st.metric("Treatment Rate", f"{treatment_rate:.3f}", f"{treatment_successes}/{treatment_n}")
    
    with col2:
        st.metric("Difference", f"{observed_effect:.3f}")
        st.metric("P-value", f"{p_value:.4f}")
    
    # Test-specific results
    if design_data['test_type'] == 'Superiority Test':
        # Superiority test - focus on improvement
        st.subheader("🎯 Superiority Test Results")
        
        if p_value < 0.05:
            if observed_effect > 0:
                st.success("✅ **Statistically Significant Improvement**")
                st.write(f"Treatment is **{observed_effect:.3f}** better than control")
            else:
                st.error("❌ **Statistically Significant Decline**")
                st.write(f"Treatment is **{abs(observed_effect):.3f}** worse than control")
        else:
            st.warning("⚠️ **Not Statistically Significant**")
            st.write("Cannot conclude treatment is better than control")
        
        # Practical significance
        mde = design_data.get('expected_lift', 0) / 100
        if observed_effect >= mde:
            st.success(f"✅ **Practically Significant:** Exceeds MDE of {mde:.3f}")
        else:
            st.warning(f"⚠️ **Not Practically Significant:** Below MDE of {mde:.3f}")
    
    else:
        # Non-inferiority test - focus on margin
        margin = design_data.get('non_inferiority_margin', 0) / 100
        st.subheader("🎯 Non-Inferiority Test Results")
        
        if p_value < 0.05:
            st.success("✅ **Statistically Significant Non-Inferiority**")
            st.write(f"Treatment is not worse than control by more than {margin:.3f}")
        else:
            st.warning("⚠️ **Cannot Conclude Non-Inferiority**")
            st.write(f"Treatment may be worse than control by more than {margin:.3f}")
        
        # Practical significance
        if observed_effect >= -margin:
            st.success(f"✅ **Practically Significant:** Within margin of {margin:.3f}")
        else:
            st.warning(f"⚠️ **Not Practically Significant:** Outside margin of {margin:.3f}")
    
    # Confidence interval in expander
    with st.expander("📈 Confidence Interval", expanded=False):
        st.write(f"95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]")
        st.write(f"Standard Error: {se:.4f}")

def perform_mean_analysis(control_n, control_mean, control_std, treatment_n, treatment_mean, treatment_std, design_data):
    """Perform statistical analysis for mean data (Revenue, EPL)"""
    
    # Calculate pooled standard deviation
    pooled_std = np.sqrt(((control_n - 1) * control_std**2 + (treatment_n - 1) * treatment_std**2) / (control_n + treatment_n - 2))
    
    # Calculate standard error
    se = pooled_std * np.sqrt(1/control_n + 1/treatment_n)
    
    # Calculate t-statistic
    t_stat = (treatment_mean - control_mean) / se
    
    # Calculate observed effect
    observed_effect = treatment_mean - control_mean
    
    # Calculate degrees of freedom
    df = control_n + treatment_n - 2
    
    # Calculate p-value based on test type
    if design_data['test_type'] == 'Superiority Test':
        # One-tailed test for superiority (H1: treatment > control)
        p_value = 1 - t.cdf(t_stat, df)
    else:
        # Non-inferiority test: H0: treatment_mean - control_mean <= -margin
        # H1: treatment_mean - control_mean > -margin
        margin = design_data.get('non_inferiority_margin', 0)  # For means, this is already in original units
        # Test statistic for non-inferiority: (observed_effect - (-margin)) / se
        non_inferiority_t = (observed_effect - (-margin)) / se
        p_value = 1 - t.cdf(non_inferiority_t, df)  # One-tailed test
    
    # Calculate confidence interval
    ci_lower = (treatment_mean - control_mean) - 1.96 * se
    ci_upper = (treatment_mean - control_mean) + 1.96 * se
    
    # Display results - Clean and concise
    st.subheader("📊 Statistical Results")
    
    # Key metrics in a clean format
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Control Mean", f"{control_mean:.2f}")
        st.metric("Treatment Mean", f"{treatment_mean:.2f}")
    
    with col2:
        st.metric("Difference", f"{observed_effect:.2f}")
        st.metric("P-value", f"{p_value:.4f}")
    
    # Test-specific results
    if design_data['test_type'] == 'Superiority Test':
        # Superiority test - focus on improvement
        st.subheader("🎯 Superiority Test Results")
        
        if p_value < 0.05:
            if observed_effect > 0:
                st.success("✅ **Statistically Significant Improvement**")
                st.write(f"Treatment is **{observed_effect:.2f}** better than control")
            else:
                st.error("❌ **Statistically Significant Decline**")
                st.write(f"Treatment is **{abs(observed_effect):.2f}** worse than control")
        else:
            st.warning("⚠️ **Not Statistically Significant**")
            st.write("Cannot conclude treatment is better than control")
        
        # Practical significance
        mde = design_data.get('expected_lift', 0)  # For means, this is already in original units
        if observed_effect >= mde:
            st.success(f"✅ **Practically Significant:** Exceeds MDE of {mde:.2f}")
        else:
            st.warning(f"⚠️ **Not Practically Significant:** Below MDE of {mde:.2f}")
    
    else:
        # Non-inferiority test - focus on margin
        margin = design_data.get('non_inferiority_margin', 0)  # For means, this is already in original units
        st.subheader("🎯 Non-Inferiority Test Results")
        
        if p_value < 0.05:
            st.success("✅ **Statistically Significant Non-Inferiority**")
            st.write(f"Treatment is not worse than control by more than {margin:.2f}")
        else:
            st.warning("⚠️ **Cannot Conclude Non-Inferiority**")
            st.write(f"Treatment may be worse than control by more than {margin:.2f}")
        
        # Practical significance
        if observed_effect >= -margin:
            st.success(f"✅ **Practically Significant:** Within margin of {margin:.2f}")
        else:
            st.warning(f"⚠️ **Not Practically Significant:** Outside margin of {margin:.2f}")
    
    # Confidence interval in expander
    with st.expander("📈 Confidence Interval", expanded=False):
        st.write(f"95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]")
        st.write(f"Standard Error: {se:.4f}") 