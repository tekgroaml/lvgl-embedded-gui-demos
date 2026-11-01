"""Square-first convenience command; standard lifecycle stays in scene_app."""
from demos.product_showcase.cli import parser,command
from scene_app.cli import main as app_main


def main(argv=None):
    p=parser(default_shape='square',fixed_shape=True,prog='./demos/square_showcase/demo')
    p.description='Dual-square smart-home, PC-case and industrial showcase; 39s loop.'
    return app_main(command(p.parse_args(argv)))


if __name__=='__main__':raise SystemExit(main())
