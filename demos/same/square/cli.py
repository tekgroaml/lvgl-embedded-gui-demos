"""Square-only same-content script using the common standard lifecycle."""
from demos.shared.cli import parser,command
from scene_app.cli import main as app_main


def main(argv=None):
    p=parser(default_shape='square',fixed_shape=True,prog='./demos/same/square/demo',same_content=True)
    p.description='Square same-content: retail, meeting room, parcel pickup. Intro3s/effect10s; loop39s.'
    return app_main(command(p.parse_args(argv)))


if __name__=='__main__':raise SystemExit(main())
