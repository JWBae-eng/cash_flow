import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Personal Cash Flow", layout="wide")

# --- DATA CLEANING FUNCTION ---
def clean_data(df):
    """
    Removes credit card payments (Online Services) that match refunds.
    """
    try:
        # Create copies to avoid SettingWithCopy warnings
        neg_candidates = df[
            (df['Category'] == 'Online Services') & 
            (df['Amount'] < 0)
        ].copy()
        
        pos_candidates = df[
            (df['Category'] == 'Refunds & Reimbursements') & 
            (df['Amount'] > 0)
        ].copy()

        drop_indices = []
        available_pos_indices = list(pos_candidates.index)

        for neg_idx, neg_row in neg_candidates.iterrows():
            target_amount = abs(neg_row['Amount'])
            
            match_idx_to_remove = -1
            match_found = False
            
            for pos_idx in available_pos_indices:
                # Use a small epsilon for float comparison
                if abs(df.loc[pos_idx, 'Amount'] - target_amount) < 0.01:
                    match_idx_to_remove = pos_idx
                    match_found = True
                    break
            
            if match_found:
                drop_indices.append(neg_idx)
                drop_indices.append(match_idx_to_remove)
                available_pos_indices.remove(match_idx_to_remove)

        if drop_indices:
            st.toast(f"🧹 Cleaned {len(drop_indices)} payment transfer rows.")
            return df.drop(drop_indices)
        
        return df

    except Exception as e:
        st.warning(f"Cleaning algorithm skipped due to error: {e}")
        return df

# --- MAIN APP ---
st.title("📊 Monthly Cash Flow Visualizer")

uploaded_file = st.file_uploader("Upload Empower CSV", type="csv")

if uploaded_file:
    try:
        # 1. Load Data
        df = pd.read_csv(uploaded_file)
        
        # Standardize column names
        df.columns = [c.strip() for c in df.columns]

        # 2. Robust Date Conversion (THE FIX)
        # Coerce errors to NaT, then drop them
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        
        # Convert to strict Python date objects (Fixes Pyarrow serialization error)
        df['Date'] = df['Date'].dt.date 

        # 3. Robust Amount Conversion
        if df['Amount'].dtype == 'object':
            df['Amount'] = df['Amount'].astype(str).str.replace('$', '', regex=False)
            df['Amount'] = df['Amount'].str.replace(',', '', regex=False)
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        
        df = df.dropna(subset=['Amount'])

        # 4. Sidebar Controls
        st.sidebar.header("Controls")
        
        # Cleaning Toggle
        enable_cleaning = st.sidebar.checkbox("Enable Transfer Cleaning", value=True)
        if enable_cleaning:
            df = clean_data(df)

        # Account Filter
        all_accounts = list(df['Account'].unique())
        selected_accounts = st.sidebar.multiselect("Select Accounts", options=all_accounts, default=all_accounts)
        
        if not selected_accounts:
            st.warning("Please select at least one account in the sidebar.")
            st.stop()

        df_filtered = df[df['Account'].isin(selected_accounts)]

        # 5. Metrics
        total_spend = df_filtered[df_filtered['Amount'] < 0]['Amount'].sum()
        total_income = df_filtered[df_filtered['Amount'] > 0]['Amount'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Spending", f"${abs(total_spend):,.2f}")
        col2.metric("Total Income", f"${total_income:,.2f}")
        col3.metric("Net Cash Flow", f"${(total_income + total_spend):,.2f}")

        st.divider()

        # 6. Visualizations
        tab1, tab2, tab3 = st.tabs(["Spending by Category", "Top Merchants", "Trend Analysis"])

        with tab1:
            spend_df = df_filtered[df_filtered['Amount'] < 0].copy()
            if not spend_df.empty:
                spend_df['AbsAmount'] = spend_df['Amount'].abs()
                cat_group = spend_df.groupby('Category')['AbsAmount'].sum().reset_index()
                
                fig_cat = px.pie(cat_group, values='AbsAmount', names='Category', title="Spending Distribution")
                st.plotly_chart(fig_cat, width='stretch')
            else:
                st.info("No spending data found.")

        with tab2:
            spend_df = df_filtered[df_filtered['Amount'] < 0].copy()
            if not spend_df.empty:
                spend_df['AbsAmount'] = spend_df['Amount'].abs()
                merch_group = spend_df.groupby('Description')['AbsAmount'].sum().reset_index()
                merch_group = merch_group.sort_values(by='AbsAmount', ascending=False).head(15)
                
                fig_merch = px.bar(merch_group, x='AbsAmount', y='Description', orientation='h', title="Top 15 Merchants")
                fig_merch.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_merch, width='stretch')
            else:
                st.info("No spending data found.")

        with tab3:
            # Daily Trend Line
            daily_spend = df_filtered[df_filtered['Amount'] < 0].copy()
            if not daily_spend.empty:
                daily_spend['AbsAmount'] = daily_spend['Amount'].abs()
                # Group by date
                daily_trend = daily_spend.groupby('Date')['AbsAmount'].sum().reset_index()
                
                fig_trend = px.line(daily_trend, x='Date', y='AbsAmount', markers=True, title="Daily Spending Trend")
                st.plotly_chart(fig_trend, width='stretch')
            else:
                st.info("No spending data found.")

        # 7. Raw Transactions (Restored to Full View)
        st.divider()
        st.subheader("📝 Raw Transactions")
        
        st.dataframe(
            df_filtered.sort_values(by='Date', ascending=False),
            width='stretch',
            hide_index=True
        )

    except Exception as e:
        st.error("🚨 An error occurred processing the file.")
        st.code(str(e))

else:
    st.info("Waiting for file upload...")
