import dash_auth
import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime as dt


app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server


auth = dash_auth.BasicAuth(
app,
{'adria': 'riteh'}
)

def clean_data(df):
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df=df[['Datetime','Room_temp','Set_temp', 'Fan_speed', 'Window','Hvac_state', 'Valve','Room_occupation']]
    return df

#Function for reading 2 datasets on page 2 
def read_data(data):
    if data == 'Room_918':
        dataset0 = pd.read_csv('data/2013_11_12_918.csv')
        dataset = clean_data(dataset0)
    elif data == 'Room_920':
        dataset0 = pd.read_csv('data/2014_11_12_920.csv')
        dataset = clean_data(dataset0)
    return dataset.to_dict('records')

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                return name, operator_type[0].strip(), value

    return [None] * 3

# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("AdriaApp", className="display-4"),
        html.Hr(),
        html.P(
            "Data visualization tool for analytics of HVAC systems.", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Analytics", href="/", active="exact"),
                dbc.NavLink("Compare", href="/compare", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),

    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content,
    dcc.Store(id='store-data', data=[], storage_type='memory'), # 'local' or 'session'
    dcc.Store(id='store-data2', data=[], storage_type='memory')
])

app.config.suppress_callback_exceptions = True
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return [
            dbc.Row([
                dbc.Card([ 

                    html.H6('Choose data:'),
                    dcc.Dropdown(id='data-set-chosen', multi=False, value='Room_918',
                    options=[{'label':'Room_918', 'value':'Room_918'},
                            {'label':'Room_920', 'value':'Room_920'}])
                            ],className="col-md-4 row-sm-4 p-3 border bg-light"),

               dbc.Card([ 
                       

                                        html.H6('Choose date:'),
                                        dcc.DatePickerRange(
                                        id="date-picker-select",
                                        start_date=dt(2013, 11, 1),
                                        end_date=dt(2013, 11, 2),
                                        min_date_allowed=dt(2013, 11, 1),
                                        max_date_allowed=dt(2014, 12, 31),
                                        initial_visible_month=dt(2013, 11, 1),
                                        updatemode ='bothdates',
                                        persistence=True,
                                        persisted_props=['start_date','end_date'],
                                        persistence_type='session'),
                            ],className="col-md-4 row-sm-4 p-3 border bg-light"),
                                    
                dbc.Card([
                       

                                        html.H6('Choose parameters:'),
                                        dcc.Dropdown(id='Dropdown',
                                         options=[{"label": 'Set Temp', "value": 'Set_temp'},
                                        {"label": 'Room Temp', "value": 'Room_temp'},
                                        {"label": 'HVAC Speed', "value": 'Fan_speed'},
                                        {"label": 'Window', "value": 'Window'},
                                        {"label": 'HVAC State (On/Off)', "value": 'Hvac_state'},
                                        {"label": 'HVAC  Valve', "value": 'Valve'},
                                        {"label": 'Room_occupation', "value": 'Room_occupation'}],
                                        value=['Set_temp','Room_temp'], multi=True, persistence_type='session',
                                        persistence=True)
                                        ],className="col-md-4 row-sm-4 p-3 border bg-light"),
                                        ]),

            dbc.Row([
                dbc.Card(
                        dbc.CardBody(

                                        dbc.Col(html.Div(id='graph1', children=[])),

                                    ),className="col-md-8 row-sm-4 p-3 border bg-light",),

               dbc.Card(
                        dbc.CardBody(

                                        dbc.Col(dcc.Graph(id="heatmap")),

                                    ),className="col-md-4 row-sm-4 p-3 border bg-light",)]),
            dbc.Row([
                
                        dbc.CardBody(

                                        dbc.Col(dcc.Graph(id="p-cor"),

                                    ),className="col-md-8 p-3 border bg-light"),


                
                        dbc.CardBody(

                                        dbc.Col(dcc.Graph(id="density"),

                                    ),className="col-md-4 row-sm-4 p-3 border bg-light",)
                                    
                                    ]),


            dbc.Row(dbc.Card(
                    dbc.CardBody(
                        [  
                            html.P("Filter data by using: >=,<=,>,=,!=,'contains ','datestartswith '") ,
                            dash_table.DataTable(
                                id='table-sorting-filtering',
                                columns=[{'name': 'Date', 'id': 'Date', 'deletable': True},{'name': 'Fan_speed', 'id': 'Fan_speed', 'deletable': True}, {'name': 'Hvac_state', 'id': 'Hvac_state', 'deletable': True}, {'name': 'Room_occupation', 'id': 'Room_occupation', 'deletable': True}, {'name': 'Room_temp', 'id': 'Room_temp', 'deletable': True}, {'name': 'Set_temp', 'id': 'Set_temp', 'deletable': True}, {'name': 'Valve', 'id': 'Valve', 'deletable': True}, {'name': 'Window', 'id': 'Window', 'deletable': True}],
                                page_current= 0,
                                page_size= 10,
                                page_action='custom',

                                filter_action='custom',
                                filter_query='',

                                sort_action='custom',
                                sort_mode='multi',
                                sort_by=[]
                            ),
                        ]
                    ),
                    className="row-md-12 row-sm-4 p-3 border bg-light",
                )),

                ]
    elif pathname == "/compare":
        return [
                dbc.Row([

                dbc.Card([ 

                    html.H6('Choose 1. data:'),
                    dcc.Dropdown(id='data-set-chosen1', multi=False, value='Room_918',
                                options=[{'label':'Room_918', 'value':'Room_918'},
                                        {'label':'Room_920', 'value':'Room_920'}])

                            ],className="col-md-3 row-sm-4 p-3 border bg-light"),

               dbc.Card([ 

                   html.H6('Select 1. date:'),
                   dcc.DatePickerRange(
                            id="date-picker-select1",
                            start_date=dt(2013, 11, 1),
                            end_date=dt(2013, 11, 2),
                            min_date_allowed=dt(2013, 11, 1),
                            max_date_allowed=dt(2013, 12, 31),
                            initial_visible_month=dt(2013, 11, 1),
                            updatemode ='bothdates',
                            persistence=True,
                            persisted_props=['start_date','end_date'],
                            persistence_type='session'
                        )
                            ],className="col-md-3 row-sm-4 p-3 border bg-light"),
                dbc.Card([ 

                   html.H6('Choose 2. data:'),
                   dcc.Dropdown(id='data-set-chosen2', multi=False, value='Room_920',
                                options=[{'label':'Room_918', 'value':'Room_918'},
                                        {'label':'Room_920', 'value':'Room_920'}]
                )              
                            ],className="col-md-3 row-sm-4 p-3 border bg-light"),

                dbc.Card([
                    html.H6('Select 2. date:'),
                    dcc.DatePickerRange(
                        id="date-picker-select2",
                        start_date=dt(2014, 11, 1),
                        end_date=dt(2014, 11, 2),
                        min_date_allowed=dt(2014, 11, 1),
                        max_date_allowed=dt(2014, 12, 31),
                        initial_visible_month=dt(2014, 11, 1),
                        updatemode ='bothdates',
                        persistence=True,
                        persisted_props=['start_date','end_date'],
                        persistence_type='session'
                    )
                                        ],className="col-md-3 row-sm-4 p-3 border bg-light"),
                                        ]),

                dbc.Row([
                dbc.Card([ 
                    dbc.Col(dcc.Graph(id="density1")),
                            ],className="col-md-4 row-sm-4 p-3 border bg-light"),
               dbc.Card([ 
                   dbc.Col(dcc.Graph(id="box-plot2")),
                            ],className="col-md-4 row-sm-4 p-3 border bg-light"),
                dbc.Card([ 
                    dbc.Col(dcc.Graph(id="density2")),
                            ],className="col-md-4 row-sm-4 p-3 border bg-light"),
                                        ]),

                dbc.Row([
                dbc.Card([ 
                    dbc.Col(dcc.Graph(id="heatmap1")),
                            ],className="col-md-4 row-sm-4 p-3 border bg-light"),
                dbc.Card([ 
                    dbc.Col(dcc.Graph(id="pie")),
                            ],className="col-md-4 row-sm-4 p-3 border bg-light"),

                dbc.Card([ 
                    dbc.Col(dcc.Graph(id="heatmap2")),
                            ],className="col-md-4  row-sm-4 p-3 border bg-light"),
                                        ]),
                ]
    else:
        print('error 404')
    
