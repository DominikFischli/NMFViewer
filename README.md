# NMF Viewer

The NMF Viewer is a graphical user interface meant to enable users to visualize results of an NMF computation.
It bases itself off the [automatic-spike-detection](https://automatic-spike-detection.readthedocs.io) package.

## Usage

The NMF Viewer can either be used as a stand alone application from the command line or it can be integrated into a PyQt application.

### Command Line
Clone this repository and navigate to the NMF Viewer directory.\
Run ```python app.py``` to open the NMF Window.

### PyQt Application
Install the NMF Viewer with `pip install nmfviewer` \
or clone this repository and include it with `pip install -e path/to/viewer/`

To include the NMF Window in your application, place the import statement at the top of your file: \
`from nmfViewer.NMFWindow import NMFWindow`

Use `NMFWindow` as you would use any `QWidget`.

## Results Format

The results are expected to correspond to the structure given by the available `automatic-spike-detection` package.
The viewer uses the functions provided by `spidet.save.nmf_data` to load the results.
