#
# (C) Copyright 2008 Hewlett-Packard Development Company, L.P.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# Author: Tim Potter <tpot@hp.com>
#

"""A small utility to wrap up a PyWBEM session in a Python interactive
console.

Usage:
  wbemcli.py HOSTNAME [-u USERNAME -p PASSWORD] [-n namespace] [--no-ssl] \
      [--port PORT]

The utility creates a ``pywbem.WBEMConnection`` object for the specified
WBEM server location. Subsequent operatoins then use that connection.

There are two sets of aliases available for usage in the interpreter. For
example, the following two commands are equivalent:

  >>> EnumerateInstanceNames('SMX_ComputerSystem')
  >>> ein('SMX_ComputerSystem')

Pretty-printing of results is also available using the 'pp'
function. For example:

  >>> cs = ei('SMX_ComputerSystem')[0]
  >>> pp(cs.items())
  [(u'RequestedState', 12L),
   (u'Dedicated', [1L]),
   (u'StatusDescriptions', [u'System is Functional']),
   (u'IdentifyingNumber', u'6F880AA1-F4F5-11D5-8C45-C0116FBAE02A'),
  ...
"""

from __future__ import absolute_import

import sys as _sys
import os as _os
import getpass as _getpass
import errno as _errno
import code as _code
import argparse as _argparse

# Additional symbols for use in the interactive session
from pprint import pprint as pp # pylint: disable=unused-import

# Conditional support of readline module
try:
    import readline as _readline
    _HAVE_READLINE = True
except ImportError as arg:
    _HAVE_READLINE = False

from . import WBEMConnection
from ._cliutils import SmartFormatter as _SmartFormatter

__all__ = []

# Connection global variable. Set by remote_connection and use
# by all functions that execute operations.
CONN = None

def _remote_connection(server, opts):
    """Initiate a remote connection, via PyWBEM. Arguments for
       the request are part of the command line arguments and include
       user name, password, namespace, etc.
    """

    global CONN     # pylint: disable=global-statement

    if server[0] == '/':
        url = server
    else:
        proto = 'https'

        if opts.no_ssl:
            proto = 'http'

        url = '%s://%s' % (proto, server)

        if opts.port is not None:
            url += ':%d' % opts.port

    creds = None

    if opts.user is not None and opts.password is None:
        opts.password = _getpass.getpass('Enter password for %s: ' % opts.user)

    if opts.user is not None or opts.password is not None:
        creds = (opts.user, opts.password)

    CONN = WBEMConnection(url, creds, default_namespace=opts.namespace)

    CONN.debug = True

    return CONN

#
# Create some convenient global functions to reduce typing
#

# The following pylint disable is because many of the functions
# in this file use CamelCase specifically to maintain equivalence to
# the client functions in other languages. Do not change these names.
# pylint: disable=invalid-name

def EnumerateInstanceNames(cn, ns=None):
    """
    Enumerate the instance paths of instances of a class (including instances
    of its subclasses) in a namespace.

    Parameters:

      cn (string): Class name.

      ns (string): Namespace name. None will use the default namespace.

    Returns:

      list(CIMInstanceName): The enumerated instance paths.
    """

    return CONN.EnumerateInstanceNames(cn, ns)

# pylint: disable=too-many-arguments
def EnumerateInstances(cn, ns=None, lo=None, di=None, iq=None, ico=None,
                       pl=None):
    """
    Enumerate the instances of a class (including instances of its subclasses)
    in a namespace.

    Parameters:

      cn (string): Class name.

      ns (string): Namespace name. None will use the default namespace.

      lo (bool):   LocalOnly flag: Exclude inherited properties.
                   Deprecated: Server impls for True vary; Set to False.
                   None causes it not to be included in request to server.
                   Server default: True

      di (bool):   DeepInheritance flag: Include properties added by subclasses.
                   None causes it not to be included in request to server.
                   Server default: True

      iq (bool):   IncludeQualifiers flag: Include qualifiers.
                   Deprecated: Instance qualifiers have been deprecated in CIM.
                   None causes it not to be included in request to server.
                   Server default: False

      ico (bool):  IncludeClassOrigin flag: Include class origin info for props.
                   Deprecated: Server may treat as False.
                   None causes it not to be included in request to server.
                   Server default: False

      pl (iterable):
                   Iterable of property names to be included. None means all.
                   None causes it not to be included in the request to server.
                   Server default: None

    Returns:

      list(CIMInstance): The enumerated instances.
    """

    return CONN.EnumerateInstances(cn, ns,
                                   LocalOnly=lo,
                                   DeepInheritance=di,
                                   IncludeQualifiers=iq,
                                   IncludeClassOrigin=ico,
                                   PropertyList=pl)