#STORING DATA
# Storing data for 1. page : analytics
@app.callback(
    Output('store-data', 'data'),
    Input('data-set-chosen', 'value')
)
def store_data(value):
    if value == 'Room_918':
        dataset0 = pd.read_csv('data/2013_11_12_918.csv')
        dataset = clean_data(dataset0)
    elif value == 'Room_920':
        dataset0 = pd.read_csv('data/2014_11_12_920.csv')
        dataset = clean_data(dataset0)
    return dataset.to_dict('records')

#Storing 2 datas 
@app.callback(
    Output('store-data2', 'data'),
    Input('data-set-chosen1', 'value'),
    Input('data-set-chosen2', 'value')
)
def store_data2(value1,value2):
    data1=read_data(value1)
    data2=read_data(value2) 
    data = [data1,data2]
    return data


#Visualizations for 1.page - analytics
#Line graph and dropdown
@app.callback(
    Output('graph1', 'children'),
    [Input('store-data', 'data'),
    Input('data-set-chosen', 'value'),
    Input('Dropdown', 'value'),
    Input("date-picker-select", "start_date"),
    Input("date-picker-select", "end_date")]
)
def create_graph1(data, value, param, start, end):
    dff = pd.DataFrame(data)
    dff=dff.set_index('Datetime')
    dff = dff.loc[start+" 00:05:00":end+" 00:05:00"]
    df_selection=dff[param]
    fig1 = px.line(df_selection, x=dff.index, y=df_selection.columns)
    return dcc.Graph(figure=fig1)


