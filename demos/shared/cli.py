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
        shape=getattr(args,'shape','round')
        same=getattr(args,'content','different')=='same'
        if same:
            base='product-showcase-same-square' if shape=='square' else 'product-showcase-same'
            view=base if args.signal=='clone' else base+'-sbs'
            layout=f'{base}-{args.signal}-{args.size}'
        else:
            view='product-showcase-square' if shape=='square' else 'product-showcase'
            layout=f'{view}-sbs-{args.size}'
        result+=['--shape',shape,'--panels','2','--input','none','--view',view,
                 '--layout',layout,'--content','same' if same else 'different','--data-source','demo']
        if getattr(args,'replace',False):result+=['--replace']
    if action=='logs' and args.follow:result+=['--follow']
    return result


def parser(default_shape='round',fixed_shape=False,prog='./demos/different/round/demo',same_content=False):
    p=argparse.ArgumentParser(prog=prog,description='Round or square dual-display showcase. Title 3s + effect 10s; loop 39s.')
    p.add_argument('--version',action='version',version=VERSION)
    actions=p.add_subparsers(dest='action',required=True)
    actions.add_parser('info')
    for action in ('check','start','run','status','stop','restart','logs'):
        sub=actions.add_parser(action)
        sub.add_argument('--port',type=int,choices=(1,2),required=True)
        if action in ('check','start','run'):
            sub.add_argument('--size',type=int,choices=(480,720,800),default=480)
            if same_content:
                sub.set_defaults(content='same')
                sub.add_argument('--signal',choices=('clone','sbs'),default='clone')
            if fixed_shape:sub.set_defaults(shape=default_shape)
            else:sub.add_argument('--shape',choices=('round','square'),default=default_shape)
        if action=='start':sub.add_argument('--replace',action='store_true')
        if action=='logs':sub.add_argument('--follow',action='store_true')
    return p


def main(argv=None):
    return app_main(command(parser().parse_args(argv)))


if __name__=='__main__':raise SystemExit(main())
