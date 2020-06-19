import math
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import random
import datetime
from Ship import Sprinter, Galleon

from dash.dependencies import Input, Output, State, MATCH, ALL
from flask_caching import Cache

random.seed()
app = dash.Dash(__name__)

starttime = datetime.datetime.now()

ships = {
    "A": {'ship': Sprinter([0,0]), 'linecolor': "DarkGreen", 'fillcolor': 'LightGreen'},
    "B": {'ship': Sprinter([20,40]), 'linecolor': "DarkBlue", 'fillcolor': 'LightBlue'},
    "C": {'ship': Sprinter([-20,75]), 'linecolor': "DarkCyan", 'fillcolor': 'LightCyan'},
    "D": {'ship': Sprinter([-50,-80]), 'linecolor': "Red", 'fillcolor': 'Pink'},
}

inputs = dict()

fig = go.Figure(go.Scatter(
    fill = 'toself',
    mode='lines',
))

fig.update_layout(
    yaxis=dict(
        scaleanchor="x",
        scaleratio=1,
        range=[-300, 300],
    ),
)

for key, value in ships.items():
    fig.add_trace(go.Scatter(
        name=key + '-ship',
        x = value['ship'].get_ship_data()[:,0],
        y = value['ship'].get_ship_data()[:,1],
        fill='toself',
        mode='lines',
        line_color=value['linecolor'],
        fillcolor=value['fillcolor'],
    ))

    fig.add_trace(go.Scatter(
        name=key + '-path',
        x = None,
        y = None,
        fill='toself',
        mode='lines',
        line_color=value['linecolor'],
    ))

    inputs[key] = {'steer': 0, 'thrust': 0, 'roll': 0}


def create_ship_controls(name, color):
    return html.Div(
        className="row",
        style={
            "border": "solid darkgrey",
            "background-color": color,
            "max-height": "400px",
        },
        children=[
            html.H5(name, style={"text-align": "center"}),
            dcc.Slider(
                className="slider-pad",
                id={"type": "input", "ship": name, "control": "thrust"},
                min=-1.0,
                max=1.0,
                step=0.05,
                value=0,
                included=False,
                # updatemode='drag',
                marks={
                    0: {'label': 'Steady as she goes!'},
                    -1: {'label': 'Full stop!'},
                    1: {'label': 'Full steam ahead!'}
            }),
            dcc.Slider(
                className="slider-pad",
                id={"type": "input", "ship": name, "control": "steer"},
                min=-1.0,
                max=1.0,
                step=0.05,
                value=0,
                included=False,
                # updatemode='drag',
                marks={
                    -1: {'label': 'Hard to port!'},
                    0: {'label': 'Dead ahead!'},
                    1: {'label': 'Hard to starboard!'}
            }),
            html.Div(
                className="row mgn",
                children=[
                    html.Label(
                        "Navigation Roll:",
                        className="six columns",
                        style={"text-align": "right",
                               "padding-top": "7px",
                               "padding-right": "10px"}
                    ),
                    dcc.Input(
                        className="three columns",
                        id={"type": "input", "ship": name, "control": "roll"},
                        type="number",
                    ),
                ]
            ),
            html.Div(
                className="row",
                style={"margin-top": "10px"},
                children=[
                    html.Label(
                        "Current AC",
                        className="six columns",
                        style={"text-align": "center"}
                    ),
                    html.Label(
                        "Current Speed",
                        className="six columns",
                        style={"text-align": "center"}
                    ),
                ]
            ),
            html.Div(
                className="row",
                style={"margin-bottom": "10px"},
                children=[
                    html.Label(
                        "0",
                        id={"ship": name, "type": "ac"},
                        className="six columns",
                        style={"text-align": "center"}
                    ),
                    html.Label(
                        "0",
                        id={"ship": name, "type": "speed"},
                        className="six columns",
                        style={"text-align": "center"}
                    ),
                ]
            ),
            html.Div(
                id={'ship': name, 'type': 'dummy', 'control': 'thrust'},
                hidden=True, children=[]),
            html.Div(
                id={'ship': name, 'type': 'dummy', 'control': 'steer'},
                hidden=True, children=[]),
            html.Div(
                id={'ship': name, 'type': 'dummy', 'control': 'roll'},
                hidden=True, children=[]),
        ]
    )