#Density graph
@app.callback(
    Output("density", "figure"), 
    [Input('store-data', 'data'),
    Input("date-picker-select", "start_date"),
    Input("date-picker-select", "end_date")])
def update_density(data, start, end):
    df = pd.DataFrame(data)
    df=df.set_index('Datetime')
    df = df.loc[start+" 00:05:00":end+" 00:05:00"]
    fig = px.density_heatmap(df, x="Set_temp", y="Room_temp", marginal_x="histogram", marginal_y="histogram")
    return fig

#Heatmap graph
@app.callback(
    Output("heatmap", "figure"), 
    [Input('store-data', 'data'),
    Input("date-picker-select", "start_date"),
    Input("date-picker-select", "end_date")])
def update_plot_box(data, start, end):
    dff = pd.DataFrame(data)
    dff=dff.set_index('Datetime')
    dff = dff.loc[start+" 00:05:00":end+" 00:05:00"]
    df=dff[['Room_temp','Set_temp', 'Fan_speed','Hvac_state', 'Valve','Room_occupation', 'Window']]
    corr = df.corr()
    fig = go.Figure(data=go.Heatmap(
                       z=corr.values,
                       x=corr.index.values,
                       y=corr.columns.values,
                       colorscale='PuBu_r',
                       hoverongaps = False))
    return fig

#Paralel-coordinates graph
@app.callback(
    Output("p-cor", "figure"), 
    [Input('store-data', 'data'),
    Input("date-picker-select", "start_date"),
    Input("date-picker-select", "end_date")])
def update_parallel_coordinates(data, start, end):
    dff = pd.DataFrame(data)
    mask = (dff['Datetime'] > start+" 00*") & (dff['Datetime'] <= end+" 00*")
    dff=dff.loc[mask]
    fig = px.parallel_coordinates(dff, color="Room_temp")
    return fig

#Table
@app.callback(
    Output('table-sorting-filtering', 'data'),
    [Input('table-sorting-filtering', "page_current"),
    Input('table-sorting-filtering', "page_size"),
    Input('table-sorting-filtering', 'sort_by'),
    Input('table-sorting-filtering', 'filter_query'),
    Input('store-data', 'data'),
    Input("date-picker-select", "start_date"),
    Input("date-picker-select", "end_date")])
def update_table(page_current, page_size, sort_by, filter,data, start, end):
    filtering_expressions = filter.split(' && ')
    dff = pd.DataFrame(data)
    dff['Date']=dff[['Datetime']]
    dff=dff.set_index('Datetime')
    first_column = dff.pop('Date')
    dff.insert(0, 'Date', first_column)
    dff = dff.loc[start+" 00:05:00":end+" 00:05:00"]

    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)
        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    page = page_current
    size = page_size
    return dff.iloc[page * size: (page + 1) * size].to_dict('records')


#Visualizations for 2. page - compare
#Density graph1.
@app.callback(
    Output("density1", "figure"), 
    [Input('store-data2', 'data'),
    Input("date-picker-select1", "start_date"),
    Input("date-picker-select1", "end_date")])
def update_density1(data, start, end):
    data1=data[0]
    df1 = pd.DataFrame(data1)

    df1=df1.set_index('Datetime')
    df1 = df1.loc[start+" 00:05:00":end+" 00:05:00"]

    fig = px.density_heatmap(df1, x="Set_temp", y="Room_temp", marginal_x="histogram", marginal_y="histogram")
    return fig

