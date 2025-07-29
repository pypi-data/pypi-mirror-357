2.0.0 (released 2025-06-23)
---------------------------

- Rewrite attachment handling to improve compatibility when sending html parts
  with embedded images
- Drop Python 2 support

1.1.1 (released 2020-06-19)
---------------------------

- Add support for url quoted usernames/passwords in SMTP urls

1.1.0 (released 2020-06-18)
---------------------------

- Add support for sending through commandline MTAs (sendmail etc)

1.0.3 (released 2019-12-02)
---------------------------

- Bugfix: no longer request the SMTPUTF8 extension for addresses that do not
  appear in SMTP commands.

1.0.2 (released 2019-11-28)
---------------------------

- Fixed broken 1.0.1 release

1.0.1 (released 2019-11-28)
---------------------------

- Bugfix: Mail.send() now sets the envelope from/to addresses correctly from
  message headers in the form "Name <address@example.com>"

1.0.0 (released 2019-11-27)
---------------------------

- Dropped Python 2 support
- Feature: Mail.send() now accepts optional keyword only arguments
  ``envelope_from`` and ``envelope_to``.

0.1.5 (released 2019-06-18)
---------------------------

- Bugfix: don't add a duplicate Message-Id header if one is provided

0.1.4 (released 2017-08-27)
---------------------------

- Bugfix: extra_headers option is now python 3 compatible

0.1.3 (released 2017-04-19)
---------------------------

- Added ability to send stdlib email.message.Message objects via mailsend

0.1.2 (released 2016-09-02)
---------------------------

- The mime structure of HTML emails is now compatible with Outlook 2011
- The SMTPUTF8 extension is requested when messages contain utf-8 addresses.
  (feature is available in Python 3.5 only)

0.1.1 (released 2015-12-21)
---------------------------

- Fixes for compatibility with envparse-0.2

0.1 (released 2015-12-19)
-------------------------

- Forked from https://github.com/rconradharris/tinysmtp
- Added configuration via URL (eg ``Connection('smtp://user@example.org')``)
- Various bug fixes
- Added ``rewrite_to`` argument to Mail class constructor method. This causes
  all messages to be rewritten to the given address(es), and is
  expected to be used for development/testing.
- Added ``bcc`` argument to Mail class constructor method. This causes
  all messages to be bcc'd to the given address(es).
- Added ``suppress_send`` argument to the Mail class constructor. This
  causes messages to not be sent (but may be still accessed via
  ``Mail.subscribe``)
