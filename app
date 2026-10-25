#!/bin/sh
set -eu
export PYTHONPATH="$(dirname -- "$0")${PYTHONPATH:+:$PYTHONPATH}"
if [ "$(uname -s)" = Linux ]; then
    exec /usr/bin/python3 -m scene_app.cli "$@"
fi
exec python3 -m scene_app.cli "$@"
