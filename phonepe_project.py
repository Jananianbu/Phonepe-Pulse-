import streamlit as st
import plotly.express as px
import mysql.connector
import pandas as pd
import requests


# Function to fetch data from MySQL
def fetch_data():
    # Connect to the database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="phonepe_pulse",
        auth_plugin='mysql_native_password'  # Specify the authentication plugin explicitly
    )

    query1 = """SELECT State, Year, Quarter, Transaction_amount, Transaction_count, name FROM transaction"""
    query2 = """SELECT State, Year, Quarter, Transaction_amount AS map_Transaction_amount, 
                Transaction_count AS map_Transaction_count, Districts FROM map_trans"""
    query3 = """SELECT State, Year, Quarter, Transaction_amount AS top_Transaction_amount, 
                Transaction_count AS top_Transaction_count, Entityname FROM top_transaction"""

    df1 = pd.read_sql(query1, conn)
    df2 = pd.read_sql(query2, conn)
    df3 = pd.read_sql(query3, conn)

    conn.close()

    # Merge tables
    df_merged3 = pd.merge(df1, df2, on=['State', 'Year', 'Quarter'], how='outer')
    df_merged3 = pd.merge(df_merged3, df3, on=['State', 'Year', 'Quarter'], how='outer')
    # Merge tables

    # Select and rename columns to avoid duplication
    df_merged3 = df_merged3[
        ['State', 'Year', 'Quarter', 'Transaction_amount', 'Transaction_count', 'name', 'Districts', 'Entityname']]

    # Display merged DataFrame
    return df_merged3


def Aggre_insurance_Y(df_merged4, year, quarter):
    # Filter data for the selected year and quarter
    df_filtered3 = df_merged4[(df_merged4['Year'] == year) & (df_merged4['Quarter'] == quarter)]

    # Perform aggregation
    df_agg3 = df_filtered3.groupby('State').agg({
        'Transaction_count': 'sum',
        'Transaction_amount': 'sum'
    }).reset_index()

    return df_agg3, df_filtered3


def display_pie_chart(df_filtered4, selected_state2):
    state_data = df_filtered4[df_filtered4['State'] == selected_state2]
    if not state_data.empty:
        # Use unique values of 'name' for the selected state
        unique_names = state_data['name'].unique()
        name_counts = pd.DataFrame({'name': unique_names, 'count': [1] * len(unique_names)})

        fig_pie = px.pie(name_counts, names='name', values='count', title=f'{selected_state2} - Name Distribution')
        st.plotly_chart(fig_pie)
    else:
        st.write(f"No data available for {selected_state2}")


def display_plots(df_agg3, year, quarter):
    # Load GeoJSON data for states
    url = ("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw"
           "/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson")
    response = requests.get(url)
    data_geojson = response.json()

    # Plotly Bar Charts
    st.title(f'{year} Q{quarter} Transactions')
    st.subheader('Transaction Amount and Count by State')

    col1, col2 = st.columns(2)

    with col1:
        # Plot bar chart for Transaction Amount
        fig_amount = px.bar(df_agg3, x='State', y='Transaction_amount',
                            title=f'{year} Q{quarter} Transaction Amount by State',
                            labels={'State': 'State', 'Transaction_amount': 'Transaction Amount'})
        st.plotly_chart(fig_amount)

    with col2:
        # Plot bar chart for Transaction Count
        fig_count = px.bar(df_agg3, x='State', y='Transaction_count',
                           title=f'{year} Q{quarter} Transaction Count by State',
                           labels={'State': 'State', 'Transaction_count': 'Transaction Count'})
        st.plotly_chart(fig_count)

    # Plotly Choropleth Maps
    st.title(f'{year} Q{quarter} Choropleth Maps')
    st.subheader('Transaction Amount and Count by State')

    col3, col4 = st.columns(2)

    with col3:
        # Choropleth map for Transaction Amount
        fig_amount_map = px.choropleth(df_agg3, geojson=data_geojson,
                                       locations='State', featureidkey="properties.ST_NM",
                                       color='Transaction_amount',
                                       color_continuous_scale='Sunsetdark',
                                       range_color=(
                                           df_agg3['Transaction_amount'].min(), df_agg3['Transaction_amount'].max()),
                                       hover_name='State',
                                       labels={'Transaction_amount': 'Transaction Amount'})
        fig_amount_map.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig_amount_map)

    with col4:
        # Choropleth map for Transaction Count
        fig_count_map = px.choropleth(df_agg3, geojson=data_geojson,
                                      locations='State', featureidkey="properties.ST_NM",
                                      color='Transaction_count',
                                      color_continuous_scale='Sunsetdark',
                                      range_color=(
                                          df_agg3['Transaction_count'].min(), df_agg3['Transaction_count'].max()),
                                      hover_name='State',
                                      labels={'Transaction_count': 'Transaction Count'})
        fig_count_map.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig_count_map)


