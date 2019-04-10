#!/bin/bash

SAVED_PWD=$PWD

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

cd "$DIR"

. venv/bin/activate
SAVED_PWD=$SAVED_PWD python3.7 -Bum mediaman.interfaces.cli "$@"
