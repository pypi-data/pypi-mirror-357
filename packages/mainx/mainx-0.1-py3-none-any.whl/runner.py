import runpy
import os

def main():
    current_dir = os.path.dirname(__file__)
    script_path = os.path.join(current_dir, "main1.py")
    runpy.run_path(script_path, run_name="__main__")
