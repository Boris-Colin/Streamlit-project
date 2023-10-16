import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

st.set_page_config(page_title="My first dashboard with streamlit", initial_sidebar_state='expanded')
#Ensures the sidebar is visible in the beginning
#since this function could only be ran once, I had to put it here
image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Logo_Efrei_2022.svg/2560px-Logo_Efrei_2022.svg.png'
weekday_mapping = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}
month_mapping = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}
links = {
    "My Linkedin": "https://www.linkedin.com/in/boris-colin2022/",
    "My Github": "https://github.com/Boris-Colin",
}

def get_weekday(dt):
    return dt.weekday()
def get_month(dt):
    return dt.month
def count_rows(rows):
    return len(rows)

@st.cache_data  # <-- This function will be cached
def load_and_clean_data(file_path):
    data = pd.read_csv(file_path, delimiter=';')
    vit = data.dropna() #because of the error='corece', I still had to drop Na after this
    vit[['longitude', 'latitude']] = vit['position'].str.split(expand=True) #separating longitude and latitude
    # Convert the new columns to float if needed
    vit['longitude'] = pd.to_numeric(vit['longitude'], errors='coerce')
    vit['latitude'] = pd.to_numeric(vit['latitude'], errors='coerce')
    vit['latitude'], vit['longitude'] = vit['longitude'], vit['latitude'] #in fact, I had them switched
    vit.drop(columns=['position'], inplace=True) #dropped the original position column
    # Split the 'datetime' column into 'date' and 'hour' columns
    vit[['datej', 'hour']] = vit['date'].str.split('T', expand=True)#a 'T' separated the date and hour
    # Convert the 'date' and 'hour' columns to datetime objects,and drop Na
    vit = vit.dropna(subset=['datej'])
    vit['datej'] = pd.to_datetime(vit['datej'], errors='coerce')
    vit['hour'] = pd.to_datetime(vit['hour'], format='%H:%M').dt.time
    vit.drop(columns=['date'], inplace=True)
    vit['weekday'] = vit['datej'].map(get_weekday)  # creation of a new column called weekday
    vit['month'] = vit['datej'].map(get_month)  # creation of a new column called month
    vit['difference'] = vit['mesure'] - vit['limite']
    vit['hour'] = vit['hour'].apply(lambda x: x.hour).astype(int)
    vit['weekday_name'] = vit['weekday'].map(weekday_mapping)
    #vit = vit.drop(columns=['weekday'])
    vit['month_name'] = vit['month'].map(month_mapping)
    #vit = vit.drop(columns=['month'])
    #to be more user friendly I included the names of months and weekday, but dropping the orignial values meant ugly heatmaps, so I kept them

    filtered_vit = vit[(vit['difference'] >= 0) & ((vit['longitude'] != 0) | (vit['latitude'] != 0))]
    df2 = filtered_vit.groupby(['hour', 'weekday']).apply(count_rows).unstack()
    df3 = filtered_vit.groupby(['weekday', 'month']).apply(count_rows).unstack()
    valid_data = filtered_vit.dropna(subset=['latitude', 'longitude'])
    #I could have only kept valid_data, but at that point, I would've had to replace too many variables
    return filtered_vit, df2, valid_data, df3

