""" Speedscope recorder for python.

See also: https://www.speedscope.app
"""

import argparse
import time
import json
import sys
from collections import namedtuple
import contextlib


@contextlib.contextmanager
def track(filename):
    recorder = Recorder()
    recorder.start()
    yield
    recorder.stop()
    recorder.export_to_json(filename)


Record = namedtuple("Record", ["timestamp", "typ", "filename", "line", "name"])


class Recorder:
    def __init__(self):
        self.records = []

    def get_nanos(self):
        return int(time.perf_counter() * 1e9)

    def start(self):
        self._begin_time = self.get_nanos()
        sys.setprofile(self._trace_func)

    def stop(self):
        sys.setprofile(None)
        self._end_time = self.get_nanos()

    def _trace_func(self, frame, event, arg):
        filename = frame.f_code.co_filename
        if filename == __file__:
            # Ignore this file itself
            return

        if event == "call":
            typ = "O"
        elif event == "return":
            typ = "C"
        else:
            # Ignore everything else.
            return

        timestamp = self.get_nanos()
        line = frame.f_code.co_firstlineno
        name = frame.f_code.co_name
        self.records.append(Record(timestamp, typ, filename, line, name))

    def export_to_json(self, filename):
        data = self._make_speed_scope_dict()
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def _make_speed_scope_dict(self):
        events = []
        frames = []
        frame_cache = {}

        # Strip off first and last events from entering and leaving this library.
        while self.records[0][1] == "C":
            self.records.pop(0)

        while self.records[-1][1] == "O":
            self.records.pop(-1)

        for timestamp, event, filename, line, name in self.records:
            key = (filename, line, name)
            if key not in frame_cache:
                frame_cache[key] = len(frames)
                frames.append({"name": name, "file": filename, "line": line, "col": 1})
            frame_index = frame_cache[key]
            events.append({"type": event, "at": timestamp, "frame": frame_index})

        data = {
            "$schema": "https://www.speedscope.app/file-format-schema.json",
            "profiles": [
                {
                    "type": "evented",
                    "name": "python",
                    "unit": "nanoseconds",
                    "startValue": self._begin_time,
                    "endValue": self._end_time,
                    "events": events,
                }
            ],
            "shared": {"frames": frames},
            "activeProfileIndex": 0,
            "exporter": "pyspeedscope",
            "name": "profile for python script",
        }
        return data
