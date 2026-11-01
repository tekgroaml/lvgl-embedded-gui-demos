"""Canonical round different-content entrypoint; common parsing is shared."""
from demos.shared.cli import parser,command
from scene_app.cli import main as app_main


def main(argv=None):
    return app_main(command(parser(prog='./demos/different/round/demo').parse_args(argv)))


if __name__=='__main__':raise SystemExit(main())
