from dash import Dash, html, dcc, callback, clientside_callback, Output, Input, no_update
from mandelbrot import smoothed_mandelbrot
from werkzeug.middleware.profiler import ProfilerMiddleware
from utils import *
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os 

NAME = 'Dino de Raad'
APP_TITLE = f'Mandelbrot Zoom App by {NAME}'
FIGURE_TITLE = 'Mandelbrot Set'
DEFAULT_RESOLUTION = 500
DEFAULT_ITERATION_MAX = 300
ABOUT_TITLE = "About the Infinite Zoom Mandelbrot App"
ABOUT_BODY = f"""
Hello!\n
Welcome to the {APP_TITLE}! Please click and drag on the graph to zoom. Click "ABOUT" to dismiss this box. If you can no longer see the mandelbrot set, please hit the "RESET" button.\n
My name is Dino de Raad and I made this app so that you, dear reader, can zoom into the mandelbrot set, an object native to the Complex plane.\n
Please save any plots you particularly like using the "plot as png" camera button that appears when you hover over the graph.\n
The app is written in Python, and wraps the core plotting functions of plotly in Dash (which are built on Flask).\n
The mandelbrot set is generated with a custom algorithm, optimized for speed on certain types of computer architecture.\n
If you are using the web version and find the resolution to be lacking, please consider visiting the [github](https://github.com/dderaad/mandelbrot) and build the app for faster home use.\n
\n
If you'd like to give me your thoughts, send your favorite plot to me, or contribute to the project, please email me at [dideraad@gmail.com](mailto:dideraad@gmail.com)\n
\n
The application is hosted on onrender, and I thank them for the use of their site and resources.
"""
environment = {"resolution": DEFAULT_RESOLUTION,
               "iteration_max": DEFAULT_ITERATION_MAX}

# Mandelbrot Graph Stuff

def mandelbrot_graph(*args):
    if args:
        C, real_line, imag_line = generate_grid(*args)
    else:
        C, real_line, imag_line = generate_grid(resolution=environment["resolution"])
    continuous_dwell, lt_grid, iter_grid, gradient = smoothed_mandelbrot(C, environment["iteration_max"])
    Mb_color = mandelbrot_to_colorspace(continuous_dwell, 
                                        lt_grid, 
                                        iter_grid, 
                                        gradient, 
                                        environment['iteration_max'], 
                                        environment['resolution'],
                                        s=[0.1, 1])

    labels = {"x": "Re(z)",
              "y": "Im(z)"}
    

    # fig = go.Figure(go.Heatmap(z=lt_grid, 
    #                            x=real_line,
    #                            y=imag_line,
    #                            colorscale=custom_colorscale,
    #                            showscale=False,
    #                            ),
    #                     )
    fig = px.imshow(Mb_color,
                    x=real_line,
                    y=imag_line,)
    fig.update_layout(template="simple_white",
                      coloraxis_showscale=False,
                      margin=dict(l=0, r=0, t=5, b=0),
                      title={'text': FIGURE_TITLE, 'automargin': True},
                      yaxis = dict(title=f"{labels['y']}", scaleanchor = 'x'),
                      xaxis = dict(title=f"{labels['x']}"),
                      )
    
    
    return fig

fig = mandelbrot_graph()

# App stuff



app = Dash()
server = app.server
#app.wsgi_app = ProfilerMiddleware(app.wsgi_app) # Profiler


resolution_slider_marks = {**{f'{2**x}':f'{(2**x)**2} px' for x in range(8, 12, 1)}}
iteration_slider_marks = {i: f'{i}' for i in range(100, 2000+100, 100)}

plot_config = {'doubleClick': False, 
               'scrollZoom': True, 
               'displayModeBar': True, 
               'displaylogo': False,
               'toImageButtonOptions': {
                   'filename': 'mandelbrot_render',
                   'height': 2160,
                   'width': 3840,
                   'scale': 0.5
               }
               }

app.layout = [
    html.Div(children=[html.H1(APP_TITLE), 
                       html.Div([html.Button('ABOUT', id='about-button'), html.Button('RESET', id='reset-button')])
                       ], style={"display":"flex", "gap":"40%", "align-items":"flex-start"}),

    html.Div(
    [
        html.Div(
            [
                html.Div(children='Resolution'),
                dcc.Slider(min=256, max=2048, step=None, marks=resolution_slider_marks, value=DEFAULT_RESOLUTION, vertical=True, id='resolution-slider', tooltip={"placement": "bottom"})
                ], style={'gap': "10%"}
        ),
        html.Div(
            [
                html.Div(children='Iteration Max'),
                dcc.Slider(min=100, max=2000, step=None, marks=iteration_slider_marks,  value=DEFAULT_ITERATION_MAX, vertical=True, id='iteration-slider', tooltip={"placement": "bottom"})
                ], style={'gap': "10%"}
        ),
        dcc.Loading(
            children=dcc.Graph(id='mandelbrot-fig', figure=fig, style={'height': '80vh', 'width': '80vw'}, config=plot_config),
            type="cube", 
            id="loading-1", 
            overlay_style={"visibility": "visible", "filter":"blur(1px)"},
            delay_show=200,
            ),
            html.Div(
            html.Dialog(children=html.Div([html.H2(ABOUT_TITLE), 
                                        html.Span(format_html(ABOUT_BODY))
                                        ]), 
                                        title=ABOUT_TITLE, id='about-dialogue', open=False, 
                                        style={
                                            'position': 'absolute', 
                                            'top': 30, 
                                            'left': "65%", 
                                            'width': '25%', 
                                            'height': '80%', 
                                            'background': 
                                            'rgba(255, 255, 255, 0.85)', 
                                            'z-index': 9999}
                        ),
                ),
    ], style={'display': 'flex', 'flexDirection': 'row', 'height': '10vh', 'align-items':'flex-start', 'gap':'4%'}),
    
    

    html.Div(id='zoom-display', children='', style={'position': 'absolute', 'top': '95%'}),
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
    xbounds = [0, 0]
    ybounds = [0, 0]
    zoom_or_pan = False
    try:
        xbounds = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']] 
        ybounds = [relayout_data['yaxis.range[0]'], relayout_data['yaxis.range[1]']]
        zoom_or_pan = True
    except (KeyError, TypeError):
        pass

    if zoom_or_pan:
        grid_args = (xbounds, ybounds, environment['resolution'])
        zoomed_figure = mandelbrot_graph(*grid_args)

    return zoomed_figure, format_html(f'Re(z) = [{xbounds[0]:.4f}, {xbounds[1]:.4f}]\nIm(z) = [{ybounds[0]:.4f}, {ybounds[0]:.4f}]')

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


# Slider functionality
@callback(
    [],
    [Input('resolution-slider', 'value'),
     Input('iteration-slider', 'value')]
)
def update_res_and_iter(resolution, iteration):
    environment['resolution'] = resolution
    environment['iteration_max'] = iteration
    return None

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
