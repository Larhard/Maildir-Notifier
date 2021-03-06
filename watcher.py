import email.header
import logging
import pyinotify
import re
import notify
import mailbox

logger = logging.getLogger('watcher')


def decode_header(header):
    return ''.join((k[0] if isinstance(k[0], str) else bytes.decode(k[0], k[1] or 'ascii')) for k in email.header.decode_header(header))


class MailEventHandler(pyinotify.ProcessEvent):
    def my_init(self, maildir):
        self.new_mails = set()

        self.maildir = mailbox.Maildir(maildir)
        assert self.maildir is not None

        self.pevent = lambda event: not re.match('.*:.*', event.name)

    def process_IN_CREATE(self, event):
        logger.debug('"{}" created'.format(event.name))

        self.new_mails.add(event.name)

    def process_IN_CLOSE_WRITE(self, event):
        if event.name in self.new_mails:
            logger.debug('"{}" written'.format(event.name))

            self.new_mails.remove(event.name)

            self.new_mail_notify(event.name)

    def new_mail_notify(self, mail_path):
        mail_id, *_ = mail_path.split(':')
        mail = self.maildir.get(mail_id)
        assert mail is not None

        mail_from = decode_header(mail.get('From'))
        mail_subject = decode_header(mail.get('Subject'))

        notify.send('New Mail', 'From: {}\nSubject: {}'.format(mail_from, mail_subject))


def watch_maildir(maildir):
    logger.info('watching "{}"'.format(maildir))

    notify.init('mail notifier')

    watch_manager = pyinotify.WatchManager()

    handler = MailEventHandler(maildir=maildir)
    notifier = pyinotify.Notifier(watch_manager, handler)

    watch_manager.add_watch(maildir, pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE, rec=True)

    notifier.loop()
    logger.info('exit')
