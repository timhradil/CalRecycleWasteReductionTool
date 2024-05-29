import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

@st.cache_data
def load_data():
    data = pd.read_csv("wastedata.csv")
    return data

data = load_data()

# Adjust data structure to long format for easy plotting
data_long = data.melt(id_vars=['Sector'], value_vars=['Disposed', 'Recycle', 'Organics', 'Other'],
                      var_name='Waste_Type', value_name='Amount')

# Title and Introduction
st.title("Waste Reduction Visualization Tool")
st.markdown("""
This tool is designed to help visualize waste production by sector, based on the comprehensive study 
performed in 2014, as reported in the 'Generator-Based Characterization of Commercial Sector Disposal and 
Diversion in California' by CalRecycle. The aim is to identify and implement effective waste reduction 
strategies across various sectors.
""")

# Main page for user inputs
sector = st.selectbox('Select Your Sector:', [None] + list(data['Sector'].unique()))

if sector is not None:
    # Filter data by selected sector
    sector_data = data_long[data_long['Sector'] == sector].copy()

    # Display current waste production overview
    st.write(f"## Current Waste Production for {sector}")
    fig = go.Figure()
    colors = {'Disposed': 'red', 'Recycle': 'blue', 'Organics': 'green', 'Other': 'purple'}  # Define colors for each waste type
    for waste_type in sector_data['Waste_Type'].unique():
        fig.add_trace(go.Bar(
            name=waste_type,
            x=[waste_type],  # Set waste type as x-axis
            y=[sector_data[sector_data['Waste_Type'] == waste_type]['Amount'].values[0]],
            marker_color=colors[waste_type]  # Use consistent color
        ))

    fig.update_layout(
        barmode='stack', 
        title=f"Current Waste Overview for {sector}",
        xaxis_title="Waste Type",
        yaxis_title="Tons per Employee per Year",
        xaxis={'categoryorder':'total descending'}  # Optional: this will order the bars by descending amount
    )
    st.plotly_chart(fig)

    # Improvement Options Description
    st.markdown("""
    ## Potential Waste Reduction Strategies
    Below, you can select various waste reduction strategies tailored to the specific waste types 
    generated within the selected sector. As you select different strategies, observe the potential 
    improvements reflected in the waste production amounts.
    """)

    # Initialize Improved Amount with current amounts
    sector_data['Improved_Amount'] = sector_data['Amount']

    # Dictionary of improvement actions with their potential reduction percentages
    improvement_actions = {
        'Disposed': {'Implement waste sorting': 0.05, 'Reduce single-use items': 0.10},
        'Recycle': {'Improve sorting instructions': 0.10, 'Upgrade recycling bins': 0.05},
        'Organics': {'Start composting': 0.20, 'Enhance staff training on composting': 0.10},
        'Other': {'Optimize material use': 0.15, 'Improve process efficiency': 0.10}
    }

    # Interactive improvement checklist and calculations
    for waste_type, actions in improvement_actions.items():
        st.write(f"### Improvements for {waste_type} Waste")
        for action, effect in actions.items():
            if st.checkbox(f"{action} ({int(effect * 100)}% reduction)", key=sector+waste_type+action):
                # Apply the reduction to the corresponding waste type
                sector_data.loc[sector_data['Waste_Type'] == waste_type, 'Improved_Amount'] *= (1 - effect)

    # Display the potential waste reduction side by side
    st.write("## Comparison of Current vs. Improved Waste Production")
    fig2 = go.Figure()
    for waste_type in sector_data['Waste_Type'].unique():
        fig2.add_trace(go.Bar(
            name=waste_type,
            x=['Current'],
            y=[sector_data.loc[sector_data['Waste_Type'] == waste_type, 'Amount'].values[0]],
            marker_color=colors[waste_type]
        ))
        fig2.add_trace(go.Bar(
            name=waste_type,
            x=['Improved'],
            y=[sector_data.loc[sector_data['Waste_Type'] == waste_type, 'Improved_Amount'].values[0]],
            marker_color=colors[waste_type],
            showlegend=False  # Hide duplicate legend items
        ))

    fig2.update_layout(barmode='stack', title=f"Improvement Potential for {sector}",
                       xaxis_title="Category", yaxis_title="Tons per Employee per Year")
    st.plotly_chart(fig2)