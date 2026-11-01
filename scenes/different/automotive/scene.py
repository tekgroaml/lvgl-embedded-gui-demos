"""Dual-round car scene registration, with the observed dual480 native rate."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('automotive','Dual-round automotive instruments',('round','round'),'automotive-sbs',
                      ('drive-speed','engine-status'),
                      ('scenes.different.automotive.panels:DrivingPanel','scenes.different.automotive.panels:EnginePanel'),
                      'scenes.different.automotive.model:AutomotiveDemo',native_dual480=True)
