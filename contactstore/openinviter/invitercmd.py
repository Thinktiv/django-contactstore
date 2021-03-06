#!/usr/bin/env python


"""A python wrapper around openinviter.

This is designed to be called by python libraries but there is a
simple command line interface as well.


Command Line

call this like:

  invitecmd username@hotmail.com password

and it will contact hotmail with openinviter and print the contacts it pulled down.

You can also invoke like this:

  invitecmd

and it will try to run through a list of tests. The list of tests can
be defined in the python module:

  contactstore_TESTS

the invitecmd automatically adds the current working directory to the
Python sys path so it's easier to find such modules.

eg:

  contactstore_TESTS.py
    TESTS = [{ 
         "username": "yahoomailaddress@yahoo.com",
         "password": "somepassword"
         },{
         "username": "hotmailaddress@hotmail.com",
         "password": "somepassword",
         },{
         "username": "gmailaddress@gmail.com",
         "password": "somepasword"
         },
     ]

and then:

  invitecmd

will result in those addresses being tested.


If you don't want to use a module you can pass a filename to
invitercmd by use of the INVITEDEFS environment variable:

  INVITEDEFS=~/.mytestemails invitecmd

will result in addresses defined in the file ~/.mytestemails being tested.

The format of the file is emailaddress SPACE password:

yahoomailaddress@yahoo.com somepassword
hotmailaddress@hotmail.com somepassword
gmailaddress@gmail.com somepasword



Test Help

if you call get_contacts with test_mode=True then you get the extra
addresses (those in TEST_LINES) that help assert things.
"""

from __future__ import with_statement

from subprocess import Popen
from subprocess import PIPE
from os.path import join as joinpath
from os.path import dirname
from os.path import expanduser
from os.path import expandvars
import re

class ImporterException(Exception):
    """An exception to indicate some problem with the importer."""
    pass

class LoginException(ImporterException):
    """Indicates a failure to authorize"""
    pass

class UnsupportedImporterException(ImporterException):
    """We don't support this provider"""
    pass

EMAIL = re.compile("[^']+@[A-Za-z.-]+")

TEST_LINES = (
    "nic@one,",
    "nic@woomeduplicate.com,nic",       # help assert that you can't have duplicates
    "nic@woomeduplicate.com,nicholas",
    "asadlkqjcbqjbk",                   # help assert you can't get less than 2 parts
    ",blah",                            # help assert you can't get non-emails
    )

def _get_contact_iter(provider, email, password, test_mode=False):
    path = joinpath(dirname(__file__), "php", "script.php")
    proc = Popen([
            "php",
            path,
            email,
            password,
            provider
            ], stdout=PIPE, stderr=PIPE)
    pid = proc.pid
    stdout, stderr, = proc.communicate()
    if stdout.startswith("error:"):
        error = stdout.split("error:")[1].strip()
        if error == "login error":
            raise LoginException("login error pid=%s email=%s" % (pid, email))
        else:
            raise ImporterException(error)

    # Otherwise we have some addressses
    lines = stdout.split("\n")
    if test_mode:
        lines += TEST_LINES

    emails = {}
    for line in lines:
        parts = line.split(",")
        if len(parts) > 0:
            email = parts[0]
            if EMAIL.match(email):
                if emails.get(email, None):
                    continue
                emails[email] = parts
                yield email, " ".join(parts[1:])
    return


_DOMAIN_RE = re.compile("[^@]+@(?P<provider>[^.]+)\\..*")
_PROVIDER_MAP = {
    "googlemail": 'gmail',
    "gmail": "gmail",
    "yahoo": "yahoo",
    "hotmail": "hotmail",
    "live": "hotmail",
    "msn": "msn",
    "aol": "aol",
    "plaxo" : "plaxo",
    "lycos" : "lycos",
}

_DEFAULT_PROVIDER = 'gmail'
def get_provider_from_domain(domain_name):
    return _PROVIDER_MAP.get(domain_name, _DEFAULT_PROVIDER)

def get_contacts(email, password, test_mode=False):
    """The contacts list is a unique list of contacts.

    Each contact is a pair of emailaddress, contact detail (usuaully name).

    The contacts are unique by email address. The first contact found
    with the email address is used.

    This python wrapper manages a mapping of domain parts to provider
    names. The domain part being the first part of the domain name
    after the @ in the email parameter.
    """
    domain = _DOMAIN_RE.match(email)
    if domain:
        domain_name = domain.group("provider")
        try:
            provider = get_provider_from_domain(domain_name)
        except KeyError, e:
            raise UnsupportedImporterException(e)
        else:
            addresses = list(_get_contact_iter(provider, email, password, test_mode))
            return addresses

def _get_tests():
    import os
    TESTS = []
    try:
        cwd = os.getcwd()
        if not (cwd in sys.path or "." in sys.path):
            sys.path += [cwd]

        import contactstore_TESTS
    except Exception, e:
        barefile = os.environ.get("INVITEDEFS")
        if barefile:
            filename = expandvars(expanduser(barefile))
            with open(filename) as fd:
                pairs = [line.strip().split(" ") for line in fd]
                TESTS = [{"username": e[0], "password": e[1] } for e in pairs]
    else:
        TESTS = contactstore_TESTS.TESTS
    return TESTS

import sys
def main():
    if sys.argv[1:]:
        if sys.argv[1] in ["help", "--help", "-h", "-?", "?"]:
            print __doc__
            return

        if len(sys.argv[1:]) != 2:
            print >>sys.stderr, "Wrong args - use: providername email password"
        else:
            print "%s %s\n" % (
                sys.argv[1], 
                get_contacts(*sys.argv[1:])
                )
        return

    tests = _get_tests()
    for a in tests:
        try:
            print "%s %s\n" % (a["username"], get_contacts(a["username"], a["password"]))
        except Exception, e:
            print e

if __name__ == "__main__":
    main()

# End
