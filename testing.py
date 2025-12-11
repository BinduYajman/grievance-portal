import streamlit as st
import csv
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta
import uuid 
import re 
import pandas as pd 
from io import BytesIO 

# -------------------------
# Config / file locations
# -------------------------
BASE_DIR = Path(__file__).parent.resolve() 
USERS_CSV = BASE_DIR / "users.csv"
COMPLAINTS_CSV = BASE_DIR / "complaints.csv"
ANNOUNCEMENTS_CSV = BASE_DIR / "announcements.csv"
POSTS_CSV = BASE_DIR / "posts.csv"
FEEDBACK_CSV = BASE_DIR / "feedback.csv" 
# -------------------------
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True) 

# -------------------------
# Define the specific region this portal serves
TARGET_REGION = "Park View Colony"
# -------------------------

# -------------------------
# NEW: Language and Translation Support
# -------------------------

# Kannada strings for translation (Standardized to English keys)
TRANSLATIONS = {
    "en": {
        # General
        "system_title": "🏛️ Public Grievance Redressal System",
        "region_name": TARGET_REGION,
        "region_admin": "Administration",
        "log_in": "Log In",
        "log_out": "Log Out",
        "profile": "Profile",
        "authenticated": "Authenticated",
        "role": "Role",
        "citizen": "Citizen",
        "administrator": "Administrator",
        "registered_details": "Registered Details",
        "area_code": "Area Code",
        "password": "Password",
        "username": "Username",
        "access_required": "User authentication is required to access public services.",
        "welcome_message": "Welcome. I am the **Digital Assistant** for this portal. Please state your query regarding services like Grievances, Announcements, or Community Board.",
        "system_login": "System Login",
        "authenticate_button": "Authenticate and Log In",
        "credential_admin": "Administration Account: Area **9000**, User **admin** / Pass **password**",
        "credential_citizen": "Citizen Account Example: Area **1234**, User **resident** / Pass **password**",
        
        # Citizen Tabs
        "tab_announcements": "Official Announcements",
        "tab_raise_grievance": "File New Grievance",
        "tab_status_tracking": "Grievance Status Tracking",
        "tab_community": "Community Board",
        "tab_assistant": "Digital Assistant",
        
        # Citizen UI
        "file_grievance_title": "File New Grievance: Public Issue Reporting",
        "file_grievance_info": "Please complete all mandatory fields. The system will automatically classify the priority of your grievance.",
        "submit_grievance": "Submit Formal Grievance",
        "name_input": "Complainant's Full Name",
        "house_input": "Registered Address / Property Identification",
        "house_placeholder": "E.g., Flat 101, Block B or Plot No. 45",
        "grievance_category": "Grievance Category",
        "grievance_desc": "Detailed Description of the Grievance",
        "grievance_desc_placeholder": "Clearly describe the nature of the issue, its precise location, and the impact on the community. Use keywords like 'emergency' or 'critical' if necessary.",
        "attachment_header": "Supporting Documentation",
        "attachment_upload": "Upload Supporting Document or Photograph",
        "status_tracking_title": "Grievance Status Tracking",
        "no_grievances": "No grievances have been registered under your account yet.",
        "resolution_status": "Resolution Status and Administrative Notes",
        "notes_caption": "The administration has not yet recorded specific notes or resolution details.",
        "feedback_survey": "Citizen Satisfaction Survey",
        "feedback_info": "Please rate your satisfaction with the resolution of this grievance.",
        "feedback_rating": "Resolution Rating (Mandatory)",
        "feedback_suggestion": "Suggestion/Comment for Improvement (Optional)",
        "feedback_submit": "Submit Resolution Feedback",
        "feedback_success": "Feedback submitted successfully. Your input is valued for system improvement.",
        "posted_by": "Posted by",
        "on_date": "on",
        "official_post_banner": "📢 **Official Post from Administration**",
        "community_discussions": "Discussions from {} Residents",
        "post_subject": "Subject of Discussion",
        "post_image_upload": "Upload Supporting Image (Optional)",
        "post_as_admin": "Post as Admin",
        "post_as_citizen": "Post",
        "post_success": "The post has been submitted to the Community Board.",
        "post_error": "Discussion content or an image attachment is required.",
        "no_discussions": "No community discussions available at this time.",
        
        # Admin Tabs
        "admin_tab_manage": "Admin Grievance Management",
        "admin_tab_feedback": "Citizen Satisfaction Review",
        "admin_tab_analysis": "Analysis",
        "admin_tab_map": "Hotspot Map",
        "admin_tab_publish": "Administrative Publishing",
        
        # Admin UI
        "admin_manage_title": "Administrative Grievance Management",
        "admin_publish_title": "Administrative Announcement Publishing",
        "admin_content_label": "Official Circular Content",
        "admin_content_placeholder": "Enter the text of the official announcement or circular.",
        "admin_publish_button": "Publish Official Announcement",
        "current_announcements": "Currently Published Official Announcements",
        "admin_action": "Administrative Action and Assignment",
        "update_status": "Update Grievance Status",
        "assign_dept": "Assign Department and Record Notes",
        "download_data": "Download ALL Grievance Data (Excel .xlsx)",
        "admin_assignment_note": "Administrative Notes / Resolution Details",
        "save_assignment": "💾 Save Assignment and Notes",
        "execute_status": "Execute Status Change",
        
        # Complaint Details (Priority & Status Keys - MUST NOT CHANGE)
        "priority_emergency": "Emergency",
        "priority_high": "High Priority",
        "priority_standard": "Standard Priority",
        "status_open": "Open",
        "status_in_progress": "In Progress",
        "status_resolved": "Resolved",
        "sla_status": "SLA Status",
        "sla_overdue": "OVERDUE",
        "sla_due_now": "DUE NOW",
    },
    "kn": {
        # General
        "system_title": "🏛️ ಸಾರ್ವಜನಿಕ ಕುಂದುಕೊರತೆ ನಿವಾರಣಾ ವ್ಯವಸ್ಥೆ",
        "region_name": TARGET_REGION,
        "region_admin": "ಆಡಳಿತ",
        "log_in": "ಲಾಗ್ ಇನ್ ಮಾಡಿ",
        "log_out": "ಲಾಗ್ ಔಟ್ ಮಾಡಿ",
        "profile": "ಪ್ರೊಫೈಲ್",
        "authenticated": "ದೃಢೀಕರಿಸಲಾಗಿದೆ",
        "role": "ಪಾತ್ರ",
        "citizen": "ನಾಗರಿಕ",
        "administrator": "ನಿರ್ವಾಹಕ",
        "registered_details": "ನೋಂದಾಯಿತ ವಿವರಗಳು",
        "area_code": "ಪ್ರದೇಶ ಕೋಡ್",
        "password": "ಪಾಸ್ವರ್ಡ್",
        "username": "ಬಳಕೆದಾರ ಹೆಸರು",
        "access_required": "ಸಾರ್ವಜನಿಕ ಸೇವೆಗಳನ್ನು ಪ್ರವೇಶಿಸಲು ಬಳಕೆದಾರರ ದೃಢೀಕರಣದ ಅಗತ್ಯವಿದೆ.",
        "welcome_message": "ಸ್ವಾಗತ. ನಾನು ಈ ಪೋರ್ಟಲ್‌ನ **ಡಿಜಿಟಲ್ ಸಹಾಯಕ**. ದಯವಿಟ್ಟು ಕುಂದುಕೊರತೆ, ಪ್ರಕಟಣೆಗಳು ಅಥವಾ ಸಮುದಾಯ ಮಂಡಳಿಯಂತಹ ಸೇವೆಗಳ ಕುರಿತು ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ತಿಳಿಸಿ.",
        "system_login": "ವ್ಯವಸ್ಥೆಯ ಲಾಗಿನ್",
        "authenticate_button": "ದೃಢೀಕರಿಸಿ ಮತ್ತು ಲಾಗ್ ಇನ್ ಮಾಡಿ",
        "credential_admin": "ಆಡಳಿತ ಖಾತೆ: ಪ್ರದೇಶ **9000**, ಬಳಕೆದಾರ **admin** / ಪಾಸ್ವರ್ಡ್ **password**",
        "credential_citizen": "ನಾಗರಿಕ ಖಾತೆ ಉದಾಹರಣೆ: ಪ್ರದೇಶ **1234**, ಬಳಕೆದಾರ **resident** / ಪಾಸ್ವರ್ಡ್ **password**",
        
        # Citizen Tabs
        "tab_announcements": "ಅಧಿಕೃತ ಪ್ರಕಟಣೆಗಳು",
        "tab_raise_grievance": "ಹೊಸ ಕುಂದುಕೊರತೆ ಸಲ್ಲಿಸಿ",
        "tab_status_tracking": "ಕುಂದುಕೊರತೆ ಸ್ಥಿತಿ ಟ್ರ್ಯಾಕಿಂಗ್",
        "tab_community": "ಸಮುದಾಯ ಮಂಡಳಿ",
        "tab_assistant": "ಡಿಜಿಟಲ್ ಸಹಾಯಕ",
        
        # Citizen UI
        "file_grievance_title": "ಹೊಸ ಕುಂದುಕೊರತೆ ಸಲ್ಲಿಸಿ: ಸಾರ್ವಜನಿಕ ಸಮಸ್ಯೆ ವರದಿ",
        "file_grievance_info": "ದಯವಿಟ್ಟು ಎಲ್ಲಾ ಕಡ್ಡಾಯ ಕ್ಷೇತ್ರಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ. ನಿಮ್ಮ ಕುಂದುಕೊರತೆಯ ಆದ್ಯತೆಯನ್ನು ವ್ಯವಸ್ಥೆಯು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ವರ್ಗೀಕರಿಸುತ್ತದೆ.",
        "submit_grievance": "ಔಪಚಾರಿಕ ಕುಂದುಕೊರತೆ ಸಲ್ಲಿಸಿ",
        "name_input": "ಕುಂದುಕೊರತೆದಾರರ ಪೂರ್ಣ ಹೆಸರು",
        "house_input": "ನೋಂದಾಯಿತ ವಿಳಾಸ / ಆಸ್ತಿ ಗುರುತಿಸುವಿಕೆ",
        "house_placeholder": "ಉದಾ. ಫ್ಲಾಟ್ 101, ಬ್ಲಾಕ್ ಬಿ ಅಥವಾ ಪ್ಲಾಟ್ ನಂ. 45",
        "grievance_category": "ಕುಂದುಕೊರತೆ ವರ್ಗ",
        "grievance_desc": "ಕುಂದುಕೊರತೆಯ ವಿವರವಾದ ವಿವರಣೆ",
        "grievance_desc_placeholder": "ಸಮಸ್ಯೆಯ ಸ್ವರೂಪ, ನಿಖರ ಸ್ಥಳ ಮತ್ತು ಸಮುದಾಯದ ಮೇಲಿನ ಪರಿಣಾಮವನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ವಿವರಿಸಿ. 'ತುರ್ತು' ಅಥವಾ 'ನಿರ್ಣಾಯಕ' ನಂತಹ ಪ್ರಮುಖ ಪದಗಳನ್ನು ಬಳಸಿ.",
        "attachment_header": "ಪೋಷಕ ದಾಖಲೆ",
        "attachment_upload": "ಪೋಷಕ ದಾಖಲೆ ಅಥವಾ ಛಾಯಾಚಿತ್ರವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ",
        "status_tracking_title": "ಕುಂದುಕೊರತೆ ಸ್ಥಿತಿ ಟ್ರ್ಯಾಕಿಂಗ್",
        "no_grievances": "ನಿಮ್ಮ ಖಾತೆಯ ಅಡಿಯಲ್ಲಿ ಇನ್ನೂ ಯಾವುದೇ ಕುಂದುಕೊರತೆಗಳನ್ನು ನೋಂದಾಯಿಸಲಾಗಿಲ್ಲ.",
        "resolution_status": "ಪರಿಹಾರದ ಸ್ಥಿತಿ ಮತ್ತು ಆಡಳಿತಾತ್ಮಕ ಟಿಪ್ಪಣಿಗಳು",
        "notes_caption": "ಆಡಳಿತವು ಇನ್ನೂ ನಿರ್ದಿಷ್ಟ ಟಿಪ್ಪಣಿಗಳು ಅಥವಾ ಪರಿಹಾರ ವಿವರಗಳನ್ನು ದಾಖಲಿಸಿಲ್ಲ.",
        "feedback_survey": "ನಾಗರಿಕರ ತೃಪ್ತಿ ಸಮೀಕ್ಷೆ",
        "feedback_info": "ದಯವಿಟ್ಟು ಈ ಕುಂದುಕೊರತೆಯ ಪರಿಹಾರದ ಕುರಿತು ನಿಮ್ಮ ತೃಪ್ತಿಯನ್ನು ರೇಟ್ ಮಾಡಿ.",
        "feedback_rating": "ಪರಿಹಾರ ರೇಟಿಂಗ್ (ಕಡ್ಡಾಯ)",
        "feedback_suggestion": "ಸುಧಾರಣೆಗಾಗಿ ಸಲಹೆ/ಟಿಪ್ಪಣಿ (ಐಚ್ಛಿಕ)",
        "feedback_submit": "ಪರಿಹಾರ ಪ್ರತಿಕ್ರಿಯೆ ಸಲ್ಲಿಸಿ",
        "feedback_success": "ಪ್ರತಿಕ್ರಿಯೆಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಸಲ್ಲಿಸಲಾಗಿದೆ. ನಿಮ್ಮ ಇನ್‌ಪುಟ್ ಅನ್ನು ಸಿಸ್ಟಮ್ ಸುಧಾರಣೆಗಾಗಿ ಮೌಲ್ಯಯುತವಾಗಿದೆ.",
        "posted_by": "ಪೋಸ್ಟ್ ಮಾಡಿದವರು",
        "on_date": "ದಿನಾಂಕ",
        "official_post_banner": "📢 **ಆಡಳಿತದಿಂದ ಅಧಿಕೃತ ಪೋಸ್ಟ್**",
        "community_discussions": "{} ನಿವಾಸಿಗಳಿಂದ ಚರ್ಚೆಗಳು",
        "post_subject": "ಚರ್ಚೆಯ ವಿಷಯ",
        "post_image_upload": "ಪೋಷಕ ಚಿತ್ರವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ (ಐಚ್ಛಿಕ)",
        "post_as_admin": "ನಿರ್ವಾಹಕರಾಗಿ ಪೋಸ್ಟ್ ಮಾಡಿ",
        "post_as_citizen": "ಪೋಸ್ಟ್ ಮಾಡಿ",
        "post_success": "ಪೋಸ್ಟ್ ಅನ್ನು ಸಮುದಾಯ ಮಂಡಳಿಗೆ ಸಲ್ಲಿಸಲಾಗಿದೆ.",
        "post_error": "ಚರ್ಚೆಯ ವಿಷಯ ಅಥವಾ ಚಿತ್ರದ ಲಗತ್ತು ಅಗತ್ಯವಿದೆ.",
        "no_discussions": "ಈ ಸಮಯದಲ್ಲಿ ಯಾವುದೇ ಸಮುದಾಯ ಚರ್ಚೆಗಳು ಲಭ್ಯವಿಲ್ಲ.",
        
        # Admin Tabs
        "admin_tab_manage": "ನಿರ್ವಾಹಕ ಕುಂದುಕೊರತೆ ನಿರ್ವಹಣೆ",
        "admin_tab_feedback": "ನಾಗರಿಕರ ತೃಪ್ತಿ ವಿಮರ್ಶೆ",
        "admin_tab_analysis": "ವಿಶ್ಲೇಷಣೆ",
        "admin_tab_map": "ಹಾಟ್‌ಸ್ಪಾಟ್ ನಕ್ಷೆ",
        "admin_tab_publish": "ಆಡಳಿತಾತ್ಮಕ ಪ್ರಕಟಣೆ",
        
        # Admin UI
        "admin_manage_title": "ಆಡಳಿತಾತ್ಮಕ ಕುಂದುಕೊರತೆ ನಿರ್ವಹಣೆ",
        "admin_publish_title": "ಆಡಳಿತಾತ್ಮಕ ಪ್ರಕಟಣೆ ಪ್ರಕಟಣೆ",
        "admin_content_label": "ಅಧಿಕೃತ ಸುತ್ತೋಲೆಯ ವಿಷಯ",
        "admin_content_placeholder": "ಅಧಿಕೃತ ಪ್ರಕಟಣೆ ಅಥವಾ ಸುತ್ತೋಲೆಯ ವಿಷಯವನ್ನು ನಮೂದಿಸಿ.",
        "admin_publish_button": "ಅಧಿಕೃತ ಪ್ರಕಟಣೆ ಪ್ರಕಟಿಸಿ",
        "current_announcements": "ಪ್ರಸ್ತುತ ಪ್ರಕಟಿಸಲಾದ ಅಧಿಕೃತ ಪ್ರಕಟಣೆಗಳು",
        "admin_action": "ಆಡಳಿತಾತ್ಮಕ ಕ್ರಮ ಮತ್ತು ನಿಯೋಜನೆ",
        "update_status": "ಕುಂದುಕೊರತೆ ಸ್ಥಿತಿಯನ್ನು ನವೀಕರಿಸಿ",
        "assign_dept": "ವಿಭಾಗವನ್ನು ನಿಯೋಜಿಸಿ ಮತ್ತು ಟಿಪ್ಪಣಿಗಳನ್ನು ದಾಖಲಿಸಿ",
        "download_data": "ಎಲ್ಲಾ ಕುಂದುಕೊರತೆ ಡೇಟಾವನ್ನು ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ (Excel .xlsx)",
        "admin_assignment_note": "ಆಡಳಿತಾತ್ಮಕ ಟಿಪ್ಪಣಿಗಳು / ಪರಿಹಾರ ವಿವರಗಳು",
        "save_assignment": "💾 ನಿಯೋಜನೆ ಮತ್ತು ಟಿಪ್ಪಣಿಗಳನ್ನು ಉಳಿಸಿ",
        "execute_status": "ಸ್ಥಿತಿಯ ಬದಲಾವಣೆಯನ್ನು ಕಾರ್ಯಗತಗೊಳಿಸಿ",
        
        # Complaint Details (Priority & Status Keys - MUST NOT CHANGE)
        "priority_emergency": "ತುರ್ತು",
        "priority_high": "ಹೆಚ್ಚಿನ ಆದ್ಯತೆ",
        "priority_standard": "ಪ್ರಮಾಣಿತ ಆದ್ಯತೆ",
        "status_open": "ತೆರೆದಿದೆ",
        "status_in_progress": "ಪ್ರಗತಿಯಲ್ಲಿದೆ",
        "status_resolved": "ಪರಿಹಾರವಾಗಿದೆ",
        "sla_status": "SLA ಸ್ಥಿತಿ",
        "sla_overdue": "ಕಾಲಾವಧಿ ಮೀರಿದೆ",
        "sla_due_now": "ಈಗ ಬಾಕಿ ಇದೆ",
    }
}

