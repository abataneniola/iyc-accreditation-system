import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, date
import os
import tempfile

# Page configuration
st.set_page_config(page_title="IYC Accreditation System", page_icon="📋", layout="wide")

# Define zones and their branches
ZONES_BRANCHES = {
    "Ayetoro Zone": ["Ayetoro", "Imasayi", "Kajola", "Igbogila", "Imala"],
    "Ilaro Zone": ["Ilaro", "Idogo", "Ohunbe", "Oja odan", "Iwoye"],
    "Itori-Oke Zone": ["Itori-Oke", "Adehun", "Olosun", "Ibara-Orile", "Adigbe", "Olomore", "Ita-Oshin"],
    "Oke Abetu Zone": ["Oke-Abetu", "Gbonagun", "Mawuko", "Ita Elega", "Imeko", "Igbo-Ora", "Jangede"],
    "Owode Zone": ["Powerline", "Kajola", "Ogunmakin", "Obafemi", "Ofada", "Odofin-Oke", "Oba-Erin", "Itoku-Aro", "Siun"],
    "Odeda Zone": ["Odeda", "Agbetu", "Olugbo", "Orile-ilugun", "Olofin", "Fagbohun", "Olokokun"]
}

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
    }
    .success-message {
        padding: 10px;
        background-color: #d4edda;
        color: #155724;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-message {
        padding: 10px;
        background-color: #fff3cd;
        color: #856404;
        border-radius: 5px;
        margin: 10px 0;
    }
    .remove-button > button {
        background-color: #dc3545;
        color: white;
    }
    .remove-button > button:hover {
        background-color: #c82333;
    }
    .present-badge {
        background-color: #28a745;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        display: inline-block;
    }
    .absent-badge {
        background-color: #dc3545;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        display: inline-block;
    }
    .not-marked-badge {
        background-color: #ffc107;
        color: #856404;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize ALL session state variables at the beginning
def initialize_session_state():
    """Initialize all session state variables"""
    if 'participants_df' not in st.session_state:
        st.session_state.participants_df = None
    if 'attendance_df' not in st.session_state:
        st.session_state.attendance_df = None
    if 'new_participants' not in st.session_state:
        st.session_state.new_participants = []
    if 'show_success' not in st.session_state:
        st.session_state.show_success = False
    if 'success_message' not in st.session_state:
        st.session_state.success_message = ""
    if 'clear_form' not in st.session_state:
        st.session_state.clear_form = False
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = None
    if 'selected_zone' not in st.session_state:
        st.session_state.selected_zone = "Ayetoro Zone"
    if 'temp_file_path' not in st.session_state:
        st.session_state.temp_file_path = None
    if 'last_save_time' not in st.session_state:
        st.session_state.last_save_time = None
    if 'auto_save_enabled' not in st.session_state:
        st.session_state.auto_save_enabled = True

# Call initialization
initialize_session_state()

def save_to_temp_file(df):
    """Save dataframe to temporary file for persistence"""
    if df is not None and st.session_state.auto_save_enabled:
        try:
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"iyc_accreditation_{st.session_state.uploaded_file_name}.csv")
            df.to_csv(temp_file, index=False)
            st.session_state.temp_file_path = temp_file
            st.session_state.last_save_time = datetime.now()
            return True
        except Exception as e:
            st.error(f"Error saving to temp file: {str(e)}")
            return False
    return False

def load_from_temp_file():
    """Load dataframe from temporary file"""
    if st.session_state.temp_file_path and os.path.exists(st.session_state.temp_file_path):
        try:
            df = pd.read_csv(st.session_state.temp_file_path)
            return df
        except Exception as e:
            st.error(f"Error loading from temp file: {str(e)}")
            return None
    return None

def load_csv(file):
    """Load CSV file and prepare dataframe"""
    try:
        df = pd.read_csv(file)
        # Standardize column names (remove spaces, make lowercase)
        df.columns = df.columns.str.strip().str.replace(' ', '_')
        
        # Add unique ID if not present
        if 'participant_id' not in df.columns:
            df.insert(0, 'participant_id', [str(uuid.uuid4())[:8] for _ in range(len(df))])
        
        # Add attendance status column if not present
        if 'attendance_status' not in df.columns:
            df['attendance_status'] = 'Not Marked'
        
        # Add attendance timestamp column
        if 'attendance_time' not in df.columns:
            df['attendance_time'] = ''
        
        # Save to temp file for persistence
        save_to_temp_file(df)
        
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def search_participants(df, search_term, search_by):
    """Search participants by selected field"""
    if search_term:
        mask = df[search_by].astype(str).str.contains(search_term, case=False, na=False)
        return df[mask]
    return df

