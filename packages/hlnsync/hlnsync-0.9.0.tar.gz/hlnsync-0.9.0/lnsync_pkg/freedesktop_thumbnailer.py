#!/usr/bin/python3

"""
Create and fetch thumbnails in a Freedesktop-compatible way.

https://specifications.freedesktop.org/thumbnail-spec/latest/creation.html

The image format for thumbnails is the PNG format, regardless in which format
the original file was saved. To be more specific it must be a 8bit,
non-interlaced PNG image with full alpha transparency (means 255 possible alpha
values). However, every program should use the best possible quality when
creating the thumbnail. The exact meaning of this is left to the specific
program but it should consider applying antialiasing.

"""

from vignette import get_thumbnail

# import os
# THUMBNAIL_DIRS = (("normal", 128),
#                   ("large", 256),
#                   ("x-large", 512),
#                   ("xx-large", 1024))
#
# class ThumbnailerError(Exception):
#     def __init__(self, msg, path):
#         super().__init__(msg)
#         self.path = path
#
# class GnomeThumbnailer:
#     def __init__(self):
#         try:
#             cache_dir = os.environ([XDG_CACHE_HOME])
#         except KeyError:
#             cache_dir = os.path.expandvars("$HOME/.cache")
#         self._thumbnail_dir = os.path.join(cache_dir, ".cache")
#         for dirname, iconsize in THUMBNAIL_DIRS:
#             subdir = os.path.join(self._thumbnail_dir, dirname)
#             if not os.path.exists(subdir):
#                 os.mkdir(subdir)
#             elif not os.path.isdir(subdir):
#                 raise RuntimeError(f"Expected a directory: {subdir}")
# 
#     def make_thumbnail(self, filename):
#         """
#         Return the thumbnail path or raise a RuntimeError exception.
#         """
#         factory = self.factory
#         mtime = os.path.getmtime(filename)
#         # Use Gio to determine the URI and mime type
#         file_obj = Gio.file_new_for_path(filename)
#         uri = file_obj.get_uri()
#         info = file_obj.query_info(
#             'standard::content-type', Gio.FileQueryInfoFlags.NONE, None)
#         mime_type = info.get_content_type()
#         thumbnail_path = factory.lookup(uri, mtime)
#         if thumbnail_path is not None:
#             return thumbnail_path
#         if not factory.can_thumbnail(uri, mime_type, mtime):
#             raise ThumbnailerError("cannot make thumbnail:", filename)
#         thumbnail = factory.generate_thumbnail(uri, mime_type)
#         if thumbnail is None:
#             raise RuntimeError("error making thumbnail for: "+filename)
#         factory.save_thumbnail(thumbnail, uri, mtime)
#         thumbnail_path = factory.lookup(uri, mtime)
#         assert thumbnail_path is not None
#         return thumbnail_path
