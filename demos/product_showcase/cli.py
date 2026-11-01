"""Convenient product-video wrapper around the project's standard ./app API."""
import argparse
from scene_app.cli import main as app_main
from scene_app import VERSION


def command(args):
    action=args.action
    result=[action]
    if action=='info':
        return ['info','--json']
    result+=['--port',str(args.port)]
    if action in ('check','start','run'):
        result+=['--shape','round','--panels','2','--input','none','--view','product-showcase',
                 '--layout',f'product-showcase-sbs-{args.size}','--content','different','--data-source','demo']
        if getattr(args,'replace',False):result+=['--replace']
    if action=='logs' and args.follow:result+=['--follow']
    return result


def parser():
    p=argparse.ArgumentParser(prog='./demos/product_showcase/demo',description='Product showcase: flight, car/motorcycle, PC case. Title 3s + effect 10s; loop 39s.')
    p.add_argument('--version',action='version',version=VERSION)
    actions=p.add_subparsers(dest='action',required=True)
    actions.add_parser('info')
    for action in ('check','start','run','status','stop','restart','logs'):
        sub=actions.add_parser(action)
        sub.add_argument('--port',type=int,choices=(1,2),required=True)
        if action in ('check','start','run'):sub.add_argument('--size',type=int,choices=(480,720,800),default=480)
        if action=='start':sub.add_argument('--replace',action='store_true')
        if action=='logs':sub.add_argument('--follow',action='store_true')
    return p


def main(argv=None):
    return app_main(command(parser().parse_args(argv)))


if __name__=='__main__':raise SystemExit(main())
