# Statistics Processing and Analysing ----- by Meng Rong & Bao Huan

import pandas as pd
import plotly.express as px             # Plotly Express
import plotly.graph_objs as go
from tkinter import messagebox

# Merging DataFrame when loading in 2 Dataframes (Columns must have same name to combine)
def mergedf(df1, df2):
    '''
    Merge DF1 with DF2, using full outer join style, where the insections are the same columns found in both DF

    DF1                     DF2                     Merged DF
    A   |   B               B   |   C               A   |   B   |   C
    Index1                  Index1                  Index1
    Index2                  Index2                  Index2
    '''
    samecol = [x for x in list(df1.columns) if x in list(df2.columns)]
    combinedf = df1.merge(df2, on=samecol, how='outer') # on=samecol has to be there or else a similar column name will have <same col>_y new columns, if the second column in the on-key has a different value, that row of table1 and table2 wont show
    return combinedf


# Functions to create New DataFrames to merge for export ---------------------- Author: Meng Rong and Bao Huan
def activecasesDF(df):    
    '''
    Creates a new DataFrame from "Kaggle" DF, input results from formula into new column.
    
    "Current Active Cases" Structure:
    Date    ||      ICU     ||      General Ward        ||      In Isolation      ||      (new added column)
    
    Formula:
    Current Active Cases = (ICU + General Ward + Isolation)
    '''
    activecasesdf = df[["Date", "Intensive Care Unit (ICU)", "General Wards MOH report", "In Isolation MOH report"]].copy()
    activecasesdf["Current Active Cases"] = df["Intensive Care Unit (ICU)"] + df["General Wards MOH report"] + df["In Isolation MOH report"]
    return activecasesdf


def percentO2DF(df):
    '''
    Creates a new DataFrame from "Kaggle" DF, input results from formula into new column.

    "PercentO2" Structure:
    Date    ||      ICU     ||      General Ward        ||      Require O2 Supplementation      ||      (new added column)
    
    Formula:
    Percentage req O2 Supplementation  = (O2 Count / (ICU + General Ward)  * 100
    '''
    percentO2df = df[["Date", "Intensive Care Unit (ICU)", "General Wards MOH report", "Requires Oxygen Supplementation"]].copy()
    percentO2df["Percentage Oxygen Supplementation"] = (df["Requires Oxygen Supplementation"] / (df["Intensive Care Unit (ICU)"] + df["General Wards MOH report"])  * 100).round(2)
    return percentO2df


def icuByAgeDF(df):       
    '''
    Creates a new DataFrame from "Hospital" DF, input results from formula into new column.

    "icuByAge" Structure:
    Date    ||      (1st Age Group + ICU Keyword))    || (2nd Age Group + ICU keyword)      ||      ....
                            Count of cases                      Count of cases
    
    Formula:
    (Age Group + ICU Keyword) ....
    '''    
    # Regex for the ICU people - to be changed if Original value from dataset changes
    icuRegex = "Critically ill and Intubated in ICU"

    # Single out all the Rows that are related to ICU and make a pivot table dataframe to get individual age groups as a column
    tempdf = df.loc[df['clinical_status'].str.contains(pat=icuRegex, regex=True)]
    newdf = pd.pivot_table(tempdf, values="count_of_case", index="Date", columns="age_groups")
    
    # Rename the columns into (Age Group + ICU) at the end. Thus, e.g. "70 years old and above ICU"
    for value in list(newdf.columns):
        newdf = newdf.rename(columns={value: value+" in ICU"})
    
    newdf = newdf.reset_index().rename_axis(None, axis=1)       # Reset the index and Remove the name of axis of the row made by pivot table
    newdf = newdf.fillna(0)
    return newdf


def localsByAgeDF(df):
    '''
    Creates a new DataFrame from "LocalCasesByAgeGroup" DF, input results from formula into new column.

    "localsByAge" Structure:
    Date    ||      (1st Age Group + Local Cases Keyword))    || (2nd Age Group + Local Cases keyword)      ||      ....

    Formula:
    (Age Group + Local Cases Keyword) ....
    '''
    newdf = pd.pivot_table(df, values="count_of_case", index="Date", columns="age_group")
    for value in list(newdf.columns):
        newdf = newdf.rename(columns={value: value+" Local Cases"})
    
    newdf = newdf.reset_index().rename_axis(None, axis=1)
    newdf = newdf.fillna(0)
    return newdf


# Functions for plotting Analysis Graph ------------------------ Author: Meng Rong
def analysis_bar_ActiveCases(df):
    '''
    Manipulates "Current Active Cases" DF:

    "Current Active Cases" Structure:
    Date    ||      ICU     ||      General Ward        ||      In Isolation      ||      (new added column)
    '''
    list1 = ["Intensive Care Unit (ICU)", "General Wards MOH report", "In Isolation MOH report"]
    fig = px.bar(df, x='Date', y=list1, text='Current Active Cases')

    # Styling of Graphs
    fig.update_traces(
        textfont_size=22,
        hovertemplate='Date: %{x}\
                        <br>Value: %{y}\
                        <br>Total for the day: %{text}',
        hoverlabel=dict(
            bgcolor="white",
            font_size=18,
            font_family="Rockwell"
        )
    )
    fig.update_layout(
        title_text='Daily Active Cases bargraph',
        legend_title = "Legends",
        font=dict(
            family="Arial, Sans-serif",
            size=16,
        ),
    )
    fig.show()


