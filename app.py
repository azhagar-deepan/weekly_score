import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    layout="wide"
)  # This centers the layout and can reduce the chance of scroll bars appearing


# Streamlit App
st.title("Weekly Scores")

# Input Google Sheet URL
sheet_name = "Sheet1"  # Replace with your actual sheet name
sheet_id = (
    "1mCdsuttyAkd3tEgsAz_EDMuJVW2T4rli8kNNb3ZLnrI"  # Replace with your actual sheet ID
)
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Load data from the Google Sheet
try:
    test = pd.read_csv(url, header=None)  # header=None for sheets without headers
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Mapping activity types to column indices
activity_columns = {
    "Selfcare": 26,
    "Interpersonal": 27,
    "Communication": 28,
    "Work": 29,
}

# Sidebar Inputs
with st.sidebar:
    st.header("Filters")
    person = st.selectbox(
        "Choose a Person", test[3].unique()
    )  # Select person from column 4
    activities = st.multiselect(
        "Select Activities",
        ["Selfcare", "Interpersonal", "Communication", "Work"],
        default=["Selfcare"],
    )
    # Filter Data for Selected Person
    person_data = test[test[3] == person]  # Filter for selected person (4th column)

    # Get valid week range
    min_week = int(person_data[25].min())
    max_week = int(person_data[25].max())
    week_range = st.slider(
        "Select Week Range for Line Chart:",
        min_value=min_week,
        max_value=max_week,
        value=(min_week, max_week),
    )
    specific_week = st.slider(
        "Select a Week for Table View:",
        min_value=min_week,
        max_value=max_week,
        value=min_week,
    )

# Layout with two columns
col1, col2 = st.columns([2, 0.75])  # Equal width columns

# First Column: Table with a single-week slider
with col2:

    # Select Score Category to View Scores for All Persons
    selected_activity = st.selectbox(
        "",
        ["Selfcare", "Interpersonal", "Communication", "Work"],
        index=0,
    )

    # Get the column index for the selected activity
    col_index = activity_columns[selected_activity]

    # Filter for the selected week and all persons
    week_table_data = test[
        test[25] == specific_week
    ]  # Filter data for the specific week
    table_data = week_table_data[[3, col_index]].copy()  # Person and selected score
    table_data.columns = ["Person", "Score"]

    # Sort the DataFrame in descending order by Score
    table_data = table_data.sort_values(by="Score", ascending=False)

    if not table_data.empty:
        st.dataframe(table_data, width=700)  # Set a specific width for the table
    else:
        st.warning("No data available for the selected week or category.")

# Second Column: Line chart with range slider
with col1:
    # Filter for the week range
    week_range_data = person_data[
        (person_data[25] >= week_range[0]) & (person_data[25] <= week_range[1])
    ]

    # Prepare Data for Line Chart
    plot_data = pd.DataFrame()
    for activity in activities:
        col_index = activity_columns[activity]
        temp_data = week_range_data[[25, col_index]].copy()  # Week and Activity column
        temp_data.columns = ["Week", "Score"]
        temp_data["Activity"] = activity
        plot_data = pd.concat([plot_data, temp_data])

    plot_data["Week"] = pd.to_numeric(plot_data["Week"], errors="coerce")
    plot_data["Score"] = pd.to_numeric(plot_data["Score"], errors="coerce")

    if not plot_data.empty:
        fig = px.line(
            plot_data,
            x="Week",
            y="Score",
            color="Activity",
            title=f"{person}'s Scores Across Selected Weeks and Activities",
            labels={"Week": "Week", "Score": "Score"},
        )
        st.plotly_chart(fig)
    else:
        st.warning("No data available for the selected week range.")
