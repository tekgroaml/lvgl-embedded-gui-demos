"""The original mixed-shape scene retains its original live JSON contract."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('automotive-industrial','Mixed automotive and industrial instruments',
                      ('round','square'),'automotive-industrial-sbs',('automotive','industrial'),
                      ('scenes.automotive_industrial.automotive_panel:AutomotiveGauge',
                       'scenes.automotive_industrial.industrial_panel:IndustrialPanel'),
                      'scenes.automotive_industrial.model:TelemetrySource',live_factory='common.telemetry:JsonTelemetrySource')
