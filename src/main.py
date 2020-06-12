import math
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import numpy as np
import random
import datetime
from Ship import Sprinter

from dash.dependencies import Input, Output

random.seed()
app = dash.Dash(__name__)

starttime = datetime.datetime.now()

s = Sprinter()
    

fig = go.Figure(
    layout=go.Layout(
        yaxis=dict(
            scaleanchor="x",
            scaleratio=1,
            range=[-50, 50]
        ),
        shapes=[
            dict(
                type="path",
                path=s.get_path(),
                fillcolor="LightGreen",
                line_color="DarkGreen",
            )
        ]
    ),
)
# fig.update_yaxes(range=[-10, 10])
# fig.update_layout(
#     yaxis = dict(
#         scaleanchor = "x",
#         scaleratio = 1,
#     ),
#     shapes=[
#         dict(
#             type="path",
#             path=get_ship_svg(135, np.array([[12.4], [-6]]), 5, 2),
#             fillcolor="LightGreen",
#             line_color="DarkGreen",
#         )
#     ]
# )

app.layout = html.Div(children=[
    dcc.Graph(
        id='Test',
        figure=fig,
        animate=False,
        animation_options = dict(
            frame={"redraw": True},
        )
    ),
    dcc.Interval(
        id='interval',
        interval=100,
        n_intervals=0,
    )
])

@app.callback(Output('Test', 'figure'),
             [Input('interval', 'n_intervals')])
def update_plot(n):
    if n == 1:
        s.set_motion(0.9, 0.5)
    elif n == 20:
        s.start_movement(20)
    elif n > 20:
        s.update()
    
    f = go.Figure(
        layout=go.Layout(
            yaxis=dict(
                scaleanchor="x",
                scaleratio=1,
                range=[-50, 50]
            ),
            shapes=[
                dict(
                    type="path",
                    path=s.get_path(),
                    fillcolor="LightGreen",
                    line_color="DarkGreen",
                )
            ]
        ),
    )
    return f

app.run_server()
# def rot_vector(v, theta):
#     rot_mat = np.matrix([[math.cos(theta), math.sin(theta)],
#                          [-math.sin(theta), math.cos(theta)]])
#     return rot_mat * v

# def transform_path(path, theta, d):
#     rot_mat = np.matrix([[math.cos(theta), math.sin(theta)],
#                          [-math.sin(theta), math.cos(theta)]])
#     verts = [(rot_mat * v.reshape(2,1)).getA1() for v in path.vertices] 
#     codes = path.codes
#     return mpath.Path(verts, codes)





# # s1 = Galleon()
# s2 = Sprinter(np.array([[50.0], [75.0]]))
# s2.start_movement(1.0, 1.0, 10)

# def init():
#     ax.set_xlim(-50, 50)
#     ax.set_ylim(-50, 50)
#     patch = ax.add_patch(s2.patch)
#     return []

# def update(frame):
#     path = transform_path(s2.patch.get_path(), frame * 0.2, 0)
#     patch = mpatches.PathPatch(path, facecolor='g', alpha=0.75)
#     return ax.add_patch(patch),

# ani = FuncAnimation(fig, update, init_func=init, frames=20, interval=20, blit=True)
# # for _ in range(20):
# #     s2.step_movement()

# # ax.add_patch(s2.patch)
# # # # s1.draw(ax, 'b')
# # # s2.draw(ax, 'g')
# ax.axis('equal')
# plt.show()