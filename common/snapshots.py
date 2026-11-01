"""Read one bounded regular JSON snapshot without blocking on pipes/devices."""
import json
import os
import stat


def read_snapshot(path,limit=65536):
    descriptor=os.open(path,os.O_RDONLY|os.O_NONBLOCK)
    with os.fdopen(descriptor,'rb') as stream:
        info=os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):raise ValueError('Snapshot must be a regular file')
        raw=stream.read(limit+1)
    if len(raw)>limit:raise ValueError('Snapshot exceeds the size limit')
    value=json.loads(raw)
    if not isinstance(value,dict):raise ValueError('Expected a snapshot object')
    return value,info.st_mtime
