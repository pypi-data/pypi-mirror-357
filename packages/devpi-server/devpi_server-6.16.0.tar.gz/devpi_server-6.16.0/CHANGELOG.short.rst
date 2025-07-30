

=========
Changelog
=========




.. towncrier release notes start

6.16.0 (2025-06-25)
===================

Deprecations and Removals
-------------------------

- Dropped support for Python 3.7 and 3.8.



Features
--------

- Update stored package metadata fields to version 2.4 for license expressions (PEP 639).



Bug Fixes
---------

- Preserve hash when importing mirror data to prevent unnecessary updates later on.

- Keep original metadata_version in database.



6.15.0 (2025-05-18)
===================

Features
--------

- Add ``--connection-limit`` option to devpi-server passed on to waitress.



6.14.0 (2024-10-16)
===================

Features
--------

- Allow pushing of versions which only have documentation and no releases.

- Allow pushing of release files only with no documentation. Requires devpi-client 7.2.0.

- Allow pushing of documentation only with no release files. Requires devpi-client 7.2.0.



Bug Fixes
---------

- No longer automatically "register" a project when pushing releases to PyPI. The reply changed from HTTP status 410 to 400 breaking the upload. With devpi-client 7.2.0 there is a ``--register-project`` option if it is still required for some other package registry.



6.13.0 (2024-09-19)
===================

Deprecations and Removals
-------------------------

- Remove/Deprecate "master" related terminology in favor of "primary".
  Usage related changes are the switch to ``--primary-url`` instead of ``--master-url`` and ``--role=primary`` instead of ``--role=master``.
  Using the old terms will now output warnings.
  The ``+status`` API has additional fields and the ``role`` field content will change with 7.0.0.



Features
--------

- Enable logging command line options for all commands.

- Added support uv pip as an installer.



Bug Fixes
---------

- Don't report on lagging event processing while replicating.

- Report primary serial correctly with streaming replication.

- Don't store file data in memory when fetching a release while pushing from a mirror.

- Only warn about replica not being in sync instead of fatal status while still replicating.



6.12.1 (2024-07-24)
===================

Bug Fixes
---------

- Support Python 3.13 by depending on legacy-cgi.

- Preserve query string when proxying requests from replica to primary. This fixes force removal on non-volatile indexes and probably other bugs.

- Fix #1044: Correctly update cache expiry time when mirrored server returns 304 Not Modified.


