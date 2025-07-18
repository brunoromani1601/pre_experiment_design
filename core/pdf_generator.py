import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

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
        
        # Owner and Stakeholders
        story.append(Paragraph("<b>Experiment Team:</b>", styles['Heading2']))
        team_data = [
            ("Experiment Owner", form_data.get('owner_name', 'N/A')),
            ("Stakeholders", form_data.get('stakeholders', 'N/A'))
        ]
        
        for label, value in team_data:
            story.append(Paragraph(f"<b>{label}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 12))
        
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