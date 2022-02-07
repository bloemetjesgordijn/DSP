# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import plot_lines
import time
import plotly.io as pio
from keywords import term_dict
from sewage import amphetamine_series, methamphetamine_series, MDMA_series, cocaine_series
import datetime
import dash_bootstrap_components as dbc
import plotly.figure_factory as ff
import plotly.express as px


# app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
pio.templates.default = "plotly_white"
app.title = 'DSP F6'

amphetamine_df = pd.DataFrame({'count': amphetamine_series.values, 'type': 'Amphetamine in sewage'}, index = amphetamine_series.index)
methamphetamine_df = pd.DataFrame({'count': methamphetamine_series.values, 'type': 'Methamphetamine in sewage'}, index = methamphetamine_series.index)
MDMA_df = pd.DataFrame({'count': MDMA_series.values, 'type': 'MDMA in sewage'}, index = MDMA_series.index)
cocaine_df = pd.DataFrame({'count': cocaine_series.values, 'type': 'Cocaine in sewage'}, index = cocaine_series.index)

extra_terms = []
local_term_dict = term_dict.copy()
relevant_cases = []


options = []
def get_options():
    global options
    for key in local_term_dict:
        globals()[key + "_mentions_results"] = []
        globals()[key + "_cases_results"] = []
        curr = {'label': " " + key, 'value': key}
        if curr not in options:
            options.append(curr)
    return options
get_options()

globals()["click_data"] = []
globals()['graph_df'] = []

app.layout = html.Div(children=[
    html.H1(children='Data Systems Project group F6',
    style={'text-align': 'center'}),

    html.Div(children='''
        Uncovering modus operandi using court cases
    ''',
    style={'text-align': 'center'}),

    dcc.Graph(
        id='sliding-graph'
    ),
    dcc.Loading(
            id="loading-1",
            type="default",
            children=[html.Div(id="loading-output"),
            html.Div(id="loading-output2"),
            html.Div(id="loading-output3"),
            html.Div(id="loading-output4")]
        ),
    html.Div(children='''
        Rolling mean slider
    '''),
    dcc.Slider(
        id='rolling-mean-slider',
        min=1,
        max=25,
        value=1,
        step=1,
        marks={
        1: '1',
        5: '5',
        10: '10',
        15: '15',
        25: '25'
    },
    ),
    dcc.RadioItems(
        id='mentions_case_selector',
    options=[
        {'label': 'Mentions', 'value': 'mentions'},
        {'label': 'Cases', 'value': 'cases'}
    ],
    value='mentions',
    inputStyle={"margin-left": "10px"}),
     html.Br(),
    html.Div(children='''
        Court mentions
    '''),
    dcc.Checklist(
        id="line-selector",
        options=get_options(),
        value=[],
        labelStyle={'display': 'inline-block'},
        inputStyle={"margin-left": "10px"}
    ),
    html.Br(),
    html.Div(children='''
        Sewage data
    '''),
    dcc.Checklist(
        id="sewage-selector",
        options=[{'label': 'Amphetamines', 'value': 'amphetamines'},
        {'label': 'Methamphetamines', 'value': 'methamphetamines'},
        {'label': 'MDMA', 'value': 'MDMA'},
        {'label': 'Cocaine', 'value': 'cocaine'}],
        value=[],
        inputStyle={"margin-left": "10px"}
    ),
    html.Br(),
    html.Div(children='''
        Extra terms:
    '''),
    dcc.Input(
        id="input", type="text", placeholder="", debounce=True),
    html.Div(id="output"),
    dcc.Checklist(
        id="extra-terms-selector",
        options=[],
        value=[],
        inputStyle={"margin-left": "10px"}
    ),
    html.Button('Delete extra terms', id='delete-extra-items', n_clicks_timestamp = 0),
    html.Br(),
    html.Br(),    
    html.Button('Correlation Matrix', id='corr_btn', n_clicks = 0),
    dbc.Collapse(
            dbc.Card(dbc.CardBody(dcc.Graph(
        id='output_corr'
    ))),
            id="collapse",
            is_open=False,
        ),
    html.Br(),
    html.Div(children='''
        Find cases by mentions:
    '''),
    dcc.Input(
        id="specific-case-input", type="text", placeholder="", debounce=True),
        dcc.Input(
        id="specific-case-amount-input", type="number", placeholder="20", debounce=True),
    html.Div(
        children=[
            html.Ul(id='specific-case-output', children=[html.Li(i) for i in relevant_cases])
        ],
    ),
    dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Court cases")),
                dbc.ModalBody(html.Div(
        children=[
            html.Ul(id='specific-click-output', children=[html.Li(i) for i in relevant_cases])
        ],
    ),),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="modal",
            size="lg",
            is_open=False,
        ),
])

