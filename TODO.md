# To-Do List

## Features
- Commands without service specified

- Aliases for services (db = dropbox, ext = local w/ specific filepath, ...)
    - JSON file for service listing

- Commands:
    - sync: Synchronize services with each other
    - stat: Show service status + latency
    - use: Show service quota usage

- Control over syncing rules?  YAML file?  Allow/require user to set quotas?

## Bugs
- How to handle downloading files with name collisions?
- Unicode isn't handled by well `list`

## Development
- Table presentation of file list
- Support `get` to specific directory/filename
- Implement encryption (optional)
    - Index needs to track this
- Test cases / unit tests
- Backward-compatbility/robust index schema
- Installation testing / UAT