def GetInstance(ip, lo=None, iq=None, ico=None, pl=None):
    """
    Retrieve an instance.

    Parameters:

      ip (CIMInstanceName): Instance path.

      lo (bool):   LocalOnly flag: Exclude inherited properties.
                   Deprecated: Server impls for True vary; Set to False.
                   None causes it not to be included in request to server.
                   Server default: True

      iq (bool):   IncludeQualifiers flag: Include qualifiers.
                   Deprecated: Instance qualifiers have been deprecated in CIM.
                   None causes it not to be included in request to server.
                   Server default: False

      ico (bool):  IncludeClassOrigin flag: Include class origin info for props.
                   Deprecated:  Server impls. vary; Server may treat as False.
                   None causes it not to be included in request to server.
                   Server default: False

      pl (iterable):
                   Iterable of property names to be included. None means all.
                   None causes it not to be included in request to server.
                   Server default: None

    Returns:

      CIMInstance: The retrieved instance.
    """

    return CONN.GetInstance(ip,
                            LocalOnly=lo,
                            IncludeQualifiers=iq,
                            IncludeClassOrigin=ico,
                            PropertyList=pl)


def ModifyInstance(mi, iq=None, pl=None):
    """
    Modify the property values of an instance.

    Parameters:

      mi (CIMInstance): Modified instance.

      iq (bool):   IncludeQualifiers flag: Include qualifiers.
                   Deprecated: Instance qualifiers have been deprecated in CIM.
                   None causes it not to be included in request to server.
                   Server default: False

      pl (iterable):
                   Iterable of property names to be included. None means all.
                   None causes it not to be included in request to server.
                   Server default: None
    """

    CONN.ModifyInstance(mi,
                        IncludeQualifiers=iq,
                        PropertyList=pl)


def CreateInstance(ni):
    """
    Create an instance in a namespace.

    Parameters:

      ni (CIMInstance): New instance (with namespace, classname, and properties
                        attributes set).

    Returns:
      CIMInstanceName: Instance path of the new instance.
    """

    return CONN.CreateInstance(ni)


def DeleteInstance(ip):
    """
    Delete an instance.

    Parameters:

      ip (CIMInstanceName): Instance path.
    """

    CONN.DeleteInstance(ip)


def AssociatorNames(op, ac=None, rc=None, r=None, rr=None):
    """
    Instance level use: Retrieve the instance paths of the instances
    associated to a source instance.

    Class level use: Retrieve the class paths of the classes associated to a
    source class.

    Parameters:

      op (CIMInstanceName): Source instance path; select instance level use.
      op (CIMClassName): Source class path; select class level use.

      ac (string): AssociationClass filter: Include only traversals across
                   this association class.
                   None causes it not to be included in request to server.
                   Server default: None

      rc (string): ResultClass filter: Include only traversals to this
                   associated (result) class.
                   None causes it not to be included in request to server.
                   Server default: None

      r (string):  Role filter: Include only traversals from this role
                   (= reference name) in source object.
                   None causes it not to be included in request to server.
                   Server default: None

      rr (string): ResultRole filter: Include only traversals to this role
                   (= reference name) in associated (=result) objects.
                   None causes it not to be included in request to server.
                   Server default: None

    Returns:

      list(CIMInstanceName): The instance paths of the associated instances.
    """

    return CONN.AssociatorNames(op,
                                AssocClass=ac,
                                ResultClass=rc,
                                Role=r,
                                ResultRole=rr)


