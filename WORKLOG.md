# WORK LOG

## 2024-Mar-28
### 2
With only moderate effort, created `clone` command.
Restoring local MediaMan folder with
```
mm clone -t local -f sam -H `cat RECOVERY/blackbook-air-local-hashes.txt` --log=info
```
(Clone FROM sam TO local, restricted to the hashes in the file)

Reminder done with
```
mm clone -t local -H `cat RECOVERY/blackbook-air-local-hashes.txt)`
```

Learnings:
- Being able to pass input args with `cat` is very good
- Really need helpers for common computations like "what does this service need? what do these have that those don't?" etc.
- Might be nice to have some CLI commands to say "compare" or "difference" or "what isn't present" given a list of hashes

### 1
Started working on using random IVs for file encryption in crypto.py.
Tested out random IV on a file with `mm local put`.
Didn't think ahead to mlist and index files being updated with random IVs too.
Local mlist/index files randomly encrypted and lost.
Fortunately had a copy of the `mm local list` output in my terminal.
That output is in RECOVERY/blackbook-air-local-list-backup.txt.
Hashes alone are in RECOVERY/blackbook-air-local-hashes.txt.
Undid the code change and tested on `mm devnull list` to confirm safety.
Then ran
```
mm all has-hash `cat RECOVERY/blackbook-air-local-hashes.txt`
```
to confirm that MediaMan can completely recover the lost local files.
Time to implement hash-based, crowdsourced recovery command, I guess!

Learnings:
- Need to be able to test that enc/dec are perfectly reversible in isolation
    - Perhaps MM should refuse to act if this test fails
- Need to be able to do e2e tests in a temporary MediaMan folder
    - Include some stub file/sample zip of folder?  Static key
