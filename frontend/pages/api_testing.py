"""API Testing page - Test API endpoints and export data"""
import streamlit as st
import requests
from utils.api_client import API_BASE


def show_api_testing():
    """Show API testing interface."""
    st.title("🔧 API Testing Center")
    st.markdown("Test various API endpoints and security features")
    
    # Test protected route
    st.subheader("🛡️ Protected Route Test")
    if st.button("Test Protected Endpoint"):
        with st.spinner("Testing protected route access..."):
            result = st.session_state.auth_client.access_protected_route(st.session_state.access_token)
        
        if result["success"]:
            st.success("✅ Protected route accessed successfully!")
            st.json(result["data"])
        else:
            st.error(f"❌ Access denied: {result['error']}")
    
    # Test user info endpoint
    st.subheader("👤 User Info Test")
    if st.button("Fetch User Information"):
        with st.spinner("Fetching user information..."):
            result = st.session_state.auth_client.get_user_info(st.session_state.access_token)
        
        if result["success"]:
            st.success("✅ User information retrieved!")
            st.json(result["data"])
        else:
            st.error(f"❌ Failed to get user info: {result['error']}")
    
    # Security features display
    st.markdown("---")
    st.subheader("🔒 Enhanced Security Features")
    
    security_features = [
        "✅ **Argon2 Password Hashing**: Industry-leading password security",
        "✅ **JWT with Enhanced Claims**: Secure tokens with additional security metadata",
        "✅ **Application-Layer Encryption**: Sensitive data encrypted beyond TLS",
        "✅ **Rate Limiting**: Protection against brute force attacks",
        "✅ **Session Timeout**: Automatic logout after 30 minutes of inactivity",
        "✅ **Strong Password Requirements**: Enforced password complexity",
        "✅ **Security Headers**: CSRF, XSS, and clickjacking protection",
        "✅ **Trusted Host Validation**: Protection against host header attacks",
        "✅ **Real-time Token Validation**: Continuous session security checks"
    ]
    
    for feature in security_features:
        st.markdown(feature)


def show_export_data():
    """
    Export data from database to CSV files.
    
    Database-First Pattern:
    - Manual CSV export (not automatic)
    - Reads from database (single source of truth)
    - Generates CSV for analysis/backup
    """
    st.title("📊 Export Data to CSV")
    st.markdown("Generate CSV files from database for analysis and backup")
    
    st.info("💡 **Database-First Pattern**: CSV files are generated from the database on demand. All production data is stored in PostgreSQL.")
    
    # Export buttons in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Multi-Agent Data", type="primary", use_container_width=True):
            with st.spinner("Exporting multi-agent results from database..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/api/storage/export-multi-agent",
                        headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Exported {result['records']} records to: `{result['csv_path']}`")
                    else:
                        st.error(f"❌ Export failed: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
    
    with col2:
        if st.button("⏰ Export Temporal Data", type="primary", use_container_width=True):
            with st.spinner("Exporting temporal version chains from database..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/api/storage/export-temporal",
                        headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Exported {result['records']} versions to: `{result['csv_path']}`")
                    else:
                        st.error(f"❌ Export failed: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
    
    with col3:
        if st.button("📦 Export All Data", type="primary", use_container_width=True):
            with st.spinner("Exporting all data from database..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/api/storage/export-all",
                        headers={"Authorization": f"Bearer {st.session_state.access_token}"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        paths = result['csv_paths']
                        st.success(f"✅ Exported all data:")
                        for name, path in paths.items():
                            st.success(f"  - {name}: `{path}`")
                    else:
                        st.error(f"❌ Export failed: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
    
    st.markdown("---")
    
    # Export information
    st.subheader("📋 Export Information")
    
    st.markdown("""
    **What gets exported:**
    - **Multi-Agent Data**: All prompt versions from different agents (syntax, structure, domain)
    - **Temporal Data**: Version chains with parent-child relationships and change types
    
    **Why export to CSV:**
    - 📊 Analysis in Excel, Python, R
    - 💾 Backup and archival
    - 📈 Custom visualizations
    - 🔍 Data exploration
    
    **Database-First Pattern:**
    - ✅ PostgreSQL is the single source of truth
    - ✅ CSV files are generated on demand
    - ✅ No data drift between database and CSV
    - ✅ All queries read from database (not CSV)
    """)

