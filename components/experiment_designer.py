import streamlit as st
from core.calculator import SampleSizeCalculator
from core.pdf_generator import PDFGenerator
from core.session_manager import SessionManager

def experiment_designer():
    st.markdown('<div class="step-header"><h2>🎯 Pre-Experiment Design Tool</h2></div>', unsafe_allow_html=True)
    
    # ===== STEP 1: BASIC INFORMATION =====
    st.markdown('<div class="step-header"><h3>Step 1: Basic Information</h3></div>', unsafe_allow_html=True)
    
    experiment_name = st.text_input(
        "🏷️ Experiment Name",
        value=SessionManager.get_form_data('experiment_name', ''),
        placeholder="e.g., Test Dynamic CTA Text on PPC Ad Chain",
        help="Give your experiment a descriptive name that clearly identifies what you're testing. Include the specific feature, component, or change you're testing.",
        key="experiment_name_input"
    )
    
    # Auto-save to session state
    if experiment_name != SessionManager.get_form_data('experiment_name', ''):
        SessionManager.set_form_data('experiment_name', experiment_name)
    
    feature_description = st.text_area(
        "⚙️ Feature Being Tested",
        value=SessionManager.get_form_data('feature_description', ''),
        placeholder="e.g., CTA text change from 'Apply Now' to 'Get Approved Fast'",
        help="Describe what you're testing in detail. Include any data analysis or insights that led to this experiment idea. Be specific about the change and why you think it will work.",
        key="feature_description_input"
    )
    
    # Auto-save to session state
    if feature_description != SessionManager.get_form_data('feature_description', ''):
        SessionManager.set_form_data('feature_description', feature_description)
    
    hypothesis = st.text_area(
        "🔬 Hypothesis",
        value=SessionManager.get_form_data('hypothesis', ''),
        placeholder="e.g., Changing CTA will increase App Rate by 1.2% because...",
        help="State your hypothesis clearly. For superiority tests: 'Changing X will increase Y by Z% because...' For non-inferiority tests: 'The new X will not decrease Y by more than Z% while improving...'",
        key="hypothesis_input"
    )
    
    # Auto-save to session state
    if hypothesis != SessionManager.get_form_data('hypothesis', ''):
        SessionManager.set_form_data('hypothesis', hypothesis)
    
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
    if primary_metric != SessionManager.get_form_data('primary_metric', ''):
        SessionManager.set_form_data('primary_metric', primary_metric)
    
    baseline_value = st.number_input(
        "📊 Current Baseline Value (%)" if primary_metric in ["App Rate", "Sold Rate", "Fund Rate"] else "📊 Current Baseline Value",
        value=SessionManager.get_form_data('baseline_value', 75.0 if primary_metric == "App Rate" else 0.0),
        help="Current performance of your primary metric. Make sure this reflects the specific user segment you're targeting.",
        key="baseline_value_input"
    )
    
    # Auto-save to session state
    if baseline_value != SessionManager.get_form_data('baseline_value', 0.0):
        SessionManager.set_form_data('baseline_value', baseline_value)
    
    secondary_metrics = st.multiselect(
        "📊 Secondary Metrics",
        ["App Rate", "Revenue", "EPL", "Sold Rate", "Fund Rate", "EPS"],
        default=SessionManager.get_form_data('secondary_metrics', []),
        help="Additional metrics to monitor for any unexpected effects",
        key="secondary_metrics_input"
    )
    
    # Auto-save to session state
    if secondary_metrics != SessionManager.get_form_data('secondary_metrics', []):
        SessionManager.set_form_data('secondary_metrics', secondary_metrics)
    
    # Then, get the test type
    test_type = st.selectbox(
        "🎯 Test Type",
        ["Superiority Test", "Non-Inferiority Test"],
        index=0 if SessionManager.get_form_data('test_type') == 'Superiority Test' else 1,
        help="Superiority Test: Testing if the new version performs better than the current version. Non-Inferiority Test: Testing if the new version is not worse than the current version by more than a specified margin.",
        key="test_type_input"
    )
    
    # Auto-save to session state
    if test_type != SessionManager.get_form_data('test_type', ''):
        SessionManager.set_form_data('test_type', test_type)
    
    # Initialize variables to avoid None issues
    expected_lift = None
    non_inferiority_margin = None
    
    # Dynamic lift input based on test type - NOW UPDATES IN REAL-TIME!
    if test_type == "Superiority Test":
        expected_lift = st.number_input(
            "📈 Expected Lift (% absolute)",
            value=SessionManager.get_form_data('expected_lift', 1.2),
            help="Expected improvement in absolute percentage points. E.g., if baseline is 75% and you expect 76.2%, enter 1.2 (not 1.6% relative). This directly impacts sample size - smaller lifts require larger sample sizes.",
            key="expected_lift_input"
        )
        
        # Auto-save to session state
        if expected_lift != SessionManager.get_form_data('expected_lift', 0.0):
            SessionManager.set_form_data('expected_lift', expected_lift)
            SessionManager.set_form_data('non_inferiority_margin', None)
        
    else:
        non_inferiority_margin = st.number_input(
            "📉 Non-Inferiority Margin (% absolute)",
            value=SessionManager.get_form_data('non_inferiority_margin', 1.0),
            help="Maximum acceptable decrease in absolute percentage points. E.g., if baseline is 75% and margin is 1%, you're testing that treatment ≥ 74%.",
            key="non_inferiority_margin_input"
        )
        
        # Auto-save to session state
        if non_inferiority_margin != SessionManager.get_form_data('non_inferiority_margin', 0.0):
            SessionManager.set_form_data('non_inferiority_margin', non_inferiority_margin)
            SessionManager.set_form_data('expected_lift', None)
    
    # ===== SAMPLE SIZE & RUNTIME CALCULATION =====
    st.markdown('<div class="subsection-header"><h4>📊 Sample Size & Runtime Calculator</h4></div>', unsafe_allow_html=True)
    
    # Statistical parameters and traffic input in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🔬 Statistical Parameters")
        alpha = st.number_input(
            "Significance Level (α)", 
            value=SessionManager.get_form_data('alpha', 0.05), 
            min_value=0.01, 
            max_value=0.10, 
            help="Probability of Type I error (false positive)",
            key="alpha_input"
        )
        
        # Auto-save to session state
        if alpha != SessionManager.get_form_data('alpha', 0.05):
            SessionManager.set_form_data('alpha', alpha)
        
        power = st.number_input(
            "Statistical Power", 
            value=SessionManager.get_form_data('power', 0.80), 
            min_value=0.70, 
            max_value=0.99, 
            help="Probability of detecting a true effect (1 - Type II error)",
            key="power_input"
        )
        
        # Auto-save to session state
        if power != SessionManager.get_form_data('power', 0.80):
            SessionManager.set_form_data('power', power)
    
    with col2:
        st.subheader("👥 Traffic Volume")
        traffic_period = st.radio(
            "📅 Traffic Period",
            ["Daily", "Weekly", "Monthly"],
            index=["Daily", "Weekly", "Monthly"].index(SessionManager.get_form_data('traffic_period', 'Daily')),
            help="Select the time period for your traffic volume",
            key="traffic_period_input"
        )
        
        # Auto-save to session state
        if traffic_period != SessionManager.get_form_data('traffic_period', 'Daily'):
            SessionManager.set_form_data('traffic_period', traffic_period)
        
        if traffic_period == "Daily":
            traffic_volume = st.number_input(
                "👥 Daily Users",
                value=SessionManager.get_form_data('daily_users', 12000),
                help="How many users per day will enter this experiment?",
                key="daily_users_input"
            )
            
            # Auto-save to session state
            if traffic_volume != SessionManager.get_form_data('daily_users', 12000):
                SessionManager.set_form_data('daily_users', traffic_volume)
            
            daily_users = traffic_volume
        elif traffic_period == "Weekly":
            weekly_users = st.number_input(
                "👥 Weekly Users",
                value=SessionManager.get_form_data('weekly_users', 84000),
                help="How many users per week will enter this experiment?",
                key="weekly_users_input"
            )
            
            # Auto-save to session state
            if weekly_users != SessionManager.get_form_data('weekly_users', 84000):
                SessionManager.set_form_data('weekly_users', weekly_users)
            
            daily_users = weekly_users / 7
        else:  # Monthly
            monthly_users = st.number_input(
                "👥 Monthly Users",
                value=SessionManager.get_form_data('monthly_users', 360000),
                help="How many users per month will enter this experiment?",
                key="monthly_users_input"
            )
            
            # Auto-save to session state
            if monthly_users != SessionManager.get_form_data('monthly_users', 360000):
                SessionManager.set_form_data('monthly_users', monthly_users)
            
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
                SessionManager.set_form_data('calculated_sample_size', sample_size)
                SessionManager.set_form_data('treatment_rate', baseline_value + expected_lift)
                
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
            SessionManager.set_form_data('calculated_sample_size', sample_size)
            SessionManager.set_form_data('min_acceptable_rate', baseline_value - non_inferiority_margin)
            
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
            SessionManager.set_form_data('estimated_runtime', runtime)
            SessionManager.set_form_data('daily_users_calculated', daily_users)
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
        index=["FastLoanAdvance-Google", "GraceLoanAdvance-Google", "5k Dupes"].index(SessionManager.get_form_data('campaign', 'FastLoanAdvance-Google')),
        help="Which campaign will this experiment run in?",
        key="campaign_input"
    )
    
    # Auto-save to session state
    if campaign != SessionManager.get_form_data('campaign', ''):
        SessionManager.set_form_data('campaign', campaign)
    
    traffic_type = st.selectbox(
        "🚦 Traffic Type",
        ["PPC", "RESID", "RAQID", "Prepop", "Affiliate"],
        index=["PPC", "RESID", "RAQID", "Prepop", "Affiliate"].index(SessionManager.get_form_data('traffic_type', 'PPC')),
        help="What type of traffic will be included in this experiment?",
        key="traffic_type_input"
    )
    
    # Auto-save to session state
    if traffic_type != SessionManager.get_form_data('traffic_type', ''):
        SessionManager.set_form_data('traffic_type', traffic_type)
    
    control_variant = st.text_input(
        "🎛️ Control Variant ID",
        value=SessionManager.get_form_data('control_variant', ''),
        placeholder="e.g., 8980",
        help="ID for the control (current) version",
        key="control_variant_input"
    )
    
    # Auto-save to session state
    if control_variant != SessionManager.get_form_data('control_variant', ''):
        SessionManager.set_form_data('control_variant', control_variant)
    
    treatment_variant = st.text_input(
        "🎛️ Treatment Variant ID",
        value=SessionManager.get_form_data('treatment_variant', ''),
        placeholder="e.g., 9255",
        help="ID for the treatment (new) version",
        key="treatment_variant_input"
    )
    
    # Auto-save to session state
    if treatment_variant != SessionManager.get_form_data('treatment_variant', ''):
        SessionManager.set_form_data('treatment_variant', treatment_variant)
    
    # ===== STEP 4: TARGET AUDIENCE =====
    st.markdown('<div class="step-header"><h3>Step 4: Target Audience</h3></div>', unsafe_allow_html=True)
    
    user_segment = st.selectbox(
        "👥 User Segment",
        ["All Users", "New Users", "Lookup Users"],
        index=["All Users", "New Users", "Lookup Users"].index(SessionManager.get_form_data('user_segment', 'All Users')),
        help="Which user segment will see this experiment? This affects your baseline rates.",
        key="user_segment_input"
    )
    
    # Auto-save to session state
    if user_segment != SessionManager.get_form_data('user_segment', ''):
        SessionManager.set_form_data('user_segment', user_segment)
    
    device_type = st.selectbox(
        "📱 Device Type",
        ["All Devices", "Mobile", "Desktop"],
        index=["All Devices", "Mobile", "Desktop"].index(SessionManager.get_form_data('device_type', 'All Devices')),
        help="Which devices will be included in the experiment?",
        key="device_type_input"
    )
    
    # Auto-save to session state
    if device_type != SessionManager.get_form_data('device_type', ''):
        SessionManager.set_form_data('device_type', device_type)
    
    # ===== STEP 5: PRIORITY & BUSINESS CONTEXT =====
    st.markdown('<div class="step-header"><h3>Step 5: Priority & Business Context</h3></div>', unsafe_allow_html=True)
    
    priority = st.selectbox(
        "🚨 Priority",
        ["High", "Medium", "Low"],
        index=["High", "Medium", "Low"].index(SessionManager.get_form_data('priority', 'Medium')),
        help="How important is this experiment to current business objectives?",
        key="priority_input"
    )
    
    # Auto-save to session state
    if priority != SessionManager.get_form_data('priority', ''):
        SessionManager.set_form_data('priority', priority)
    
    business_goal = st.text_area(
        "🎯 Business Goal",
        value=SessionManager.get_form_data('business_goal', ''),
        placeholder="e.g., Test messaging shift before major campaign push in August",
        help="Explain why this experiment is important to the business and how it fits into broader goals.",
        key="business_goal_input"
    )
    
    # Auto-save to session state
    if business_goal != SessionManager.get_form_data('business_goal', ''):
        SessionManager.set_form_data('business_goal', business_goal)
    
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
            'traffic_period': SessionManager.get_form_data('traffic_period', 'Daily'),
            'daily_users': SessionManager.get_form_data('daily_users_calculated', 0),
            'calculated_sample_size': SessionManager.get_form_data('calculated_sample_size'),
            'estimated_runtime': SessionManager.get_form_data('estimated_runtime'),
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
            
            saved_sample_size = SessionManager.get_form_data('calculated_sample_size')
            if not saved_sample_size:
                st.error("❌ Sample size calculation failed. Please check your test parameters.")
                return
            
            # Get saved values from session state
            saved_runtime = SessionManager.get_form_data('estimated_runtime')
            saved_daily_users = SessionManager.get_form_data('daily_users_calculated')
            
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
                'traffic_period': SessionManager.get_form_data('traffic_period', 'Daily'),
                'daily_users': saved_daily_users or 0,
                'calculated_sample_size': saved_sample_size,
                'estimated_runtime': saved_runtime,
                'priority': priority,
                'business_goal': business_goal
            }
            
            # Save to session state
            SessionManager.update_form_data(final_form_data)
            
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