def get_layout():
    return html.Div(
        className="row",
        children=[
            html.Div(
                className="three columns",
                style={"max-height": "100vh", "overflow-y": "auto"},
                children=[create_ship_controls(k, v['fillcolor']) for k, v in ships.items()]
            ),
            html.Div(
            className="nine columns",
            style={
                "height": "95vh",
            },
            children=[
                dcc.Graph(
                    style={
                        "width": "100%",
                        "height": "100%",
                    },
                    id='plot',
                    figure=fig,
                    animate=True,
                    animation_options = dict(
                        frame={"redraw": True},
                    )
                ),
                html.Button(
                    "Start Round",
                    id="start",
                    n_clicks=0,),
            ]),
            # dcc.Interval(
            #     id='short-interval',
            #     interval=500,
            #     n_intervals=0,
            # ),
            dcc.Interval(
                id='long-interval',
                interval=2000,
                n_intervals=0,
            ),
        ]
    )

app.layout = get_layout
motion_in_progress = False

@app.callback(Output({'type': 'dummy', 'ship': MATCH, 'control': MATCH}, 'children'),
              [Input({'type': 'input', 'ship': MATCH, 'control': MATCH}, 'value')],
              [State({'type': 'input', 'ship': MATCH, 'control': MATCH}, 'id')])
def update_inputs(value, info):
    global inputs
    changed_ids = '\n'.join([p['prop_id'] for p in dash.callback_context.triggered])
    inputs[info['ship']][info['control']] = value
    return []


@app.callback([Output('plot', 'figure'),
               Output({'type': 'input', 'ship': ALL, 'control': ALL}, 'value')],
              [Input('long-interval', 'n_intervals')],
              [State({'type': 'input', 'ship': ALL, 'control': ALL}, 'id')])
def update_plot(_, info):
    global inputs, fig
    changed_ids = '\n'.join([p['prop_id'] for p in dash.callback_context.triggered])
    out = []

    for i in info:
        out.append(inputs[i['ship']][i['control']])

    for s in ships.keys():
        ships[s]['ship'].set_motion(inputs[s]['thrust'], inputs[s]['steer'])
        fig.update_traces(
            selector={'name': s + '-ship'},
            x = ships[s]['ship'].get_ship_data()[:,0],
            y = ships[s]['ship'].get_ship_data()[:,1])
        fig.update_traces(
            selector={'name': s + '-path'},
            x = ships[s]['ship'].get_path_data()[:,0],
            y = ships[s]['ship'].get_path_data()[:,1])

    return fig, out


# @app.callback([Output('plot', 'figure'),
#                Output({'type': 'input', 'ship': ALL, 'cntrl': ALL, 'last': ALL}, 'value')],
#              [Input('long-interval', 'n_intervals'),
#               Input('start', 'n_clicks')],
#               [State({'type': 'input', 'ship': ALL, 'cntrl': ALL, 'last': ALL}, 'value'),
#                State({'type': 'input', 'ship': ALL, 'cntrl': ALL, 'last': ALL}, 'id')])
# def update_plot(n_intervals, n_clicks, controls, ids):
#     global fig, motion_in_progress, inputs
    # # Collect changed controls in single string for easier parsing
    # changed_ids = '\n'.join([p['prop_id'] for p in dash.callback_context.triggered])

    # # If motion stops, clear inputs
    # if motion_in_progress and all([v[0].finished() for v in ships.values()]):
    #     motion_in_progress = False
    #     for key in inputs.keys():
    #         inputs[key] = {'thrust': 0, 'steer': 0, 'roll': 0}

    # # Apply inputs to sliders
    # out_vals = []
    # for i in ids:
    #     out_vals.append(inputs[i['ship']][i['cntrl']])

    # if 'start' in changed_ids:
    #     for v in ships.values():
    #         v[0].start_movement(25)
    #         motion_in_progress = True

    # # Don't output figure unless triggered by interval
    # if 'long-interval' not in changed_ids:
    #     raise PreventUpdate

    # if not all([v[0].finished() for v in ships.values()]):
    #     for k, v in ships.items():
    #         v[0].update()
    #         fig.update_shapes(selector={'name': k + '-ship'}, path=v[0].get_ship())
    #     return fig, out_vals
    # else:
    #     # Clear inputs if motion just finished
    #     if motion_in_progress:
    #         motion_in_progress = False
    #         for ship, i in inputs:
    #             for cntrl, _ in i:
    #                 inputs[ship][cntrl] = 0

    #     for k, v in ships.items():
    #         v[0].set_motion(inputs[k]['thrust'], inputs[k]['steer'])
    #         fig.update_shapes(selector={"name": k + '-path'}, path=v[0].get_path())

    return fig, out_vals

app.run_server(debug=True, port=8050, host='0.0.0.0')