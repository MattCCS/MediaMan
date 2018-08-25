# To-Do List

## Features
- Commands without service specified

- Aliases for services (db = dropbox, ext = local w/ specific filepath, ...)
    - JSON file for service listing

- Commands:
    - del: Delete file
    - sync: Synchronize services with each other
    - stat: Show service status + latency
    - use: Show service quota usage

- Add tagging to files for search/filtering

- Control over syncing rules?  YAML file?  Allow/require user to set quotas?

## Bugs
- How to handle downloading files with name collisions?
- Unicode isn't handled by well `list`

## Development
- Separate out id conversion from metadata?
- Remove hash function from classes
- Table presentation of file list
- Support `get` to specific directory/filename
- Implement encryption (optional)
    - Index needs to track this
- Test cases / unit tests
- Backward-compatbility/robust index schema
- Installation testing / UAT
