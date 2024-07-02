from dash import Dash, html, dcc, callback, Output, Input, no_update
from mandelbrot import smoothed_mandelbrot
from utils import *
import plotly.express as px
import numpy as np
import os 

NAME = 'Dino de Raad'
APP_TITLE = f'Mandelbrot Zoom App by {NAME}'
FIGURE_TITLE = 'Mandelbrot Set'

# Mandelbrot Graph Stuff

def mandelbrot_graph(*args):
    if args:
        C, real_line, imag_line = generate_grid(*args)
    else:
        C, real_line, imag_line = generate_grid()
    Mb = smoothed_mandelbrot(C, 100)

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

app.layout = [
    html.Div(children=APP_TITLE),
    dcc.Loading(
        dcc.Graph(id='mandelbrot-fig', figure=fig, 
            style={'height': '90vh'}), 
        type="cube", id="loading-1", 
        overlay_style={"visibility": "visible", "filter":"blur(2px)"},
        delay_show=200,
        ),
    html.Div(id='zoom-display', children=''),
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
        
        #print("x, y:", xbounds, ybounds)

        grid_args = (xbounds, ybounds, 750)

        zoomed_figure = mandelbrot_graph(*grid_args)
    except (KeyError, TypeError):
        pass

    return zoomed_figure, f'Re(z) = {xbounds}\nIm(z) = {ybounds}'


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
