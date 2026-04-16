import os
import csv
import numpy as np

def _ensure_line_format(data: dict) -> dict:
    return {
        key: {'line': value} if not isinstance(value, dict) else value
        for key, value in data.items()
    }


def extract_axes(data: dict) -> dict:
    data = _ensure_line_format(data)
    sides = ['L', 'R']
    segs  = ['TIB', 'HDF', 'FOF', 'HLX', 'WLF']
    nums  = ['0', '1', '2', '3']
    keys  = [f"{s}{seg}{n}" for s in sides for seg in segs for n in nums]
    return {k: data[k] for k in keys if k in data}


def extract_angles(data: dict) -> dict:
    data = _ensure_line_format(data)
    sides  = ['Left', 'Right']
    joints = ['HFTB', 'FFHF', 'HXFF', 'FFTB', 'WFTB']
    axes   = ['x', 'y', 'z']
    keys   = [f"{s}{j}A_{a}" for s in sides for j in joints for a in axes]
    return {k: data[k] for k in keys if k in data}


def _export(data: dict, subject: str, label: str, extractor):

    out_dir = os.path.join(os.getcwd(), 'processed')
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{subject}_OFM_{label}.csv")

    data = extractor(data)

    headers = ['frame']
    columns = []

    for key, entry in data.items():
        arr = np.asarray(entry['line'])
        if arr.ndim == 1:
            headers.append(key)
            columns.append(arr)
        elif arr.ndim == 2:
            for j in range(arr.shape[1]):
                headers.append(f"{key}_{j}")
                columns.append(arr[:, j])
        else:
            raise ValueError(f"{key}: unsupported shape {arr.shape}")

    table = np.column_stack([np.arange(columns[0].shape[0]), *columns])

    with open(out_file, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(table.tolist())

    print(f"{label.capitalize()} exported to: {out_file}")


def export_angles(data: dict, subject: str):
    _export(data, subject, 'angles', extract_angles)

def export_axes(data: dict, subject: str):
    _export(data, subject, 'axes', extract_axes)