@app.callback(
    Output('sliding-graph', 'figure'),
    Output("loading-output", "children"),
    Output('corr_btn', 'n_clicks'),
    Input('rolling-mean-slider', 'value'),
    Input('line-selector', 'value'),
    Input('sewage-selector', 'value'),
    Input('mentions_case_selector', 'value'),
    Input('extra-terms-selector', 'value'))
def update_figure(rolling_mean_value, line_selector, sewage_selector, mentions_case_selector, extra_terms):
    globals()["mentions_case_selector"] = mentions_case_selector
    df = pd.DataFrame(columns = ['count', 'type'])
    for var in line_selector:
        if mentions_case_selector == 'mentions':
            if not (len(globals()[var + "_mentions_results"]) > 0):
                globals()[var + "_mentions_results"] = plot_lines.get_line(term_dict[var], 'mentions')
            globals()["monthly_" + var + "_mentions_results"] = globals()[var + "_mentions_results"].rolling(window=rolling_mean_value).mean()
            globals()["monthly_" + var + "_mentions_results"]['type'] = var
            df = df.append(globals()["monthly_" + var + "_mentions_results"])
        elif mentions_case_selector == 'cases':
            if not (len(globals()[var + "_cases_results"]) > 0):
                globals()[var + "_cases_results"] = plot_lines.get_line(term_dict[var], 'cases')
            globals()["monthly_" + var + "_cases_results"] = globals()[var + "_cases_results"].rolling(window=rolling_mean_value).mean()
            globals()["monthly_" + var + "_cases_results"]['type'] = var
            df = df.append(globals()["monthly_" + var + "_cases_results"])

    if 'amphetamines' in sewage_selector:
        df = df.append(amphetamine_df)
    if 'methamphetamines' in sewage_selector:
        df = df.append(methamphetamine_df)
    if 'MDMA' in sewage_selector:
        df = df.append(MDMA_df)
    if 'cocaine' in sewage_selector:
        df = df.append(cocaine_df)
    
    for var in extra_terms:
        print(extra_terms)
        globals()[var + "_mentions_results"] = []
        globals()[var + "_cases_results"] = []
        if mentions_case_selector == 'mentions':
            if not (len(globals()[var + "_mentions_results"]) > 0):
                globals()[var + "_mentions_results"] = plot_lines.get_line([var], 'mentions')
            globals()["monthly_" + var + "_mentions_results"] = globals()[var + "_mentions_results"].rolling(window=rolling_mean_value).mean()
            globals()["monthly_" + var + "_mentions_results"]['type'] = var
            df = df.append(globals()["monthly_" + var + "_mentions_results"])
        elif mentions_case_selector == 'cases':
            if not (len(globals()[var + "_cases_results"]) > 0):
                globals()[var + "_cases_results"] = plot_lines.get_line([var], 'cases')
            globals()["monthly_" + var + "_cases_results"] = globals()[var + "_cases_results"].rolling(window=rolling_mean_value).mean()
            globals()["monthly_" + var + "_cases_results"]['type'] = var
            df = df.append(globals()["monthly_" + var + "_cases_results"])


    df['date'] = df.index
    globals()['graph_df'] = df
    fig = px.line(df, x="date", y="count", title='Monthly mentions', color='type')
    fig.update_layout(transition_duration=500)
    return fig, line_selector, 0

@app.callback(
    [Output("extra-terms-selector", "options"),
    Output("extra-terms-selector", "value"),],
    [Input("input", "value"),
    Input("delete-extra-items", "n_clicks_timestamp"),
    Input("extra-terms-selector", "value")]
)
def update_output(input, n_clicks_timestamp, value):
    delete_terms_button_timestamp = time.time()
    curr_time = str(int(time.time()))
    click_time = str(n_clicks_timestamp)[:-3]
    new_list = []
    clean_terms_list = []

    

    if input is not None:
        extra_terms.append(input)
        globals()['extra_terms'] = extra_terms
    if curr_time == click_time:
        new_list = []
        clean_terms_list = []
        globals()['extra_terms'] = []
        return [], []
    else:
        for i in globals()['extra_terms']:
            if i not in clean_terms_list:
                clean_terms_list.append(i)
        for term in clean_terms_list:
            if term != "":
                curr = {'label': term, 'value': term}
                new_list.append(curr)
        print(new_list)
        return new_list, value
    # return new_list, new_list

