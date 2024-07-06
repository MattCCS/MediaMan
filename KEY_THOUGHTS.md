# Key Thoughts

## Key Rotation

- Track master key ID used at top level...?
    - Just avoid this rotation for now.

## Different Key per Blob

Currently:
- One master key
    - Same for each service
    - Used for each blob
- Static IV (implicitly, generated from static key)
- Random salt (implicitly)

Desired:
- One master key
- Random key per blob
    - Derive blob key from multiple parameters:
        - Master key (never to be used directly)
        - 
- Random IV (stored in blob if possible, otherwise in metadata)
- Random salt (explicitly)
- _Guessing master key doesn't expose any files_
    - Also need ...


## Misc
- The "saltbox" idea boils down to a hash function
    - It statically maps inputs to outputs
    - It has ideally the same properties as a hash function
        - Unguessable inputs, given outputs
    - Though it CANNOT map "ABC" to "AAA" on output.
        - So it's a worse hash function.
    - At that point, why not just use the saltbox AS a secret?
        - Feed it to PBKDF2 as the key, and the other input as a salt

- Master key = "key-generating key"
- Blob key = PBKDF2(key=Master key, salt=public nonce, sha512, rounds=1, len=16)
