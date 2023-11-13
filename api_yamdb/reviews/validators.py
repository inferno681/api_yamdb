from datetime import date
import re

from django.core.exceptions import ValidationError


INVALID_USERNAME_MESSAGE = ('Имя пользователя содержит недопустимые символы: '
                            '{invalid_symbols}.')
INVALID_USERNAME_ME_MESSAGE = 'Нельзя использовать имя пользователя <me>'
WRONG_YEAR_MESSAGE = ('Нельзя публиковать произведения из будущего! '
                      '{year} > {current_year}')
USER_PROFILE_PATH = 'me'


def validate_username(username):
    if username == USER_PROFILE_PATH:
        raise ValidationError(INVALID_USERNAME_MESSAGE,
                              params={'username': username})
    invalid_symbols = re.sub(r'[\w@.+-]', '', username)
    if invalid_symbols:
        raise ValidationError(
            INVALID_USERNAME_MESSAGE.format(
                invalid_symbols="".join(set(invalid_symbols)))
        )
    return username


def validate_year(year):
    if year > date.today().year:
        raise ValidationError(WRONG_YEAR_MESSAGE.format(
            year=year, current_year=date.today().year))
    return year
