import glob
import subprocess

json_files = glob.glob('filmset-lighting-library/Fixtures/**/*.json', recursive=True)

for file in json_files:
    subprocess.run(['python', 'filmset-lighting-library/tests/update_db.py', file, 'Fixtures'])