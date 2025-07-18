import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm, t
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def post_experiment_analysis():
    st.markdown('<div class="step-header"><h2>📊 Post-Experiment Analysis</h2></div>', unsafe_allow_html=True)
    st.markdown("Analyze your completed experiment results and determine statistical and practical significance")
    
    # ===== STEP 1: EXPERIMENT TYPE & METRIC =====
    st.markdown('<div class="subsection-header"><h3>Step 1: Experiment Configuration</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        experiment_type = st.selectbox(
            "Experiment Type",
            ["Superiority", "Non-inferiority"],
            help="Superiority: Test if treatment is better than control. Non-inferiority: Test if treatment is not worse than control by more than a margin."
        )
    
    with col2:
        primary_metric = st.selectbox(
            "Primary Metric",
            ["App Rate", "Revenue", "EPL"],
            help="App Rate: Binary outcome (conversion). Revenue/EPL: Continuous outcome."
        )
    
    # ===== STEP 2: CONTROL GROUP DATA =====
    st.markdown('<div class="subsection-header"><h3>Step 2: Control Group Results</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        control_sample_size = st.number_input(
            "Control Sample Size",
            min_value=1,
            value=1000,
            help="Number of users in control group"
        )
    
    if primary_metric == "App Rate":
        with col2:
            control_successes = st.number_input(
                "Control Applications",
                min_value=0,
                max_value=control_sample_size,
                value=100,
                help="Number of applications in control group"
            )
        control_rate = control_successes / control_sample_size if control_sample_size > 0 else 0
        st.info(f"Control App Rate: {control_rate:.3f} ({control_successes}/{control_sample_size})")
    else:
        with col2:
            control_mean = st.number_input(
                "Control Mean",
                value=50.0,
                help=f"Average {primary_metric.lower()} per user in control group"
            )
        control_std = st.number_input(
            "Control Standard Deviation",
            min_value=0.1,
            value=10.0,
            help=f"Standard deviation of {primary_metric.lower()} in control group"
        )
    
    # ===== STEP 3: TREATMENT GROUP DATA =====
    st.markdown('<div class="subsection-header"><h3>Step 3: Treatment Group Results</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        treatment_sample_size = st.number_input(
            "Treatment Sample Size",
            min_value=1,
            value=1000,
            help="Number of users in treatment group"
        )
    
    if primary_metric == "App Rate":
        with col2:
            treatment_successes = st.number_input(
                "Treatment Applications",
                min_value=0,
                max_value=treatment_sample_size,
                value=110,
                help="Number of applications in treatment group"
            )
        treatment_rate = treatment_successes / treatment_sample_size if treatment_sample_size > 0 else 0
        st.info(f"Treatment App Rate: {treatment_rate:.3f} ({treatment_successes}/{treatment_sample_size})")
    else:
        with col2:
            treatment_mean = st.number_input(
                "Treatment Mean",
                value=55.0,
                help=f"Average {primary_metric.lower()} per user in treatment group"
            )
        treatment_std = st.number_input(
            "Treatment Standard Deviation",
            min_value=0.1,
            value=10.0,
            help=f"Standard deviation of {primary_metric.lower()} in treatment group"
        )
    
    # ===== STEP 4: PRE-EXPERIMENT PARAMETERS =====
    st.markdown('<div class="subsection-header"><h3>Step 4: Pre-Experiment Design Parameters</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if experiment_type == "Superiority":
            mde = st.number_input(
                "Minimum Detectable Effect (MDE)",
                min_value=0.0001,
                max_value=1.0 if primary_metric == "App Rate" else 1000.0,
                value=0.05 if primary_metric == "App Rate" else 5.0,
                step=0.0001 if primary_metric == "App Rate" else 0.01,
                format="%.4f" if primary_metric == "App Rate" else "%.2f",
                help="Minimum effect size considered meaningful (absolute difference, e.g., 0.015 = 1.5 percentage points for App Rate)"
            )
        else:
            # For non-inferiority, we don't use MDE
            mde = None
    
    with col2:
        alpha = st.number_input(
            "Significance Level (α)",
            min_value=0.01,
            max_value=0.1,
            value=0.05,
            step=0.01,
            help="Type I error rate (typically 0.05)"
        )
    
    if experiment_type == "Non-inferiority":
        non_inferiority_margin = st.number_input(
            "Non-inferiority Margin",
            min_value=0.0001,
            max_value=1.0 if primary_metric == "App Rate" else 100.0,
            value=0.02 if primary_metric == "App Rate" else 2.0,
            step=0.0001 if primary_metric == "App Rate" else 0.01,
            format="%.4f" if primary_metric == "App Rate" else "%.2f",
            help="Maximum acceptable difference for non-inferiority (absolute difference, e.g., 0.015 = 1.5 percentage points for App Rate)"
        )
    else:
        non_inferiority_margin = None
    
    # ===== STEP 5: ANALYSIS =====
    if st.button("🔍 Analyze Results", type="primary"):
        perform_analysis(
            experiment_type, primary_metric,
            control_sample_size, control_successes if primary_metric == "App Rate" else control_mean,
            control_std if primary_metric != "App Rate" else None,
            treatment_sample_size, treatment_successes if primary_metric == "App Rate" else treatment_mean,
            treatment_std if primary_metric != "App Rate" else None,
            mde, alpha,
            non_inferiority_margin
        )

def perform_analysis(experiment_type, primary_metric, control_n, control_data, control_std,
                    treatment_n, treatment_data, treatment_std, mde, alpha, non_inferiority_margin=None):
    """Perform statistical analysis based on metric type and experiment type"""
    
    st.markdown('<div class="step-header"><h3>📈 Analysis Results</h3></div>', unsafe_allow_html=True)
    
    if primary_metric == "App Rate":
        # Binary outcome analysis
        control_rate = control_data / control_n
        treatment_rate = treatment_data / treatment_n
        
        # Calculate effect size and test statistic
        pooled_rate = (control_data + treatment_data) / (control_n + treatment_n)
        se = np.sqrt(pooled_rate * (1 - pooled_rate) * (1/control_n + 1/treatment_n))
        
        if experiment_type == "Superiority":
            effect_size = treatment_rate - control_rate
            z_stat = effect_size / se
            p_value = 1 - norm.cdf(z_stat)  # One-tailed test
        else:
            # Non-inferiority test
            effect_size = treatment_rate - control_rate
            z_stat = (effect_size + non_inferiority_margin) / se
            p_value = 1 - norm.cdf(z_stat)  # One-tailed test
        
        # Calculate confidence interval
        ci_lower = effect_size - norm.ppf(1 - alpha/2) * se
        ci_upper = effect_size + norm.ppf(1 - alpha/2) * se
        
        display_results(
            experiment_type, primary_metric,
            effect_size, p_value, alpha,
            ci_lower, ci_upper,
            mde,
            non_inferiority_margin=non_inferiority_margin
        )
        
    else:
        # Continuous outcome analysis
        control_mean = control_data
        treatment_mean = treatment_data
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((control_n - 1) * control_std**2 + (treatment_n - 1) * treatment_std**2) / (control_n + treatment_n - 2))
        
        # Calculate effect size and test statistic
        effect_size = treatment_mean - control_mean
        se = pooled_std * np.sqrt(1/control_n + 1/treatment_n)
        df = control_n + treatment_n - 2
        
        if experiment_type == "Superiority":
            t_stat = effect_size / se
            p_value = 1 - t.cdf(t_stat, df)  # One-tailed test
        else:
            # Non-inferiority test
            t_stat = (effect_size + non_inferiority_margin) / se
            p_value = 1 - t.cdf(t_stat, df)  # One-tailed test
        
        # Calculate confidence interval
        ci_lower = effect_size - t.ppf(1 - alpha/2, df) * se
        ci_upper = effect_size + t.ppf(1 - alpha/2, df) * se
        
        display_results(
            experiment_type, primary_metric,
            effect_size, p_value, alpha,
            ci_lower, ci_upper,
            mde,
            non_inferiority_margin=non_inferiority_margin
        )

