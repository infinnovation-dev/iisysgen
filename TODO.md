- Use specific dir e.g. /diverted-etc rather than /var/local (owner)
- 'export-tarball' subcmd (from within container or via docker export)
- Add 'add_tarball' backend method
- Add 'run_multi' backend method (for reducing docker depth)
- Enable multi-stage docker (with cpio trick for file ownership)

Further in the future
- 'build' subcmd
- chroot backend
- user-mode-linux backend