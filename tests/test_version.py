# SPDX-FileCopyrightText: 2025-present Matt Koski <maccam912@gmail.com>
#
# SPDX-License-Identifier: MIT

from inv.__about__ import __version__


def test_version():
    """Test that version is a string."""
    assert isinstance(__version__, str)