def main():
    st.title('My Speed Record Dashboard')
    st.subheader("This is the display of the values")
    st.write("This is my dashboard based on car recorded speed in france.")


    st.sidebar.header('Dashboard `version 1`')

    st.sidebar.subheader('Heat map parameter')
    heatmap_data_option = st.sidebar.selectbox('Select data for heatmap', ('df2', 'df3'))
    heatmap_data = df2 if heatmap_data_option == 'df2' else df3

    available_palettes = ['viridis', 'plasma', 'coolwarm', 'mako', 'rocket']
    selected_palette = st.sidebar.selectbox('Select color palette', available_palettes)


    st.sidebar.subheader('Pie chart parameter')
    pie_chart_param = st.sidebar.selectbox('Select data', ('weekday_name', 'month_name'))
    #will select wether to see the percentage of infractions per day of the week or per month


    st.sidebar.subheader('Line chart parameters')
    line_chart_height = st.sidebar.slider('Specify plot height', 200, 500, 300)


    unique_limits = sorted(valid_data['limite'].unique()) #gets all the possible values for speed limit
    st.sidebar.subheader('Speed Limits Selection')
    user_limit = st.sidebar.selectbox('Select Limit', options=unique_limits) #I don't know why, but I got an error without the option here. Maybe because it came from a dataframe?

    nbins = st.sidebar.slider('Select number of bins', min_value=5, max_value=100, value=20)


    st.sidebar.markdown('''
    ---
    Boris Colin #Dataviz2023
    ''')
    for name, url in links.items():
        st.sidebar.markdown(f'<a href="{url}" target="_blank">{name}</a>', unsafe_allow_html=True)
    st.sidebar.image(image_url, use_column_width=True)
    # Display data overview
    st.subheader('Data Preview:')
    st.dataframe(filtered_vit.describe())

    # Row A
    st.markdown('### Metrics')
    col1, col2, col3 = st.columns(3) #indicates col order and col size (the same for all here)
    col1.metric("Average Difference", f"{filtered_vit['difference'].mean():.2f}")
    col2.metric("Max Difference", f"{filtered_vit['difference'].max()}")
    col3.metric("Total Entries", f"{len(filtered_vit)}")

    # Row B
    c1, c2 = st.columns((6, 4)) #this time the first is larger
    with c1:
        st.markdown('### Heatmap')
        plt.figure(figsize=(10, 8))
        sns.heatmap(heatmap_data, cmap=selected_palette, linewidths = .5)
        st.pyplot(plt)
        plt.clf()
    with c2:
        st.markdown('### Pie chart')
        fig2 = px.pie(filtered_vit, names=pie_chart_param)
        st.plotly_chart(fig2)

    st.markdown("As we can see through both heatmaps and piecharts, most infractions happen in the middle "
                "of the week either at the beginning or the end of the workday."
                "Contrary to what I expected, there are fewer infraction during the weekend, and more right before."
                "My guess is that people hurry back from work after the week."
                "Then, we get to observe something most interesting: save for one month, the number of infraction"
                "only increases each month. Although this could be due to the fact that the whole dataset takes place"
                "in 2021, right after covid, and circulation gradually came back to normal levels.")

    # Row C
    st.markdown('### Line chart')
    fig3 = px.histogram(filtered_vit, x='datej', y='difference')
    fig3.update_layout(
        height=line_chart_height,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    st.plotly_chart(fig3)


    # Row D
    st.subheader('Data Visualization:')
    fig, ax = plt.subplots()
    ax.hist(filtered_vit['difference'], bins=60, alpha=0.5, color='b')
    ax.set_xlabel('Difference')
    ax.set_ylabel('Frequency')
    st.pyplot(fig)
    st.markdown("We can see that most infraction are hardly severe. Most drivers get close to the speed limit, and "
                "go abose it by a few kilometers per hour. However, there are a few cases of severe violation, the"
                "record here being going 139 km per hour over the limit.")

    st.subheader('Map:')
    st.map(valid_data[['latitude', 'longitude']])
    st.markdown("We can see on this interactive map, that we have almost no data in the south-east of France. The "
                "reason for that isn't specified in the original dataset")


    filtered_data2 = valid_data[valid_data['limite'] == user_limit]
    fig = px.histogram(filtered_data2, x='hour', color='limite',
                     nbins=nbins,
                     labels={'hour': 'Hour'},
                     title=f"Histogram of 'count' over 'hour' with limit {user_limit}")
    st.plotly_chart(fig)

    fig = px.histogram(filtered_data2, x='difference', color='limite',
                       nbins=nbins,
                       labels={'difference': 'Difference'},
                       title=f"Histogram of 'count' over 'difference' with limit {user_limit}")
    st.plotly_chart(fig)
    st.markdown("When doing these two plots, I was wondering whether people were wore likely to go over the limit if"
                "it was low, and in that case, would the infraction be more severe. "
                "It appears that there are few infractions at a limit of 50, but conversely they are sevevere. In "
                "contrast, most infractions are commited when the limit is at 90, but the infractions are minor. It"
                "seems likely that there are few infractions on the highway or when it rains (110), since people "
                "either don't want to pay, or are genrally aware that going over the limit is very dangerous when it"
                "rains")

if __name__ == "__main__":
    filtered_vit, df2, valid_data, df3 = load_and_clean_data("C:/Users/1thom/Downloads/opendata-vitesse-2021-01-01-2021-12-31.csv")
    #this allows me to only do the data cleaning once when I first load the page and keep it in the cache
    main()
