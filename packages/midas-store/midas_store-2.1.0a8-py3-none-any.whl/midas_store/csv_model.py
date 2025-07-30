import csv
import json
import logging
import multiprocessing as mp
import os
import queue
import threading
import traceback
from multiprocessing.context import SpawnProcess
from typing import Any, Callable, Union, cast
from uuid import uuid4

import numpy as np
from midas.util.dict_util import convert_val
from midas.util.runtime_config import RuntimeConfig
from mosaik.exceptions import SimulationError
from typing_extensions import TypeAlias

LOG = logging.getLogger(__name__)

AnyQueue: TypeAlias = Union[mp.Queue, queue.Queue]


class CSVModel:
    def __init__(
        self,
        filename: str,
        *,
        path: str | None = None,
        unique_filename: bool = False,
        keep_old_files: bool = False,
        timeout: int = 300,
        in_process: bool = False,
        file_suffix: str = "csv",
    ) -> None:
        if path is None:
            path = RuntimeConfig().paths["output_path"]
            if path is None:
                path = ""
        os.makedirs(path, exist_ok=True)

        self.filename = os.path.abspath(os.path.join(path, filename))

        if self.filename and unique_filename:
            fp, suf = self.filename.rsplit(".", 1)
            self.filename = f"{fp}-{str(uuid4())}.{suf}"
        elif not self.filename:
            self.filename = f"midas-store-results-{str(uuid4())}.{file_suffix}"

        if keep_old_files:
            LOG.debug(
                "Keep_old_files is set to True. Attempting to find a unique "
                "filename for the database."
            )
            incr = 2
            new_filename = self.filename
            while os.path.exists(new_filename):
                fp, suf = self.filename.rsplit(".", 1)
                new_filename = f"{fp}_{incr:03d}.{suf}"
                incr += 1
            self.filename = new_filename
        elif os.path.exists(self.filename):
            os.rename(self.filename, f"{self.filename}.old")

        LOG.info("Saving results to database at '%s'.", self.filename)
        self._columns: list[str] = []
        self._data: dict[str, str | bool | int | float | None] = {}
        self._ctr: int = 0
        self._timeout: int = timeout

        self._in_process = in_process
        self._ctx = mp.get_context("spawn")
        self._io_proc: SpawnProcess | threading.Thread | None = None
        self._queue: AnyQueue
        self._result: AnyQueue
        if self._in_process:
            self._queue = queue.Queue()
            self._result = queue.Queue()
        else:
            self._queue = self._ctx.Queue()
            self._result = self._ctx.Queue()

    def to_memory(self, sid: str, eid: str, attr: str, val: Any) -> None:
        key = build_column_key(sid, eid, attr)
        self._data[key] = serialize(val)

    def step(self):
        if self._io_proc is None:
            self._columns = list(self._data)
            self._start_writer(run_writer)

        if not self._result.empty():
            msg = "Writer process terminated early."
            try:
                msg += self._result.get()
            except Exception:
                msg += "Can't continue from here."

            raise SimulationError(msg)

        self._queue.put(self._data)

    def _start_writer(self, run_fnc: Callable) -> None:
        if self._in_process:
            self._io_proc = threading.Thread(
                target=run_fnc,
                args=(
                    self.filename,
                    self._columns,
                    self._queue,
                    self._result,
                    self._timeout,
                ),
            )
            LOG.debug("Starting file writer as thread ...")
        else:
            self._io_proc = self._ctx.Process(
                target=run_fnc,
                args=(
                    self.filename,
                    self._columns,
                    self._queue,
                    self._result,
                    self._timeout,
                ),
            )
            LOG.debug("Starting file writer as separate process ...")

        self._io_proc.start()

    def finalize(self):
        LOG.info("Shutting down the writer process ...")
        if self._io_proc is None:
            LOG.info("Writer is already None (likely was never initialized).")
        else:
            try:
                self._attempt_last_data()
                self._queue.put(-1)
            except ValueError:
                LOG.debug("Queue was already closed.")

            LOG.debug("Waiting for writer to finish ...")
            self._io_proc.join()
            LOG.debug("Writer finished. Check if it left a message ...")

            try:
                msg = self._result.get(timeout=1)
            except queue.Empty:
                LOG.error("Writer finished without message.")
            else:
                log_msg = f"Writer finished with message {msg}"
                if msg.startswith("Error"):
                    LOG.error(log_msg)
                else:
                    LOG.info(log_msg)

        if not self._in_process:
            cast(mp.Queue, self._result).close()
            cast(mp.Queue, self._queue).close()

    def _attempt_last_data(self):
        pass


def run_writer(
    filename: str,
    fields: list[str],
    lines: AnyQueue,
    result: AnyQueue,
    timeout=300,
):
    res_msg = "Finished successfully."
    to_ctr = timeout
    try:
        with open(filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()

            while True:
                try:
                    item = lines.get(block=True, timeout=1)
                except queue.Empty:
                    to_ctr -= 1
                    if to_ctr <= 0:
                        res_msg = (
                            f"Writer received no item in the last {timeout} "
                            "seconds."
                        )
                        break
                    continue
                except ValueError:
                    res_msg = "Queue was closed. Terminating!"
                    break

                if isinstance(item, int):
                    LOG.info("Received -1. Terminating!")
                    break

                writer.writerow(item)
                to_ctr = timeout

    except Exception:
        res_msg = f"Error writing csv: {traceback.format_exc()}"
    except KeyboardInterrupt:
        res_msg = "Interrupted by user!"
    try:
        result.put(res_msg)
    except ValueError:
        LOG.info("Result queue was already closed.")


def build_column_key(sid, eid, attr) -> str:
    return f"{sid}.{eid}.{attr}"


def serialize(val):
    new_val = convert_val(val)

    if new_val == "MISSING_VALUE":
        if isinstance(val, (list, dict, np.ndarray)):
            return json.dumps(val)

    return new_val
