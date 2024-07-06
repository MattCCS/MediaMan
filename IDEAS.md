# Ideas

## Things I need to be able to do to review my files

- check the redundancy of files
    - check the storage TYPE redundancy of files
    - check the storage LOCALE redundancy of files

- `fsck` (filesystem consistency check)!
    - report on files that are present but untracked
        - possibly with tools to pull them down for recovery
    - report on files that are tracked but not present
    - stream and hash EVERY TRACKED FILE to verify they're not rotting
        - recover from adjacent services if they're rotting

- report under-redundant files

- see TIMESTAMPS for files (datetime added)

- sort files by size/name when listing/searching


## Things I need to be able to do to MANAGE my files

- REPLACE FILES with updated versions!
    - could be a tag `mm:replaced-by:<hash>`

- sync BETWEEN services
    - (ideally without even touching the local filesystem)
        - (that would require continuous hashing)

- assign redundancy goals for files
    - by name
    - doesn't necessarily have to be a persistent setting.  can be done ad-hoc.
        - if not persistent, it would have to sync immediately
        - if persistent, it could do that in bulk with a `sync` command

```
(can sort of already do these...)

    - operate on RANGES of files
        - hash range (which would implicitly resolve to "order added" range)

    - operate on GROUPS of files (*THINK ON THIS*)
        - grouped by tag for example, or search result
        - COULD pipe results of a query into another command
        - COULD use range selection
        - ...
```

- download files to a destination
    - check `isatty`
    - if no destination, maybe ask if it's OK to write to `pwd`?
    - if destination, could stream... (6.4 vs 7.2 seconds)
    - if destination and multiple files, make a folder out of the name


## Things I would like to be able to do

- selectively unencrypt files
- key management
    - rotate keys
    - per-service keys
    - per-file keys (not by default, possibly risky)
- hash management
    - rotate hash functions
    - multiple hash functions (for comparison with online DBs)

- `mm archive` command?
    - recursive version of `put`
    - tag XATTRs so subsequent `archive`s are fast
        - maybe `<size>:<hash>` to quickly check if file changed...
    - option to archive entire folder as a `.zip` of the .mm hash files?

- auto-tag files
    - filepath
    - hostname
    - ...? datetime?
    - DURATION? (audio/video)
    - origin (e.g. if done via URL link)

- add files straight from Internet
    - add tag of URL origin
    - could auto-pull title, description, uploader, dates, etc.
    - use `yt-dlp` for this


## Other features I would like

- hash-prefix-based folders for `local` files
    - faster enumeration
    - avoids filesystem limits

- EMERGENCY ARCHIVES of index and crypt files from other services
    - (if that was lost, recovery would be slow)
    - (or basically impossible if key material or per-file keys were lost)
    - would need a very robust versioning ("serial") system to make sure old indices don't replace new ones
        - a la Lamport clocks, or Terraform statefiles

- ANSI color highlighting

- pipe to `less -SFX` by default

- output formats
    - ASCII table (done)
    - JSON rows
    - CSV?
    - something POSIX-friendly

- recursive .zip files (mmServer)
