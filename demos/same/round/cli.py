"""Same-content39s showcase using the project's standard app lifecycle."""
from demos.shared.cli import parser,command
from scene_app.cli import main as app_main


def main(argv=None):
    p=parser(fixed_shape=True,prog='./demos/same/round/demo',same_content=True)
    p.description='Same-content music, RGB lighting and clock. Intro3s + effect10s; loop39s. No sound.'
    return app_main(command(p.parse_args(argv)))


if __name__=='__main__':raise SystemExit(main())
