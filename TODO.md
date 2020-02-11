- Use specific dir e.g. /diverted-etc rather than /var/local (owner)
- 'export-tarball' subcmd (from within container or via docker export)
- Enable multi-stage docker (with cpio trick for file ownership)

Further in the future
- 'build' subcmd
- chroot backend
- user-mode-linux backend