def Associators(op, ac=None, rc=None, r=None, rr=None, iq=None, ico=None,
                pl=None):
    """
    Instance level use: Retrieve the instances associated to a source instance.

    Class level use: Retrieve the classes associated to a source class.

    Parameters:

      op (CIMInstanceName): Source instance path; select instance level use.
      op (CIMClassName): Source class path; select class level use.

      ac (string): AssociationClass filter: Include only traversals across
                   this association class.
                   None causes it not to be included in request to server.
                   Server default: None

      rc (string): ResultClass filter: Include only traversals to this
                   associated (result) class.
                   None causes it not to be included in request to server.
                   Server default: None

      r (string):  Role filter: Include only traversals from this role
                   (= reference name) in source object.
                   None causes it not to be included in request to server.
                   Server default: None

      rr (string): ResultRole filter: Include only traversals to this role
                   (= reference name) in associated (=result) objects.
                   None causes it not to be included in request to server.
                   Server default: None

      iq (bool):   IncludeQualifiers flag: Include qualifiers.
                   Deprecated: Instance qualifiers have been deprecated in CIM.
                   None causes it not to be included in request to server.
                   Server default: False

      ico (bool):  IncludeClassOrigin flag: Include class origin info for props.
                   Deprecated:  Server impls. vary; Server may treat as False.
                   None causes it not to be included in request to server.
                   Server default: False

      pl (iterable):
                   Iterable of property names to be included. None means all.
                   None causes it not to be included in request to server.
                   Server default: None

    Returns:

      list(CIMInstance): The associated instances.
    """

    return CONN.Associators(op,
                            AssocClass=ac,
                            ResultClass=rc,
                            Role=r,
                            ResultRole=rr,
                            IncludeQualifiers=iq,
                            IncludeClassOrigin=ico,
                            PropertyList=pl)


def ReferenceNames(op, rc=None, r=None):
    """
    Instance level use: Retrieve the instance paths of the association
    instances referencing a source instance.

    Class level use: Retrieve the class paths of the association classes
    referencing a source class.

    Parameters:

      op (CIMInstanceName): Source instance path; select instance level use.
      op (CIMClassName): Source class path; select class level use.

      rc (string): ResultClass filter: Include only traversals across this
                   association (result) class.
                   None causes it not to be included in request to server.
                   Server default: None

      r (string):  Role filter: Include only traversals from this role
                   (= reference name) in source object.
                   None causes it not to be included in request to server.
                   Server default: None

    Returns:
      list(CIMInstanceName): The instance paths of the association instances.
    """

    return CONN.ReferenceNames(op,
                               ResultClass=rc,
                               Role=r)


def References(op, rc=None, r=None, iq=None, ico=None, pl=None):
    """
    Instance level use: Retrieve the association instances referencing a source
    instance.

    Class level use: Retrieve the association classes referencing a source
    class.

    Parameters:

      op (CIMInstanceName): Source instance path; select instance level use.
      op (CIMClassName): Source class path; select class level use.

      rc (string): ResultClass filter: Include only traversals across this
                   association (result) class.
                   None causes it not to be included in request to server.
                   Server default: None

      r (string):  Role filter: Include only traversals from this role
                   (= reference name) in source object.
                   None causes it not to be included in request to server.
                   Server default: None

      iq (bool):   IncludeQualifiers flag: Include qualifiers.
                   Deprecated: Instance qualifiers have been deprecated in CIM.
                   None causes it not to be included in request to server.
                   Server default: False

      ico (bool):  IncludeClassOrigin flag: Include class origin info for props.
                   Deprecated:  Server impls. vary; Server may treat as False.
                   None causes it not to be included in request to server.
                   Server default: False

      pl (iterable):
                   Iterable of property names to be included. None means all.
                   None causes it not to be included in request to server.
                   Server default: None

    Returns:

      list(CIMInstance): The association instances.
    """

    return CONN.References(op,
                           ResultClass=rc,
                           Role=r,
                           IncludeQualifiers=iq,
                           IncludeClassOrigin=ico,
                           PropertyList=pl)


