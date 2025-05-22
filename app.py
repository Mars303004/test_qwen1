import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ... (fungsi load_data, compare_usage, get_filtered_data)

# --- Main App ---
st.title("📊 BU1 Performance Dashboard - Februari 2025")

# Upload File
uploaded_file = st.file_uploader("Upload CSV/Excel File", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        # Tabs
        tabs = st.tabs([
            "Overall BU Performance",
            "BU1",
            "BU2",
            "BU3",
            "KPI Raw",
            "SI"
        ])

        with tabs[1]:  # BU1
            st.header("BU1 Performance")

            # Filter Bulan
            selected_month = st.selectbox("Pilih Bulan", ["Jan-25", "Feb-25"])
            prev_month = "Jan-25" if selected_month == "Feb-25" else "Feb-25"

            # Perspective Buttons
            perspectives = ['Financial', 'Customer n Service', 'Quality', 'Employee']
            cols = st.columns(len(perspectives))
            for i, col in enumerate(cols):
                if col.button(perspectives[i], key=f"persp_{i}"):
                    st.session_state.perspective = perspectives[i]

            perspective = st.session_state.get('perspective', perspectives[0])

            st.markdown("---")

            # Subdiv / Produk Tabs
            if perspective == 'Customer n Service':
                sub_tabs = ['PRODUK 1', 'PRODUK 2', 'PRODUK 3']
            else:
                sub_tabs = ['Subdiv 1', 'Subdiv 2', 'Subdiv 3']

            sub_tabs_obj = st.tabs(sub_tabs)

            for idx, sub in enumerate(sub_tabs):
                with sub_tabs_obj[idx]:
                    data = get_filtered_data(df, perspective, sub, selected_month)
                    jan_data = get_filtered_data(df, perspective, sub, prev_month)

                    if data.empty:
                        st.warning("Data tidak ditemukan")
                        continue

                    if perspective == 'Customer n Service':
                        cust_count = data['Number of customer'].iloc[0]
                        sat_avg = data['Customer satisfaction'].iloc[0]
                        sat_prev = jan_data['Customer satisfaction'].iloc[0] if not jan_data.empty else 0

                        # Pisahkan pie chart dan scorecard ke dalam dua kolom
                        col1, col2 = st.columns(2)
                        with col1:
                            fig_donut = go.Figure(data=[go.Pie(labels=['Jumlah Pelanggan', 'Lainnya'],
                                                               values=[cust_count, 100 - cust_count],
                                                               hole=.7)])
                            fig_donut.update_layout(title_text='Distribusi Pelanggan')
                            st.plotly_chart(fig_donut)

                        with col2:
                            st.markdown(f"""
                                <div style="background-color:#f0f0f0;padding:10px;border-radius:10px;">
                                    <h4>Jumlah Pelanggan</h4>
                                    <h3>{cust_count}</h3>
                                    <small>{compare_usage(cust_count, jan_data['Number of customer'].iloc[0])}</small>
                                </div>
                            """, unsafe_allow_html=True)

                        # Tambahkan gauge customer satisfaction
                        fig_gauge = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=sat_avg,
                            delta={'reference': sat_prev},
                            title={'text': "Customer Satisfaction"},
                            gauge={'axis': {'range': [0, 5]}, 'bar': {'color': "#FFA726"}}
                        ))
                        st.plotly_chart(fig_gauge)
