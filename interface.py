import streamlit as st
import xarray as xr
import pandas as pd
import pydeck as pdk

# Set page configuration
st.set_page_config(page_title="Gridded Rainfall Extractor", layout="wide")
st.title("Gridded Rainfall Extractor")

# Input section
col1, col2 = st.columns(2)
with col1:
    lat_min = st.number_input("Latitude Min", value=25.0)
    lat_max = st.number_input("Latitude Max", value=30.0)
    start_year = st.number_input("Start Year", min_value=1901, max_value=2024, value=2018)
with col2:
    lon_min = st.number_input("Longitude Min", value=70.0)
    lon_max = st.number_input("Longitude Max", value=75.0)
    end_year = st.number_input("End Year", min_value=1901, max_value=2024, value=2018)

# Trigger button
if st.button("Get Rainfall Data"):
    try:
        ds = xr.open_dataset("final_merged.nc")
        sel = ds.sel(
            LATITUDE=slice(lat_min, lat_max),
            LONGITUDE=slice(lon_min, lon_max),
            TIME=slice(f"{start_year}-01-01", f"{end_year}-12-31")
        )
        df = sel.to_dataframe().reset_index()
        df["YEAR"] = pd.to_datetime(df["TIME"]).dt.year

        # Gridded daily rainfall data pivoted by lat-lon
        gridded = df.pivot_table(index="TIME", columns=["LATITUDE", "LONGITUDE"], values="RAINFALL")
        max_rf = gridded.resample("Y").max()
        annual_rf = gridded.resample("Y").sum()

        st.success("Rainfall Data Extracted")
        st.subheader("Gridded Daily Data")
        st.dataframe(gridded.head())

        # Download buttons
        st.download_button("Download Gridded Daily CSV", gridded.to_csv(), file_name="gridded_daily.csv")
        st.download_button("Download Annual Max Rainfall", max_rf.to_csv(), file_name="max_rainfall.csv")
        st.download_button("Download Annual Total Rainfall", annual_rf.to_csv(), file_name="annual_rainfall.csv")

        # Visual map
        df_map = df.dropna(subset=["RAINFALL"])
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_map,
            get_position=["LONGITUDE", "LATITUDE"],
            get_color=[0, 0, 255],
            get_radius=5000,
            pickable=True
        )
        view_state = pdk.ViewState(latitude=df_map["LATITUDE"].mean(), longitude=df_map["LONGITUDE"].mean(), zoom=4)
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{RAINFALL} mm"}))
    except Exception as e:
        st.error(f"Error: {e}")