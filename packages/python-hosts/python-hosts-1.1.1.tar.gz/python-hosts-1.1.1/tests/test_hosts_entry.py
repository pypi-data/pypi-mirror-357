# -*- coding: utf-8 -*-
import os
import sys

from python_hosts.hosts import HostsEntry

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_create_ipv4_instance():
    """ add an ipv4 type entry """
    hosts_entry = HostsEntry(entry_type='ipv4', address='1.2.3.4',
                             names=['example.com', 'example'],
                             comment='this is a comment')
    assert hosts_entry.entry_type == 'ipv4'
    assert hosts_entry.address == '1.2.3.4'
    assert hosts_entry.names == ['example.com', 'example']
    assert hosts_entry.comment == 'this is a comment'


def test_str_to_hostentry_ipv4():
    str_entry = HostsEntry.str_to_hostentry(
        '10.10.10.10 example.com example.org example # another comment')
    assert str_entry.entry_type == 'ipv4'
    assert str_entry.address == '10.10.10.10'
    assert str_entry.names == ['example.com', 'example.org', 'example']
    assert str_entry.comment == 'another comment'


def test_str_to_hostentry_ipv6():
    str_entry = HostsEntry.str_to_hostentry(
        '2001:0db8:85a3:0042:1000:8a2e:0370:7334 example.com example '
        '# more comments here')
    assert str_entry.entry_type == 'ipv6'
    assert str_entry.address == '2001:0db8:85a3:0042:1000:8a2e:0370:7334'
    assert str_entry.names == ['example.com', 'example']
    assert str_entry.comment == 'more comments here'


def test_str_to_hostentry_returns_fails_with_false():
    result = HostsEntry.str_to_hostentry('invalid example.com example')
    assert not result


def test_hostentry_repr():
    an_entry = HostsEntry(entry_type='ipv4', address='1.2.3.4',
                          comment='test comment', names=[
            'example.com', 'example.org'])
    repr_str = repr(an_entry)
    # Check that the representation contains the essential information
    assert "HostsEntry(" in repr_str
    assert "entry_type=" in repr_str
    assert "ipv4" in repr_str
    assert "address=" in repr_str
    assert "1.2.3.4" in repr_str
    assert "names=" in repr_str
    assert "example.com" in repr_str
    assert "example.org" in repr_str
    assert "comment=" in repr_str
    assert "test comment" in repr_str


def test_hostentry_ipv4_str():
    an_entry = HostsEntry(entry_type='ipv4', address='1.2.3.4',
                          comment='more comments coming',
                          names=['example.com', 'example.org'])
    assert (str(an_entry)) == ("TYPE=ipv4, ADDR=1.2.3.4, "
                               "NAMES=example.com example.org, "
                               "COMMENT=more comments coming")


def test_hostentry_comment_str():
    an_entry = HostsEntry(entry_type='comment', address=None,
                          comment='This is a comment', names=None)
    assert (str(an_entry)) == "TYPE = comment, COMMENT = This is a comment"


def test_hostentry_blank_str():
    an_entry = HostsEntry(entry_type='blank', address=None,
                          comment=None, names=None)
    assert (str(an_entry)) == "TYPE = blank"
