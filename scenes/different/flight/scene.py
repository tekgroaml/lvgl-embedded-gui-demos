"""Registration and supported display/data features for dual-round flight."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('flight','Dual-round flight instruments',('round','round'),'flight-sbs',
                      ('attitude','air-data'),
                      ('scenes.different.flight.panels:AttitudePanel','scenes.different.flight.panels:AirDataPanel'),
                      'scenes.different.flight.model:FlightDemo',native_dual480=True,layout_versions=((480,'1.1.0'),))
