"""Compatibility imports; each scene now owns its model/panels/registration."""
from common.simulation import smooth
from scenes.flight.model import FlightData,FlightDemo
from scenes.industrial.model import ProcessData,ProcessDemo,process_demand
from scenes.registry import make_scene