def add_new_participant(df, new_data):
    """Add new participant to dataframe"""
    new_id = str(uuid.uuid4())[:8]
    new_row = {
        'participant_id': new_id,
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'First_Name': new_data['first_name'],
        'Last_Name': new_data['last_name'],
        'Username/Email': new_data['email'],
        'Phone_Number': new_data['phone'],
        'Date_of_Birth': new_data['dob'],
        'Gender': new_data['gender'],
        'Zone': new_data['zone'],
        'Branch_Church': new_data['branch'],
        'Marital_Status': new_data['marital_status'],
        'Occupation': new_data['occupation'],
        'Preferred_Password': new_data['password'],
        'attendance_status': 'Present',
        'attendance_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Save to temp file after adding
    save_to_temp_file(updated_df)
    
    return updated_df

def update_attendance(df, participant_id, status):
    """Update attendance status for a participant"""
    df.loc[df['participant_id'] == participant_id, 'attendance_status'] = status
    df.loc[df['participant_id'] == participant_id, 'attendance_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Save to temp file after update
    save_to_temp_file(df)
    
    return df

def remove_csv():
    """Remove the loaded CSV and reset all data"""
    st.session_state.participants_df = None
    st.session_state.uploaded_file_name = None
    st.session_state.show_success = False
    st.session_state.success_message = ""
    
    # Clear temp file if exists
    if st.session_state.temp_file_path and os.path.exists(st.session_state.temp_file_path):
        try:
            os.remove(st.session_state.temp_file_path)
        except:
            pass
    st.session_state.temp_file_path = None

def get_attendance_badge(status):
    """Return HTML badge for attendance status"""
    if status == 'Present':
        return '✅ Present'
    elif status == 'Absent':
        return '❌ Absent'
    else:
        return '⏳ Not Marked'

def main():
    st.title("🎯 IYC Participants Accreditation System")
    st.markdown("---")
    
    # Check for temp file recovery on startup
    if st.session_state.participants_df is None and st.session_state.temp_file_path:
        recovered_df = load_from_temp_file()
        if recovered_df is not None:
            st.session_state.participants_df = recovered_df
            st.warning("🔄 Recovered previously saved data from temporary storage!")
    
    # Display success message if exists
    if st.session_state.show_success:
        st.success(st.session_state.success_message)
        st.session_state.show_success = False
        st.session_state.success_message = ""
    
    # Auto-save status indicator
    if st.session_state.participants_df is not None and st.session_state.last_save_time:
        st.caption(f"💾 Last auto-saved: {st.session_state.last_save_time.strftime('%H:%M:%S')}")
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Data Management")
        
        # Auto-save toggle
        if st.session_state.participants_df is not None:
            auto_save = st.checkbox("Enable Auto-Save", value=st.session_state.auto_save_enabled)
            if auto_save != st.session_state.auto_save_enabled:
                st.session_state.auto_save_enabled = auto_save
                if auto_save and st.session_state.participants_df is not None:
                    save_to_temp_file(st.session_state.participants_df)
                    st.success("Auto-save enabled and data saved!")
        
        # Manual save button
        if st.session_state.participants_df is not None:
            if st.button("💾 Manual Save Now", use_container_width=True):
                if save_to_temp_file(st.session_state.participants_df):
                    st.success(f"Data saved manually at {datetime.now().strftime('%H:%M:%S')}")
                else:
                    st.error("Failed to save data")
        
        st.markdown("---")
        
        # Show current file status
        if st.session_state.participants_df is not None:
            st.info(f"📄 Currently loaded: **{st.session_state.uploaded_file_name}**")
            st.markdown(f"**Total records:** {len(st.session_state.participants_df)}")
            
            # Show recent changes
            present_count = len(st.session_state.participants_df[st.session_state.participants_df['attendance_status'] == 'Present'])
            st.caption(f"✅ Present: {present_count}")
        
        # File uploader (only show if no file loaded or after removal)
        if st.session_state.participants_df is None:
            uploaded_file = st.file_uploader("Upload CSV File", type=['csv'])
            
            if uploaded_file is not None:
                st.session_state.participants_df = load_csv(uploaded_file)
                st.session_state.uploaded_file_name = uploaded_file.name
                if st.session_state.participants_df is not None:
                    st.success(f"✅ Loaded {len(st.session_state.participants_df)} participants")
                    st.rerun()
        
        # Remove CSV button (only show if file is loaded)
        if st.session_state.participants_df is not None:
            st.markdown("---")
            st.markdown('<div class="remove-button">', unsafe_allow_html=True)
            if st.button("🗑️ Remove Current CSV", type="secondary", use_container_width=True):
                remove_csv()
                st.success("CSV data removed! You can now upload a new file.")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Download button
        if st.session_state.participants_df is not None:
            st.markdown("---")
            st.header("💾 Export Data")
            
            # Prepare download data
            download_df = st.session_state.participants_df.copy()
            
            # Remove password column for download (optional)
            if 'Preferred_Password' in download_df.columns:
                download_df = download_df.drop(columns=['Preferred_Password'])
            
            csv = download_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Updated CSV",
                data=csv,
                file_name=f"iyc_participants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Statistics with visual indicators
            st.markdown("---")
            st.header("📊 Attendance Statistics")
            total = len(st.session_state.participants_df)
            present = len(st.session_state.participants_df[st.session_state.participants_df['attendance_status'] == 'Present'])
            absent = len(st.session_state.participants_df[st.session_state.participants_df['attendance_status'] == 'Absent'])
            not_marked = len(st.session_state.participants_df[st.session_state.participants_df['attendance_status'] == 'Not Marked'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Participants", total)
                st.metric("✅ Present", present, delta=f"{present/total*100:.1f}%" if total > 0 else "0%")
            with col2:
                st.metric("❌ Absent", absent, delta=f"{absent/total*100:.1f}%" if total > 0 else "0%")
                st.metric("⏳ Not Marked", not_marked, delta=f"{not_marked/total*100:.1f}%" if total > 0 else "0%")
    
    # Main content area
    if st.session_state.participants_df is not None:
        df = st.session_state.participants_df
        
        # Search section
        st.header("🔍 Search Participant")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("Enter search term", placeholder="Type name, branch, or zone...", key="search_input")
        
        with col2:
            search_by = st.selectbox("Search by", ['First_Name', 'Last_Name', 'Zone', 'Branch_Church', 'Username/Email', 'attendance_status'], key="search_by")
        
        with col3:
            if st.button("🔄 Clear Search", use_container_width=True):
                search_term = ""
                st.rerun()
        
        # Search and display results
        if search_term:
            filtered_df = search_participants(df, search_term, search_by)
            st.info(f"Found {len(filtered_df)} matching participants")
        else:
            filtered_df = df
            st.info(f"Showing all {len(filtered_df)} participants")
        
        # Display participants in a table with attendance buttons
        st.markdown("---")
        st.header("📋 Participants List")
        
        # Display each participant in an expandable card
        for idx, participant in filtered_df.iterrows():
            # Get attendance badge text
            attendance_badge = get_attendance_badge(participant.get('attendance_status', 'Not Marked'))
            
            # Create expander without HTML in title
            with st.expander(f"👤 {participant['First_Name']} {participant['Last_Name']} - {participant.get('Zone', 'N/A')} | {attendance_badge}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Display participant details
                    st.markdown(f"""
                    **📧 Email:** {participant.get('Username/Email', 'N/A')}  
                    **📱 Phone:** {participant.get('Phone_Number', 'N/A')}  
                    **🎂 Date of Birth:** {participant.get('Date_of_Birth', 'N/A')}  
                    **⚥ Gender:** {participant.get('Gender', 'N/A')}  
                    **📍 Zone:** {participant.get('Zone', 'N/A')}  
                    **⛪ Branch Church:** {participant.get('Branch_Church', 'N/A')}  
                    **💍 Marital Status:** {participant.get('Marital_Status', 'N/A')}  
                    **💼 Occupation:** {participant.get('Occupation', 'N/A')}  
                    **✅ Attendance Status:** {participant.get('attendance_status', 'Not Marked')}  
                    **🕐 Attendance Time:** {participant.get('attendance_time', 'Not marked yet') if participant.get('attendance_time') else 'Not marked yet'}
                    """)
                
                with col2:
                    st.markdown("### Mark Attendance")
                    current_status = participant.get('attendance_status', 'Not Marked')
                    
                    # Show current status
                    if current_status == 'Present':
                        st.success("✅ Currently: PRESENT")
                    elif current_status == 'Absent':
                        st.error("❌ Currently: ABSENT")
                    else:
                        st.warning("⏳ Currently: NOT MARKED")
                    
                    st.markdown("---")
                    
                    if st.button("✅ Mark Present", key=f"present_{participant['participant_id']}"):
                        st.session_state.participants_df = update_attendance(
                            st.session_state.participants_df, 
                            participant['participant_id'], 
                            'Present'
                        )
                        st.success(f"✅ {participant['First_Name']} {participant['Last_Name']} marked as PRESENT at {datetime.now().strftime('%H:%M:%S')}")
                        st.rerun()
                    
                    if st.button("❌ Mark Absent", key=f"absent_{participant['participant_id']}"):
                        st.session_state.participants_df = update_attendance(
                            st.session_state.participants_df, 
                            participant['participant_id'], 
                            'Absent'
                        )
                        st.warning(f"❌ {participant['First_Name']} {participant['Last_Name']} marked as ABSENT at {datetime.now().strftime('%H:%M:%S')}")
                        st.rerun()
        
        # Add new participant section
        st.markdown("---")
        st.header("➕ Add New Participant (Not in CSV)")
        
        # Zone and Branch selection OUTSIDE the form for dynamic updates
        col_zone, col_branch = st.columns(2)
        
        with col_zone:
            selected_zone = st.selectbox(
                "Select Zone *", 
                options=list(ZONES_BRANCHES.keys()),
                key="zone_selector",
                help="Choose the participant's zone"
            )
        
        with col_branch:
            # Get branches for selected zone
            available_branches = ZONES_BRANCHES.get(selected_zone, [])
            selected_branch = st.selectbox(
                "Select Branch Church *", 
                options=available_branches,
                key="branch_selector",
                help="Choose the participant's branch church"
            )
        
        # Now the form for the rest of the details
        with st.form(key="new_participant_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name *")
                last_name = st.text_input("Last Name *")
                email = st.text_input("Email/Username *")
                phone = st.text_input("Phone Number *")
                
                # Date of Birth with expanded range (1930 to current year)
                min_date = date(1930, 1, 1)
                max_date = date.today()
                dob = st.date_input(
                    "Date of Birth *", 
                    value=None,
                    min_value=min_date,
                    max_value=max_date,
                    help="Select date of birth (from 1930 onwards)"
                )
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            
            with col2:
                marital_status = st.selectbox("Marital Status", ["Single", "Married", "Divorced", "Widowed"])
                occupation = st.text_input("Occupation *")
                password = st.text_input("Preferred Password *", type="password")
            
            submitted = st.form_submit_button("➕ Register New Participant", use_container_width=True)
            
            if submitted:
                # Validate all required fields
                if all([first_name, last_name, email, phone, selected_zone, selected_branch, occupation, password, dob]):
                    new_data = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'phone': phone,
                        'dob': dob.strftime('%Y-%m-%d') if dob else '',
                        'gender': gender,
                        'zone': selected_zone,
                        'branch': selected_branch,
                        'marital_status': marital_status,
                        'occupation': occupation,
                        'password': password
                    }
                    
                    st.session_state.participants_df = add_new_participant(
                        st.session_state.participants_df, 
                        new_data
                    )
                    
                    # Set success message
                    st.session_state.show_success = True
                    st.session_state.success_message = f"✅ {first_name} {last_name} has been successfully registered and marked as PRESENT!"
                    
                    # Rerun to clear the form
                    st.rerun()
                else:
                    st.error("❌ Please fill all required fields (*)")
    
    else:
        # Welcome screen when no file uploaded
        st.info("👋 Welcome to the IYC Accreditation System!")
        st.markdown("""
        ### How to use:
        1. **Upload** your CSV file using the sidebar
        2. **Search** for participants by name, branch, or zone
        3. **Mark attendance** as Present or Absent
        4. **Add new participants** who aren't in the system
        5. **Download** the updated CSV when you're done
        6. **Remove CSV** to start over with a new file
        
        ### Features:
        - ✅ Persistent data while you work
        - ✅ Add unlimited new participants
        - ✅ Search and filter functionality
        - ✅ Real-time attendance tracking
        - ✅ Export updated data anytime
        - ✅ Attendance timestamps recorded
        - ✅ Visual badges for attendance status
        - 💾 **Auto-save to temporary storage (prevents data loss)**
        
        ### CSV Format Expected:
        The system expects columns similar to:
        - Timestamp, First Name, Last Name, Username/Email, Phone Number
        - Date of Birth, Gender, Zone, Branch Church, Marital Status
        - Occupation, Preferred Password
        
        **The system automatically adds:**
        - attendance_status (Present/Absent/Not Marked)
        - attendance_time (when attendance was marked)
        """)
        
        # Sample data display
        st.markdown("---")
        st.subheader("📝 Sample CSV Format")
        sample_data = {
            'Timestamp': ['2024-01-01 10:00:00'],
            'First Name': ['John'],
            'Last Name': ['Doe'],
            'Username/Email': ['john.doe@example.com'],
            'Phone Number': ['+1234567890'],
            'Date of Birth': ['1990-01-01'],
            'Gender': ['Male'],
            'Zone': ['Itori-Oke Zone'],
            'Branch Church': ['Ita Oshin'],
            'Marital Status': ['Single'],
            'Occupation': ['Engineer'],
            'Preferred Password': ['password123']
        }
        st.dataframe(pd.DataFrame(sample_data))

if __name__ == "__main__":
    main()