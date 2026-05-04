import streamlit as st
import pandas as pd
from utils.radar import scan_for_anomalies

def render_radar():
    st.markdown("""
    <h2 style="font-family:'Space Grotesk',sans-serif;font-weight:600;margin-bottom:4px;">
        🚨 Anomaly Radar
    </h2>
    <p style="color:var(--muted,#6B7280);font-size:14px;margin-bottom:20px;">
        Proactive monitoring for behavioral red flags and hidden patterns in your data.
    </p>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.info("📂 Upload a dataset from the sidebar to activate the radar.")
        return

    df = st.session_state.df

    # Radar state management
    if "radar_findings" not in st.session_state:
        st.session_state.radar_findings = None

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🛰️ Scan Data", type="primary", use_container_width=True):
            with st.spinner("Scanning for red flags..."):
                st.session_state.radar_findings = scan_for_anomalies(df)
    
    with col2:
        if st.session_state.radar_findings:
            st.success(f"Radar scan complete. Found {len(st.session_state.radar_findings)} interesting patterns.")

    if st.session_state.radar_findings:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        
        for finding in st.session_state.radar_findings:
            severity = finding.get("severity", "Low")
            color = "#EF4444" if severity == "High" else "#F59E0B" if severity == "Medium" else "#10B981"
            bg_color = "rgba(239, 68, 68, 0.08)" if severity == "High" else "rgba(245, 158, 11, 0.08)" if severity == "Medium" else "rgba(16, 185, 129, 0.08)"
            
            st.markdown(f"""
            <div style="background:{bg_color}; border:1px solid {color}44; border-left:4px solid {color}; 
                        padding:20px; border-radius:12px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <div style="font-weight:700; font-size:16px; color:{color}; text-transform:uppercase;">{finding['title']}</div>
                    <div style="font-size:10px; padding:2px 8px; background:{color}; color:white; border-radius:100px; font-weight:700;">{severity} SEVERITY</div>
                </div>
                <div style="font-size:14px; margin-bottom:12px; line-height:1.5;">{finding['description']}</div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; font-size:12px; opacity:0.8;">
                    <div><b>Impact:</b><br>{finding.get('impact', 'N/A')}</div>
                    <div><b>Recommended Action:</b><br>{finding.get('action', 'N/A')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action button for each anomaly
            if st.button(f"🔍 Investigate {finding['title']}", key=f"btn_{finding['title']}"):
                # Redirect to chat with a pre-filled query
                st.session_state.active_tab = "Chat"
                st.session_state.pending_query = f"Can you investigate this anomaly: '{finding['title']}'? The radar says: {finding['description']}"
                st.rerun()
    else:
        # Empty state
        st.markdown(f"""
        <div style="text-align:center; padding:60px 20px; border:2px dashed var(--border); border-radius:20px; opacity:0.6;">
            <div style="font-size:40px; margin-bottom:10px;">🛰️</div>
            <div style="font-size:18px; font-weight:600;">Radar is Idle</div>
            <div style="font-size:14px;">Click the Scan button to search for hidden patterns.</div>
        </div>
        """, unsafe_allow_html=True)