def analysis_scatter_percentO2(df):
    '''
    Manipulates "PercentO2" DF:

    "PercentO2" Structure:
    Date    ||      ICU     ||      General Ward        ||      Require O2 Supplementation      ||      (new added column)
    '''
    list1 = ["Intensive Care Unit (ICU)", "General Wards MOH report", "Requires Oxygen Supplementation"]
    internaldf = df.dropna(subset=["Percentage Oxygen Supplementation"])
    fig = px.scatter(internaldf, x="Date", y="Percentage Oxygen Supplementation", trendline="ols", 
        hover_data = {
            "No of Required Oxygen": internaldf['Requires Oxygen Supplementation'],
            "No. of ICU": internaldf['Intensive Care Unit (ICU)'],
            "No. of General Wards": internaldf['General Wards MOH report'],
        }
    )
    # Styling of Graphs
    fig.update_layout(
        title_text='Percentage Oxygen Supplement required by Hospitalised patients',
        font=dict(
            family="Arial, Sans-serif",
            size=16,
        ),
        hovermode='x unified'
    )
    fig.show()


def analysis_pie_ICU_AgeGroup(df):
    '''
    Manipulate "icuByAge" DF

    "icuByAge" Structure:
    Date    ||      (1st Age Group + ICU Keyword))    || (2nd Age Group + ICU keyword)      ||      ....
                            Count of cases                      Count of cases
    '''
    date = str(df.sort_values(by='Date').iloc[0,0].date())
    dict1 = {}
    # Store values into dict1
    # Key = Age Group Column Name
    # Value = Total count of all values in (Age Group) column
    colhead = [x for x in df.columns if x != "Date"]
    for value in colhead:
        dict1[value] = df[value].sum()

    # Show pie chart 
    labels = []
    values = []
    for k,v in dict1.items():
        labels.append(k)
        values.append(v)

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    # Styling of Graphs
    fig.update_traces(
        textinfo='label+percent',
        textfont_size=22,
        hovertemplate='Age Group: %{label}\
                        <br>Number of Cases: %{value}', 
        hoverlabel=dict(
            bgcolor="white",
            font_size=18,
            font_family="Rockwell"
        )
    )
    fig.update_layout(
        title_text='Total ICU based on Age Group from ' + date,
        legend_title = "Legends",
        font=dict(
            family="Arial, Sans-serif",
            size=22,
        ),
    )
    fig.show()


def analysis_pie_TotalCases_AgeGroup(df):
    '''
    Manipulates "localsByAge" DF:

    "localsByAge" Structure:
    Date    ||      (1st Age Group + Local Cases keyword))    || (2nd Age Group + Local Cases keyword)      ||      ....
    '''
    date = str(df.sort_values(by='Date').iloc[0,0].date())
    dict1 = {}

    # Store values into dict1
    # Key = Age Group Column Name
    # Value = Total count of all values in (Age Group) column
    colhead = [x for x in df.columns if x != "Date"]
    for value in colhead:
        dict1[value] = df[value].sum()

    labels = []
    values = []
    for k,v in dict1.items():
        labels.append(k)
        values.append(v)

    # Calculate total cases to show in hover styling for interactive graph
    total = sum(values)

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    # Styling of Graphs
    fig.update_traces(
        textinfo='label+percent',
        textfont_size=22,
        hovertemplate='Age Group: %{label}\
                        <br>Number of Cases: %{value}',
        hoverlabel=dict(
            bgcolor="white",
            font_size=18,
            font_family="Rockwell"
        )
    )
    fig.update_layout(
        title_text='Total ICU based on Age Group from ' + date,
        legend_title = "Legends",
        font=dict(
            family="Arial, Sans-serif",
            size=22,
        ),
    )
    fig.show()


# Functions for plotting Basic Graph (Y-axis Columns) ----------------------------------Author: Meng Rong
def basic_line_graph(df, y_axis):
    '''
    Creates a Line Graph of DataFrame:

    df = Cleaned Pandas DataFrame (with starting column, labelled as "Date")
    y_axis = Column name used for y-axis (list)
    '''
    try:
        fig = px.line(df, x="Date", y=y_axis)
        
        fig.update_layout(
            xaxis_title = "Date",
            yaxis_title = "Total Value",
            legend_title = "Legends",
            font=dict(
                family="Courier New, monospace",
                size=18,
            ),
        )
        fig.show()

    except ValueError:
        messagebox.showerror("Invalid Inputs", "Some Y-axis are not plot-able together with others, please try other combinations")


def basic_bar_graph(df, y_axis):
    '''
    Creates a Bar Graph of based on DataFrame:

    df = Cleaned Pandas DataFrame (with starting column, labelled as "Date")
    y_axis = Column name used for y-axis (list)
    '''
    try:
        fig = px.bar(df, x="Date", y=y_axis)

        fig.update_layout(
            xaxis_title = "Date",
            yaxis_title = "Total Value",
            legend_title = "Legends",
            font=dict(
                family="Courier New, monospace",
                size=18,
            ),
        )
        fig.show()

    except ValueError:
        messagebox.showerror("Invalid Inputs", "Some Y-axis are not plot-able together with others, please try other combinations")