# User Guide

Generic MediaMan command format:

        mm [<service>] <command> [<file(s)>]

A command without a service specified is called a "global" command.

        mm <command> [<file(s)>]

A command with a service specified is called a "service" command.

        mm <service> <command> [<file(s)>]

## Service Types
1. `local` Filesystem
    a. Local / USB device
    b. Network (TBD)
2. `drive` - Google Drive
3. `glacier` - Amazon Glacier (TBD)
4. `dropbox` - Dropbox (TBD)

## Commands

## Global or Service
- (blank)
- list
- list <file(s)>
- has <file(s)>
- get <file(s)>
- put <file(s)>
- stat | status (TBD)
- use | usage (TBD)

## Global only
- sync (TBD)
