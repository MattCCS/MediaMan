# User Stories (CLI)

## Commands
There are some options for how generic `mm` commands should work.

For example, for the `has` command, MediaMan could tell you:
- whether EVERY service has the file, e.g.
- whether ANY service has the file
- whether ANY REMOTE service has the file
- whether some quorum of services have the file
- some information depending on custom rules: (drive OR (local + AWS))

### Has
        $ mm has bad.txt
        [-] No file with the name 'bad.txt' was found.

        $ mm has old.txt
        Yes

        $ mm has new.txt
        No


## Service commands

### Has
        $ mm local has bad.txt
        [-] No file with the name 'bad.txt' was found.

        $ mm local has old.txt
        Yes

        $ mm local has new.txt
        No


## Global commands
        $ mm all has bad.txt
        [-] No file with the name 'bad.txt' was found.

        $ mm all has old.txt
        +---------+----------+
        | Service | Has file |
        +---------+----------+
        | Local   | Yes      |
        | Drive   | No       |
        | AWS     | Yes      |
        +---------+----------+

        $ mm all has new.txt
        +---------+----------+
        | Service | Has file |
        +---------+----------+
        | Local   | No       |
        | Drive   | No       |
        | AWS     | No       |
        +---------+----------+
