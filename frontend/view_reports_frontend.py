from backend.account_backend import load_all_reports
import streamlit as st

# Number of reports to display per page
REPORTS_PER_PAGE = 8

def main():
    if st.session_state.logged_in:
        st.title('View All Reports')
        
        # Load all reports
        reports = load_all_reports()
        
        # Filter options
        filter_options = ['Email', 'Issue']
        selected_filter = st.selectbox('Filter by:', filter_options)

        # Search bar
        search_query = st.text_input(f'Search {selected_filter.lower()}')

        # Apply filters and search
        filtered_reports = apply_filters_and_search(reports, selected_filter, search_query)

        # Pagination
        total_reports = len(filtered_reports)
        total_pages = (total_reports // REPORTS_PER_PAGE) + (1 if total_reports % REPORTS_PER_PAGE != 0 else 0)

        # Get current page from session state or default to page 1
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = 1
        
        # Calculate indices for the current page
        start_index = (st.session_state["current_page"] - 1) * REPORTS_PER_PAGE
        end_index = min(start_index + REPORTS_PER_PAGE, total_reports)

        # Display reports for the current page
        if filtered_reports:
            for report in filtered_reports[start_index:end_index]:
                st.subheader(f"Report ID: {report['id']}")
                st.write(f"Email: {report['email']}")
                st.write(f"Issue: {report['issue']}")
                st.write(f"Timestamp: {report['timestamp']}")
                
                # Add a section for admin responses
                response_key = f"response_{report['id']}"
                response_sent = st.checkbox(f"Response sent to {report['email']}", key=response_key)
                if response_sent:
                    admin_response = st.text_area(f"Admin Response to {report['email']}")
                    if st.button(f"Send Response to {report['email']}"):
                        send_response(report['email'], admin_response)
                st.markdown("---")
            
            # Pagination controls
            if total_pages > 1:
                st.markdown("---")
                st.write(f"Page {st.session_state['current_page']} of {total_pages}")
                if st.session_state["current_page"] > 1:
                    if st.button("Previous"):
                        st.session_state["current_page"] -= 1
                if st.session_state["current_page"] < total_pages:
                    if st.button("Next"):
                        st.session_state["current_page"] += 1
        else:
            st.write("No reports found.")

    def send_response(user_email, response_message):
        try:
            # Implement your logic to send response here (e.g., send email, update database)
            # For demonstration purposes, let's print the response message
            st.success(f"Response sent to {user_email}: {response_message}")
        except Exception as e:
            st.error(f"Failed to send response: {e}")

def apply_filters_and_search(reports, selected_filter, search_query):
    filtered_reports = []
    if search_query:
        for report in reports:
            if selected_filter == 'Email' and search_query.lower() in report['email'].lower():
                filtered_reports.append(report)
            elif selected_filter == 'Issue' and search_query.lower() in report['issue'].lower():
                filtered_reports.append(report)
    else:
        filtered_reports = reports
    
    return filtered_reports

if __name__ == "__main__":
    main()
