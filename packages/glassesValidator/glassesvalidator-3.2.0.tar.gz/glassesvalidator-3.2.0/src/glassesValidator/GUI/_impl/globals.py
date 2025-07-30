﻿import pathlib
import sys
import threading

from glassesTools import platform

from ... import __version__
version           = __version__
pypi_page         = "https://pypi.org/project/glassesValidator/"
github_page       = "https://github.com/dcnieho/glassesValidator"
developer_page    = "https://scholar.google.se/citations?user=uRUYoVgAAAAJ&hl=en"
paper_page        = "https://doi.org/10.3758/s13428-023-02105-5"
reference         = r"Niehorster, D.C., Hessels, R.S., Benjamins, J.S., Nyström, M. & Hooge, I.T.C. (2023). GlassesValidator: Data quality tool for eye tracking glasses. Behavior Research Methods. doi: 10.3758/s13428-023-02105-5"
reference_bibtex  = r"""@article{niehorster2023glassesValidator,
    Author = {Niehorster, Diederick C. and Hessels, Roy S. and Benjamins, Jeroen S. and Nystr{\"o}m, Marcus and Hooge, Ignace T. C.},
    Journal = {Behavior Research Methods},
    Number = {},
    Pages = {},
    Title = {GlassesValidator: A data quality tool for eye tracking glasses},
    Year = {2023},
    doi = {10.3758/s13428-023-02105-5}
}
"""


from .structs import CounterContext, JobDescription, Recording, Settings
from .gui import MainGUI

frozen = getattr(sys, "frozen", False)
match platform.os:
    case platform.Os.Windows:
        data_path = "AppData/Roaming/glassesValidator"
    case platform.Os.Linux:
        data_path = ".config/glassesValidator"
    case platform.Os.MacOS:
        data_path = "Library/Application Support/glassesValidator"

home = pathlib.Path.home()
data_path = home / data_path
data_path.mkdir(parents=True, exist_ok=True)

# Variables
popup_stack = []
project_path: pathlib.Path = None
gui: MainGUI = None
settings: Settings = None
rec_id: CounterContext = CounterContext()
recordings: dict[int, Recording] = None
recording_lock = threading.Lock()
selected_recordings: dict[int, bool] = None
jobs: dict[int, JobDescription] = None
coding_job_queue: dict[int, JobDescription] = None

def cleanup():
    global popup_stack, project_path, gui, settings, rec_id, recordings, selected_recordings, jobs, coding_job_queue
    popup_stack = []
    project_path = None
    gui = None
    settings = None
    rec_id = CounterContext()
    recordings = None
    selected_recordings = None
    jobs = None
    coding_job_queue = None