import math
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import numpy as np
import random
import datetime
from Ship import Sprinter, Galleon

from dash.dependencies import Input, Output, State, MATCH, ALL

random.seed()
app = dash.Dash(__name__)

starttime = datetime.datetime.now()

ships = {
    "A": (Sprinter([0,0]), "Green"),
    "B": (Sprinter([20, 40]), "Blue"),
    "C": (Sprinter([-20, 75]), "Cyan"),
    "D": (Galleon([-50, -80]), "Blue"),
}

inputs = dict()
input_state = dict()

fig = go.Figure(
    layout=go.Layout(
        yaxis=dict(
                scaleanchor="x",
                scaleratio=1,
                range=[-300, 300],
            ),
    ),
)

for key, value in ships.items():
    fig.add_shape(
        name=key + "-ship",
        type="path",
        path=value[0].get_ship(),
        line_color="Dark" + value[1],
        fillcolor="Light" + value[1],
    )

    fig.add_shape(
        name=key + "-path",
        type="path",
        path=value[0].get_path(),
        line_color="Dark" + value[1],
    )

    inputs[key] = {'thrust': 0, 'steer': 0, 'roll':0}
    input_state[key] = {'thrust': False, 'steer': False, 'roll': False}


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
                id={"type": "input", "ship": name, "cntrl": "thrust", "last": 0},
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
                id={"type": "input", "ship": name, "cntrl": "steer", "last": 0},
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
                        id={"type": "input", "ship": name, "cntrl": "roll", "last": 0},
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
        ]
    )

app.layout = html.Div(
    className="row",
    children=[
        html.Div(
            className="three columns",
            style={"max-height": "100vh", "overflow-y": "auto"},
            children=[create_ship_controls(k, 'Light' + v[1]) for k, v in ships.items()]
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
        dcc.Interval(
            id='long-interval',
            interval=1000,
            n_intervals=0,
        ),
    ]
)


motion_in_progress = False

@app.callback([Output('plot', 'figure'),
               Output({'type': 'input', 'ship': ALL, 'cntrl': ALL, 'last': ALL}, 'value'),
               Output({'type': 'input', 'ship': ALL, 'cntrl': ALL, 'last': ALL}, 'id')],
             [Input('long-interval', 'n_intervals'),
              Input('start', 'n_clicks')],
              [State({'type': 'input', 'ship': ALL, 'cntrl': ALL, 'last': ALL}, 'value'),
               State({'type': 'input', 'ship': ALL, 'cntrl': ALL, 'last': ALL}, 'id')])
def update_plot(n_intervals, n_clicks, controls, ids):
    global fig, motion_in_progress, inputs
    # Collect changed controls in single string for easier parsing
    changed_ids = '\n'.join([p['prop_id'] for p in dash.callback_context.triggered])

    # Apply any changed inputs
    for idx, (c, i) in enumerate(zip(controls, ids)):
        if i['last'] != c:
            inputs[i['ship']][i['cntrl']] = c
        ids[idx]['last'] = c

    # If motion stops, clear inputs
    if motion_in_progress and all([v[0].finished() for v in ships.values()]):
        motion_in_progress = False
        for key in inputs.keys():
            inputs[key] = {'thrust': 0, 'steer': 0, 'roll': 0}

    # Apply inputs to sliders
    out_vals = []
    for i in ids:
        out_vals.append(inputs[i['ship']][i['cntrl']])
    out_ids = ids

    if 'start' in changed_ids:
        for v in ships.values():
            v[0].start_movement(25)
            motion_in_progress = True

    # Don't output figure unless triggered by interval
    if 'long-interval' not in changed_ids:
        raise PreventUpdate

    if not all([v[0].finished() for v in ships.values()]):
        for k, v in ships.items():
            v[0].update()
            fig.update_shapes(selector={'name': k + '-ship'}, path=v[0].get_ship())
        return fig, out_vals, out_ids
    else:
        # Clear inputs if motion just finished
        if motion_in_progress:
            motion_in_progress = False
            for ship, i in inputs:
                for cntrl, _ in i:
                    inputs[ship][cntrl] = 0

        for k, v in ships.items():
            v[0].set_motion(inputs[k]['thrust'], inputs[k]['steer'])
            fig.update_shapes(selector={"name": k + '-path'}, path=v[0].get_path())

    return fig, out_vals, out_ids

app.run_server(debug=True, port=8050, host='0.0.0.0')