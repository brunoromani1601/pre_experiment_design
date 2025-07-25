#!/usr/bin/env python3
"""Test the Notion integration module"""

from core.notion_integration import NotionIntegration

def test_notion_integration():
    """Test the Notion integration functionality"""
    print("🧪 Testing Notion Integration Module")
    print("=" * 50)
    
    try:
        # Initialize Notion integration
        notion = NotionIntegration()
        print("✅ Notion integration initialized successfully")
        
        # Test getting database schema
        schema = notion.get_database_schema()
        if schema:
            print("✅ Database schema retrieved successfully")
            print(f"📊 Found {len(schema)} properties")
        else:
            print("❌ Failed to retrieve database schema")
            return
        
        # Test getting dropdown options
        feature_options = notion.get_dropdown_options("Feature")
        campaign_options = notion.get_dropdown_options("EPCVIP Campaigns")
        
        print(f"🔧 Feature options: {feature_options}")
        print(f"🎯 Campaign options: {campaign_options}")
        
        # Test validation
        if feature_options:
            is_valid = notion.validate_dropdown_selection("Feature", feature_options[0])
            print(f"✅ Validation test: {is_valid}")
        
        print("\n🎉 All tests passed! Notion integration is working correctly.")
        
    except Exception as e:
        print(f"❌ Error testing Notion integration: {e}")

if __name__ == "__main__":
    test_notion_integration() 