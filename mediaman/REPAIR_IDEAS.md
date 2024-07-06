# Repairing

Maybe a misnomer.  Refers to incrementally adjusting the backing
files and file structure of a given MediaMan service.

(In a global situation, this might mean incrementally adding
redundancy to backed-up files, or migrating tags.)

## Requirements

- For _some_ of these, we need a way to persistently "label" files, groups, etc. as being targets of repair actions
    - Using tags seems like a natural conclusion

## "Repair" actions

### File metadata check

- This does NOT include re-checking hashes.  That's an FSCK.

#### Ensure preferred hash is present
- If not, pull the file down, check the original hash, and add the preferred hash

#### Resolve conflicting hashes (multiple of same type, e.g. xxh64)

### Migrate index files towards distribution target

#### Split index files

#### Merge index files

### (Future) Move files into hash prefix folders
- This only matters for filesystem-based services
    - It has performance implications -- getting the mlist and index files is slow if we also have to list every data blob to get them

- Though this might be bad over the network -- each listing of files incurs a cost

### (Global) Copy files between services to meet redundancy requirements

### (Global) Produce removal _recommendations_ to meet desired storage properties
- Never auto-delete, never delete N without N consents

### (Future) Migrate desired keys

### (Future) Migrate desired encryption