@app.callback(
    Output("specific-case-output", "children"),
    Output("loading-output2", "children"),
    Input("specific-case-input", "value"),
    Input("specific-case-amount-input", "value")
)
def update_case_check(input, amount):
    cases = input
    complete = []
    if len(input) > 0:
        result = plot_lines.get_case_that_exceed_count([input], amount)
        counts = result[0]
        cases = result[1]
        dates = result[2]
        for i in range(len(counts)):
            link = html.A(cases[i])
            link.href = 'https://uitspraken.rechtspraak.nl/inziendocument?id=' + cases[i]
            link.target = '_blank'
            curr = html.Div([
                html.P(str(counts[i]) + " mentions in " + dates[i]),
                link
            ])
            curr_el = html.Li(curr)
            complete.append(curr_el)
        if len(complete) > 0:
            relevant_cases = complete
        else:
            relevant_cases = []
    return relevant_cases, []

@app.callback(
    [Output("specific-click-output", "children"),
    Output("modal", "is_open"),
    Output("loading-output3", "children")],
    [Input('sliding-graph', 'clickData'),
    Input('sliding-graph', 'figure'),
    Input("close", "n_clicks"),
    State("modal", "is_open")]
)
def graph_click(click_data, figure, n1, is_open):
    update = False
    if globals()['click_data'] != click_data:
        update = True
        globals()["click_data"] = click_data
    if is_open == True:
        return [], False, []
    elif update:
        fig_data = figure.get('data')
        points = click_data.get('points')[0]
        x_axis = fig_data[0].get('x')
        point_index = points.get('pointIndex')
        click_date = x_axis[point_index]
        curvenumber = points.get('curveNumber')
        figure_data = figure.get('data')
        click_type = figure.get('data')[curvenumber].get('legendgroup')
        if click_type in term_dict.keys():
            words = term_dict.get(click_type)
        else:
            words = [click_type]
        df = []
        if globals()["mentions_case_selector"] == 'mentions':
            df = plot_lines.count_mentions(words)
        elif globals()["mentions_case_selector"] == 'cases':
            df = plot_lines.count_cases(words)
        formatted_date = datetime.datetime.strptime(click_date[:10], '%Y-%m-%d')
        final_date = formatted_date.strftime('%m-%Y')
        df = df[df['date'].str.contains(final_date)]
        df = df.sort_values(by=['count'], ascending=False)
        complete = []
        for i in range(len(df)):
            current = df.iloc[i]
            link = html.A(current['id'])
            link.href = 'https://uitspraken.rechtspraak.nl/inziendocument?id=' + current['id'].replace('-', ':')
            link.target = '_blank'
            curr_el = []
            if globals()["mentions_case_selector"] == 'mentions':
                curr = html.Div([
                    html.P(str(current['count']) + " " + click_type + " mentions in " + current['date']),
                    link
                ])
                curr_el = html.Li(curr)
            elif globals()["mentions_case_selector"] == 'cases':
                curr = html.Div([
                        html.P(current['date']),
                        link
                    ])
                curr_el = html.Li(curr)
            complete.append(curr_el)
        if len(complete) > 0:
            relevant_cases = complete
        else:
            relevant_cases =  [html.Div([
                    html.P("0 court cases found.")
                ])]
        return relevant_cases, True, []
    
@app.callback(
    [Output('output_corr', 'figure'),
    Output('collapse', 'is_open')],
    [Input('corr_btn', 'n_clicks'),
    State('collapse', 'is_open')]
)
def update_output(n_clicks, is_open):
    corr = []
    df = globals()['graph_df']
    terms = df['type'].unique()
    if len(terms) > 1:
        relevant_df = pd.DataFrame()
        for i in terms:
            relevant_df[i] = df[df['type'] == i]['count']
        corr = relevant_df.corr()
    if (is_open == False) and (n_clicks != 0):
        return px.imshow(corr, text_auto = True), True
    else:
        return px.imshow(corr, text_auto = True), False

    
if __name__ == '__main__':
    app.run_server(debug=False)