"""Sample offers and smooth price-card countdown; no pricing backend."""
from dataclasses import dataclass
from common.simulation import validate_elapsed


@dataclass
class StoreData:
    elapsed_s: float
    product: str
    tagline: str
    price: str
    category: str
    offer_index: int
    offer_progress: float
    stale: bool = False
    simulated: bool = True


OFFERS=(('ICED LATTE','Your afternoon refresh.','$4.50','CAFE SPECIAL'),
        ('FRESH LEMONADE','A little sunshine in a glass.','$3.90','SUMMER PICK'),
        ('MATCHA CLOUD','Freshly whisked. Smooth finish.','$5.20',"TODAY'S FAVORITE"))


def sample(elapsed):
    validate_elapsed(elapsed)
    i=int(elapsed//6)%len(OFFERS)
    return StoreData(elapsed,*OFFERS[i],i,(elapsed%6)/6)


class StoreDemo:
    path=None
    def read(self,elapsed):return sample(elapsed)