# Function to fetch translation
def t(key):
    """Fetches the translated string for the current language."""
    lang = st.session_state.language
    return TRANSLATIONS.get(lang, {}).get(key, key) # Fallback to key if not found


def set_language(lang):
    """Sets the application language and reruns."""
    st.session_state.language = lang
    st.rerun()
# -------------------------
# Utilities (Functions) - Updated to use t()
# -------------------------
def determine_priority_and_sla(category: str, description: str) -> tuple[str, str]:
    """
    Categorizes the complaint into Emergency, High, or Standard Priority 
    and assigns an SLA due date. 
    (Logic remains English/Keyword-based for reliability)
    """
    desc_lower = description.lower()
    
    # Keywords for severity detection 
    emergency_keywords = ['fire', 'leak', 'danger', 'injury', 'collapse', 'immediate', 'life threatening', 'emergency']
    high_keywords = ['urgent', 'major break', 'no power', 'blockage', 'broken', 'hazard', 'severe', 'critical']
    
    # High-risk categories
    high_risk_categories = ["Security", "Water Supply", "Electricity/Power", "Infrastructure/Roads"] 
    
    # Priority strings must match the keys used in the t() function's dictionary for consistency
    priority_key = "priority_standard"
    sla_days = 7 # Default SLA (7 days)

    # 1. Check for Emergency Priority (1 day / 24 hours)
    if any(k in category for k in high_risk_categories) and any(keyword in desc_lower for keyword in emergency_keywords):
        priority_key = "priority_emergency"
        sla_days = 1 
    
    # 2. Check for High Priority (3 days)
    elif any(k in category for k in high_risk_categories) or any(keyword in desc_lower for keyword in high_keywords):
        priority_key = "priority_high"
        sla_days = 3
    
    # 3. Default to Standard Priority (7 days)
    
    # Calculate SLA due date
    sla_due_date = datetime.utcnow() + timedelta(days=sla_days)
    
    return priority_key, sla_due_date.isoformat() # Return the KEY

