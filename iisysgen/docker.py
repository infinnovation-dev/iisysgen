#=======================================================================
#       Generate operating system image using docker
#=======================================================================
import sys
import os
import re
from shlex import quote

class DockerGen(object):
    """Generic docker generator"""
    def __init__(self, builddir='.'):
        self.builddir = builddir
        if not os.path.exists(builddir):
            os.makedirs(builddir)
        self._lines = []
        self.helpers = {}

    def from_named(self, image):
        """Start from a named source (docker image)"""
        self.put('FROM %s' % image)

    def from_tarball(self, tarball, dest='/'):
        """Start from a previously built tarball"""
        self.put('FROM scratch')
        self.put('ADD %s %s' % (tarball, dest))

    def env(self, var, value):
        self.put('ENV %s %s' % (var, value))

    def install(self, *packages):
        """Install one or more packages"""
        self.run(['apt-get','install','-y','--no-install-recommends']
                 + list(packages))

#    def ADD(self, src, dest):
#        self.put('ADD %s %s' % (src, dest))

#    def WORKDIR(self, workdir):
#        self.put('WORKDIR %s' % workdir)
#
    def run(self, cmd, stdin=None):
        """Run a command"""
        if isinstance(cmd, (tuple,list)):
            cmd = self.quote_args(cmd)
        if stdin:
            cmd += ' < ' + quote(stdin)
        self.put('RUN %s' % cmd)

    def run_multi(self, *cmds):
        """Run several commands"""
        qcmds = [self.quote_args(cmd) if isinstance(cmd, (tuple,list)) else cmd
                 for cmd in cmds]
        self.put('RUN %s' % (' \\\n && '.join(qcmds)))

    def mkdir(self, path, mode=None):
        if mode is not None:
            self.run(['mkdir','-p','-m',mode,path])
        else:
            self.run(['mkdir','-p',path])

    def symlink(self, src, dest):
        self.run(['ln','-sf', src, dest])

    def write_lines(self, dest, *lines):
        self._write(dest, lines)

    def append_lines(self, dest, *lines):
        self._write(dest, lines, append=True)

    def _write(self, dest, lines, append=False):
        if not lines:
            return
        cmd = '; '.join(['echo %s' % quote(line) for line in lines])
        if len(lines) > 1:
            cmd = '( ' + cmd + ' )'
        self.run('%s %s %s' % (cmd, '>>' if append else '>', quote(dest)))

    def copy_file(self, src, dest, mode='644'):
        """Install a file copied from host filesystem"""
        name = os.path.basename(src)
        with open(src, 'rb') as f:
            helper = self.write_helper(name, f.read(), mode)
        self.put('COPY %s %s' % (helper, dest))

    def copy_as_helper(self, src, name=None):
        """Copy file from host as helper in target"""
        if name is None:
            name = os.path.basename(src)
        helper = '/helpers/%s' % name
        self.copy_file(src, helper)
        return helper

    def write_helper(self, name, content, mode='644'):
        # Pass file content to image via helpers directory
        if name in self.helpers:
            raise ValueError('helper "%s" already exists' % name)
        self.helpers[name] = (content, mode) # To be written in finish()
        helper = 'helpers/%s' % name
        return helper

    def comment(self, text):
        self.put('# %s' % text)

    def quote_args(self, args):
        return ' '.join([quote(a) for a in args])

    def _out(self, line):
        # Default is to accumulate lines, then write() at the end
        self._lines.append(line)

    def put(self, line):
        """Output a line"""
        self._out(line)

    def nl(self):
        self._out('\n')

    def finish(self):
        """Output the generated dockerfile"""
        with self.xopen(os.path.join(self.builddir, 'Dockerfile'), 'w') as f:
            for line in self._lines:
                print(line, file=f)
        if self.helpers:
            helpdir = os.path.join(self.builddir, 'helpers')
            for name, (content, mode) in self.helpers.items():
                path = os.path.join(helpdir, name)
                with self.xopen(path, 'wb') as f:
                    f.write(content)
                os.chmod(path, int(mode,8))

    def xopen(self, name, *args, **kw):
        # Open file, creating directories if necessary
        dirname = os.path.dirname(name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return open(name, *args, **kw)
