PYLF - The Over-Engineered Web File-Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PYLF is a file-manager web application written in Python3_ and using
(among lots of other things) the Pyramid_ web framework and Jinja2_
templates.

While PYLF was initially conceived to provide web-based access to
local files, it has a backend abstraction that is meant to allow for
other means of storing files and meta data.

Similarly, the support for authentication and authorization is meant
to be flexible, and several authentication backends are already
available. Authorization on the other hand, is practically
non-existent at the time of this writing.

.. _Python3: http://www.python.org
.. _Pyramid: http://www.pylonsproject.org/projects/pyramid
.. _Jinja2: http://jinja.pocoo.org/


Quick start
===========

There are various ways of setting up a python application along with
its dependencies. If you don't know them already, now is as good a
time to learn them as any.

Configuration
-------------

Assuming PYLF and its dependencies are installed, running it is as
simple as::

  pserve conf/development.conf

There currently are only a few settings in ``development.conf`` that
need to be set to get PYLF to actually do anything:

``mounts_directories``
  List of directories containing "mount" configurations. These define the
  files that are accessible through the PYLF instance.

``icons_path``
  Path to a folder containing icons for mime-types. On a linux-like
  system, any of the ``mimetypes`` folders below ``/usr/share/icons``
  should do. On a not-linux-like system, good luck.


Mounts
------

A *mount* is a directory tree that is served up by PYLF. Mounts are
configured through files in the directories listed in the
``mounts_directories`` setting.

As an example, lets serve the machine's ``/tmp`` directory through
PYLF::

  [backend]
  type = fs
  path = /tmp
  
  [auth]
  realm = tmp
  
  [authentication]
  type = inline
  users = {
      "pylf": {
        "name": "PYLF Test User",
        "password": {
          "type": "sha512",
          "salt": "e3sXQn0V8nE=",
          "hash": "n/bK26hk3mXpF0qdLlTPQ3IXxRRmrWfdts/H7K1bqaj+uJjNC1CXZg2pAxfv7gOVUEU9YOQ6TlHvb5kuZfcXrQ=="	
        }
      }
    }

This mount configuration sets up the ``fs`` backend to server the
``/tmp`` directory. It also configures the ``inline`` authentication
backend to know about a single user with login "pylf" and password
"test1234". The ``auth.realm`` setting is used for the server's
authentication challenge, but this setting will likely change.

Copy the above configuration into a file named "tmp.conf" in your
mounts directory (watch out for the indentation of the ``users``
setting, none of the lines may start in column 0).
