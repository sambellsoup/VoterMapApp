#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Data handling
import pandas as pd
import numpy as np

# Bokeh libraries
from bokeh.io import output_file, output_notebook
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
from bokeh.layouts import row, column, gridplot
from bokeh.models.widgets import Tabs, Panel

#Plotting
import geopandas as gpd

fig = figure()


df = pd.read_csv('cleanfeatures.csv', index_col=0)
df.rename(columns={'Election type':'Election_type'}, inplace=True)

# Import reset_output (only needed once)
from bokeh.plotting import reset_output

# Use reset_output() between subsequent show() calls, as needed
reset_output()


shapefile = 'Shape_Files/ne_110m_admin_0_countries.shp'
#Read shapefile using Geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
#Rename columns.
gdf.columns = ['country', 'country_code', 'geometry']
gdf = gdf.drop(gdf.index[159])


#Drop row corresponding to 'Antarctica'
gdf = gdf.drop(gdf.index[159])


from bokeh.io import curdoc, output_notebook
from bokeh.models import Slider, HoverTool
from bokeh.layouts import widgetbox, row, column
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer
import json
#Define function that returns json_data for year selected by user.

def json_data(selectedYear):
    yr = selectedYear
    df_yr = df[df['Year'] == yr]
    merged = gdf.merge(df_yr, left_on = 'country_code', right_on ='iso3', how = 'left')
    merged.fillna('No data', inplace = True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data
#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = json_data(2016))
#Define a sequential multi-hue color palette.
palette = brewer['YlGnBu'][5]
#Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]
#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
color_mapper = LinearColorMapper(palette = palette, low = 0, high = 100, nan_color = '#d9d9d9')
#Define custom tick labels for color bar.
tick_labels = {'0': '0%', '20':'20%', '40':'40%', '60':'60%', '80': '80%', '100': '100%'}
#Add hover tool
hover = HoverTool(tooltips = [ ('Country/region','@Country'),('Type of election', '@Election_type'),('% of voting age population that voted', '@VAP_Turnout_Percentage{11.11}'), ('Compulsory Voting', '@Compulsory_voting')])
#Create color bar.
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
#Create figure object.
p = figure(title = 'Registered Voters who Voted, 2016', plot_height = 600 , plot_width = 950, toolbar_location = 'below', toolbar_sticky=True, tools = [hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
#Add patch renderer to figure.
p.patches('xs','ys', source = geosource,fill_color = {'field' :'VAP_Turnout_Percentage', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
#Specify layout
p.add_layout(color_bar, 'below')
# Define the callback function: update_plot
def update_plot(attr, old, new):
    yr = slider.value
    new_data = json_data(yr)
    geosource.geojson = new_data
    p.title.text = 'Voting Age Population That Voted, %d' %yr

# Make a slider object: slider
slider = Slider(title = 'Year',start = 1990, end = 2017, step = 1, value = 2016)
slider.on_change('value', update_plot)
# Make a column layout of widgetbox(slider) and plot, and add it to the current document
layout = column(p,widgetbox(slider))
curdoc().add_root(layout)

#Display plot
show(layout)
