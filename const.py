import os
import pathlib

project_root = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
data_dir = project_root / 'data'
lib_dir = project_root / 'libs'
model_dir = project_root / 'models'
log_dir = project_root / 'logs'
app_dir = project_root / 'app'