"""Smart-home scene capabilities, separate from product-showcase orchestration."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('smart-home','Home environment and energy',('square','square'),'smart-home-sbs',
                      ('home-climate','home-energy'),
                      ('scenes.smart_home.panels:ClimatePanel','scenes.smart_home.panels:EnergyPanel'),
                      'scenes.smart_home.model:HomeDemo',native_dual480=True)
