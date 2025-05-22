import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

st.set_page_config(page_title="BU1 Dashboard", layout="wide")

# --- Helper Functions ---
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except:
            df = pd.read_excel(uploaded_file)
        df['Month'] = pd.to_datetime(df['Month'], format='%b-%y')
        return df
    return None

def get_filtered_data(df, perspective, subdiv_produk, month='Feb-25'):
    filtered = df[(df['Perspective'] == perspective) & (df['Month'] == pd.to_datetime(month))]
    if 'Subdiv' in filtered.columns:
        return filtered[filtered['Subdiv'] == subdiv_produk]
    elif 'Produk' in filtered.columns:
        return filtered[filtered['Produk'] == subdiv_produk]
    return filtered

def compare_usage(current, previous):
    diff = current - previous
    color = "green" if diff >= 0 else "red"
    arrow = "↑" if diff > 0 else "↓" if diff < 0 else "→"
    return f"<span style='color:{color}'>{arrow} {abs(diff):.1f}%</span>"

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

        with tabs[0]:
            st.info("Belum ada data yang tersedia")
        with tabs[2]:
            st.info("Belum ada data yang tersedia")
        with tabs[3]:
            st.info("Belum ada data yang tersedia")
        with tabs[4]:
            st.info("Belum ada data yang tersedia")
        with tabs[5]:
            st.info("Belum ada data yang tersedia")

        with tabs[1]:  # BU1
            st.header("BU1 Performance")

            # Filter Bulan
            selected_month = st.selectbox("Pilih Bulan", ["Feb-25"])
            prev_month = "Jan-25"

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

                    if perspective == 'Financial':
                        budget = data['Budget'].iloc[0]
                        expense = data['Expense'].iloc[0]
                        usage = data['Usage'].str.replace('%', '').astype(float).iloc[0]
                        usage_prev = jan_data['Usage'].str.replace('%', '').astype(float).iloc[0] if not jan_data.empty else 0
                        profit = data['Profit'].iloc[0]
                        revenue = data['Revenue'].iloc[0]

                        profit_prev = jan_data['Profit'].iloc[0] if not jan_data.empty else 0
                        revenue_prev = jan_data['Revenue'].iloc[0] if not jan_data.empty else 0

                        col1, col2 = st.columns(2)
                        with col1:
                            fig = go.Figure()
                            fig.add_trace(go.Bar(x=['Budget', 'Expense'], y=[budget, expense], name='Budget vs Expense'))
                            fig.update_layout(title_text='Budget vs Expense')
                            st.plotly_chart(fig)

                        with col2:
                            fig_gauge = go.Figure(go.Indicator(
                                mode="gauge+number+delta",
                                value=usage,
                                delta={'reference': usage_prev},
                                title={'text': "Usage (%)"},
                                gauge={'axis': {'range': [0, 100]},
                                       'bar': {'color': "#4CAF50"}}
                            ))
                            st.plotly_chart(fig_gauge)

                        col3, col4 = st.columns(2)
                        with col3:
                            st.markdown(f"""
                                <div style="background-color:#f0f0f0;padding:10px;border-radius:10px;">
                                    <h4>Profit</h4>
                                    <h3>{profit}</h3>
                                    <small>{compare_usage(profit, profit_prev)}</small>
                                </div>
                            """, unsafe_allow_html=True)

                        with col4:
                            st.markdown(f"""
                                <div style="background-color:#f0f0f0;padding:10px;border-radius:10px;">
                                    <h4>Revenue</h4>
                                    <h3>{revenue}</h3>
                                    <small>{compare_usage(revenue, revenue_prev)}</small>
                                </div>
                            """, unsafe_allow_html=True)

                    elif perspective == 'Customer n Service':
                        cust_count = data['Number of customer'].iloc[0]
                        sat_avg = data['Customer satisfaction'].iloc[0]
                        sat_prev = jan_data['Customer satisfaction'].iloc[0] if not jan_data.empty else 0

                        st.markdown(f"""
                            <div style="background-color:#f0f0f0;padding:10px;border-radius:10px;">
                                <h4>Jumlah Pelanggan</h4>
                                <h3>{cust_count}</h3>
                                <small>{compare_usage(cust_count, jan_data['Number of customer'].iloc[0])}</small>
                            </div>
                        """, unsafe_allow_html=True)

                        fig_donut = go.Figure(data=[go.Pie(labels=['Jumlah Pelanggan', 'Lainnya'],
                                                           values=[cust_count, 100 - cust_count],
                                                           hole=.7)])
                        fig_donut.update_layout(title_text='Distribusi Pelanggan')
                        st.plotly_chart(fig_donut)

                        fig_gauge = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=sat_avg,
                            delta={'reference': sat_prev},
                            title={'text': "Customer Satisfaction"},
                            gauge={'axis': {'range': [0, 5]}, 'bar': {'color': "#FFA726"}}
                        ))
                        st.plotly_chart(fig_gauge)

                        # Line chart
                        line_df = pd.concat([jan_data, data])
                        fig_line = px.line(line_df, x='Month', y='Customer satisfaction', title='Customer Satisfaction Trend')
                        st.plotly_chart(fig_line)

                    elif perspective == 'Quality':
                        target = data['Target'].iloc[0]
                        realization = data['Realization'].iloc[0]
                        velocity = data['Velocity'].str.replace('%', '').astype(float).iloc[0]
                        quality = data['Quality'].str.replace('%', '').astype(float).iloc[0]

                        velocity_prev = jan_data['Velocity'].str.replace('%', '').astype(float).iloc[0] if not jan_data.empty else 0
                        quality_prev = jan_data['Quality'].str.replace('%', '').astype(float).iloc[0] if not jan_data.empty else 0

                        fig_bar = go.Figure()
                        fig_bar.add_trace(go.Bar(x=['Target', 'Realization'], y=[target, realization]))
                        fig_bar.update_layout(title_text='Target vs Realization')
                        st.plotly_chart(fig_bar)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                                <div style="background-color:#f0f0f0;padding:10px;border-radius:10px;">
                                    <h4>Average Velocity</h4>
                                    <h3>{velocity:.1f}%</h3>
                                    <small>{compare_usage(velocity, velocity_prev)}</small>
                                </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                                <div style="background-color:#f0f0f0;padding:10px;border-radius:10px;">
                                    <h4>Average Quality</h4>
                                    <h3>{quality:.1f}%</h3>
                                    <small>{compare_usage(quality, quality_prev)}</small>
                                </div>
                            """, unsafe_allow_html=True)

                    elif perspective == 'Employee':
                        current_mp = data['Current MP'].iloc[0]
                        needed_mp = data['Needed MP'].iloc[0]
                        competency = data['Competency'].str.replace('%', '').astype(float).iloc[0]
                        turnover = data['Turnover ratio'].str.replace('%', '').astype(float).iloc[0]

                        remaining_mp = needed_mp - current_mp

                        fig_donut = go.Figure(data=[go.Pie(
                            labels=['Current MP', 'MP Kurang'],
                            values=[current_mp, remaining_mp],
                            hole=.7)])
                        fig_donut.update_layout(title_text='Current MP vs Needed MP')
                        st.plotly_chart(fig_donut)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                                <div style="background-color:#f0f0f0;padding:10px;border-radius:10px;">
                                    <h4>Average Competency</h4>
                                    <h3>{competency:.1f}%</h3>
                                </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                                <div style="background-color:#f0f0f0;padding:10px;border-radius:10px;">
                                    <h4>Turnover Ratio</h4>
                                    <h3>{turnover:.1f}%</h3>
                                </div>
                            """, unsafe_allow_html=True)

else:
    st.warning("Silakan upload file CSV/Excel untuk melanjutkan.")
