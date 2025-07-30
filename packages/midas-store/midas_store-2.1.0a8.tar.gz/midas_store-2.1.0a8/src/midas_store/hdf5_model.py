import json
import logging
import queue
import traceback
from typing import Any

import numpy as np
import pandas as pd
from mosaik.exceptions import SimulationError
from typing_extensions import override

from midas_store.csv_model import AnyQueue, CSVModel, serialize

LOG = logging.getLogger(__name__)


class HDF5Model(CSVModel):
    def __init__(
        self,
        filename: str,
        *,
        path: str | None = None,
        unique_filename: bool = False,
        keep_old_files: bool = False,
        buffer_size: int = 1000,
        in_process: bool = False,
    ):
        super().__init__(
            filename,
            path=path,
            unique_filename=unique_filename,
            keep_old_files=keep_old_files,
            in_process=in_process,
            file_suffix="hdf5",
        )

        self._buffer_size = buffer_size
        self._buffer_ctr = 0
        self._columns_dict: dict[str, list[str]] = {}
        self._data_hdf: dict[
            str, dict[str, list[str | bool | int | float | None]]
        ] = {}

    @override
    def to_memory(self, sid: str, eid: str, attr: str, val: Any) -> None:
        sid = sid.replace("-", "__")
        key = f"{eid}___{attr}".replace("-", "__")
        if self._columns_dict:
            if sid not in self._columns_dict:
                msg = f"Invalid sid detected: {sid}"
                self._buffer_ctr = 0
                raise ValueError(msg)

            if key not in self._columns_dict[sid]:
                msg = f"Invalid key detected for sid {sid}: {key}"
                self._buffer_ctr = 0
                raise ValueError(msg)

        self._data_hdf.setdefault(sid, {})
        self._data_hdf[sid].setdefault(key, [])

        if isinstance(val, (list, dict, np.ndarray)):
            val = json.dumps(val)
        elif isinstance(val, pd.DataFrame):
            val = val.to_json()
        else:
            val = serialize(val)
        self._data_hdf[sid][key].append(val)

    def step(self):
        if self._io_proc is None:
            self._start_writer(run_writer)

            for sid, keys in self._data_hdf.items():
                self._columns_dict[sid] = []
                for k in keys:
                    self._columns_dict[sid].append(k)

        if not self._result.empty():
            msg = "Writer process terminated early. Can't continue from here."
            raise SimulationError(msg)

        self._buffer_ctr += 1

        if self._buffer_ctr >= self._buffer_size:
            dfs = {sid: pd.DataFrame(d) for sid, d in self._data_hdf.items()}
            self._queue.put(dfs)
            self._data_hdf = {}
            self._buffer_ctr = 0

    def _attempt_last_data(self):
        if self._buffer_ctr > 0:
            dfs = {sid: pd.DataFrame(d) for sid, d in self._data_hdf.items()}
            self._queue.put(dfs)


def run_writer(
    filename: str,
    fields: list[str],
    lines: AnyQueue,
    result: AnyQueue,
    timeout=300,
):
    res_msg = "Finished successfully."
    to_ctr = timeout
    append = False
    saved_rows = 0
    new_rows = 0

    try:
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

            for sid, data in item.items():
                new_rows = data.shape[0]
                data.index += saved_rows
                data.to_hdf(filename, key=sid, format="table", append=append)

            saved_rows += new_rows
            append = True
            to_ctr = timeout
    except Exception:
        res_msg = f"Error writing hdf5: {traceback.format_exc()}"
    except KeyboardInterrupt:
        res_msg = "Interrupted by user!"

    try:
        result.put(res_msg)
    except ValueError:
        LOG.info("Result queue was already closed.")
