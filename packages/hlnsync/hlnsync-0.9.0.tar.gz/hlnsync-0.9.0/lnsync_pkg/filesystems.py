#!/usr/bin/python3

# Copyright (C) 2018 Miguel Simoes, miguelrsimoes[a]yahoo[.]com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Return a unique file serial value that persists across successive mounts.
This number is the same for any path referring to the same underlying file
(i.e. hard links).

On a POSIX-compliant file system, this is the inode.
(https://en.wikipedia.org/wiki/Inode#POSIX_inode_description)

On FAT/VFAT: use hash of dirname + int(ctime) + small integer to ensure
uniqueness.

Possible implementations:
    - Use disk_partitions from psutils, but this shows all fuse systems as fuseblk.
    - call "lsblk -fJ -e 7" (exclude loopback devices) and parse the json output

"""

import sys
import os
import abc
import subprocess
import json

import lnsync_pkg.printutils as pr
from lnsync_pkg.hasher_functions import FileHasherXXHASH64
from lnsync_pkg.miscutils import MIN_INT64, MAX_INT64

FSE = sys.getfilesystemencoding() # Always UTF8 on Linux.

_mntpoint_to_fstype = {}

def _read_partitions():
    global _mntpoint_to_fstype

    def store_partition_info(obj):
        fstype = obj["fstype"]
        def store_mountpoint_info(mtpoint):
            if isinstance(mtpoint, str):
                _mntpoint_to_fstype[mtpoint] = fstype
        mtpoint = obj.get("mountpoint", None)
        store_mountpoint_info(mtpoint)
        mtpoints = obj.get("mountpoints", [])
        for mtpoint in mtpoints:
            store_mountpoint_info(mtpoint)

    try:
        res = subprocess.run(["lsblk", "-fJ", "-e", "7"],
                             capture_output=True,
                             check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("lsblk not installed or outdated")

    dic = json.loads(res.stdout)

    for blkdev in dic["blockdevices"]:
        children = blkdev.get("children", [])
        for blkdev_part in children:
            store_partition_info(blkdev_part)

def get_mountpt_and_fstype(path):
    initial_path = path
    while True:
        if path in _mntpoint_to_fstype:
            return path, _mntpoint_to_fstype[path]
        if path == os.sep:
            raise RuntimeError(
                f"could not find mountpoint for: {initial_path}")
        path = os.path.dirname(path)


SYSTEMS_W_INODE = ['ext2', 'ext3', 'ext4', 'ecryptfs',
                   'btrfs', 'ntfs', 'fuse.encfs']

SYSTEMS_WO_INODE = ['vfat', 'fat', 'FAT', 'iso9660', 'exfat']

for fs_list in SYSTEMS_W_INODE, SYSTEMS_WO_INODE:
    fs_list.extend([s.swapcase() for s in fs_list])

def make_id_computer(topdir_path):
    """
    Return an instance of the appropriate IDComputer class.
    """
    mtpoint, fstype = get_mountpt_and_fstype(topdir_path)
    if fstype in SYSTEMS_W_INODE:
        return InodeIDComputer(topdir_path, fstype)
    elif fstype in SYSTEMS_WO_INODE:
        pr.warning(f"found {fstype}, using path hash as file id for: {topdir_path}")
        return HashPathIDComputer(topdir_path, fstype, mtpoint)
    else:
        raise NotImplementedError(
            f"IDComputer: not implemented for file system: {fstype}")

class IDComputer:
    """
    Compute persistent, unique file serial numbers for files in a
    tree rooted at a given path.
    The returned value is a signed 64-bit integer.
    """
    def __init__(self, topdir_path, file_sys):
        "Init with rootdir on which relative file paths are based."
        self._topdir_path = topdir_path
        self.file_sys = file_sys
        self.subdir_invariant = True

    @abc.abstractmethod
    def get_id(self, rel_path, stat_data=None):
        """
        Return serial number for file at relative path from the root.
        """

class InodeIDComputer(IDComputer):
    """
    Return inode as file serial number.
    """
    def get_id(self, rel_path, stat_data=None):
        if stat_data is None:
            stat_data = os.stat(os.path.join(self._topdir_path, rel_path))
        return stat_data.st_ino

class HashPathIDComputer(IDComputer):
    """
    Return hash(path)+size(file)+smallint as file serial number.
    """
    def __init__(self, topdir_path, file_sys, mtpoint):
        if os.path.samefile(topdir_path, mtpoint):
            self._mtpoint_to_topdir = ""
        else:
            self._mtpoint_to_topdir = os.path.relpath(topdir_path, mtpoint)
        self._hasher = FileHasherXXHASH64()
        self._hash_plus_size_uniq = {}
        super().__init__(topdir_path, file_sys)
        self.subdir_invariant = False

    def get_id(self, rel_path, stat_data=None):
        """
        rel_path is relative to topdir_path, but we hash the relative
        path from the mount point.
        """
        if stat_data is None:
            stat_data = os.stat(os.path.join(self._topdir_path, rel_path))
        file_id = 0
        rel_path_to_mt = os.path.join(self._mtpoint_to_topdir, rel_path)
        for path_component in rel_path_to_mt.split(os.sep)[:-1]:
            path_component = path_component.encode(FSE, "surrogateescape")
            file_id += self._hasher.hash_datum(path_component)
        file_id += stat_data.st_size
        # Make sure we return a (signed) int64
        if file_id > MAX_INT64:
            file_id %= (MAX_INT64 + 1)
        if file_id < MIN_INT64:
            file_id = - (-file_id % (-MIN_INT64+1))
        while file_id in self._hash_plus_size_uniq:
            if self._hash_plus_size_uniq[file_id] == rel_path_to_mt:
                return file_id
            else:
                file_id += 1
        self._hash_plus_size_uniq[file_id] = rel_path_to_mt
        return file_id

_read_partitions()
