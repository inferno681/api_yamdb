import re

from django.core.exceptions import ValidationError


INVALID_USERNAME_MESSAGE = ('Имя пользователя содержит недопустимые символы: '
                            '{invalid_symbols}.')
INVALID_USERNAME_ME_MESSAGE = 'Нельзя использовать имя пользователя <me>'


def validate_username(username):
    if username == 'me':
        raise ValidationError(INVALID_USERNAME_MESSAGE,
                              params={'username': username})
    invalid_symbols = []
    for char in set(username):
        if not re.match(pattern=r'^[\w.@+-]+\Z', string=char):
            invalid_symbols.append(char)
    if invalid_symbols:
        raise ValidationError(INVALID_USERNAME_MESSAGE.format(
            invalid_symbols=invalid_symbols), code='invalid username')
