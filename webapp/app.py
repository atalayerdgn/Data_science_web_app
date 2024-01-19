import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
DATA_URL = (
"/Users/USER/Desktop/site/Motor_Vehicle_Collisions_-_Crashes.csv" # path to the csv file
)


st.title("Motor Vehicle Collisions in New York City")# title of the app
st.markdown("This application is a Streamlit dashboard that can be used to  \
            analyze motor vehicle collisions in NYC 🗽💥🚗")

@st.cache_data(persist=True)# cache the data
def load_data(nrows):
	data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])# load the data
	data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)# drop rows with missing values
	lowercase = lambda x: str(x).lower()# lowercase all columns in the dataframe
	data.rename(lowercase, axis='columns', inplace=True)# rename the columns
	data.rename(columns={'crash_date_crash_time':'date/time'}, inplace=True)# rename the column
	return data

data = load_data(100000)# load 100000 rows of data into the dataframe
original_data = data

st.header("Where are the most people injured in NYC?")# header
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19)# slider
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))# map

st.header("How many collisions occur during a given time of day?")# header
hour = st.slider("Hour to look at", 0, 23)# slider sidebar
data = data[data['date/time'].dt.hour == hour]# filter the data

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))# markdown

st.write(pdk.Deck(
	map_style="mapbox://styles/mapbox/light-v9",# map style
	initial_view_state={# initial view state
		"latitude": np.average(data["latitude"]),# average latitude
		"longitude": np.average(data["longitude"]),# average longitude
		"zoom": 11,# zoom
		"pitch": 50,# pitch
	},
	layers=[# layers
		pdk.Layer( # layer
		"HexagonLayer",# hexagon layer
		data=data[['date/time', 'latitude', 'longitude']],# data
		get_position=["longitude", "latitude"],# position
		radius=100,# radius
		extruded=True,# extruded
		pickable=True,# pickable
		elevation_scale=4,# elevation scale
		elevation_range=[0, 1000],# elevation range
		),
	],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))# subheader
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))# filter the data
    ]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]# histogram
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})# chart data
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)# figure
st.write(fig)# write the figure to the screen

st.header("Top 5 dangerous streets by affected type")# header
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])# selectbox
if select == 'Pedestrians':# if statement
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:5])# write the dataframe to the screen
elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])# write the dataframe to the screen
else:
	st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])
#TR

#mapbox://styles/mapbox/light-v9: Bu, kullanılacak harita stili olarak Mapbox'un "light-v9" stilini belirtir. Mapbox, farklı harita stilleri sağlayan bir hizmettir.

#initial_view_state: Bu, haritanın başlangıç görünümünü belirler. Ortalama enlem ve boylam, bir başlangıç zoom seviyesi ve bir eğim açısı içerir.

#layers: Bu, harita üzerinde görünen katmanları belirler. Bu örnekte tek bir katman kullanılır.

#HexagonLayer: Bu, hexagon (altıgen) şeklindeki bir katman oluşturur. Bu katman, veri setindeki konum verilerini kullanarak hexagonlar oluşturur. Hexagonların yüksekliği, veri setindeki bir özellikten elde edilir.

#data[['date/time', 'latitude', 'longitude']]: Bu, kullanılan veri setinden sadece tarih/saat, enlem ve boylam sütunlarını içeren bir alt küme oluşturur.

#get_position=["longitude", "latitude"]: Bu, hexagonların konumunu belirler. Enlem ve boylam sütunları kullanılarak hexagonlar harita üzerinde yerleştirilir.

#radius=100: Bu, hexagonların yarıçapını belirler.

#extruded=True: Bu, hexagonların yükseltilip yükseltilmeyeceğini belirler. True ise hexagonlar yükseltilir.

#pickable=True: Bu, kullanıcıların hexagonları seçip seçemeyeceğini belirler.

#elevation_scale=4: Bu, hexagonların yüksekliğini belirler.

#elevation_range=[0, 1000]: Bu, hexagon yüksekliğinin aralığını belirler.

if st.checkbox("Show Raw Data", False):# checkbox
	st.subheader('Raw Data') # subheader
	st.write(data) # write the dataframe to the screen

