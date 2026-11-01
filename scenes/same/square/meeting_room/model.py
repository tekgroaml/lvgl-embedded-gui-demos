"""Simulated room booking phases; no real calendar, people or meeting data."""
from dataclasses import dataclass
from common.simulation import validate_elapsed


@dataclass
class RoomData:
    elapsed_s: float
    status: str
    label: str
    seconds_remaining: float
    phase_progress: float
    status_index: int
    stale: bool = False
    simulated: bool = True


PHASES=(('AVAILABLE','Ready for your next idea.'),('STARTING SOON','Demo team planning'),('IN SESSION','Demo design workshop'))


def sample(elapsed):
    validate_elapsed(elapsed)
    i=int(elapsed//12)%3;within=elapsed%12
    return RoomData(elapsed,*PHASES[i],12-within,within/12,i)


class RoomDemo:
    path=None
    def read(self,elapsed):return sample(elapsed)