# Removed power calculation functions as they are pre-experiment design concepts

def display_results(experiment_type, primary_metric, effect_size, p_value, alpha, 
                   ci_lower, ci_upper, mde, 
                   non_inferiority_margin=None):
    """Display analysis results with visualizations"""
    
    # ===== STATISTICAL SIGNIFICANCE =====
    st.markdown('<div class="subsection-header"><h4>Statistical Significance</h4></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "P-value",
            f"{p_value:.4f}",
            delta="Significant" if p_value < alpha else "Not Significant",
            delta_color="normal" if p_value < alpha else "inverse"
        )
    
    with col2:
        significance_decision = "✅ Significant" if p_value < alpha else "❌ Not Significant"
        st.metric("Decision", significance_decision)
    
    with col3:
        effect_direction = "🟢 Positive" if effect_size > 0 else "🔴 Negative"
        st.metric("Effect Direction", effect_direction)
    
    # ===== EFFECT SIZE & CONFIDENCE INTERVALS =====
    st.markdown('<div class="subsection-header"><h4>Effect Size & Confidence Intervals</h4></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Effect Size",
            f"{effect_size:.4f}",
            help=f"Difference between treatment and control groups"
        )
        
        # Removed risk_ratio and cohens_d as they are pre-experiment concepts
    
    with col2:
        st.metric(
            f"{int((1-alpha)*100)}% Confidence Interval",
            f"[{ci_lower:.4f}, {ci_upper:.4f}]",
            help=f"Range where we are {(1-alpha)*100}% confident the true effect lies"
        )
    
    # ===== PRACTICAL SIGNIFICANCE =====
    st.markdown('<div class="subsection-header"><h4>Practical Significance</h4></div>', unsafe_allow_html=True)
    
    if experiment_type == "Superiority":
        # For superiority tests, check if effect size meets MDE
        meets_mde = abs(effect_size) >= mde if mde is not None else False
        ci_meets_mde = abs(ci_lower) >= mde if ci_lower > 0 and mde is not None else abs(ci_upper) >= mde if mde is not None else False
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Meets MDE",
                "✅ Yes" if meets_mde else "❌ No",
                delta=f"MDE: {mde:.4f}" if mde is not None else "N/A"
            )
        
        with col2:
            st.metric(
                "CI Meets MDE",
                "✅ Yes" if ci_meets_mde else "❌ No",
                help="Confidence interval excludes zero and meets MDE"
            )
        
        # Removed achieved_power_pct and power_label/power_help as they are pre-experiment concepts
        
    else:
        # For non-inferiority tests, check if treatment is within the margin
        within_margin = effect_size > -non_inferiority_margin if non_inferiority_margin is not None else False
        ci_within_margin = ci_lower > -non_inferiority_margin if non_inferiority_margin is not None else False
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Within Margin",
                "✅ Yes" if within_margin else "❌ No",
                delta=f"Margin: {non_inferiority_margin:.4f}" if non_inferiority_margin is not None else "N/A"
            )
        
        with col2:
            st.metric(
                "CI Within Margin",
                "✅ Yes" if ci_within_margin else "❌ No",
                help="Confidence interval is entirely within the non-inferiority margin"
            )
        
        # Removed achieved_power_pct and power_label/power_help as they are pre-experiment concepts
    
    # Removed Power Adequacy Warning as it's a pre-experiment concept
    
    # ===== RECOMMENDATION =====
    st.markdown('<div class="subsection-header"><h4>Recommendation</h4></div>', unsafe_allow_html=True)
    
    if experiment_type == "Superiority":
        if p_value < alpha and meets_mde:
            recommendation = "✅ **IMPLEMENT** - Significant and meaningful effect"
        elif p_value < alpha and not meets_mde:
            recommendation = "⚠️ **CONSIDER** - Significant but may not be meaningful"
        elif p_value >= alpha:
            recommendation = "❌ **DON'T IMPLEMENT** - No significant effect detected"
        else:
            recommendation = "🔄 **RUN LONGER** - Inconclusive results"
    else:
        # Non-inferiority
        if p_value < alpha and within_margin:
            recommendation = "✅ **IMPLEMENT** - Non-inferiority demonstrated"
        elif p_value < alpha and not within_margin:
            recommendation = "❌ **DON'T IMPLEMENT** - Treatment is inferior"
        elif p_value >= alpha:
            recommendation = "❌ **DON'T IMPLEMENT** - Non-inferiority not demonstrated"
        else:
            recommendation = "🔄 **RUN LONGER** - Inconclusive results"
    
    st.info(recommendation)
    
    # ===== VISUALIZATION =====
    st.markdown('<div class="subsection-header"><h4>Effect Size Visualization</h4></div>', unsafe_allow_html=True)
    
    # Create forest plot
    fig = go.Figure()
    
    # Add effect size point
    fig.add_trace(go.Scatter(
        x=[effect_size],
        y=['Effect Size'],
        mode='markers',
        marker=dict(size=12, color='blue'),
        name='Point Estimate',
        showlegend=False
    ))
    
    # Add confidence interval
    fig.add_trace(go.Scatter(
        x=[ci_lower, ci_upper],
        y=['Effect Size', 'Effect Size'],
        mode='lines',
        line=dict(color='blue', width=2),
        name='95% CI',
        showlegend=False
    ))
    
    # Add reference lines based on test type
    if experiment_type == "Superiority":
        # For superiority tests, show MDE lines
        if mde is not None:
            fig.add_vline(x=mde, line_dash="dash", line_color="red", annotation_text="MDE")
            fig.add_vline(x=-mde, line_dash="dash", line_color="red")
        fig.add_vline(x=0, line_dash="dot", line_color="gray", annotation_text="No Effect")
    else:
        # For non-inferiority tests, show margin lines
        if non_inferiority_margin is not None:
            fig.add_vline(x=-non_inferiority_margin, line_dash="dash", line_color="orange", 
                         annotation_text="Non-inferiority Margin")
        fig.add_vline(x=0, line_dash="dot", line_color="gray", annotation_text="No Effect")
    
    fig.update_layout(
        title=f"Effect Size with Confidence Interval ({experiment_type} Test)",
        xaxis_title="Effect Size",
        yaxis_title="",
        height=300,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True) 