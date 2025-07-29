import streamlit as st
from core.calculator import SampleSizeCalculator
from core.pdf_generator import PDFGenerator
from core.session_manager import SessionManager
from core.notion_integration import NotionIntegration

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_notion_initiatives():
    """Cached function to get Notion initiatives"""
    try:
        notion_integration = NotionIntegration()
        return notion_integration.get_initiative_options()
    except Exception as e:
        st.error(f"❌ Error loading EPCVIP Initiatives: {e}")
        return []

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_notion_campaigns():
    """Cached function to get Notion campaigns"""
    try:
        notion_integration = NotionIntegration()
        return notion_integration.get_campaign_options()
    except Exception as e:
        st.error(f"❌ Error loading EPCVIP Campaigns: {e}")
        return []

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_notion_affiliates():
    """Cached function to get Notion affiliates"""
    try:
        notion_integration = NotionIntegration()
        return notion_integration.get_affiliate_options()
    except Exception as e:
        st.error(f"❌ Error loading EPCVIP Affiliates: {e}")
        return []

def debounced_session_update(key, value, current_value):
    """Update session state only if value has actually changed"""
    if value != current_value:
        SessionManager.set_form_data(key, value)
        return True
    return False

def log_performance_issue(component_name):
    """Log performance issues for debugging"""
    if 'performance_issues' not in st.session_state:
        st.session_state.performance_issues = {}
    
    if component_name not in st.session_state.performance_issues:
        st.session_state.performance_issues[component_name] = 0
    
    st.session_state.performance_issues[component_name] += 1
    
    # Only show warning after multiple issues
    if st.session_state.performance_issues[component_name] > 5:
        st.warning(f"⚠️ Performance issue detected in {component_name}. Consider refreshing the page.")

