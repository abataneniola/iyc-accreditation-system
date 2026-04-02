import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# Page configuration
st.set_page_config(page_title="IYC Accreditation System", page_icon="📋", layout="wide")

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
    </style>
""", unsafe_allow_html=True)

# Initialize session state
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

def load_csv(file):
    """Load CSV file and prepare dataframe"""
    try:
        df = pd.read_csv(file)
        # Standardize column names (remove spaces, make lowercase)
        df.columns = df.columns.str.strip().str.replace(' ', '_')
        
        # Add unique ID if not present
        if 'participant_id' not in df.columns:
            df.insert(0, 'participant_id', [str(uuid.uuid4())[:8] for _ in range(len(df))])
        
        # Add attendance status column
        if 'attendance_status' not in df.columns:
            df['attendance_status'] = 'Not Marked'
        
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
        'attendance_status': 'Present'  # Auto-mark present for new registrations
    }
    return pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

def update_attendance(df, participant_id, status):
    """Update attendance status for a participant"""
    df.loc[df['participant_id'] == participant_id, 'attendance_status'] = status
    return df

def remove_csv():
    """Remove the loaded CSV and reset all data"""
    st.session_state.participants_df = None
    st.session_state.uploaded_file_name = None
    st.session_state.show_success = False
    st.session_state.success_message = ""

def main():
    st.title("🎯 IYC Participants Accreditation System")
    st.markdown("---")
    
    # Display success message if exists
    if st.session_state.show_success:
        st.success(st.session_state.success_message)
        st.session_state.show_success = False
        st.session_state.success_message = ""
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Data Management")
        
        # Show current file status
        if st.session_state.participants_df is not None:
            st.info(f"📄 Currently loaded: **{st.session_state.uploaded_file_name}**")
            st.markdown(f"**Total records:** {len(st.session_state.participants_df)}")
        
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
            if st.button("🗑️ Remove Current CSV", type="secondary"):
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
            
            csv = download_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Updated CSV",
                data=csv,
                file_name=f"iyc_participants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Statistics
            st.markdown("---")
            st.header("📊 Statistics")
            total = len(st.session_state.participants_df)
            present = len(st.session_state.participants_df[st.session_state.participants_df['attendance_status'] == 'Present'])
            absent = len(st.session_state.participants_df[st.session_state.participants_df['attendance_status'] == 'Absent'])
            not_marked = len(st.session_state.participants_df[st.session_state.participants_df['attendance_status'] == 'Not Marked'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Participants", total)
                st.metric("Present", present)
            with col2:
                st.metric("Absent", absent)
                st.metric("Not Marked", not_marked)
    
    # Main content area
    if st.session_state.participants_df is not None:
        df = st.session_state.participants_df
        
        # Search section
        st.header("🔍 Search Participant")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("Enter search term", placeholder="Type name, branch, or zone...", key="search_input")
        
        with col2:
            search_by = st.selectbox("Search by", ['First_Name', 'Last_Name', 'Zone', 'Branch_Church', 'Username/Email'], key="search_by")
        
        with col3:
            if st.button("🔄 Clear Search"):
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
            with st.expander(f"👤 {participant['First_Name']} {participant['Last_Name']} - {participant.get('Zone', 'N/A')}"):
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
                    """)
                
                with col2:
                    st.markdown("### Mark Attendance")
                    
                    if st.button("✅ Present", key=f"present_{participant['participant_id']}"):
                        st.session_state.participants_df = update_attendance(
                            st.session_state.participants_df, 
                            participant['participant_id'], 
                            'Present'
                        )
                        st.success(f"✅ {participant['First_Name']} {participant['Last_Name']} marked as PRESENT")
                        st.rerun()
                    
                    if st.button("❌ Absent", key=f"absent_{participant['participant_id']}"):
                        st.session_state.participants_df = update_attendance(
                            st.session_state.participants_df, 
                            participant['participant_id'], 
                            'Absent'
                        )
                        st.warning(f"❌ {participant['First_Name']} {participant['Last_Name']} marked as ABSENT")
                        st.rerun()
        
        # Add new participant section
        st.markdown("---")
        st.header("➕ Add New Participant (Not in CSV)")
        
        # Create a form with a unique key that resets after submission
        with st.form(key="new_participant_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name *")
                last_name = st.text_input("Last Name *")
                email = st.text_input("Email/Username *")
                phone = st.text_input("Phone Number *")
                dob = st.date_input("Date of Birth", value=None)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            
            with col2:
                zone = st.text_input("Zone *")
                branch = st.text_input("Branch Church *")
                marital_status = st.selectbox("Marital Status", ["Single", "Married", "Divorced", "Widowed"])
                occupation = st.text_input("Occupation *")
                password = st.text_input("Preferred Password *", type="password")
            
            submitted = st.form_submit_button("➕ Register New Participant", use_container_width=True)
            
            if submitted:
                if all([first_name, last_name, email, phone, zone, branch, occupation, password]):
                    new_data = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'phone': phone,
                        'dob': dob.strftime('%Y-%m-%d') if dob else '',
                        'gender': gender,
                        'zone': zone,
                        'branch': branch,
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
                    
                    # Rerun to clear the form and show success message
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
        
        ### CSV Format Expected:
        The system expects columns similar to:
        - Timestamp, First Name, Last Name, Username/Email, Phone Number
        - Date of Birth, Gender, Zone, Branch Church, Marital Status
        - Occupation, Preferred Password
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