import smtplib
from email.mime import MimeText


class Notifiers:
    def __init__(self):
        self._default = None
        self._notifiers = {}

    def add(self, name, kind, default=False, **kwargs):
        notifier = _known_notifiers[kind](**kwargs)
        self._notifiers[name] = notifier
        if default:
            if self._default:
                raise TypeError('default already set')
            self._default = notifier

    @property
    def default(self):
        if self._default is None:
            raise TypeError('no default set')
        return self._default

    def __getitem__(self, key):
        return self._notifiers[key]


class ConsoleNotifier:
    def notify(self, eq):
        print('New stuff: {}'.format(eq.added))


class EmailNotifier:
    def __init__(self, server, username, password, to_addr, from_addr=None):
        server, port = server.split(':')
        self.server = server
        self.port = int(port)
        self.username = username
        self.password = password
        self.from_addr = from_addr or username
        self.to_addr = to_addr

    def notify(self, eq):
        server = smtplib.SMTP(self.server, self.port)
        server.starttls()
        server.login(self.username, self.password)

        msg = MimeText('New stuff: {}'.format(eq.added))
        msg['From'] = self.from_addr
        msg['To'] = self.to_addr
        server.send_message(msg)
        server.quit()


_known_notifiers = {
    'console': ConsoleNotifier,
    'email': EmailNotifier,
}
