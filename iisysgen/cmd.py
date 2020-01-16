#=======================================================================
#       Generate operating system image
#=======================================================================

def main():
    import argparse
    ap = argparse.ArgumentParser()
    #ap.add_argument('--chroot',
    #                help='Use chroot for building')
    def vardef(arg):
        """Map e.g. 'user.name=Fred' to {'user':{'name':'Fred'}}"""
        n, _, v = arg.partition('=')
        try:
            v = int(v,0)
        except ValueError:
            try:
                v = float(v)
            except ValueError:
                pass
        def path2dict(path, val):
            step, sep, rest = path.partition('.')
            if sep:
                return {step: path2dict(rest, val)}
            return {path: val}
        return path2dict(n, v)
    #
    sub = ap.add_subparsers(dest='method', metavar='METHOD')
    #
    m_generate = sub.add_parser('generate',
                                help='Generate build script')
    m_generate.add_argument('-c','--config', action='append',
                            default=[],
                            help='Configuration in JSON or YAML')
    m_generate.add_argument('-v','--var', type=vardef, action='append',
                            default=[],
                            help='Definition var=value to add to configuration')
    #m_generate.add_argument('-x','--export', action='store_true',
    #                        help='Export built filetree')
    m_generate.add_argument('builder',
                            help='Name of user-supplied builder class')
    #
    #m_export = sub.add_parser('export',
    #                          help='Export built filetree')
    #m_export.add_argument('builder',
    #                      help='Name of builder class')
    #
    args = ap.parse_args()
    #if args.chroot:
    #    gen = ChrootGen(args.chroot)
    #else:
    #    raise NotImplementedError
    method = args.method
    if method == 'generate':
        cfg = {}
        for config in args.config:
            if config.endswith('.json'):
                import json
                with open(config) as f:
                    fcfg = json.load(f)
                if fcfg is not None:
                    cfg_merge(cfg, fcfg)
            elif config.endswith('.yaml'):
                try:
                    import yaml
                except ImportError:
                    raise RuntimeError('YAML not supported')
                with open(config) as f:
                    fcfg = yaml.load(f)
                if fcfg is not None:
                    cfg_merge(cfg, fcfg)
            else:
                raise ValueError('Unknown config file extension')
        for vcfg in args.var:
            cfg_merge(cfg, vcfg)
        builder = find_builder(args.builder)
        from .docker import DockerGen as gencls
        gen = gencls(args.builder) # Use same name for build dir
        builder.build(gen, cfg)
        #if args.export:
        #    gen.export(args.builder)
    #elif method == 'export':
    #    gen.export(args.builder)
    else:
        raise NotImplementedError

def find_builder(name):
    """Get builder class from name"""
    from importlib import import_module
    mod = import_module(name)
    return mod

def cfg_merge(cfg, extra, path=[]):
    """Merge configuration data"""
    for name, value in extra.items():
        if name in cfg:
            branch = cfg[name]
            if isinstance(branch, dict):
                if not isinstance(value, dict):
                    raise ValueError('Cannot merge dict with %s at %s' %
                                     (type(value), '/'.join(path)))
                cfg_merge(branch, value, path+[name])
            elif isinstance(branch, list):
                if not isinstance(value, list):
                    raise ValueError('Cannot extend list with %s at %s' %
                                     (type(value), '/'.join(path)))
                branch.extend(value)
            elif isinstance(value, dict):
                raise ValueError('Cannot merge %s with dict at %s' %
                                 (type(branch), '/'.join(path)))
            elif isinstance(value, list):
                raise ValueError('Cannot merge %s with list at %s' %
                                 (type(branch), '/'.join(path)))
            else:
                # Replace existing scalar
                cfg[name] = value
        else:
            cfg[name] = value

if __name__=='__main__':
    main()