def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()

def ensure_files_exist():
    """Checks for required CSV files and ensures they have the correct headers and initial data."""
    COMPLAINT_HEADER = ["id","username","name","house","category","description","attachment","created_at","status","department","admin_notes","latitude","longitude","sla_due","priority"]
    USER_HEADER = ["id","username","password_hash","is_admin","region","area_code"] 
    POST_HEADER = ["id","username","region","content","created_at", "votes", "attachment"] 
    FEEDBACK_HEADER = ["complaint_id", "username", "rating", "suggestion", "created_at"] 
    ANNOUNCEMENT_HEADER = ["id","author","content","created_at", "attachment"] 

    # 1. USERS_CSV Setup
    if not USERS_CSV.exists() or len(list(csv.reader(USERS_CSV.open("r", newline="", encoding="utf-8")))) <= 1:
        with USERS_CSV.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(USER_HEADER)
            w.writerow([str(uuid.uuid4()), "admin", hash_password("password"), "1", TARGET_REGION, "9000"]) 
            w.writerow([str(uuid.uuid4()), "resident", hash_password("password"), "0", TARGET_REGION, "1234"])
            w.writerow([str(uuid.uuid4()), "neighbor", hash_password("pass123"), "0", TARGET_REGION, "5678"]) 
            w.writerow([str(uuid.uuid4()), "outsider", hash_password("test"), "0", "Riverwood Heights", "9999"])
            
    # 2. COMPLAINTS_CSV Setup 
    if not COMPLAINTS_CSV.exists():
        with COMPLAINTS_CSV.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(COMPLAINT_HEADER)
            
    # 3. ANNOUNCEMENTS_CSV Setup
    if not ANNOUNCEMENTS_CSV.exists():
        with ANNOUNCEMENTS_CSV.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(ANNOUNCEMENT_HEADER)
            
    # 4. POSTS_CSV Setup and Migration 
    if not POSTS_CSV.exists():
        with POSTS_CSV.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(POST_HEADER)
            
    # 5. FEEDBACK_CSV Setup
    if not FEEDBACK_CSV.exists():
        with FEEDBACK_CSV.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(FEEDBACK_HEADER)
            
ensure_files_exist()

def read_users():
    with USERS_CSV.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
        
def check_credentials(username, password, area_code): 
    """Checks user credentials against the CSV file."""
    for u in read_users():
        if (u["username"] == username and 
            u["password_hash"] == hash_password(password)):
            
            if u.get("area_code") != area_code:
                return {"error": "area_code_mismatch"} 

            if u.get("region") != TARGET_REGION:
                return {"error": "region_mismatch"} 
                
            return u
    return None
    
def add_community_post(username, region, content, attachment_filename=""):
    """Adds a new community post to the CSV, now including an attachment."""
    with POSTS_CSV.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        # Includes the new attachment field
        w.writerow([str(uuid.uuid4()), username, region, content, datetime.utcnow().isoformat(), "0", attachment_filename])

def read_community_posts():
    """Reads all community posts."""
    with POSTS_CSV.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def update_post_votes(post_id, username):
    # ... [Voting logic remains identical] ...
    rows = []
    updated = False
    POST_HEADER = ["id","username","region","content","created_at", "votes", "attachment"]
    
    if "voted_posts" not in st.session_state:
        st.session_state.voted_posts = {}
        
    if post_id in st.session_state.voted_posts.get(username, []):
        return False
        
    with POSTS_CSV.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row["id"] == post_id:
                try:
                    current_votes = int(row.get("votes", 0))
                    row["votes"] = str(current_votes + 1)
                    updated = True
                except ValueError:
                    row["votes"] = "1"
                    updated = True
                    
            rows.append(row)
            
    if updated:
        with POSTS_CSV.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=POST_HEADER)
            w.writeheader()
            w.writerows(rows)
            
        if username not in st.session_state.voted_posts:
            st.session_state.voted_posts[username] = []
        st.session_state.voted_posts[username].append(post_id)
        
    return updated