@st.cache_data(ttl=60)  # Cache for 1 minute
def calculate_sample_size(test_type, primary_metric, baseline_value, expected_lift=None, non_inferiority_margin=None, alpha=0.05, power=0.80):
    """Cached sample size calculation"""
    calc = SampleSizeCalculator()
    
    if test_type == "Superiority Test" and expected_lift is not None:
        if primary_metric in ["App Rate", "Sold Rate", "Fund Rate"]:
            p1 = baseline_value / 100
            p2 = (baseline_value + expected_lift) / 100
            return calc.calculate_proportions(p1, p2, alpha, power)
    elif test_type == "Non-Inferiority Test" and non_inferiority_margin is not None:
        p1 = baseline_value / 100
        return calc.calculate_non_inferiority(p1, non_inferiority_margin / 100, alpha, power)
    
    return None

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
    
    col1, col2 = st.columns(2)
    
    with col1:
        owner_name = st.text_input(
            "👤 Experiment Owner",
            value=SessionManager.get_form_data('owner_name', ''),
            placeholder="e.g., John Smith",
            help="Name of the person responsible for this experiment",
            key="owner_name_input"
        )
        
        # Auto-save to session state
        if owner_name != SessionManager.get_form_data('owner_name', ''):
            SessionManager.set_form_data('owner_name', owner_name)
    
    with col2:
        stakeholders = st.text_input(
            "👥 Stakeholders",
            value=SessionManager.get_form_data('stakeholders', ''),
            placeholder="e.g., Marketing Team, Product Manager",
            help="People or teams who should be informed about this experiment",
            key="stakeholders_input"
        )
        
        # Auto-save to session state
        if stakeholders != SessionManager.get_form_data('stakeholders', ''):
            SessionManager.set_form_data('stakeholders', stakeholders)
    
    # Add EPCVIP Initiative dropdown with search
    initiative_options = get_notion_initiatives()
    initiative_names = [initiative['name'] for initiative in initiative_options]
    
    # Add "None" option for optional selection
    initiative_names_with_none = ["None"] + initiative_names
    
    # Get saved value and handle case where it might not be in current list
    saved_initiative = SessionManager.get_form_data('epcvip_initiative', 'None')
    if saved_initiative not in initiative_names_with_none:
        saved_initiative = 'None'
    
    epcvip_initiative = st.selectbox(
        "🎯 EPCVIP Initiative",
        initiative_names_with_none,
        index=initiative_names_with_none.index(saved_initiative),
        help="Select the EPCVIP Initiative from Notion database (optional). Type to search through 100+ initiatives.",
        key="epcvip_initiative_input"
    )
    
    # Convert "None" to empty string for storage
    if epcvip_initiative == "None":
        epcvip_initiative = ""
    
    # Auto-save to session state
    if epcvip_initiative != SessionManager.get_form_data('epcvip_initiative', ''):
        SessionManager.set_form_data('epcvip_initiative', epcvip_initiative)
            
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
    
    # Add EPCVIP Campaigns dropdown
    campaign_options = get_notion_campaigns()
    campaign_names = [campaign['name'] for campaign in campaign_options]
    
    # Add "None" option for optional selection
    campaign_names_with_none = ["None"] + campaign_names
    
    # Get saved value and handle case where it might not be in current list
    saved_campaign = SessionManager.get_form_data('epcvip_campaign', 'None')
    if saved_campaign not in campaign_names_with_none:
        saved_campaign = 'None'
    
    epcvip_campaign = st.selectbox(
        "🎯 EPCVIP Campaign",
        campaign_names_with_none,
        index=campaign_names_with_none.index(saved_campaign),
        help="Select the EPCVIP Campaign from Notion database (optional)",
        key="epcvip_campaign_input"
    )
    
    # Convert "None" to empty string for storage
    if epcvip_campaign == "None":
        epcvip_campaign = ""
    
    # Auto-save to session state
    if epcvip_campaign != SessionManager.get_form_data('epcvip_campaign', ''):
        SessionManager.set_form_data('epcvip_campaign', epcvip_campaign)
            
    # Add EPCVIP Affiliates dropdown
    affiliate_options = get_notion_affiliates()
    affiliate_names = [affiliate['name'] for affiliate in affiliate_options]
    
    # Add "None" option for optional selection
    affiliate_names_with_none = ["None"] + affiliate_names
    
    # Get saved value and handle case where it might not be in current list
    saved_affiliate = SessionManager.get_form_data('epcvip_affiliate', 'None')
    if saved_affiliate not in affiliate_names_with_none:
        saved_affiliate = 'None'
    
    epcvip_affiliate = st.selectbox(
        "🤝 EPCVIP Affiliate",
        affiliate_names_with_none,
        index=affiliate_names_with_none.index(saved_affiliate),
        help="Select the EPCVIP Affiliate from Notion database (optional)",
        key="epcvip_affiliate_input"
    )
    
    # Convert "None" to empty string for storage
    if epcvip_affiliate == "None":
        epcvip_affiliate = ""
    
    # Auto-save to session state
    if epcvip_affiliate != SessionManager.get_form_data('epcvip_affiliate', ''):
        SessionManager.set_form_data('epcvip_affiliate', epcvip_affiliate)
    
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
    
    # Add JIRA Link field
    jira_link = st.text_input(
        "🔗 JIRA Link (Ad Chain)",
        value=SessionManager.get_form_data('jira_link', ''),
        placeholder="https://jira.company.com/browse/EXP-123",
        help="Optional: Link to the JIRA ticket for this experiment",
        key="jira_link_input"
    )
    
    # Auto-save to session state
    if jira_link != SessionManager.get_form_data('jira_link', ''):
        SessionManager.set_form_data('jira_link', jira_link)
    
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
            'owner_name': owner_name or "Not specified",
            'stakeholders': stakeholders or "Not specified",
            'feature_description': feature_description or "Not specified",
            'hypothesis': hypothesis or "Not specified",
            'test_type': test_type,
            'primary_metric': primary_metric,
            'baseline_value': baseline_value,
            'expected_lift': expected_lift if test_type == "Superiority Test" else None,
            'non_inferiority_margin': non_inferiority_margin if test_type == "Non-Inferiority Test" else None,
            'secondary_metrics': secondary_metrics,
            'epcvip_campaign': epcvip_campaign,
            'epcvip_affiliate': epcvip_affiliate,
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
            st.write(f"**Owner:** {preview_data['owner_name']}")
            st.write(f"**Stakeholders:** {preview_data['stakeholders']}")
            st.write(f"**Test Type:** {preview_data['test_type']}")
            st.write(f"**Primary Metric:** {preview_data['primary_metric']} (Baseline: {preview_data['baseline_value']}%)")
            
            if preview_data['test_type'] == "Superiority Test" and preview_data['expected_lift']:
                st.write(f"**Expected Lift:** {preview_data['expected_lift']}%")
            elif preview_data['test_type'] == "Non-Inferiority Test" and preview_data['non_inferiority_margin']:
                st.write(f"**Non-Inferiority Margin:** {preview_data['non_inferiority_margin']}%")
            
            if preview_data['epcvip_campaign']:
                st.write(f"**EPCVIP Campaign:** {preview_data['epcvip_campaign']}")
            if preview_data['epcvip_affiliate']:
                st.write(f"**EPCVIP Affiliate:** {preview_data['epcvip_affiliate']}")
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
            
        if not owner_name:
            validation_issues.append("⚠️ Experiment owner recommended")
        else:
            validation_issues.append("✅ Experiment owner provided")
            
        if not stakeholders:
            validation_issues.append("⚠️ Stakeholders recommended")
        else:
            validation_issues.append("✅ Stakeholders provided")
            
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
    st.markdown('<div class="step-header"><h3>🚀 Create Experiment in Notion</h3></div>', unsafe_allow_html=True)
    
    # Create final form data
    saved_sample_size = SessionManager.get_form_data('calculated_sample_size')
    saved_runtime = SessionManager.get_form_data('estimated_runtime')
    saved_daily_users = SessionManager.get_form_data('daily_users_calculated')
    
    final_form_data = {
        'experiment_name': experiment_name,
        'owner_name': owner_name,
        'stakeholders': stakeholders,
        'epcvip_initiative': epcvip_initiative,
        'feature_description': feature_description,
        'hypothesis': hypothesis,
        'test_type': test_type,
        'primary_metric': primary_metric,
        'baseline_value': baseline_value,
        'expected_lift': expected_lift if test_type == "Superiority Test" else None,
        'non_inferiority_margin': non_inferiority_margin if test_type == "Non-Inferiority Test" else None,
        'secondary_metrics': secondary_metrics,
        'epcvip_campaign': epcvip_campaign,
        'epcvip_affiliate': epcvip_affiliate,
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
        'business_goal': business_goal,
        'jira_link': jira_link
    }
    
    # Save to session state
    SessionManager.update_form_data(final_form_data)
    
    # Step 1: Review Notion Data
    if st.button("📋 Review Notion Data", type="primary"):
        # Validate required fields
        if not experiment_name or not feature_description or not hypothesis:
            st.error("❌ Please fill in all required fields: Experiment Name, Feature Being Tested, and Hypothesis")
            return
        
        if not saved_sample_size:
            st.error("❌ Sample size calculation failed. Please check your test parameters.")
            return
        
        # Validate EPCVIP Campaign if selected
        if epcvip_campaign:
            try:
                notion_integration = NotionIntegration()
                if not notion_integration.validate_campaign_selection(epcvip_campaign):
                    st.error(f"❌ Selected EPCVIP Campaign '{epcvip_campaign}' not found in Notion database")
                    return
            except Exception as e:
                st.error(f"❌ Error validating EPCVIP Campaign: {e}")
                return
        
        # Validate EPCVIP Affiliate if selected
        if epcvip_affiliate:
            try:
                notion_integration = NotionIntegration()
                if not notion_integration.validate_affiliate_selection(epcvip_affiliate):
                    st.error(f"❌ Selected EPCVIP Affiliate '{epcvip_affiliate}' not found in Notion database")
                    return
            except Exception as e:
                st.error(f"❌ Error validating EPCVIP Affiliate: {e}")
                return
        
        # Validate EPCVIP Initiative if selected
        if epcvip_initiative:
            try:
                notion_integration = NotionIntegration()
                if not notion_integration.validate_initiative_selection(epcvip_initiative):
                    st.error(f"❌ Selected EPCVIP Initiative '{epcvip_initiative}' not found in Notion database")
                    return
            except Exception as e:
                st.error(f"❌ Error validating EPCVIP Initiative: {e}")
                return
        
        # Show preview of what will be sent to Notion
        st.success("✅ Form validation passed!")
        
        st.subheader("📋 Notion Preview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Notion Properties:**")
            st.write(f"• **Test Order:** 1 (title)")
            st.write(f"• **Ad Chain:** {treatment_variant}")
            if jira_link:
                st.write(f"• **JIRA Link (Ad Chain):** {jira_link}")
            if epcvip_campaign:
                st.write(f"• **EPCVIP Campaigns:** {epcvip_campaign}")
            if epcvip_initiative:
                st.write(f"• **Feature:** {epcvip_initiative}")
            st.write("• **Feature Status:** Planned (default for new experiments)")
        
        with col2:
            st.write("**Page Content Preview:**")
            st.write("📋 Experiment Details")
            st.write(f"• **Experiment Name:** {experiment_name} (will be in page content)")
            st.write(f"• Owner: {owner_name}")
            st.write(f"• Test Type: {test_type}")
            st.write(f"• Sample Size: {saved_sample_size:,} users per group")
            st.write(f"• Runtime: {saved_runtime} days")
            if epcvip_campaign:
                st.write(f"• EPCVIP Campaign: {epcvip_campaign}")
            if epcvip_affiliate:
                st.write(f"• EPCVIP Affiliate: {epcvip_affiliate}")
            if epcvip_initiative:
                st.write(f"• EPCVIP Initiative: {epcvip_initiative}")
        
        # Store form data in session for the next step
        st.session_state.notion_form_data = final_form_data
        st.session_state.show_create_button = True
    
    # Step 2: Create in Notion
    if st.session_state.get('show_create_button', False):
        st.markdown("---")
        st.subheader("🚀 Create Experiment")
        
        if st.button("✅ Create in Notion", type="primary"):
            try:
                # Initialize Notion integration
                notion_integration = NotionIntegration()
                
                # Create experiment in Notion
                new_page = notion_integration.create_experiment_page(st.session_state.notion_form_data)
                
                if new_page:
                    st.success("✅ Experiment created successfully in Notion!")
                    
                    # Display success information
                    page_url = f"https://notion.so/{new_page['id'].replace('-', '')}"
                    st.write(f"**Page ID:** {new_page['id']}")
                    st.write(f"**View in Notion:** [Click here]({page_url})")
                    
                    # Clear session state
                    st.session_state.show_create_button = False
                    if 'notion_form_data' in st.session_state:
                        del st.session_state.notion_form_data
                else:
                    st.error("❌ Failed to create experiment in Notion. Please check the error messages above.")
                    
            except Exception as e:
                st.error(f"❌ Error connecting to Notion: {e}")
                st.error("Please check your Notion token and try again.") 