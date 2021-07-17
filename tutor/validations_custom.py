from wtforms import ValidationError


class PasswordEqualToIfProvided(object):
    """
    Compares the values of two passwords if they exist.
    This is used when you need to compare two passwords but only if they were provided by the user.
    Returns True if either the passwords match or no password was provided.

    :param password:
        The name of the other field to compare to.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """
    def __init__(self, password, message=None):
        self.password = password
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.password]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.password)
        if field.data and field.data != other.data:
            d = {
                'other_label': hasattr(other, 'label') and other.label.text or self.password,
                'other_name': self.password
            }
            message = self.message
            if message is None:
                message = field.gettext('Passwords do not match.')

            raise ValidationError(message % d)


class LengthIfProvided(object):
    """
    Validates the length of a string if anything was provided.
    This is used when you need to validate length if the user provided any value at all.
    eg.: A user can opt not to change their password when editing personal information.
         In this case, we should only check for length if they provided a new password.
         Otherwise, the password remains unchanged and no validations are needed.

    :param min:
        The minimum required length of the string. Needs to be greater than zero.
        If not provided, minimum length will not be checked.
    :param max:
        The maximum length of the string. If not provided, maximum length
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)d` and `%(max)d` if desired. Useful defaults
        are provided depending on the existence of min and max.
    """
    def __init__(self, min=-1, max=-1, message=None):
        assert min != -1 or max != -1, 'At least one of `min` or `max` must be specified.'
        assert max == -1 or min <= max, '`min` cannot be more than `max`.'
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, form, field):
        l = field.data and len(field.data) or 0
        if l > 0:
            if l < self.min or self.max != -1 and l > self.max:
                message = self.message
                if message is None:
                    if self.max == -1:
                        message = field.ngettext('Field must be at least %(min)d character long.',
                                                 'Field must be at least %(min)d characters long.', self.min)
                    elif self.min == -1:
                        message = field.ngettext('Field cannot be longer than %(max)d character.',
                                                 'Field cannot be longer than %(max)d characters.', self.max)
                    elif self.min == self.max:
                        message = field.ngettext('Field must be exactly %(max)d character long.',
                                                 'Field must be exactly %(max)d characters long.', self.max)
                    else:
                        message = field.gettext('Field must be between %(min)d and %(max)d characters long.')

                raise ValidationError(message % dict(min=self.min, max=self.max, length=l))
