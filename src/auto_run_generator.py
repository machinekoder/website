import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time

class RunOnChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            print(f"Change detected in {event.src_path}, running generator.py...")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            subprocess.run([sys.executable, os.path.join(script_dir, "generator.py")])

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    watch_dirs = [os.path.join(script_dir, "..", "static"), os.path.join(script_dir, "..", "templates")]
    event_handler = RunOnChangeHandler()
    observer = Observer()
    for path in watch_dirs:
        observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("Watching 'static' and 'templates' for file changes. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
