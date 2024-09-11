#!/usr/bin/env python
# coding: utf-8

# In[43]:


import pandas as pd 
import streamlit as st 
import altair as alt  #A data visualization library
import plotly.express as px #A terse and high-level API for creating figures




st.set_page_config(
    page_title = "US Population Dashboard",
    page_icon="🏂",
    layout = "wide",
    initial_sidebar_state = "expanded")
alt.themes.enable("dark")

# In[44]:

# Load data 
population = pd.read_excel(r"US Population.xlsx", skiprows=3)
population.rename(columns={'Unnamed: 0':'States', 'Unnamed: 1':'ID'}, inplace=True)

#Unpivot columns 
population_unpivoted = pd.melt(population,id_vars=[population.columns[0],population.columns[1]],var_name="Year", value_name="Population")


population_unpivoted['Population'] = population_unpivoted['Population'].fillna(0)
population_unpivoted['Population'] = population_unpivoted['Population'].astype(int)

#population_unpivoted

with st.sidebar:
    st.title('🏂 US Population Dashboard')
    
    year_list = list(population_unpivoted.Year.unique())[::-1]
    
    selected_year = st.selectbox('Select a year', year_list, index=len(year_list)-1)
    df_selected_year = population_unpivoted[population_unpivoted.Year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="Population", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

#st.write(df_selected_year_sorted)
input_df = population_unpivoted
input_x = 'States'
input_y = 'Year'
input_color_theme = selected_color_theme
input_color= 'Population'

def make_heatmap(input_df,  input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap






#### A colored map of the 52 US states for the selected year is depicted by the choropleth map.
# input_df: The DataFrame that provides the data for the map.
# locations=input_id: The column in the DataFrame that contains the geographic locations (e.g., state abbreviations like 'CA', 'NY').
# color=input_column: The column with data values that will determine the color intensity on the map.
# locationmode="USA-states": Specifies that the geographic locations are US states.
# color_continuous_scale=input_color_theme: Sets the color scale for the map based on the input_color_theme.
# range_color=(0, max(df_selected_year.Population)): Defines the range of values for the color scale. The max function should be applied to the column in the DataFrame that holds the data values.
# scope="usa": Limits the map view to the USA.
# labels={'Population': 'Population'}: Customizes the label for the color scale in the map legend.
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(df_selected_year.Population)),
                               scope="usa",
                               labels={'Population':'Population'}
                               )
    ### update_layout: A method used to update the layout of the Plotly figure.
    # template='plotly_dark': Applies the 'plotly_dark' template to the map, giving it a dark theme.
    # plot_bgcolor='rgba(0,0,0,0)': Sets the background color of the plotting area to be fully transparent.
    # paper_bgcolor='rgba(0,0,0,0)': Sets the background color of the entire figure (including margins) to be fully transparent.
    # margin=dict(l=0, r=0, t=0, b=0): Sets the margins around the plot to zero, making the plot fill the entire available space.
    # height=350: Sets the height of the map to 350 pixels.
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0,r=0,t=0,b=0),
        height=350
    )
    return choropleth


## Donut chart 

##calculate the year-over-year population migrations
def calculate_population_difference(input_df,input_year):
    selected_year_data = input_df[input_df['Year']==input_year].reset_index()
    previous_year_data = input_df[input_df['Year']==input_year-1].reset_index()
    selected_year_data['Population_difference'] = selected_year_data.Population.sub(previous_year_data.Population,fill_value=0)
    return pd.concat([selected_year_data.States,selected_year_data.ID,selected_year_data.Population,selected_year_data.Population_difference],axis=1).sort_values("Population_difference",ascending=False)

# Creating the donut chart 
def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text


# Convert Population to text
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num//1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num/1000} K'


## Define the app layout 

col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown('#### Gains/Losses')

    df_population_difference_sorted = calculate_population_difference(population_unpivoted, selected_year)

    if selected_year > 2010:
        first_state_name = df_population_difference_sorted.States.iloc[0]
        first_state_population = format_number(df_population_difference_sorted.Population.iloc[0])
        first_state_delta = format_number(df_population_difference_sorted.Population_difference.iloc[0])
    else:
        first_state_name = '-'
        first_state_population = '-'
        first_state_delta = ''
    st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)

    if selected_year > 2010:
        last_state_name = df_population_difference_sorted.States.iloc[-1]
        last_state_population = format_number(df_population_difference_sorted.Population.iloc[-1])   
        last_state_delta = format_number(df_population_difference_sorted.Population_difference.iloc[-1])   
    else:
        last_state_name = '-'
        last_state_population = '-'
        last_state_delta = ''
    st.metric(label=last_state_name, value=last_state_population, delta=last_state_delta)

    
    st.markdown('#### States Migration')

    if selected_year > 2010:
        # Filter states with population difference > 50000
        # df_greater_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference_absolute > 50000]
        df_greater_50000 = df_population_difference_sorted[df_population_difference_sorted.Population_difference > 50000]
        df_less_50000 = df_population_difference_sorted[df_population_difference_sorted.Population_difference < -50000]
        
        # % of States with population difference > 50000
        states_migration_greater = round((len(df_greater_50000)/df_population_difference_sorted.States.nunique())*100)
        states_migration_less = round((len(df_less_50000)/df_population_difference_sorted.States.nunique())*100)
        donut_chart_greater = make_donut(states_migration_greater, 'Inbound Migration', 'green')
        donut_chart_less = make_donut(states_migration_less, 'Outbound Migration', 'red')
    else:
        states_migration_greater = 0
        states_migration_less = 0
        donut_chart_greater = make_donut(states_migration_greater, 'Inbound Migration', 'green')
        donut_chart_less = make_donut(states_migration_less, 'Outbound Migration', 'red')

    migrations_col = st.columns((0.2, 1, 0.2))
    with migrations_col[1]:
        st.write('Inbound')
        st.altair_chart(donut_chart_greater)
        st.write('Outbound')
        st.altair_chart(donut_chart_less)

# Displaying the choropleth map and heatmap using custom functions created earlier
with col[1]:
    st.markdown('#### Total Population')
    
    choropleth = make_choropleth(df_selected_year, 'ID', 'Population', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)
    
    heatmap = make_heatmap(population_unpivoted, 'Year', 'States', 'Population', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)

# ## Top states
with col[2]:
    st.markdown('#### Top States')

    st.dataframe(df_selected_year_sorted,
                 column_order=("States", "Population"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "States": st.column_config.TextColumn(
                        "States",
                    ),
                    "Population": st.column_config.ProgressColumn(
                        "Population",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.Population),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [U.S. Census Bureau](<https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html>).
            - :orange[**Gains/Losses**]: states with high inbound/ outbound migration for selected year
            - :orange[**States Migration**]: percentage of states with annual inbound/ outbound migration > 50,000
            ''')
# In[ ]:

# st.write(make_heatmap(population_unpivoted,  input_y, input_x, input_color, input_color_theme))
# st.write(make_choropleth(df_selected_year,'ID','Population',selected_color_theme))
#st.write(calculate_population_difference(population_unpivoted,population_unpivoted['Year']))






