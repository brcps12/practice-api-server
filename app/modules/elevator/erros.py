class CommandError(Exception):
    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return 'Command is invalid - ' + self.msg
