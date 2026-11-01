"""Dual-round car scene registration, with the observed dual480 native rate."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('automotive','Dual-round automotive instruments',('round','round'),'automotive-sbs',
                      ('drive-speed','engine-status'),
                      ('scenes.automotive.panels:DrivingPanel','scenes.automotive.panels:EnginePanel'),
                      'scenes.automotive.model:AutomotiveDemo',native_dual480=True)
