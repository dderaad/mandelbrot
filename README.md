# mandelbrot

A live, web-based demonstration of the Mandelbrot set, with infinite zoom.

To build the app yourself, install python 3.11.9 (preferably in a virtual environment)

## On Windows:
Pull Master

Run 
```
pip install -r requirements_windows.txt
python my_app.py
```

## On Unix:
Pull Master

Run 
```
pip install -r requirements_unix.txt
gunicorn my_app:server
```

In holdovers:
A visualization of the set, with several algorithms. Includes algorithms for computation of the Julia Set.