#Density graph2.
@app.callback(
    Output("density2", "figure"), 
    [Input('store-data2', 'data'),
    Input("date-picker-select2", "start_date"),
    Input("date-picker-select2", "end_date")])
def update_density2(data, start, end):
    data2=data[1]
    df2 = pd.DataFrame(data2)

    df2=df2.set_index('Datetime')
    df2 = df2.loc[start+" 00:05:00":end+" 00:05:00"]

    fig = px.density_heatmap(df2, x="Set_temp", y="Room_temp", marginal_x="histogram", marginal_y="histogram")
    return fig

#Boxplot graph   
@app.callback(
    Output("box-plot2", "figure"), 
    Input('store-data2', 'data'),
    Input("date-picker-select1", "start_date"),
    Input("date-picker-select1", "end_date"),
    Input("date-picker-select2", "start_date"),
    Input("date-picker-select2", "end_date"),)
def update_plot_box2(data, start1,end1,start2,end2):
    data1=data[0]
    data2=data[1]
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)

    df1=df1.set_index('Datetime')
    df1 = df1.loc[start1+" 00:05:00":end1+" 00:05:00"]
    df2=df2.set_index('Datetime')
    df2 = df2.loc[start2+" 00:05:00":end2+" 00:05:00"]

    fig = go.Figure()
    fig.add_trace(go.Box(y=df1['Room_temp'], name='Room Temp 1.'))
    fig.add_trace(go.Box(y=df1['Set_temp'], name='Set Temp 1.'))
    fig.add_trace(go.Box(y=df2['Room_temp'], name='Room Temp 2.'))
    fig.add_trace(go.Box(y=df2['Set_temp'], name='Set Temp 2.'))
    return fig

#Heatmap  1.
@app.callback(
    Output("heatmap1", "figure"), 
    [Input('store-data2', 'data'),
    Input("date-picker-select1", "start_date"),
    Input("date-picker-select1", "end_date"),])
def update_heatmap1(data, start, end):
    data1=data[0]
    df1 = pd.DataFrame(data1)

    df1=df1.set_index('Datetime')
    df1 = df1.loc[start+" 00:05:00":end+" 00:05:00"]


    df1=df1[['Room_temp','Set_temp', 'Fan_speed', 'Window','Hvac_state', 'Valve','Room_occupation']]
    corr = df1.corr()
    fig1 = go.Figure(data=go.Heatmap(
                       z=corr.values,
                       x=corr.index.values,
                       y=corr.columns.values,
                       colorscale='PuBu_r',
                       hoverongaps = False))
    return fig1

#Heatmap  2.
@app.callback(
    Output("heatmap2", "figure"), 
    [Input('store-data2', 'data'),
    Input("date-picker-select2", "start_date"),
    Input("date-picker-select2", "end_date"),])
def update_heatmap2(data, start, end):
    data2=data[1]
    df2 = pd.DataFrame(data2)
    df2=df2.set_index('Datetime')
    df2 = df2.loc[start+" 00:05:00":end+" 00:05:00"]

    df2=df2[['Room_temp','Set_temp', 'Fan_speed', 'Window','Hvac_state', 'Valve','Room_occupation']]

    corr = df2.corr()
    fig1 = go.Figure(data=go.Heatmap(
                       z=corr.values,
                       x=corr.index.values,
                       y=corr.columns.values,
                       colorscale='PuBu_r',
                       hoverongaps = False))
    return fig1

#Pie
@app.callback(
    Output("pie", "figure"), 
    [Input('store-data2', 'data'),
    Input("date-picker-select1", "start_date"),
    Input("date-picker-select1", "end_date"),
    Input("date-picker-select2", "start_date"),
    Input("date-picker-select2", "end_date"),])
def update_pie(data, start1, end1, start2,end2):
    data1=data[0]
    data2=data[1]

    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)

    df1=df1.set_index('Datetime')
    df1_loc = df1.loc[start1+" 00:05:00":end1+" 00:05:00"]
    df2=df2.set_index('Datetime')
    df2_loc = df2.loc[start2+" 00:05:00":end2+" 00:05:00"]

    occupation1=df1_loc["Room_occupation"].sum()
    occupation2=df2_loc["Room_occupation"].sum()

    labels = ["Occupancy 1.", "Occupancy 2."]
    values = [occupation1,occupation2,]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6)])

    return fig



if __name__=='__main__':
    app.run_server(debug=True)

    