def InvokeMethod(mn, op, *params, **kwparams):
    """
    Invoke a method on a target instance or a static method on a target class.

    Parameters:

      mn (string): Method name.

      op (CIMInstanceName): Target instance path.
      op (CIMClassName): Target class path.

      *params (named args): Input parameters for the method.

      **kwparams (keyword args): Input parameters for the method.

    Returns:

      tuple(rv, out): Method return value, dict with output parameters.
    """

    return CONN.InvokeMethod(mn, op, *params, **kwparams)


def EnumerateClassNames(ns=None, cn=None, di=None):
    """
    Enumerate the names of subclasses of a class, or of the top-level classes
    in a namespace.

    Parameters:

      ns (string): Namespace name. None will use the default namespace.

      cn (string): Class name. None will return the top-level classes.
                   None causes it not to be included in request to server.
                   Server default: None

      di (bool):   DeepInheritance flag: Include also indirect subclasses.
                   None causes it not to be included in request to server.
                   Server default: False

    Returns:

      list(string): The enumerated class names.
    """

    return CONN.EnumerateClassNames(ns,
                                    ClassName=ns,
                                    DeepInheritance=di)


def EnumerateClasses(ns=None, cn=None, di=None, lo=None, iq=None, ico=None):
    """
    Enumerate the subclasses of a class, or the top-level classes in a
    namespace.

    Parameters:

      ns (string): Namespace name. None will use the default namespace.

      cn (string): Class name. None will return the top-level classes.
                   None causes it not to be included in request to server.
                   Server default: None

      di (bool):   DeepInheritance flag: Include also indirect subclasses.
                   None causes it not to be included in request to server.
                   Server default: False

      lo (bool):   LocalOnly flag: Exclude inherited properties.
                   None causes it not to be included in request to server.
                   Server default: True

      iq (bool):   IncludeQualifiers flag: Include qualifiers.
                   None causes it not to be included in request to server.
                   Server default: True

      ico (bool):  IncludeClassOrigin flag: Include class origin info for props.
                   None causes it not to be included in request to server.
                   Server default: False

    Returns:

      list(string): The enumerated class names.
    """

    return CONN.EnumerateClassNames(ns,
                                    ClassName=cn,
                                    DeepInheritance=di,
                                    LocalOnly=lo,
                                    IncludeQualifiers=iq,
                                    IncludeClassOrigin=ico)


def GetClass(cn, ns=None, lo=None, iq=None, ico=None, pl=None):
    """
    Retrieve a class.

    Parameters:

      cn (string): Class name.

      ns (string): Namespace name. None will use the default namespace.

      lo (bool):   LocalOnly flag: Exclude inherited properties.
                   None causes it not to be included in request to server.
                   Server default: True

      iq (bool):   IncludeQualifiers flag: Include qualifiers.
                   None causes it not to be included in request to server.
                   Server default: True

      ico (bool):  IncludeClassOrigin flag: Include class origin info for props.
                   None causes it not to be included in request to server.
                   Server default: False

      pl (iterable):
                   Iterable of property names to be included. None means all.
                   None causes it not to be included in request to server.
                   Server default: None

    Returns:

      list(CIMClass): The retrieved class.
    """

    return CONN.GetClass(cn, ns,
                         LocalOnly=lo,
                         IncludeQualifiers=iq,
                         IncludeClassOrigin=ico,
                         PropertyList=pl)


def ModifyClass(mc, ns=None):
    """
    Modify a class.

    Parameters:

      mc (CIMClass): Modified class.

      ns (string): Namespace name. None will use the default namespace.
    """

    return CONN.ModifyClass(mc, ns)


