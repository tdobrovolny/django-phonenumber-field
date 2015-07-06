# -*- coding: utf-8 -*-

import sys
import phonenumbers
from django.core import validators
from phonenumbers.phonenumberutil import NumberParseException
from django.conf import settings


# Snippet from the `six` library to help with Python3 compatibility
if sys.version_info[0] == 3:
    string_types = str
else:
    string_types = basestring


class PhoneNumber(phonenumbers.phonenumber.PhoneNumber):
    """
    A extended version of phonenumbers.phonenumber.PhoneNumber that provides
    some neat and more pythonic, easy to access methods. This makes using a
    PhoneNumber instance much easier, especially in templates and such.
    """
    format_map = {
        'E164': phonenumbers.PhoneNumberFormat.E164,
        'INTERNATIONAL': phonenumbers.PhoneNumberFormat.INTERNATIONAL,
        'NATIONAL': phonenumbers.PhoneNumberFormat.NATIONAL,
        'RFC3966': phonenumbers.PhoneNumberFormat.RFC3966,
    }

    @classmethod
    def from_string(cls, phone_number, region=None):
        assert isinstance(phone_number, string_types)
        if phone_number.strip() == '':
            phone_number_obj = None
        else:
            phone_number_obj = cls()
            if region is None:
                region = getattr(settings, 'PHONENUMBER_DEFAULT_REGION', None)
            phonenumbers.parse(number=phone_number, region=region,
                               keep_raw_input=True, numobj=phone_number_obj)
        return phone_number_obj

    def __unicode__(self):
        format_string = getattr(settings, 'PHONENUMBER_DEFAULT_FORMAT', 'E164')
        fmt = self.format_map[format_string]
        return self.format_as(fmt)

    def is_valid(self):
        """
        checks whether the number supplied is actually valid
        (e.g. it's in an assigned exchange)
        """
        return phonenumbers.is_valid_number(self)

    def is_possible(self):
        """
        checks whether the number supplied is actually possible
        (e.g. it has the right number of digits)
        """
        return phonenumbers.is_possible_number(self)

    def format_as(self, format):
        return phonenumbers.format_number(self, format)

    @property
    def as_international(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    @property
    def as_e164(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.E164)

    @property
    def as_national(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.NATIONAL)

    @property
    def as_rfc3966(self):
        return self.format_as(phonenumbers.PhoneNumberFormat.RFC3966)

    def __len__(self):
        return len(self.__unicode__())

    def __eq__(self, other):
        """
        Override parent equality because we store only string representation
        of phone number, so we must compare only this string representation
        """
        if (isinstance(other, PhoneNumber) or
                isinstance(other, phonenumbers.phonenumber.PhoneNumber)):
            format_string = getattr(settings, 'PHONENUMBER_DB_FORMAT', 'E164')
            fmt = self.format_map[format_string]
            other_string = phonenumbers.format_number(other, fmt)
            return self.format_as(fmt) == other_string
        else:
            return False


def to_python(value):
    if value in validators.EMPTY_VALUES:  # None or ''
        phone_number = None
    elif value and isinstance(value, string_types):
        try:
            phone_number = PhoneNumber.from_string(phone_number=value)
        except NumberParseException:
            # the string provided is not a valid PhoneNumber.
            phone_number = PhoneNumber(raw_input=value)
    elif (isinstance(value, phonenumbers.phonenumber.PhoneNumber) and
          not isinstance(value, PhoneNumber)):
        phone_number = PhoneNumber()
        phone_number.merge_from(value)
    elif isinstance(value, PhoneNumber):
        phone_number = value
    else:
        # TODO: this should somehow show that it has invalid data, but not
        #       completely die for bad data in the database.
        #       (Same for the NumberParseException above)
        phone_number = None
    return phone_number