def handle_vote(post_id, username):
    """Callback function to handle voting and rerun."""
    # Using t() for toast messages
    if update_post_votes(post_id, username):
        st.toast(t("Support registered successfully."))
    else:
        st.toast(t("You have already registered support for this discussion in this session."))
    st.rerun()

def get_dummy_location(house_details):
    # ... [Location logic remains identical] ...
    base_lat = 12.9150 
    base_lon = 76.6025
    
    hash_val = int(hashlib.sha1(house_details.encode('utf-8')).hexdigest(), 16)
    
    lat_offset = (hash_val % 1000) / 100000.0 - 0.005 
    lon_offset = (hash_val % 1000) / 100000.0 - 0.005
    
    return base_lat + lat_offset, base_lon + lon_offset

def list_complaints():
    """Reads all complaint records."""
    with COMPLAINTS_CSV.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def get_next_complaint_id():
    # ... [ID generation logic remains identical] ...
    complaints = list_complaints()
    max_id = 0
    
    for c in complaints:
        try:
            if c.get("id") and c["id"].isdigit():
                max_id = max(max_id, int(c["id"]))
        except ValueError:
            continue
            
    return str(max_id + 1)

def add_complaint(username, name, house, category, description, attachment_filename):
    """Adds a new complaint record, now storing the priority KEY."""
    new_id = get_next_complaint_id() 
    lat, lon = get_dummy_location(house)
    
    # Store the priority KEY (e.g., 'priority_high') 
    priority_key, sla_due = determine_priority_and_sla(category, description)
    
    # Store the STATUS KEY (e.g., 'status_open') 
    status_key = "status_open"
    
    COMPLAINT_HEADER = ["id","username","name","house","category","description","attachment","created_at","status","department","admin_notes","latitude","longitude","sla_due","priority"]
    with COMPLAINTS_CSV.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            new_id, 
            username, 
            name, 
            house, 
            category, 
            description, 
            attachment_filename, 
            datetime.utcnow().isoformat(), 
            status_key, # Store KEY
            "", 
            "", 
            lat, 
            lon, 
            sla_due,    
            priority_key    # Store KEY
        ])

# Function remains the same, but values stored/retrieved are keys
def update_complaint_status(complaint_id, new_status_key, department=None, admin_notes=None):
    """Updates the status (key), department, and notes for a complaint."""
    rows = []
    updated = False
    COMPLAINT_HEADER = ["id","username","name","house","category","description","attachment","created_at","status","department","admin_notes","latitude","longitude","sla_due","priority"]
    with COMPLAINTS_CSV.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row["id"] == complaint_id:
                row["status"] = new_status_key # new_status_key is now the English key
                if department is not None:
                    row["department"] = department
                if admin_notes is not None:
                    row["admin_notes"] = admin_notes
                updated = True
            rows.append(row)
    if updated:
        with COMPLAINTS_CSV.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COMPLAINT_HEADER)
            w.writeheader()
            w.writerows(rows)
    return updated

def read_announcements():
    """Reads all announcements."""
    with ANNOUNCEMENTS_CSV.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
        
def add_announcement(author, content, attachment_filename=""):
    """Adds a new announcement, including optional attachment."""
    ANNOUNCEMENT_HEADER = ["id","author","content","created_at", "attachment"] 
    with ANNOUNCEMENTS_CSV.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([str(uuid.uuid4()), author, content, datetime.utcnow().isoformat(), attachment_filename])

def read_feedback():
    """Reads all citizen feedback."""
    if not FEEDBACK_CSV.exists():
        return []
    with FEEDBACK_CSV.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def add_feedback(complaint_id, username, rating, suggestion):
    """Adds a new feedback record for a resolved complaint."""
    with FEEDBACK_CSV.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([complaint_id, username, rating, suggestion, datetime.utcnow().isoformat()])

    return True
    
def has_user_given_feedback(complaint_id):
    """Checks if the current user has already submitted feedback for a specific complaint."""
    all_feedback = read_feedback()
    return any(f.get('complaint_id') == complaint_id and f.get('username') == st.session_state.user["username"] for f in all_feedback)

@st.cache_data
def complaints_to_excel(data):
    """Generates an Excel file from the complaint data."""
    df = pd.DataFrame(data)
    
    # Translate status and priority keys back to English for the Excel export
    df['status'] = df['status'].apply(lambda x: TRANSLATIONS['en'].get(x, x))
    df['priority'] = df['priority'].apply(lambda x: TRANSLATIONS['en'].get(x, x))
    
    COLUMNS_ORDER = [
        "id", "created_at", "username", "name", "house", 
        "category", "priority", "description", "status", "department", 
        "admin_notes", "attachment", "latitude", "longitude", "sla_due"
    ]
    
    for col in COLUMNS_ORDER:
        if col not in df.columns:
            df[col] = ""

    df = df[COLUMNS_ORDER]
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Complaints_Data', index=False)
    
    return output.getvalue()