def CreateClass(nc, ns=None):
    """
    Create a class in a namespace.

    Parameters:

      nc (CIMClass): New class.

      ns (string): Namespace name. None will use the default namespace.
    """

    CONN.CreateClass(nc, ns)


def DeleteClass(cn, ns=None):
    """
    Delete a class.

    Parameters:

      cn (string): Class name.

      ns (string): Namespace name. None will use the default namespace.
    """

    CONN.DeleteClass(cn, ns)


def EnumerateQualifiers(ns=None):
    """
    Enumerate qualifier types (= declarations) in a namespace.

    Parameters:

      ns (string): Namespace name. None will use the default namespace.

    Returns:

      list(CIMQualifierDeclaration): Enumerated qualifier types.
    """

    return CONN.EnumerateQualifiers(ns)


def GetQualifier(qn, ns=None):
    """
    Retrieve a qualifier type (= declaration).

    Parameters:

      qn (string): Qualifier name.

      ns (string): Namespace name. None will use the default namespace.

    Returns:

      CIMQualifierDeclaration: Retrieved qualifier type.
    """

    return CONN.GetQualifier(qn, ns)


def SetQualifier(qd, ns=None):
    """
    Create or modify a qualifier type (= declaration) in a namespace.

    Parameters:

      qd (CIMQualifierDeclaration): Qualifier type.

      ns (string): Namespace name. None will use the default namespace.
    """

    CONN.SetQualifier(qd, ns)


def DeleteQualifier(qn, ns=None):
    """
    Delete a qualifier type (= declaration).

    Parameters:

      qn (string): Qualifier name.

      ns (string): Namespace name. None will use the default namespace.
    """

    CONN.DeleteQualifier(qn, ns)


def h():
    """Print help text for interactive environment."""

    print(_get_connection_info())
    print("""
Short and long names of operation functions:
  ein = EnumerateInstanceNames
  ei  = EnumerateInstances
  gi  = GetInstance
  mi  = ModifyInstance
  ci  = CreateInstance
  di  = DeleteInstance
  an  = AssociatorNames
  a   = Associators
  rn  = ReferenceNames
  r   = References
  im  = InvokeMethod
  ecn = EnumerateClassNames
  ec  = EnumerateClasses
  gc  = GetClass
  mc  = ModifyClass
  cc  = CreateClass
  dc  = DeleteClass
  eq  = EnumerateQualifiers
  gq  = GetQualifier
  sq  = SetQualifier
  dq  = DeleteQualifier

Connection:
  CONN = WBEMConnection object connected to the WBEM server
  conn = WBEMConnection class.

Debugging support:
  pdb('<stmt>')    Enter PDB debugger to execute <stmt>

Printing support:
  pp(<obj>)        pprint function, good for dicts
  repr(<obj>)      Operation result objects have repr() for debugging
  print(<obj>.tomof())
                   Operation result objects often have a tomof()
                   producing a MOF string
  <obj>.tocimxml().toxml()
                   Operation result objects have a tocimxml()
                   producing a DOM object that has a toxml() function
                   producing an XML string

Help:
  help(<op>)       Brief help; <op> is a short operation name, e.g. help(gi)
  help(conn.<OpName>)
                   Detailed help; <OpName> is a long operation name, e.g.
                   help(conn.GetInstance).
  'q' to get back from help().

The symbols from the pywbem package namespace are available in this namespace.
""")

def pdb(stmt):
    """Run the statement under the PDB debugger."""
    import pdb
    pdb.set_trace()

    exec(stmt) # Type 3 x "s" to get to stmt, and "cont" to end debugger.

# Aliases for global functions above

ein = EnumerateInstanceNames
ei = EnumerateInstances
gi = GetInstance
mi = ModifyInstance
ci = CreateInstance
di = DeleteInstance

an = AssociatorNames
a = Associators
rn = ReferenceNames
r = References

im = InvokeMethod

ecn = EnumerateClassNames
ec = EnumerateClasses
gc = GetClass
mc = ModifyClass
cc = CreateClass
dc = DeleteClass