# Fetch the data
df_merged = fetch_data()

# Extract unique years, quarters, and states
years = sorted(df_merged['Year'].unique())
quarters = sorted(df_merged['Quarter'].unique())
states = sorted(df_merged['State'].unique())

# Define the pages
pages = ["Home", "Explore Insurance Data", "Explore Transaction Data", "Explore User Data", "Insights"]

# Streamlit App
page = st.sidebar.selectbox("Select a page", pages)

if page == "Home":
    st.title("Welcome to PhonePe Pulse Dashboard")
    st.write("Explore insights into the PhonePe Pulse and Transaction data.")

    # Display some PhonePe details
    st.subheader("PhonePe Details")
    st.markdown("""
        - **Name:** PhonePe
        - **Location:** Bengaluru, Karnataka, India
        - **Industry:** Fintech, Digital Payments
        - **Employees:** 5000+
        - **Website:** [phonepe.com](https://www.phonepe.com/)
    """)

    st.subheader("About PhonePe Pulse")
    st.markdown("""
        PhonePe Pulse is a repository of insights into the digital payment trends and habits in India.
        The data includes transaction counts and amounts across different states and quarters.
        Explore the 'Explore Insurance Data' page to analyze detailed insurance transaction data by year.
    """)

elif page == "Explore Insurance Data":
    st.title('Insurance Data Analysis')

    # Select a year and quarter
    selected_year = st.selectbox('Select a year', years)
    selected_quarter = st.selectbox('Select a Quarter', quarters)

    # Call the aggregation function with the selected year and quarter
    df_agg, df_filtered = Aggre_insurance_Y(df_merged, selected_year, selected_quarter)

    # Display the plots
    display_plots(df_agg, selected_year, selected_quarter)

elif page == "Explore Transaction Data":
    st.title('Transaction Data Analysis')

    # Select a year, quarter, and state
    selected_year = st.selectbox('Select a year', years)
    selected_quarter = st.selectbox('Select a Quarter', quarters)
    selected_state = st.selectbox('Select a State', states)

    # Call the aggregation function with the selected year and quarter
    df_agg, df_filtered = Aggre_insurance_Y(df_merged, selected_year, selected_quarter)

    # Display the plots
    display_plots(df_agg, selected_year, selected_quarter)

    # Display the pie chart for the selected state
    st.subheader(f'Distribution of Transactions by Name in {selected_state}')
    display_pie_chart(df_filtered, selected_state)

elif page == "Explore User Data":
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="phonepe_pulse",
            auth_plugin='mysql_native_password'  # Specify the authentication plugin explicitly
        )

        # Check if the connection was successful
        if conn.is_connected():
            st.write("Connected to the database successfully!")

        query4 = """SELECT State, Year, Quarter, Transaction_count, Brands, Percentage FROM agg_user"""
        query5 = """SELECT State, Year, Quarter, Districts, RegisteredUser, AppOpens FROM map_user"""
        query6 = """SELECT State, Year, Quarter, Districts, RegisteredUser FROM top_user"""

        df4 = pd.read_sql(query4, conn)
        print(df4)
        df5 = pd.read_sql(query5, conn)
        df6 = pd.read_sql(query6, conn)

        conn.close()

        df_merged1 = pd.merge(df4, df5, on=['State', 'Year', 'Quarter'], how='outer')
        df_merged1 = pd.merge(df_merged1, df6, on=['State', 'Year', 'Quarter'], how='outer')

        selected_state = st.sidebar.selectbox('Select State', df_merged1['State'].unique())
        selected_year = st.sidebar.selectbox('Select Year', df_merged1['Year'].unique())
        selected_quarter = st.sidebar.selectbox('Select Quarter', df_merged1['Quarter'].unique())

        fig1 = px.bar(df4, x='State', y='Transaction_count', title='Transaction Count', height=650, width=500)
        st.plotly_chart(fig1)

        fig2 = px.bar(df5, x='State', y='RegisteredUser', title='Registered Users')
        st.plotly_chart(fig2)

        fig3 = px.bar(df4, x='State', y='Brands', title='Brands')
        st.plotly_chart(fig3)

        fig5 = px.bar(df5, x='State', y='AppOpens', title='App Opens')
        st.plotly_chart(fig5)

    except mysql.connector.Error as err:
        st.write(f"Error: {err}")

