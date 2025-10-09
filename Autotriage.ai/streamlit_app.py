import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import os
import logging
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Page config
st.set_page_config(
    page_title="AutoTriage.AI",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

class MockTicketDataLoader:
    """Mock implementation of TicketDataLoader"""
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = self._load_mock_data()
    
    def _load_mock_data(self):
        """Create mock historical ticket data"""
        if os.path.exists(self.data_path):
            try:
                return pd.read_csv(self.data_path)
            except Exception as e:
                logging.warning(f"Could not load CSV file: {e}. Using mock data.")
        
        # Create mock data
        mock_data = {
            'issue': [
                'Software installation failed',
                'Payment gateway error',
                'Login authentication problem',
                'API integration issue',
                'Database connection timeout',
                'Email notification not working',
                'File upload size limit exceeded',
                'Performance optimization needed'
            ],
            'priority': ['High', 'Critical', 'Medium', 'High', 'Low', 'Medium', 'High', 'Low'],
            'sentiment': ['Frustrated', 'Angry', 'Neutral', 'Concerned', 'Calm', 'Irritated', 'Urgent', 'Patient'],
            'solution': [
                'Disable antivirus temporarily and retry installation',
                'Update SSL certificate to TLS 1.3',
                'Clear browser cache and cookies',
                'Check API endpoint configuration',
                'Restart database service and check connection string',
                'Verify SMTP settings and credentials',
                'Increase upload limit in server configuration',
                'Implement database indexing and query optimization'
            ],
            'resolution_time': [2.5, 1.0, 0.5, 3.2, 1.8, 1.5, 0.8, 4.5],
            'category': ['Technical', 'Payment', 'Authentication', 'Integration', 'Infrastructure', 'Email', 'Upload', 'Performance']
        }
        
        return pd.DataFrame(mock_data)
    
    def get_training_data(self):
        """Return training data for the pipeline"""
        return self.df.to_dict('records')

class MockSupportPipeline:
    """Mock implementation of SupportPipeline"""
    
    def __init__(self):
        self.issue_keywords = {
            'installation': ['install', 'setup', 'download', 'update'],
            'payment': ['payment', 'billing', 'charge', 'invoice'],
            'authentication': ['login', 'password', 'access', 'signin'],
            'api': ['api', 'integration', 'endpoint', 'webhook'],
            'performance': ['slow', 'timeout', 'performance', 'speed'],
            'email': ['email', 'notification', 'smtp', 'mail']
        }
    
    def process(self, chat_text, ticket_data):
        """Process chat text and return analysis results"""
        try:
            # Extract basic information
            issue_type = self._classify_issue(chat_text)
            sentiment = self._analyze_sentiment(chat_text)
            confidence = self._calculate_confidence(chat_text, issue_type)
            
            # Find similar cases
            similar_cases = self._find_similar_cases(issue_type, ticket_data)
            
            # Generate solution
            solution = self._generate_solution(issue_type, similar_cases)
            
            return {
                'summary': f"Customer has a {issue_type} issue with {sentiment} sentiment",
                'extracted_issue': issue_type.title() + " Problem",
                'suggested_solution': solution,
                'confidence_score': confidence,
                'similar_cases': similar_cases[:3],  # Top 3 similar cases
                'priority': self._determine_priority(sentiment, issue_type),
                'estimated_resolution_time': self._estimate_resolution_time(issue_type)
            }
            
        except Exception as e:
            logging.error(f"Pipeline processing error: {e}")
            return self._get_default_result()
    
    def _classify_issue(self, text):
        """Classify the issue based on keywords"""
        text_lower = text.lower()
        
        for issue_type, keywords in self.issue_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return issue_type
        
        return 'general'
    
    def _analyze_sentiment(self, text):
        """Simple sentiment analysis"""
        negative_words = ['error', 'failed', 'problem', 'issue', 'urgent', 'critical', 'broken']
        positive_words = ['thanks', 'good', 'working', 'resolved', 'fixed']
        
        text_lower = text.lower()
        negative_count = sum(1 for word in negative_words if word in text_lower)
        positive_count = sum(1 for word in positive_words if word in text_lower)
        
        if negative_count > positive_count:
            return 'frustrated'
        elif positive_count > negative_count:
            return 'satisfied'
        else:
            return 'neutral'
    
    def _calculate_confidence(self, text, issue_type):
        """Calculate confidence score"""
        base_confidence = 0.7
        
        # Increase confidence if specific keywords are found
        if issue_type != 'general':
            base_confidence += 0.2
        
        # Adjust based on text length and detail
        if len(text) > 100:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _find_similar_cases(self, issue_type, ticket_data):
        """Find similar historical cases"""
        similar = []
        
        for ticket in ticket_data:
            ticket_issue = ticket.get('issue', '').lower()
            ticket_category = ticket.get('category', '').lower()
            
            # Simple similarity matching
            similarity_score = 0.0
            if issue_type in ticket_issue or issue_type in ticket_category:
                similarity_score = random.uniform(0.7, 0.95)
            elif any(keyword in ticket_issue for keyword in self.issue_keywords.get(issue_type, [])):
                similarity_score = random.uniform(0.5, 0.8)
            
            if similarity_score > 0.5:
                similar.append({
                    'issue': ticket.get('issue', 'Unknown issue'),
                    'priority': ticket.get('priority', 'Medium'),
                    'sentiment': ticket.get('sentiment', 'Neutral'),
                    'solution': ticket.get('solution', 'No solution available'),
                    'similarity': similarity_score,
                    'resolution_time': ticket.get('resolution_time', 2.0)
                })
        
        # Sort by similarity score
        similar.sort(key=lambda x: x['similarity'], reverse=True)
        return similar
    
    def _generate_solution(self, issue_type, similar_cases):
        """Generate a solution based on issue type and similar cases"""
        solutions = {
            'installation': 'Try disabling antivirus software temporarily and retry the installation process.',
            'payment': 'Verify payment gateway settings and SSL certificate configuration.',
            'authentication': 'Clear browser cache and cookies, then try logging in again.',
            'api': 'Check API endpoint configuration and authentication credentials.',
            'performance': 'Monitor system resources and consider database optimization.',
            'email': 'Verify SMTP server settings and email credentials.',
            'general': 'Please provide more details about the specific issue you are experiencing.'
        }
        
        base_solution = solutions.get(issue_type, solutions['general'])
        
        # Add context from similar cases if available
        if similar_cases:
            best_case = similar_cases[0]
            if best_case['similarity'] > 0.8:
                return f"{base_solution} Based on similar cases, you might also try: {best_case['solution']}"
        
        return base_solution
    
    def _determine_priority(self, sentiment, issue_type):
        """Determine priority based on sentiment and issue type"""
        if sentiment == 'frustrated' or issue_type in ['payment', 'authentication']:
            return 'High'
        elif issue_type in ['performance', 'email']:
            return 'Medium'
        else:
            return 'Low'
    
    def _estimate_resolution_time(self, issue_type):
        """Estimate resolution time"""
        time_estimates = {
            'installation': 1.5,
            'payment': 2.0,
            'authentication': 0.5,
            'api': 3.0,
            'performance': 4.0,
            'email': 1.0,
            'general': 2.0
        }
        return time_estimates.get(issue_type, 2.0)
    
    def _get_default_result(self):
        """Return default result when processing fails"""
        return {
            'summary': 'Unable to process conversation',
            'extracted_issue': 'Processing Error',
            'suggested_solution': 'Please try again or contact support',
            'confidence_score': 0.0,
            'similar_cases': [],
            'priority': 'Medium',
            'estimated_resolution_time': 2.0
        }

def load_data():
    """Load ticket data"""
    try:
        # Try multiple possible paths
        possible_paths = [
            "Historical_ticket_data.csv",
            "data/Historical_ticket_data.csv",
            "[Usecase 7] AI-Driven Customer Support Enhancing Efficiency Through Multiagents/Historical_ticket_data.csv"
        ]
        
        data_path = None
        for path in possible_paths:
            if os.path.exists(path):
                data_path = path
                break
        
        if data_path:
            st.success(f"Data loaded from: {data_path}")
        else:
            st.info("Using mock data for demonstration (Historical_ticket_data.csv not found)")
            data_path = "mock_data.csv"  # Will trigger mock data creation
        
        loader = MockTicketDataLoader(data_path)
        return loader
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        logging.error(f"Data loading error: {str(e)}")
        return None

def analyze_conversation(conversation_text, historical_data):
    """Analyze conversation using the pipeline"""
    pipeline = MockSupportPipeline()
    return pipeline.process(
        chat_text=conversation_text,
        ticket_data=historical_data
    )

def validate_result(result):
    """Validate and clean the result data"""
    if not isinstance(result, dict):
        return False
    
    required_keys = ['summary', 'extracted_issue', 'suggested_solution', 'confidence_score']
    for key in required_keys:
        if key not in result:
            result[key] = f"No {key.replace('_', ' ')} available"
    
    # Ensure confidence_score is a valid number
    try:
        confidence = float(result.get('confidence_score', 0))
        result['confidence_score'] = max(0.0, min(1.0, confidence))
    except (ValueError, TypeError):
        result['confidence_score'] = 0.0
    
    # Ensure similar_cases is a list
    if 'similar_cases' not in result or not isinstance(result['similar_cases'], list):
        result['similar_cases'] = []
    
    return True

def display_metrics(result):
    """Display key metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        confidence = result.get('confidence_score', 0)
        st.metric("Confidence Score", f"{confidence:.1%}")
    
    with col2:
        similar_count = len(result.get('similar_cases', []))
        st.metric("Similar Cases", similar_count)
    
    with col3:
        priority = result.get('priority', 'Medium')
        st.metric("Priority", priority)
    
    with col4:
        est_time = result.get('estimated_resolution_time', 0)
        st.metric("Est. Resolution", f"{est_time:.1f}h")

def main():
    """Main application function"""
    # Sidebar
    st.sidebar.title("🔍 AutoTriage.AI")
    st.sidebar.info(
        "Let AI diagnose your support mess.\n\n"
        "Our AI-powered system automatically analyzes, categorizes, "
        "and provides solutions for your support tickets."
    )
    
    # Add some sidebar stats
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Session Stats")
    st.sidebar.metric("Analyses Today", len(st.session_state.history))
    
    # Main content
    st.title("AutoTriage.AI")
    st.subheader("Let AI diagnose your support mess")
    
    # Load data
    with st.spinner("Loading historical data..."):
        data_loader = load_data()
    
    if data_loader is None:
        st.error("Failed to load data. Please check your setup.")
        st.stop()
    
    historical_data = data_loader.get_training_data()
    
    # Input section
    st.subheader("📝 Conversation Input")
    input_method = st.radio(
        "Choose input method:",
        ["Enter Text", "Upload File", "Sample Conversations"],
        horizontal=True
    )
    
    conversation_text = ""
    
    if input_method == "Enter Text":
        conversation_text = st.text_area(
            "Enter the conversation:",
            height=200,
            placeholder="Paste your customer support conversation here..."
        )
        
    elif input_method == "Upload File":
        uploaded_file = st.file_uploader("Upload conversation file", type=['txt'])
        if uploaded_file:
            try:
                conversation_text = uploaded_file.getvalue().decode('utf-8')
                st.success(f"File uploaded: {uploaded_file.name}")
            except UnicodeDecodeError:
                st.error("File encoding not supported. Please use UTF-8 encoded files.")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                
    else:  # Sample Conversations
        samples = {
            "Software Installation Issue": """Customer: "Hi there! I've been trying to install the latest update for your design software for hours. It keeps failing at 75% with an 'unknown error.' What's wrong?"
Agent: "Hello! Thank you for reaching out. Let me help troubleshoot. Could you share a screenshot of the error message and confirm your operating system version?"
Customer: "Sure, it's Windows 11. Here's the screenshot: [image link]. I've restarted twice, same issue."
Agent: "Thank you for the details. This is a known conflict with third-party antivirus tools. Could you temporarily disable your antivirus and retry? I'll also send a direct download link as a workaround."
Customer: "Oh, disabling the antivirus worked! Installation completed. Thanks for your help!"
""",
            "Payment Gateway Integration": """Customer: "Hi, this is urgent! Your API is rejecting our payment gateway integration. Error: 'Invalid SSL certificate.' Our cert is valid and up-to-date!"
Agent: "Hello! Let's investigate immediately. Could you share the output from openssl s_client -connect yourgateway.com:443?"
Customer: "Here's the terminal output: [text]. See? No errors here."
Agent: "Thank you! Our system requires TLS 1.3, but your server supports only up to TLS 1.2. Upgrading the protocol will resolve the authentication error."
Customer: "Upgrading worked! Thanks for the quick fix!"
""",
            "Login Authentication Problem": """Customer: "I can't log into my account! It keeps saying 'invalid credentials' but I'm sure my password is correct. This is really frustrating!"
Agent: "I understand your frustration. Let's get this resolved quickly. Have you tried clearing your browser cache and cookies?"
Customer: "No, I haven't tried that. How do I do that?"
Agent: "I'll walk you through it. Go to your browser settings, find 'Clear browsing data', select cookies and cached files, then try logging in again."
Customer: "That worked! Thank you so much!"
"""
        }
        selected_sample = st.selectbox("Choose a sample conversation:", list(samples.keys()))
        conversation_text = samples[selected_sample]
        st.text_area("Sample conversation:", conversation_text, height=200, disabled=True)
    
    # Analysis button
    if st.button("🔍 Analyze Conversation", type="primary") and conversation_text.strip():
        with st.spinner("Analyzing conversation..."):
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate processing steps
            steps = [
                "Preprocessing text...",
                "Extracting key information...",
                "Analyzing sentiment...",
                "Finding similar cases...",
                "Generating solution...",
                "Finalizing results..."
            ]
            
            for i, step in enumerate(steps):
                status_text.text(step)
                progress_bar.progress((i + 1) / len(steps))
                time.sleep(0.3)
            
            # Process the conversation
            result = analyze_conversation(conversation_text, historical_data)
            
            # Validate result
            if not validate_result(result):
                st.error("Error processing conversation. Please try again.")
                return
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            st.success("✅ Analysis completed!")
            
            # Metrics
            display_metrics(result)
            
            # Results in tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis", "🔍 Similar Cases", "📈 Insights", "💡 Recommendations"])
            
            with tab1:
                st.subheader("Analysis Results")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**Summary:**")
                    st.info(result.get('summary', 'No summary available'))
                    
                    st.markdown("**Extracted Issue:**")
                    st.write(result.get('extracted_issue', 'No issue extracted'))
                    
                    st.markdown("**Suggested Solution:**")
                    st.success(result.get('suggested_solution', 'No solution available'))
                
                with col2:
                    # Confidence gauge
                    confidence = result.get('confidence_score', 0)
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=confidence,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Confidence Score"},
                        gauge={
                            'axis': {'range': [0, 1]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 0.5], 'color': "lightgray"},
                                {'range': [0.5, 0.8], 'color': "yellow"},
                                {'range': [0.8, 1], 'color': "lightgreen"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': confidence
                            }
                        }
                    ))
                    
                    fig.update_layout(
                        height=300,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.subheader("Similar Historical Cases")
                similar_cases = result.get('similar_cases', [])
                
                if similar_cases:
                    for i, case in enumerate(similar_cases, 1):
                        # Safe access to case data
                        issue_text = case.get('issue', 'No issue description available')
                        if issue_text and len(issue_text) > 50:
                            preview = issue_text[:50] + "..."
                        else:
                            preview = issue_text or "No description"
                        
                        with st.expander(f"Case {i}: {preview}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Issue:**", case.get('issue', 'Not specified'))
                                st.write("**Priority:**", case.get('priority', 'Not specified'))
                                st.write("**Sentiment:**", case.get('sentiment', 'Not specified'))
                            
                            with col2:
                                if 'similarity' in case:
                                    st.metric("Similarity", f"{case['similarity']:.1%}")
                                if 'resolution_time' in case:
                                    st.metric("Resolution Time", f"{case['resolution_time']:.1f}h")
                            
                            st.write("**Solution:**", case.get('solution', 'No solution available'))
                else:
                    st.info("No similar cases found in historical data.")
            
            with tab3:
                st.subheader("Conversation Insights")
                
                # Create some basic analytics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Issue Classification**")
                    issue_type = result.get('extracted_issue', 'Unknown')
                    st.write(f"Type: {issue_type}")
                    
                    priority = result.get('priority', 'Medium')
                    priority_color = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}.get(priority, '⚪')
                    st.write(f"Priority: {priority_color} {priority}")
                
                with col2:
                    st.markdown("**Resolution Timeline**")
                    est_time = result.get('estimated_resolution_time', 2.0)
                    st.write(f"Estimated time: {est_time:.1f} hours")
                    
                    # Simple timeline visualization
                    timeline_data = pd.DataFrame({
                        'Step': ['Analysis', 'Solution Implementation', 'Testing', 'Resolution'],
                        'Time': [0.1, est_time * 0.6, est_time * 0.2, est_time * 0.1]
                    })
                    
                    fig = go.Figure(data=[
                        go.Bar(x=timeline_data['Step'], y=timeline_data['Time'])
                    ])
                    fig.update_layout(
                        title="Estimated Resolution Timeline",
                        xaxis_title="Process Step",
                        yaxis_title="Hours",
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                st.subheader("💡 AI Recommendations")
                
                # Generate recommendations based on analysis
                recommendations = []
                
                confidence = result.get('confidence_score', 0)
                if confidence < 0.5:
                    recommendations.append("⚠️ Low confidence score - consider manual review")
                
                priority = result.get('priority', 'Medium')
                if priority == 'High':
                    recommendations.append("🚨 High priority issue - escalate to senior support")
                
                similar_count = len(result.get('similar_cases', []))
                if similar_count > 2:
                    recommendations.append("📚 Multiple similar cases found - consider creating FAQ")
                
                if not recommendations:
                    recommendations.append("✅ Standard resolution process recommended")
                
                for rec in recommendations:
                    st.write(rec)
                
                # Action buttons
                st.markdown("---")
                st.subheader("Quick Actions")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📧 Send Solution Email"):
                        st.success("Email template generated!")
                
                with col2:
                    if st.button("📝 Create Ticket"):
                        st.success("Ticket created in system!")
                
                with col3:
                    if st.button("📊 Generate Report"):
                        st.success("Analysis report generated!")
            
            # Add to history
            st.session_state.history.append({
                'timestamp': datetime.now(),
                'summary': result.get('summary', '')[:100] + "..." if len(result.get('summary', '')) > 100 else result.get('summary', ''),
                'confidence': result.get('confidence_score', 0),
                'priority': result.get('priority', 'Medium'),
                'issue_type': result.get('extracted_issue', 'Unknown')
            })
    elif st.button("🔍 Analyze Conversation", type="primary"):
        st.warning("Please enter a conversation to analyze.")
    
    # History section
    if st.session_state.history:
        st.markdown("---")
        st.subheader("📚 Analysis History")
        
        # Convert history to DataFrame for better display
        history_df = pd.DataFrame(st.session_state.history)
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
        history_df = history_df.sort_values('timestamp', ascending=False)
        
        # Display recent analyses
        st.dataframe(
            history_df.head(10),
            use_container_width=True,
            hide_index=True
        )
        
        if len(st.session_state.history) > 10:
            st.info(f"Showing latest 10 of {len(st.session_state.history)} analyses")
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()

if __name__ == "__main__":
    main()