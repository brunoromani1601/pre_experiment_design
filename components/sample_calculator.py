import streamlit as st
import pandas as pd
from core.calculator import SampleSizeCalculator
from core.session_manager import SessionManager

def sample_size_calculator():
    st.markdown('<div class="step-header"><h2>📊 Sample Size Calculator</h2></div>', unsafe_allow_html=True)
    st.markdown("Calculate required sample sizes for different test types with detailed explanations")
    
    # Initialize session state for sample size calculator
    if 'calculator_sample_size' not in st.session_state:
        st.session_state.calculator_sample_size = None
    if 'calculator_test_type' not in st.session_state:
        st.session_state.calculator_test_type = None
    
    test_type = st.selectbox(
        "🎯 Test Type",
        ["Two-Proportion Z-Test", "Continuous Metric T-Test", "Non-Inferiority Test"],
        help="Choose the appropriate test type: Two-Proportion Z-Test for percentage metrics (App Rate, Conversion Rate), Continuous Metric T-Test for continuous metrics (Revenue, EPL), or Non-Inferiority Test to show new version is not worse than current by more than a specified margin."
    )
    
    # Reset sample size if test type changes
    if test_type != st.session_state.calculator_test_type:
        st.session_state.calculator_sample_size = None
        st.session_state.calculator_test_type = test_type
    
    # Test explanations - removed to clean up UI
    # if test_type == "Two-Proportion Z-Test":
    #     st.info("📊 Use for percentage-based metrics like App Rate, Conversion Rate, etc. Tests if two proportions are significantly different.")
    # elif test_type == "Continuous Metric T-Test":
    #     st.info("📊 Use for continuous metrics like Revenue, EPL, etc. Tests if two means are significantly different.")
    # else:
    #     st.info("📊 Use when you want to show that a new version is not worse than the current version by more than a specified margin.")
    
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
            baseline_rate = st.number_input("Baseline Rate (%)", value=75.0, help="Current conversion rate") / 100
        with col2:
            expected_lift = st.number_input("Expected Lift (% absolute)", value=1.2, help="Expected improvement in absolute percentage points") / 100
        
        # Calculate treatment rate for display
        treatment_rate = baseline_rate + expected_lift
        
        # Show what we're testing - removed to clean up UI
        # st.info(f"📊 Testing if treatment rate ≥ {(baseline_rate + expected_lift)*100:.1f}% (baseline {baseline_rate*100:.1f}% + {expected_lift*100:.1f}% lift)")
        
        if st.button("🔢 Calculate Sample Size", type="primary"):
            n = calc.calculate_proportions(baseline_rate, treatment_rate, alpha, power)
            st.session_state.calculator_sample_size = n
            
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
            baseline_mean = st.number_input("Baseline Mean", value=100.0, help="Current average value")
        with col2:
            expected_lift = st.number_input("Expected Lift", value=5.0, help="Expected improvement in absolute units")
        with col3:
            std = st.number_input("Standard Deviation", value=20.0, help="Standard deviation of the metric")
        
        # Calculate treatment mean for display
        treatment_mean = baseline_mean + expected_lift
        
        # Show what we're testing - removed to clean up UI
        # st.info(f"📊 Testing if treatment mean ≥ {treatment_mean:.1f} (baseline {baseline_mean:.1f} + {expected_lift:.1f} lift)")
        
        if st.button("🔢 Calculate Sample Size", type="primary"):
            n = calc.calculate_continuous(baseline_mean, treatment_mean, std, alpha, power)
            st.session_state.calculator_sample_size = n
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 Sample Size (per group)", f"{n:,}")
            with col2:
                st.metric("👥 Total Sample Size", f"{n*2:,}")
            
            effect_size = abs(expected_lift) / std
            st.write(f"**Effect Size (Cohen's d):** {effect_size:.3f}")
            
    else:  # Non-Inferiority Test
        st.subheader("📊 Non-Inferiority Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            baseline_rate = st.number_input("Baseline Rate (%)", value=75.0, help="Current conversion rate") / 100
        with col2:
            delta = st.number_input("Non-Inferiority Margin (% absolute)", value=1.0, help="Maximum acceptable decrease (absolute)") / 100
        
        # Show what we're testing - removed to clean up UI
        # st.info(f"📊 Testing if treatment rate ≥ {(baseline_rate-delta)*100:.1f}% (i.e., not worse than {delta*100:.1f}% absolute decrease)")
        
        if st.button("🔢 Calculate Sample Size", type="primary"):
            n = calc.calculate_non_inferiority(baseline_rate, delta, alpha, power)
            st.session_state.calculator_sample_size = n
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 Sample Size (per group)", f"{n:,}")
            with col2:
                st.metric("👥 Total Sample Size", f"{n*2:,}")
    
    # Runtime estimation - now always available if sample size is calculated
    if st.session_state.calculator_sample_size is not None:
        st.subheader("⏱️ Runtime Estimation")
        
        # Show current sample size - removed to clean up UI
        # n = st.session_state.calculator_sample_size
        # st.info(f"📊 Using calculated sample size: {n:,} users per group ({n*2:,} total)")
        
        # Traffic period selection
        traffic_period = st.radio(
            "📅 Traffic Period",
            ["Daily", "Weekly", "Monthly"],
            help="Select the time period for your traffic volume"
        )
        
        # Traffic volume input based on period
        if traffic_period == "Daily":
            traffic_volume = st.number_input(
                "👥 Daily Users",
                value=12000,
                help="Total daily users entering the experiment"
            )
            daily_traffic = traffic_volume
            original_traffic_display = f"{traffic_volume:,} users/day"
        elif traffic_period == "Weekly":
            weekly_traffic = st.number_input(
                "👥 Weekly Users",
                value=84000,
                help="Total weekly users entering the experiment"
            )
            daily_traffic = weekly_traffic / 7
            original_traffic_display = f"{weekly_traffic:,} users/week"
        else:  # Monthly
            monthly_traffic = st.number_input(
                "👥 Monthly Users",
                value=360000,
                help="Total monthly users entering the experiment"
            )
            daily_traffic = monthly_traffic / 30
            original_traffic_display = f"{monthly_traffic:,} users/month"
        
        # Calculate runtime
        n = st.session_state.calculator_sample_size
        runtime = calc.estimate_runtime(n*2, daily_traffic)
        
        # Display traffic conversion info - removed to clean up UI
        # st.info(f"📊 Traffic: {original_traffic_display} = {daily_traffic:,.0f} users/day average")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("⏱️ Estimated Runtime", f"{runtime} days")
        with col2:
            st.metric("👥 Daily Users per Group", f"{daily_traffic//2:,.0f}")
        
        # Traffic allocation details
        st.subheader("🚦 Traffic Allocation")
        allocation_df = pd.DataFrame({
            'Group': ['Control', 'Treatment', 'Total'],
            'Daily Users': [f"{daily_traffic//2:,.0f}", f"{daily_traffic//2:,.0f}", f"{daily_traffic:,.0f}"],
            'Total Users Needed': [f"{n:,}", f"{n:,}", f"{n*2:,}"],
            'Days to Complete': [f"{runtime}", f"{runtime}", f"{runtime}"]
        })
        st.dataframe(allocation_df, use_container_width=True)
        
        # Additional insights based on runtime
        if runtime > 30:
            st.warning(f"⚠️ Long runtime ({runtime} days). Consider increasing traffic volume or adjusting test parameters.")
        elif runtime < 7:
            st.success(f"✅ Quick experiment - will complete in {runtime} days.")
        # Removed the moderate runtime info box to clean up UI 