# -------------------------
# App initialization
# -------------------------
st.set_page_config(page_title=t("system_title"), page_icon="🏛️", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

if "voted_posts" not in st.session_state:
    st.session_state.voted_posts = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
if "show_profile_sidebar" not in st.session_state:
    st.session_state.show_profile_sidebar = False

def toggle_profile_sidebar():
    """Toggles the visibility of the profile sidebar."""
    st.session_state.show_profile_sidebar = not st.session_state.show_profile_sidebar
    
# -------------------------
# Login/Logout UIs - Updated to use t()
# -------------------------
def do_login():
    st.markdown(f"<h1 style='text-align: center;'>{t('system_title')}</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.subheader(t("system_login"))
        with st.form("login_form"):
            area_code = st.text_input(t("area_code"), key="login_area_code", placeholder=t("area_code"), max_chars=10)
            username = st.text_input(t("username"), key="login_username", placeholder=t("username"))
            password = st.text_input(t("password"), type="password", key="login_password", placeholder=t("password"))
            
            if st.form_submit_button(t("authenticate_button"), type="primary"):
                user_check = check_credentials(username.strip(), password, area_code.strip()) 
                
                if user_check is None:
                    st.error(t("Invalid Username or Password."))
                elif isinstance(user_check, dict) and user_check.get("error") == "region_mismatch":
                    st.error(t(f"Access Denied: This portal is exclusively for residents of **{TARGET_REGION}**."))
                elif isinstance(user_check, dict) and user_check.get("error") == "area_code_mismatch":
                    st.error(t("Access Denied: The provided Area Code is incorrect for this user account."))
                else:
                    if 'points' in user_check:
                         del user_check['points']
                         
                    st.session_state.user = user_check
                    st.success(t(f"Authentication successful, {st.session_state.user['username']}. Redirecting to service dashboard."))
                    st.rerun()
        st.markdown("---")
        st.caption(t("credential_admin")) 
        st.caption(t("credential_citizen"))
        st.markdown(t("<div style='text-align: center; margin-top: 15px;'>Only registered residents and authorized personnel of this community are permitted to log in.</div>"), unsafe_allow_html=True)

def do_logout():
    st.session_state.user = None
    st.session_state.chat_history = []
    st.session_state.voted_posts = {}
    st.session_state.show_profile_sidebar = False 
    st.success(t("Session terminated. You have been logged out successfully."))
    st.rerun()
    
# UPDATED: User Profile Sidebar Function (Now includes Language Toggle)
def user_profile_sidebar():
    """Displays user profile details, log out, and language toggle in a sidebar."""
    if st.session_state.user:
        current_user = st.session_state.user
        is_admin = current_user.get("is_admin") == "1"
        
        with st.sidebar:
            st.title(t("profile"))
            st.markdown("---")
            
            # --- LANGUAGE TOGGLE ---
            st.subheader("🌐 Language/ಬಾಷೆ")
            
            # Button for Kannada
            if st.button("ಕನ್ನಡ (Kannada)", key="lang_kn", use_container_width=True, disabled=(st.session_state.language == 'kn')):
                set_language('kn')
            # Button for English
            if st.button("English", key="lang_en", use_container_width=True, disabled=(st.session_state.language == 'en')):
                set_language('en')
            
            st.markdown("---")
            
            # --- PROFILE DETAILS ---
            if is_admin:
                st.image("https://api.dicebear.com/7.x/micah/svg?seed=Admin&radius=10&scale=100&backgroundType=solid&backgroundColor=0077b6", width=100)
            else:
                st.image(f"https://api.dicebear.com/7.x/initials/svg?seed={current_user['username']}&size=100&chars=2&backgroundType=solid&backgroundColor=d3d3d3&fontColor=2c3e50", width=100)
            
            st.markdown(f"## {current_user['username'].capitalize()}")
            role_text = t('administrator') if is_admin else t('citizen')
            st.subheader(f"{t('role')}: {role_text}")
            st.caption(f"Status: **{t('authenticated')}**")
            
            st.markdown("---")
            st.markdown(f"#### {t('registered_details')}")
            st.write(f"**{t('region_name')}:** {current_user.get('region', TARGET_REGION)}")
            st.write(f"**{t('area_code')}:** {current_user.get('area_code', 'N/A')}")
            
            st.markdown("---")
            
            if st.button(t("log_out"), key="sidebar_logout_btn", type="primary", use_container_width=True):
                do_logout()
    else:
        st.sidebar.warning(t("Please log in to view profile details."))


# -------------------------
# Chatbot Logic - Updated to use t()
# -------------------------
def chatbot_response(user_input):
    """Provides canned responses to guide the user through the portal. Logic remains English."""
    text = user_input.lower().strip()
    
    # Responses use t()
    if re.search(r'\b(hello|hi|hey|greetings|start|ನಮಸ್ಕಾರ|ಶುಭಾಶಯ)\b', text):
        return t("welcome_message")
    
    if re.search(r'\b(grievance|report|issue|problem|complaint|ಕುಂದುಕೊರತೆ|ಸಮಸ್ಯೆ|ವರದಿ)\b', text):
        return t(f"To file a new grievance, please use the **{t('tab_raise_grievance')}** section. You can monitor the progress of your existing grievances in **{t('tab_status_tracking')}**.")
    
    if re.search(r'\b(status|track|pending|resolved|progress|ಸ್ಥಿತಿ|ಟ್ರ್ಯಾಕ್|ಪ್ರಗತಿ)\b', text):
        return t(f"You can check the current status and resolution details for all your reported issues under the **{t('tab_status_tracking')}** section.")

    if re.search(r'\b(notice|announcement|news|circular|ಪ್ರಕಟಣೆ|ಸುದ್ದಿ)\b', text):
        return t(f"Official notifications and circulars from the administration are posted in the **{t('tab_announcements')}** section. Kindly check there for the latest information.")

    if re.search(r'\b(post|community|talk|discussion|neighbor|ಸಮುದಾಯ|ಚರ್ಚೆ)\b', text):
        return t(f"For community discussions and neighborhood updates, please navigate to the **{t('tab_community')}** tab.")
        
    if re.search(r'\b(admin|contact|official|department|ಆಡಳಿತ|ಸಂಪರ್ಕ)\b', text):
        return t("Direct departmental contact information is not provided here. Please file a grievance, and the relevant department will process it via the **Admin Grievance Management** system.")
        
    if re.search(r'emergency|life threatening|ತುರ್ತು|ಜೀವಕ್ಕೆ ಅಪಾಯ', text):
        return t("If this is a **life-threatening emergency**, please contact local emergency services immediately (e.g., Police, Fire, Ambulance). Our digital grievance system will automatically assign **Emergency** priority to your complaint.")

    if re.search(r'\b(feedback|suggestion|rate|improve|satisfaction|ಪ್ರತಿಕ್ರಿಯೆ|ಸಲಹೆ)\b', text):
        return t("We request your valuable feedback on resolved grievances. This can be submitted via the **Grievance Status Tracking** tab after a case is marked 'Resolved'.")

    return t("I am unable to process that specific request. Please rephrase your query or refer to the main navigation tabs for specific services.")

# UPDATED: Chatbot UI
def chatbot_ui():
    st.markdown(f"## {t('tab_assistant')}")
    st.info(t(f"This assistant provides guidance on navigating the public services available on the {t('region_name')} portal."))

    chat_container = st.container()
    with chat_container:
        for sender, message in st.session_state.chat_history:
            st.chat_message(sender).write(message) 
    
    user_input = st.chat_input(t("Enter your query here..."))
    
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        bot_response_text = chatbot_response(user_input)
        st.session_state.chat_history.append(("assistant", bot_response_text))
        st.rerun()

# -------------------------
# Citizen Feature UIs (Updated to use t())
# -------------------------

def community_post_ui(current_user):
    """UI for viewing and creating community posts."""
    st.markdown(f"## {t('tab_community')}")
    
    is_admin_user = current_user.get("is_admin") == "1"

    if is_admin_user:
        st.subheader(t("Administrative Post"))
    else:
        st.subheader(t("Initiate a New Public Discussion"))

    with st.container(border=True):
        with st.form("new_post_form", clear_on_submit=True):
            post_content = st.text_area(t("post_subject") + " (Max 500 characters)", max_chars=500, key="post_content_area")
            
            uploaded_file = st.file_uploader(
                t("post_image_upload"), 
                type=["jpg", "png", "jpeg"], 
                key="post_file"
            )
            st.caption(t("Maximum file size 5MB. Only image files supported for community posts."))
            
            button_label = t("post_as_admin") if is_admin_user else t("post_as_citizen")
            
            if st.form_submit_button(button_label, type="primary"):
                if not post_content.strip() and not uploaded_file:
                    st.error(t("post_error"))
                    return
                
                attachment_name = ""
                if uploaded_file:
                    ext = Path(uploaded_file.name).suffix
                    attachment_name = f"post_{uuid.uuid4()}{ext}"
                    with open(UPLOAD_DIR / attachment_name, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                        
                user_region = current_user.get("region", TARGET_REGION)
                add_community_post(current_user["username"], user_region, post_content.strip(), attachment_name) 
                st.success(t("post_success"))
                st.rerun()
                
    
    st.markdown("---")
    st.subheader(t("community_discussions").format(t("region_name")))
    posts = read_community_posts()
    current_user_region = current_user.get("region", TARGET_REGION)
    community_posts = [p for p in posts if p.get("region") == current_user_region]
    
    # Sorting logic remains the same
    try:
        community_posts.sort(key=lambda x: (int(x.get("votes", 0)), x.get("created_at")), reverse=True)
    except ValueError:
        community_posts.sort(key=lambda x: x.get("created_at"), reverse=True)

    if not community_posts:
        st.info(t("no_discussions"))
        return
        
    for p in community_posts:
        post_id = p['id']
        votes = int(p.get('votes', 0))
        attachment_filename = p.get('attachment')
        post_author = p['username']
        
        is_post_admin = (post_author == 'admin') 
        
        if is_post_admin:
            st.info(t("official_post_banner"))
            container_start = (
                f"<div style='border: 3px solid #0077b6; "
                f"border-left: 10px solid #0077b6; padding: 10px; "
                f"border-radius: 5px; margin-top: -15px; margin-bottom: 5px;'>"
            )
            container_end = "</div>"
            st.markdown(container_start, unsafe_allow_html=True)
            container_to_use = st.container()
        else:
            container_to_use = st.container(border=True)
            
        with container_to_use:
            
            col_content, col_vote = st.columns([4, 1])

            with col_content:
                if p['content']:
                    st.markdown(f"**{p['content']}**")
                else:
                    st.markdown(t("*(Image Post)*"))
                    
                if attachment_filename:
                    file_path = UPLOAD_DIR / attachment_filename
                    if file_path.exists():
                        st.image(str(file_path), caption=t("Attached Photo"), use_column_width=False, width=300)
            
                created_at_str = p["created_at"]
                try:
                    created_dt = datetime.fromisoformat(created_at_str)
                    formatted_time = created_dt.strftime("%d %b %Y, %I:%M %p")
                except ValueError:
                    formatted_time = p['created_at'].split('T')[0]
                
                author_display = t("region_admin") if is_post_admin else post_author
                
                st.caption(f"{t('posted_by')} **{author_display}** {t('on_date')} {formatted_time}")
            
            with col_vote:
                st.button(
                    label=f"{t('Support')} ({votes})", 
                    key=f"vote_{post_id}", 
                    on_click=handle_vote, 
                    args=(post_id, current_user['username']),
                    type="secondary",
                    use_container_width=True,
                    help=t("Register support for this discussion topic.")
                )
        
        if is_post_admin:
            st.markdown(container_end, unsafe_allow_html=True)
            
        st.markdown("\n")


def complaint_form_ui(current_user):
    """UI for submitting a new complaint."""
    st.markdown(f"## {t('file_grievance_title')}")
    st.info(t("file_grievance_info"))
    with st.form("complaint_form", clear_on_submit=True):
        
        name = st.text_input(t("name_input"), 
                              value=current_user["username"], 
                              key="complaint_name", 
                              help=t("This name will be used for all correspondence."))
        
        house = st.text_input(t("house_input"), 
                              key="complaint_house", 
                              placeholder=t("house_placeholder"))
        
        st.markdown("---")
        
        # Categories remain English keys, but displayed label is translated
        categories = {
            "Sanitation": t("Sanitation"),
            "Security": t("Security"),
            "Water Supply": t("Water Supply"),
            "Electricity/Power": t("Electricity/Power"),
            "Infrastructure/Roads": t("Infrastructure/Roads"),
            "General Administration": t("General Administration")
        }
        category_options = list(categories.keys())
        display_options = list(categories.values())
        
        selected_display = st.selectbox(t("grievance_category"), display_options, key="complaint_category_display")
        
        # Map the selected display name back to the English key for storage
        category_key = next(k for k, v in categories.items() if v == selected_display)
        
        description = st.text_area(t("grievance_desc"), 
                                     height=100, 
                                     key="complaint_desc", 
                                     placeholder=t("grievance_desc_placeholder"))
        
        st.markdown("---")
        
        st.subheader(t("attachment_header"))
        file = st.file_uploader(t("attachment_upload"), type=["jpg", "png", "jpeg", "pdf"], key="complaint_file")
        st.caption(t("Maximum file size 5MB. Location details should be explicitly mentioned in the description if not embedded in the file."))
        st.markdown("---")
        
        submitted = st.form_submit_button(t("submit_grievance"), type="primary", use_container_width=True)
        if submitted:
            if not house or not description:
                st.error(t("Action Required: Please complete the Address/Property Identification and the Detailed Description."))
                return
            attachment_name = ""
            if file:
                ext = Path(file.name).suffix
                attachment_name = f"{uuid.uuid4()}{ext}"
                with open(UPLOAD_DIR / attachment_name, "wb") as f:
                    f.write(file.getbuffer())
            
            # Use the English key (category_key) for storage
            add_complaint(current_user["username"], name, house, category_key, description, attachment_name)
            st.success(t("Grievance formally submitted. Please check 'Grievance Status Tracking' for updates."))
            st.rerun()


def my_complaints_ui(current_user):
    """UI for citizens to track their complaints and submit feedback."""
    st.markdown(f"## {t('tab_status_tracking')}")
    data = list_complaints()
    user_data = [d for d in data if d["username"] == current_user["username"]]
    
    if not user_data:
        st.info(t("no_grievances"))
        return
        
    st.markdown("---")

    for c in user_data[::-1]:
        # Status and Priority keys are retrieved from CSV
        status_key = c.get('status', 'status_open')
        department = c.get('department', t('Not Yet Assigned'))
        admin_notes = c.get('admin_notes', t('No specific updates yet.'))
        complaint_id = c['id']
        priority_key = c.get('priority', 'priority_standard')
        sla_due_iso = c.get('sla_due')
        
        # Translate keys for display
        status = t(status_key)
        priority = t(priority_key)

        # Determine EMOJI for Status
        status_emoji = '⚫'
        if status_key == 'status_open':
            status_emoji = '🔴'
        elif status_key == 'status_resolved':
            status_emoji = '🟢'
        elif status_key == 'status_in_progress':
            status_emoji = '🟡'
            
        # Determine EMOJI for Priority
        priority_emoji = '🔷'
        if priority_key == "priority_emergency":
            priority_emoji = '🚨'
        elif priority_key == "priority_high":
            priority_emoji = '🟠'
        
        expander_label = (
            f"{priority_emoji} **{priority}** | {status_emoji} **{status}** | "
            f"*{t(c['category'])}* (ID {complaint_id})"
        )
        
        with st.expander(expander_label, expanded=False): 
            
            st.markdown(f"**{t('Location/Property')}:** {c['house']}")
            st.markdown(f"**{t('Grievance Summary')}:** {c['description']}")

            st.markdown("---")
            st.markdown(f"#### **{t('resolution_status')}**")
            
            sla_text = t("N/A")
            if sla_due_iso and status_key != 'status_resolved':
                try:
                    sla_dt = datetime.fromisoformat(sla_due_iso)
                    time_remaining = sla_dt - datetime.utcnow()
                    if time_remaining.total_seconds() < 0:
                        sla_text = f"**{t('sla_overdue')}**"
                    else:
                        sla_text = f"{t('Target Resolution')}: {sla_dt.strftime('%d %b')}"
                except ValueError:
                    sla_text = t("SLA Calculation Error")

            st.markdown(f"{t('Current Status')}: **{status_emoji} {status}** | **{sla_text}**")

            if status_key == 'status_resolved':
                st.success(f"**{t('Resolved by Department')}:** **{department}**")
            else:
                st.info(f"**{t('Current Department Assignment')}:** **{department}**")

            st.markdown(f"**{t('Administrative Notes')}:**")
            if admin_notes:
                st.write(admin_notes)
            else:
                st.caption(t("notes_caption"))
            
            st.caption(f"{t('Grievance Reference ID')}: {complaint_id}")
            
            # --- CONDITIONAL FEEDBACK FORM ---
            if status_key == 'status_resolved':
                st.markdown("---")
                if not has_user_given_feedback(complaint_id):
                    st.subheader(t("feedback_survey"))
                    st.info(t("feedback_info"))

                    with st.form(f"feedback_form_{complaint_id}", clear_on_submit=True):
                        # Use English keys for consistency, translate in the UI
                        rating_options_en = [
                            "5 - Highly Satisfied", "4 - Satisfied", "3 - Neutral", 
                            "2 - Dissatisfied", "1 - Highly Dissatisfied"
                        ]
                        
                        if st.session_state.language == 'kn':
                             rating_options_kn = [
                                "5 - ಹೆಚ್ಚು ತೃಪ್ತಿ", "4 - ತೃಪ್ತಿ", "3 - ತಟಸ್ಥ", 
                                "2 - ಅತೃಪ್ತಿ", "1 - ಹೆಚ್ಚು ಅತೃಪ್ತಿ"
                            ]
                             display_options = rating_options_kn
                        else:
                            display_options = rating_options_en

                        rating = st.radio(t("feedback_rating"), display_options, index=1, key=f"rating_{complaint_id}")
                        
                        suggestion = st.text_area(t("feedback_suggestion"), 
                                                     max_chars=300, 
                                                     key=f"suggestion_{complaint_id}")
                        
                        if st.form_submit_button(t("feedback_submit"), type="primary"):
                            # Always store the simple numeric rating
                            clean_rating = rating.split(' - ')[0]
                            
                            if add_feedback(complaint_id, current_user["username"], clean_rating, suggestion.strip()):
                                st.success(t("feedback_success"))
                                st.rerun()
                            else:
                                st.error(t("Failed to submit feedback."))
                else:
                    st.success(t("✅ Feedback for this resolution has already been recorded."))
            
        st.markdown("\n") 


def announcements_ui():
    """UI for viewing official announcements."""
    st.markdown(f"## {t('tab_announcements')}")
    ann = read_announcements() 
    
    if not ann:
        st.info(t("No official announcements or circulars available at this time."))
        return
        
    for idx, a in enumerate(ann[::-1]):
        with st.container(border=True):
            st.markdown(f"**{a['content']}**")
            
            attachment_filename = a.get("attachment")
            if attachment_filename:
                file_path = UPLOAD_DIR / attachment_filename
                if file_path.exists():
                    st.markdown("---")
                    
                    ext = file_path.suffix.lower()
                    if ext in [".jpg", ".jpeg", ".png"]:
                        st.image(str(file_path), caption=t("Attached Image/Notice"), use_column_width=True)
                    else:
                        st.download_button(
                            label=t(f"Download Attached Document ({ext.upper()})"),
                            data=file_path.read_bytes(),
                            file_name=attachment_filename,
                            key=f"ann_download_{a['id']}",
                            help=t("Download official circular document.")
                        )

            created_at_str = a["created_at"]
            try:
                created_dt = datetime.fromisoformat(created_at_str)
                formatted_time = created_dt.strftime("%d %B %Y | %I:%M %p UTC")
            except ValueError:
                formatted_time = a['created_at'].split('T')[0] 
            
            st.caption(f"{t('Issued by')}: {a['author']} | {t('Date')}: {formatted_time}")
        st.markdown("\n")


# -------------------------
# Admin Feature UIs (Updated to use t())
# -------------------------
def admin_post_announcement_ui(current_user):
    """Admin UI for creating new announcements, and displays existing announcements below."""
    st.markdown(f"## {t('admin_tab_publish')}")
    
    # 1. Announcement Publishing Form
    with st.form("announcement_form", clear_on_submit=True):
        
        text = st.text_area(t("admin_content_label") + " (Max 500 characters)", max_chars=500, key="admin_announcement_text", placeholder=t("admin_content_placeholder"))
        
        file = st.file_uploader(t("Upload Supporting Image/Document (Optional)"), 
                                 type=["jpg", "png", "jpeg", "pdf"], 
                                 key="announcement_file")
        st.caption(t("Acceptable formats: JPG, PNG, PDF. One attachment per announcement."))
        st.markdown("---")
        
        if st.form_submit_button(t("admin_publish_button"), type="primary"):
            if not text.strip() and not file:
                st.error(t("Error: Announcement must contain text or an attached document."))
                return
                
            attachment_name = ""
            if file:
                ext = Path(file.name).suffix
                attachment_name = f"{uuid.uuid4()}{ext}"
                with open(UPLOAD_DIR / attachment_name, "wb") as f:
                    f.write(file.getbuffer())
                    
            add_announcement(current_user["username"], text.strip(), attachment_name)
            st.success(t("Official Announcement published successfully to the portal."))
            st.rerun()
            
    # 2. Display Existing Announcements
    st.markdown("---")
    st.subheader(t("current_announcements"))
    announcements_ui()


def admin_hotspot_map_ui():
    """Admin UI for Complaint Map Hotspots."""
    st.markdown(f"## {t('admin_tab_map')}: Geographic Incident Mapping")
    
    data = list_complaints()
    if not data:
        st.info(t("No recorded grievances to display on the geographic map."))
        return

    df = pd.DataFrame(data)
    
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    
    st.markdown(f"### {t('Visualization of Active and Pending Grievance Locations')}")
    map_data = df.dropna(subset=['latitude', 'longitude'])
    
    if not map_data.empty:
        st.map(map_data, 
                latitude='latitude', 
                longitude='longitude', 
                size='id', 
                color='#0077b6',
                zoom=15, 
                use_container_width=True
                )

    else:
        st.warning(t("No location data available for plotting the geographic map."))


def admin_analysis_ui():
    """Admin UI for Status Breakdown by Category chart."""
    st.markdown(f"## {t('admin_tab_analysis')}: Grievance Status Breakdown")
    
    data = list_complaints()
    if not data:
        st.info(t("No grievance data submitted for performance analysis."))
        return
        
    df = pd.DataFrame(data)
    
    # Translate keys to English for reliable Pandas grouping
    df['status'] = df['status'].apply(lambda x: TRANSLATIONS['en'].get(x, x))
    df['category'] = df['category'].apply(lambda x: TRANSLATIONS['en'].get(x, x))
    
    st.markdown(f"### {t('Grievance Volume by Category and Resolution Status')}")
    
    status_counts = df.groupby(['category', 'status']).size().reset_index(name=t('Count'))

    if not status_counts.empty:
        st.bar_chart(
            status_counts, 
            x='category', 
            y=t('Count'), 
            color='status',
            use_container_width=True
        )
        st.caption(t("Total count of grievances categorized by type and their current processing status."))
    else:
        st.info(t("Insufficient data for status breakdown chart."))


def admin_review_feedback_ui():
    """Admin UI for reviewing citizen feedback on resolutions."""
    st.markdown(f"## {t('admin_tab_feedback')}: Resolution Feedback")
    st.subheader(t("Citizen Feedback on Resolved Grievances"))
    all_feedback = read_feedback()
    
    if not all_feedback:
        st.info(t("No citizen feedback has been submitted for resolved grievances yet."))
        return

    try:
        total_rating = sum(int(f.get('rating', 0)) for f in all_feedback)
        avg_rating = total_rating / len(all_feedback) if len(all_feedback) > 0 else 0
    except ValueError:
        avg_rating = 0
        
    col_count, col_avg = st.columns(2)
    col_count.metric(t("Total Feedback Records"), len(all_feedback))
    col_avg.metric(t("Average Satisfaction Rating (1-5)"), f"{avg_rating:.2f}")

    st.markdown("---")
    st.markdown(f"### {t('Individual Feedback Records (Most Recent First)')}")
    for f in all_feedback[::-1]:
        rating_value = int(f.get('rating', 0))
        
        # Formal rating color mapping
        if rating_value >= 4:
            icon = t("High Satisfaction")
        elif rating_value == 3:
            icon = t("Neutral")
        else:
            icon = t("Low Satisfaction")
            
        complaint_id_display = f.get('complaint_id', t('N/A (Old Record)'))
            
        with st.expander(f"{t('Rating')}: {rating_value}/5 | {t('Status')}: {icon} | {t('Date')}: {f['created_at'].split('T')[0]}", expanded=False):
            st.caption(f"{t('Reference Grievance ID')}: `{complaint_id_display}` ({t('Submitted by')}: {f['username']})")
            if f['suggestion']:
                st.write(f"**{t('Citizen Comment/Suggestion')}:** {f['suggestion']}")
            else:
                st.caption(t("No written comment provided by citizen."))
        st.markdown("\n")


def admin_manage_complaints_ui(current_user):
    """Admin UI for viewing and updating all citizen complaints, split into tabs."""
    st.markdown(f"## {t('admin_manage_title')}")
    data = list_complaints()
    
    if not data:
        st.info(t("No grievances have been filed by citizens yet."))
        return

    # Sort data by Priority KEY (Emergency first) and then by creation date
    priority_order = {"priority_emergency": 3, "priority_high": 2, "priority_standard": 1}
    data.sort(key=lambda x: (priority_order.get(x.get('priority', 'priority_standard'), 1), x.get('created_at', '2000-01-01T00:00:00')), reverse=True)


    tab_management, tab_export = st.tabs([t("Individual Grievance Processing"), t("Data Export and Review")])

    with tab_management:
        st.subheader(t("Active and Pending Grievances (Prioritized List)"))
        st.markdown("---")
        
        for idx, c in enumerate(data): 
            
            # Retrieve keys from CSV
            status_key = c.get('status', 'status_open')
            priority_key = c.get('priority', 'priority_standard') 
            
            # Translate keys for display
            status = t(status_key)
            priority = t(priority_key)
            
            sla_due_iso = c.get('sla_due')                      
            complaint_id = c['id'] 
            current_dept = c.get('department', t('Unassigned'))
            current_notes = c.get('admin_notes', '')

            # Calculate and display SLA (Time Remaining)
            sla_text = ""
            sla_color = "gray"
            
            if sla_due_iso and status_key != 'status_resolved':
                try:
                    sla_dt = datetime.fromisoformat(sla_due_iso)
                    time_remaining = sla_dt - datetime.utcnow()
                    
                    if time_remaining.total_seconds() < 0:
                        sla_text = t("sla_overdue")
                        sla_color = "#FF4B4B" # Red for overdue
                    elif time_remaining.days < 1:
                        hours_remaining = int(time_remaining.total_seconds() / 3600)
                        if hours_remaining <= 0:
                            sla_text = t("sla_due_now")
                            sla_color = "#FF4B4B"
                        else:
                            sla_text = f"{t('Due in')}: {hours_remaining} {t('hrs')}"
                            sla_color = "#FFA500" # Orange for imminent
                    else:
                        sla_text = f"{t('Due in')}: {time_remaining.days} {t('days')}"
                        sla_color = "green"
                except ValueError:
                    sla_text = t("SLA Error")

            # Priority Styling
            priority_color = "blue"
            if priority_key == "priority_emergency":
                priority_color = "red"
            elif priority_key == "priority_high":
                priority_color = "orange"

            with st.container(border=True):
                
                # --- HEADER ROW: Priority, SLA, Status ---
                header_cols = st.columns([2, 2, 2])
                with header_cols[0]:
                    st.markdown(f"**{t('Priority')}:** <span style='font-weight: bold; color: {priority_color};'>{priority.upper()}</span>", unsafe_allow_html=True)
                with header_cols[1]:
                    if status_key != 'status_resolved':
                        st.markdown(f"**{t('sla_status')}:** <span style='font-weight: bold; color: {sla_color};'>{sla_text}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{t('sla_status')}:** <span style='font-weight: bold; color: green;'>{t('RESOLVED')}</span>", unsafe_allow_html=True)
                with header_cols[2]:
                    status_text_display = status.upper()
                    status_color_display = "gray"
                    if status_key == 'status_open':
                        status_color_display = "#FF4B4B" 
                    elif status_key == 'status_resolved':
                        status_color_display = "#00FF7F" 
                    else:
                        status_color_display = "#FFA500" 
                    st.markdown(f"<div style='text-align: right;'>{t('Status')}: <span style='font-weight: bold; color: {status_color_display};'>{status_text_display}</span></div>", unsafe_allow_html=True)
                
                st.markdown("---")

                # --- COMPLAINT DETAILS ROW ---
                st.markdown(f"### {t('Reference No.')} <span style='color:#0077b6;'>{complaint_id}</span>: {t(c['category'])}", unsafe_allow_html=True)
                st.caption(f"{t('Filed by')}: **{c['username']}** | {t('Location')}: {c['house']} | {t('Date')}: {c['created_at'].split('T')[0]}")


                with st.expander(t("Grievance Details and Resolution Action"), expanded=(status_key == 'status_open' or priority_key == 'priority_emergency')):
                    st.markdown("---")
                    st.markdown(f"#### {t('Complaint Details')}")
                    st.write(f"**{t('Full Description')}:** {c['description']}")
                    
                    if c["attachment"]:
                        file_path = UPLOAD_DIR / c["attachment"]
                        if file_path.exists():
                            st.download_button(t("Download Attached Supporting Document"), file_path.read_bytes(), c["attachment"], key=f"admin_download_{complaint_id}")
                    
                    st.markdown("---")
                    st.markdown(f"#### **{t('admin_action')}**")

                    col_status, col_assign = st.columns(2)
                    
                    with col_status:
                        # Status Update Form
                        with st.form(f"status_update_form_{complaint_id}"):
                            st.markdown(f"**1. {t('update_status')}**")
                            
                            # Use English Keys for the options list
                            status_options_keys = ["status_open", "status_in_progress", "status_resolved"]
                            # Translate the keys for display
                            status_options_display = [t(k) for k in status_options_keys]
                            
                            try:
                                current_status_index = status_options_keys.index(status_key)
                            except ValueError:
                                current_status_index = 0

                            new_status_display = st.selectbox(
                                t("Select New Status"), 
                                status_options_display, 
                                index=current_status_index, 
                                key=f"status_select_{complaint_id}"
                            )
                            # Find the key for the selected display name
                            new_status_key = status_options_keys[status_options_display.index(new_status_display)]
                            
                            if st.form_submit_button(t("execute_status"), type="primary", use_container_width=True):
                                if update_complaint_status(complaint_id, new_status_key, current_dept, current_notes):
                                    st.success(t(f"Grievance status successfully updated to **{new_status_display}**."))
                                    st.rerun()
                                else:
                                    st.error(t("Error executing status update."))
                    
                    with col_assign:
                        # Assignment and Notes Form
                        with st.form(f"assignment_update_form_{complaint_id}"):
                            st.markdown(f"**2. {t('assign_dept')}**")
                            DEPARTMENTS = [t("Sanitation Dept."), t("Security & Law Enforcement"), t("Water Management"), t("Electrical Board"), t("Public Works/Roads"), t("General Administration"), t("Unassigned")]
                            
                            try:
                                current_dept_index = DEPARTMENTS.index(current_dept)
                            except ValueError:
                                current_dept_index = len(DEPARTMENTS) - 1

                            updated_department = st.selectbox(t("Assign to Department"), DEPARTMENTS, index=current_dept_index, key=f"dept_select_{complaint_id}")
                            updated_notes = st.text_area(t("admin_assignment_note"), value=current_notes, key=f"notes_text_{complaint_id}", height=100)
                            
                            if st.form_submit_button(t("save_assignment"), type="secondary", use_container_width=True):
                                if update_complaint_status(complaint_id, status_key, updated_department, updated_notes):
                                    st.info(t("Department assignment and notes saved successfully."))
                                    st.rerun()
                                else:
                                    st.error(t("Error saving administrative data."))
                                    
            st.markdown("\n") 
            
    with tab_export:
        st.subheader(t("Full Grievance Data Table"))

        st.caption(t("Complete, scrollable data set of all citizen grievances."))
        st.dataframe(pd.DataFrame(data).sort_values(by='created_at', ascending=False).reset_index(drop=True), use_container_width=True, height=500)

        st.markdown("---")

        excel_data = complaints_to_excel(data)

        st.download_button(
            label=t("download_data"),
            data=excel_data,
            file_name=f"Grievance_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )


# -------------------------
# Main App Flow
# -------------------------
st.title(t("system_title"))

is_admin = st.session_state.user and st.session_state.user["is_admin"] == "1"

# --- Login/Logout Header ---
if st.session_state.user:
    st.markdown("---")
    header_cols = st.columns([8.5, 1])
    with header_cols[1]:
        if st.button(f"☰ {t('profile')}", key="header_profile_btn", use_container_width=True, on_click=toggle_profile_sidebar):
            pass 
    st.markdown("---")

# --- Conditional Sidebar Rendering ---
if st.session_state.show_profile_sidebar:
    user_profile_sidebar()

# --- Content Rendering ---

if not st.session_state.user:
    st.warning(t("access_required"))
    do_login()
    st.stop()
    
# Post-login state content rendering (using st.tabs)

if is_admin:
    # --- ADMIN VIEW (Community Board REMOVED) ---
    pages = [
        t("admin_tab_manage"),         
        t("admin_tab_feedback"),
        t("admin_tab_analysis"),                             
        t("admin_tab_map"),                          
        t("admin_tab_publish"),         
    ] 
    
    tab_manage_comp, tab_feedback, tab_status_breakdown, tab_map_analytics, tab_post_ann = st.tabs(pages)
    
    with tab_manage_comp:
        admin_manage_complaints_ui(st.session_state.user)
        
    with tab_feedback:
        admin_review_feedback_ui()

    with tab_status_breakdown:
        admin_analysis_ui() 

    with tab_map_analytics:
        admin_hotspot_map_ui() 
        
    with tab_post_ann:
        admin_post_announcement_ui(st.session_state.user)
        
else:
    # --- CITIZEN VIEW ---
    pages = [
        t("tab_announcements"), 
        t("tab_raise_grievance"), 
        t("tab_status_tracking"), 
        t("tab_community"), 
        t("tab_assistant")
    ] 
    
    tab_announcements, tab_raise, tab_mycomplaints, tab_community, tab_bot = st.tabs(pages)
    
    with tab_announcements:
        announcements_ui()

    with tab_raise:
        complaint_form_ui(st.session_state.user)
        
    with tab_mycomplaints:
        my_complaints_ui(st.session_state.user)
        
    with tab_community: 
        community_post_ui(st.session_state.user)
        
    with tab_bot:
        chatbot_ui()