eq = EnumerateQualifiers
gq = GetQualifier
sq = SetQualifier
dq = DeleteQualifier

conn = WBEMConnection

def _get_connection_info():
    """Return a string with the connection info."""

    info = 'Connected to %s' % CONN.url
    if CONN.creds is not None:
        info += ' as %s' % CONN.creds[0]
    else:
        info += ' without credentials'
    info += ', default namespace %s' % CONN.default_namespace
    return info


def _get_banner():
    """Return a banner message for the interactive console."""

    result = ''
    result += '\nPython %s' % _sys.version
    result += '\n\nWbemcli interactive shell'
    result += '\n%s' % _get_connection_info()

    # Give hint about exiting. Most people exit with 'quit()' which will
    # not return from the interact() method, and thus will not write
    # the history.
    result += '\nPress Ctrl-D to exit'
    result += '\nType h() for help'

    return result

def main():
    """Parse command line arguments, connect to the WBEM server and
    open the interactive shell.
    A help message is printed with `-h` or `--help`.
    """

    global CONN     # pylint: disable=global-statement

    prog = "wbemcli"  # Name of the script file invoking this module
    usage = '%(prog)s [options] server'
    desc = 'Provide an interactive shell for issuing operations against a ' \
           'WBEM server.'
    epilog = """
Example:
  %s localhost --port 15989 -n root/cimv2 -u sheldon -p penny42
""" % prog
    argparser = _argparse.ArgumentParser(
        prog=prog, usage=usage, description=desc, epilog=epilog,
        add_help=False, formatter_class=_SmartFormatter)

    pos_arggroup = argparser.add_argument_group(
        'Positional arguments')
    pos_arggroup.add_argument(
        'server', metavar='server', nargs='?',
        help='Host name or IP address of the WBEM server.')

    server_arggroup = argparser.add_argument_group(
        'Server related options',
        'Specify the WBEM server and namespace')
    server_arggroup.add_argument(
        '--port', dest='port', metavar='port', type=int,
        default=None,
        help='Port where the WBEM server listens')
    server_arggroup.add_argument(
        '--no-ssl', dest='no_ssl',
        action='store_true',
        help='Don\'t use SSL')
    server_arggroup.add_argument(
        '-n', '--namespace', dest='namespace', metavar='namespace',
        default='root/cimv2',
        help='R|Namespace in the WBEM server to work against.\n' \
             'Default: %(default)s')
    server_arggroup.add_argument(
        '-u', '--user', dest='user', metavar='user',
        help='R|Username for authenticating with the WBEM server.\n' \
             'Default: No username')
    server_arggroup.add_argument(
        '-p', '--password', dest='password', metavar='password',
        help='R|Password for authenticating with the WBEM server.\n' \
             'Default: Will be prompted for, if username was specified.')

    general_arggroup = argparser.add_argument_group(
        'General options')
    general_arggroup.add_argument(
        '-v', '--verbose', dest='verbose',
        action='store_true', default=False,
        help='Print more messages while processing')
    general_arggroup.add_argument(
        '-h', '--help', action='help',
        help='Show this help message and exit')

    args = argparser.parse_args()

    if not args.server:
        argparser.error('No WBEM server specified')

    # Set up a client connection
    CONN = _remote_connection(args.server, args)

    # Determine file path of history file
    home_dir = '.'
    if 'HOME' in _os.environ:
        home_dir = _os.environ['HOME'] # Linux
    elif 'HOMEPATH' in _os.environ:
        home_dir = _os.environ['HOMEPATH'] # Windows
    histfile = '%s/.wbemcli_history' % home_dir

    # Read previous command line history
    if _HAVE_READLINE:
        try:
            _readline.read_history_file(histfile)
        except IOError as arg:
            if arg[0] != _errno.ENOENT:
                raise

    # Interact
    i = _code.InteractiveConsole(globals())
    i.interact(_get_banner())

    # Save command line history
    if _HAVE_READLINE:
        _readline.write_history_file(histfile)

    return 0

