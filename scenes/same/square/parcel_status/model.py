"""Repeatable simulated shipment progress; no actual parcels or customer data."""
from dataclasses import dataclass
from common.simulation import validate_elapsed


@dataclass
class ParcelData:
    elapsed_s: float
    status: str
    stage_index: int
    stage_progress: float
    order_label: str = 'DEMO-042'
    pickup_code: str = 'A-042'
    stale: bool = False
    simulated: bool = True


STAGES=('PACKED','ON THE WAY','READY TO COLLECT')


def sample(elapsed):
    validate_elapsed(elapsed)
    return ParcelData(elapsed,STAGES[int(elapsed//8)%3],int(elapsed//8)%3,(elapsed%8)/8)


class ParcelDemo:
    path=None
    def read(self,elapsed):return sample(elapsed)