elif page == "Insights":

    if "selectbox_enabled" not in st.session_state:
        st.session_state["selectbox_enabled"] = False


    def questions(selected_option1):

        conn1 = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="phonepe_pulse",
            auth_plugin='mysql_native_password'
        )

        mycursor = conn1.cursor()
        conn1.commit()
        if selected_option1 == "1. Sum of Transaction Count in the Aggregated Insurance by State wise":
            mycursor.execute("""SELECT State, SUM(Transaction_count) as SUM_Transaction_count, Quarter 
                                FROM insurance
                                GROUP BY State, Quarter
                                ORDER BY SUM_Transaction_Count DESC, State DESC;""")
            result1 = mycursor.fetchall()
            df_top_count = pd.DataFrame(result1, columns=("states", "transaction_count", "quarter"))

            fig_top = px.bar(
                df_top_count,
                x='states',
                y='transaction_count',
                title='TRANSACTION COUNT',
                hover_name='states',
                color_discrete_sequence=px.colors.sequential.Darkmint,
                height=650,
                width=600
            )
            return fig_top

        elif selected_option1 == "2. Top Brands in the Aggregated User by State wise":
            mycursor.execute("""SELECT State, Brands, SUM(Transaction_count) AS Total_Transaction_count
                                FROM agg_user
                                GROUP BY State, Brands
                                ORDER BY Total_Transaction_count DESC;
                                """)
            result2 = mycursor.fetchall()
            df_brands = pd.DataFrame(result2, columns=("state", "brand", "total_transaction_count"))

            fig_brands = px.bar(
                df_brands,
                x='state',
                y='brand',
                title='Top 10 Brands by Total Transaction Count',
                hover_name='state',
                color='state',
                color_discrete_sequence=px.colors.sequential.Darkmint,
                height=650,
                width=600
            )
            return fig_brands

        elif selected_option1 == "3. Top 10 Transaction amount by Districts in Map Insurance":
            mycursor.execute("""SELECT State, Districts, SUM(Transaction_amount) AS Total_Transaction_amount
                                FROM map_trans
                                GROUP BY State, Districts 
                                ORDER BY Total_Transaction_amount DESC
                                LIMIT 10;""")
            result3 = mycursor.fetchall()
            df_dists = pd.DataFrame(result3, columns=("state", "districts", "total_transaction_amount"))

            fig_dist = px.bar(
                df_dists,
                x='districts',
                y='total_transaction_amount',
                title='Total Transaction Amount by Districts',
                hover_name='state',
                color='state',
                color_discrete_sequence=["rgb(0, 123, 255)"],  # Change this to your desired color
                height=650,
                width=600
            )
            return fig_dist

        elif selected_option1 == "4. Highest AppOpens in map_user":
            mycursor.execute("""SELECT State, SUM(AppOpens) as Appopens, Quarter 
                                FROM map_user
                                GROUP BY State, Quarter
                                ORDER BY Appopens DESC, State DESC;""")
            result4 = mycursor.fetchall()
            df_app = pd.DataFrame(result4, columns=("state", "appopens", "quarter"))

            fig_app = px.bar(
                df_app,
                x='state',
                y='appopens',
                title='Highest AppOpens',
                hover_name='state',
                color='state',
                color_discrete_sequence=px.colors.sequential.Darkmint,
                height=650,
                width=600
            )
            return fig_app

        elif selected_option1 == "5. Highest Registered User in map_user":
            mycursor.execute("""SELECT State, SUM(RegisteredUser) as Registered_User, Quarter 
                                FROM map_user
                                GROUP BY State, Quarter
                                ORDER BY Registered_User DESC, State DESC;""")
            result5 = mycursor.fetchall()
            df_reg = pd.DataFrame(result5, columns=("state", "registered_user", "quarter"))

            fig_reg = px.bar(
                df_reg,
                x='state',
                y='registered_user',
                title='Highest Registered User',
                hover_name='state',
                color='state',
                color_discrete_sequence=px.colors.sequential.Darkmint,
                height=650,
                width=600
            )
            return fig_reg
        elif selected_option1 == "6. Highest Registered User in Top User":
            mycursor.execute("""SELECT State, SUM(RegisteredUser) as Registered_User, Quarter 
                                FROM top_user
                                GROUP BY State, Quarter
                                ORDER BY Registered_User DESC, State DESC;""")
            result6 = mycursor.fetchall()
            df_reg_top = pd.DataFrame(result6, columns=("state", "registered_user", "quarter"))

            fig_reg_top = px.bar(
                df_reg_top,
                x='state',
                y='registered_user',
                title='Highest Registered User',
                hover_name='state',
                color='state',
                color_discrete_sequence=px.colors.sequential.Darkmint,
                height=650,
                width=600
            )
            return fig_reg_top

        elif selected_option1 == "7. Top States by Transaction Count in Insurance":
            mycursor.execute("""SELECT State, SUM(Transaction_count) as 'Transaction Count', Quarter 
                                FROM top_insurance
                                GROUP BY State, Quarter
                                ORDER BY 'Transaction Count' DESC, State DESC;""")
            result7 = mycursor.fetchall()
            df_top_trans = pd.DataFrame(result7, columns=("state", "transaction count", "quarter"))

            fig_top = px.bar(
                df_top_trans,
                x='state',
                y='transaction count',
                title='Top Transaction count',
                hover_name='state',
                color='state',
                color_discrete_sequence=px.colors.sequential.Darkmint,
                height=650,
                width=600
            )
            return fig_top


        elif selected_option1 == "8. Highest transaction amount in the Map Transactions dataset.":
            mycursor.execute("""SELECT State, SUM(Transaction_amount) as 'Transaction amount', Quarter 
                                FROM map_trans
                                GROUP BY State, Quarter
                                ORDER BY 'Transaction amount' DESC, State DESC;""")
            result8 = mycursor.fetchall()
            df_map_trans = pd.DataFrame(result8, columns=("state", "transaction amount", "quarter"))

            fig_map = px.bar(
                df_map_trans,
                x='state',
                y='transaction amount',
                title='Top Transaction amount',
                hover_name='state',
                color='state',
                color_discrete_sequence=px.colors.carto.Darkmint,
                height=650,
                width=600
            )
            return fig_map

        elif selected_option1 == "9. Transaction Amount by Payment Method and State":
            mycursor.execute("""SELECT State, name as Payment, SUM(transaction_amount) as Transaction_Amount 
                                FROM transaction 
                                GROUP BY State, Payment
                                ORDER BY State, Payment;""")
            result = mycursor.fetchall()
            df = pd.DataFrame(result, columns=("state", "payment", "transaction_amount"))

            fig6 = px.bar(
                df,
                x='state',
                y='transaction_amount',
                color='payment',
                title='Transaction Amount by Payment Method and State',
                hover_name='state',
                barmode='group',
                color_discrete_sequence=px.colors.sequential.Darkmint,
                height=650,
                width=800
            )
            return fig6

        elif selected_option1 == "10. Transaction Count by Payment Method and State":
            mycursor.execute("""SELECT State, name as Payment, SUM(Transaction_Count) as Transaction_Count 
                                FROM transaction 
                                GROUP BY State, Payment
                                ORDER BY State, Payment;""")
            result10 = mycursor.fetchall()
            df = pd.DataFrame(result10, columns=("state", "payment", "transaction_count"))

            fig4 = px.bar(
                df,
                x='state',
                y='transaction_count',
                color='payment',
                title='Transaction Count by Payment Method and State',
                hover_name='state',
                barmode='group',
                color_discrete_sequence=px.colors.sequential.Darkmint,
                height=650,
                width=500
            )
            return fig4


    # Streamlit app
    st.title("Transaction Data Visualization")

    selected_option1 = st.selectbox(
        "Choose an option",
        ["1. Sum of Transaction Count in the Aggregated Insurance by State wise",
         "2. Top Brands in the Aggregated User by State wise",
         "3. Top 10 Transaction amount by Districts in Map Insurance",
         "4. Highest AppOpens in map_user",
         "5. Highest Registered User in map_user",
         "6. Highest Registered User in Top User",
         "7. Top States by Transaction Count in Insurance",
         "8. Highest transaction amount in the Map Transactions dataset.",
         "9. Transaction Amount by Payment Method and State",
         "10. Transaction Count by Payment Method and State"]
    )

    if selected_option1:
        st.session_state["selectbox_enabled"] = True
        fig = questions(selected_option1)
        if fig:
            st.plotly_chart(fig)
