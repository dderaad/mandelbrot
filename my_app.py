from dash import Dash, html, dcc, callback, clientside_callback, Output, Input, no_update
from mandelbrot import smoothed_mandelbrot
from werkzeug.middleware.profiler import ProfilerMiddleware
from utils import *
import plotly.express as px
import numpy as np
import os 

NAME = 'Dino de Raad'
APP_TITLE = f'Mandelbrot Zoom App by {NAME}'
FIGURE_TITLE = 'Mandelbrot Set'
DEFAULT_RESOLUTION = 100
DEFAULT_ITERATION_MAX = 500
ABOUT_TITLE = "About the Infinite Zoom Mandelbrot App"
ABOUT_BODY = f"""
Hello!\n
Welcome to the {APP_TITLE}! Please click and drag on the graph to zoom. Click "ABOUT" to dismiss this box. If you can no longer see the mandelbrot set, please hit the "RESET" button.\n
My name is Dino de Raad and I made this app so that you, dear reader, can zoom into the mandelbrot set, an object native to the Complex plane.\n
The app is written in Python, and wraps the core plotting functions of plotly in Dash (which are built on flask).\n
The mandelbrot set is generated with a custom algorithm, optimized for speed on certain types of computer architecture.\n
If you are using the web version and find the resolution to be lacking, please consider visiting the [github](https://github.com/dderaad/mandelbrot) and build the app for faster home use.\n
\n
If you'd like to give me your thoughts or contibute to the project, please email me at [dideraad@gmail.com](mailto:dideraad@gmail.com)\n
\n
The application is hosted on onrender, and I thank them for the use of their site and resources.
"""

# Mandelbrot Graph Stuff

def mandelbrot_graph(*args):
    if args:
        C, real_line, imag_line = generate_grid(*args)
    else:
        C, real_line, imag_line = generate_grid(resolution=DEFAULT_RESOLUTION)
    Mb = smoothed_mandelbrot(C, DEFAULT_ITERATION_MAX)

    labels = {"x": "Re(z)",
              "y": "Im(z)"}
    
    A = np.abs(Mb).astype(np.float64)

    fig = px.imshow(A, 
                    labels = labels,
                    x = real_line,
                    y = imag_line
                    )
    fig.update_layout(template="simple_white", 
                    title=FIGURE_TITLE, 
                    coloraxis_showscale=False)
    
    return fig

fig = mandelbrot_graph()

# App stuff



app = Dash()
server = app.server
#app.wsgi_app = ProfilerMiddleware(app.wsgi_app) # Profiler

app.layout = [
    html.Div(children=APP_TITLE),
    html.Div(
    [dcc.Loading(
        children=dcc.Graph(id='mandelbrot-fig', figure=fig, style={'height': '90vh'}),
        type="cube", 
        id="loading-1", 
        overlay_style={"visibility": "visible", "filter":"blur(1px)"},
        delay_show=200,
        ),
    html.Div(
        html.Dialog(children=html.Div([html.H1(ABOUT_TITLE), 
                                       html.Span(format_html(ABOUT_BODY))
                                       ]), 
                                       title=ABOUT_TITLE, id='about-dialogue', open=True, 
                                       style={
                                           'position': 'absolute', 
                                           'top': 50, 
                                           'left': 1000, 
                                           'width': '25%', 
                                           'height': '80%', 
                                           'background': 
                                           'rgba(255, 255, 255, 0.85)', 
                                           'z-index': 9999}
                    ),
            ),
    ]),
    html.Div(id='zoom-display', children=''),
    html.Button('RESET', id='reset-button'),
    html.Button('ABOUT', id='about-button'),
]

@callback(
    [Output('mandelbrot-fig', 'figure'),
     Output('zoom-display', 'children')],
    [Input('mandelbrot-fig', 'relayoutData'),
     Input('mandelbrot-fig', 'figure')]
)
def zoom_event(relayout_data, figure):
    """
    When a zoom occurs on the mandelbrot set, the set will 
    be re-generated for the subset of the plane that is zoomed
    in on.
    Similar to https://stackoverflow.com/questions/56611105/how-to-get-zoom-level-in-time-series-data-as-callback-input-in-dash/64891612#64891612
    """

    zoomed_figure = figure
    xbounds = 0
    ybounds = 0
    try:
        xbounds = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']] 
        ybounds = [relayout_data['yaxis.range[0]'], relayout_data['yaxis.range[1]']]

        grid_args = (xbounds, ybounds, DEFAULT_RESOLUTION)

        zoomed_figure = mandelbrot_graph(*grid_args)
    except (KeyError, TypeError):
        pass

    return zoomed_figure, f'Re(z) = {xbounds}\nIm(z) = {ybounds}'

# Makes the ABOUT button summon/dismiss the dialogue
@callback(
    [Output('about-dialogue', 'open')],
    [Input('about-dialogue', 'open'),
     Input('about-button', 'n_clicks')],
     prevent_initial_call=True,
)
def summon_dismiss_dialogue(state, _):
    return [not state]
    
# Makes the RESET button reset the state
@callback(
    [Output('mandelbrot-fig', 'figure', allow_duplicate=True),
     Output('zoom-display', 'children', allow_duplicate=True),
     Output('mandelbrot-fig', 'relayoutData', allow_duplicate=True)],
    [Input('reset-button', 'n_clicks')],
    prevent_initial_call = True,
)
def reset_graph(_):
    return mandelbrot_graph(), 'Reset Successful!', {}


if __name__ == "__main__":
    if os.name == 'nt':
        app.run(debug=True)
    else:
        try:
            print(f'Running happily on {os.uname()}!')  
        except Exception as E:
            print(f'The OS {os.name} is unsupported.\n{E}')
        app.run(host='0.0.0.0', 
                    port=int(os.environ.get('PORT', 4000))
                )
