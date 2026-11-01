"""Small declarative scene contract; independent projects require no framework."""
from dataclasses import dataclass
from importlib import import_module


@dataclass(frozen=True)
class SceneDefinition:
    id: str
    title: str
    shapes: tuple
    prefix: str
    panel_ids: tuple
    panel_factories: tuple
    demo_factory: str
    live_factory: str = None
    native_dual480: bool = False
    sizes: tuple = (480,720,800)
    layout_versions: tuple = ()
    package: str = None

    @property
    def owner_package(self):
        return self.package or 'scenes.'+self.id.replace('-', '_')

    @property
    def sources(self):
        return ('demo','live') if self.live_factory else ('demo',)

    def layout_path(self,size):
        return f"{self.owner_package.replace('.', '/')}/layouts/{self.prefix}-{size}.json"

    def layout_version(self,size):
        return dict(self.layout_versions).get(size,'1.0.0')

    def rates(self,size):
        return [60,62.825226] if self.native_dual480 and size==480 else [60]

    def create_panels(self):
        return tuple(construct(name) for name in self.panel_factories)

    def create_source(self,data_source='demo',path=None):
        if data_source=='demo':return construct(self.demo_factory)
        if data_source=='live' and self.live_factory:return construct(self.live_factory,path)
        raise ValueError(f'{self.id} does not support {data_source}')


def construct(reference,*args):
    module,name=reference.split(':',1)
    return getattr(import_module(module),name)(*args)
