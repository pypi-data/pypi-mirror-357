# SweeCrypt
A basic and fun cipher module for everyone. it converts regular text into symbols on a keyboard, kind of like a cipher. This is only for fun, using this module for cybersecurity is NOT ADVISED

This is a more maintained version of the Crypty Encryption Module in Swee's Replit.

# Install

## CLI (>= 1.1.3)

```shell-session
$ pipx install sweecrypt
```

Help page:
```shell-session
$ sweecrypt --help
                                                                                                                                                                     
 Usage: sweecrypt [OPTIONS] COMMAND [ARGS]...                                                                                                                        
                                                                                                                                                                     
 An easy and fun encryption module.                                                                                                                                  
                                                                                                                                                                     
                                                                                                                                                                     
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                                                           │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                                                    │
│ --help                        Show this message and exit.                                                                                                         │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ encrypt   Encrypts a message                                                                                                                                      │
│ decrypt   Decrypts a SweeCrypt-encoded message                                                                                                                    │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

## Module

```shell-session
$ pip3 install sweecrypt
```

Import:  
```python
>>> import sweecrypt
```

# Usage

Encrypt:  
```python
>>> sweecrypt.encrypt("hello, world!")
!?~~(:,}(>~/a
```
```shell-session
$ sweecrypt encrypt "hello, world!"
!?~~(:,}(>~/a
```

Decrypt:  
```python
>>> sweecrypt.decrypt("!?~~(:,}(>~/a")
hello, world!
```
```shell-session
$ sweecrypt decrypt "!?~~(:,}(>~/a"
hello, world!
```

> [!WARNING]
> Decrypting text using the CLI may cause your shell to malfunction
>
> This can usually be fixed by using `set +H` before running these

With newer versions of sweecrypt (>= 1.1.0), you can shift the encryption database:

```python
>>> sweecrypt.encrypt("hello, world", 3)
'\\!((>ba_>](#'
>>> sweecrypt.decrypt("\\!((>ba_>](#", 3)
'hello, world'
```
```shell-session
$ sweecrypt encrypt --shift 3 "hello, world"
\!((>ba_>](#
$ sweecrypt decrypt --shift 3 "\!((>ba_>](#"
hello, world
```

So it will output a nonsense string if shifted incorrectly.

```python
>>> sweecrypt.decrypt("\\!((>ba_>](#")
'khoor?!zruog'
```
```shell-session
$ sweecrypt decrypt "\!((>ba_>](#"
khoor?!zruog
```