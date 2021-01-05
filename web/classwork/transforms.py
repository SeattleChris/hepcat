from django.db.models import DateField, DateTimeField, SmallIntegerField, PositiveIntegerField, IntegerField, Transform
# from django.db.models import F, Func


class AddDate(Transform):
    """date1: Date, days: int -> Date. Returns a date that is number of days (+ or -) from given the initial date. """
    lookup_name = 'adddate'
    function = 'ADDDATE'

    @property
    def output_field(self):
        return DateField()


class DateDiff(Transform):
    """date1: Date, date2: Date -> int. Returns the number of days between two given dates. """
    lookup_name = 'numday'
    function = 'DATEDIFF'

    @property
    def output_field(self):
        return SmallIntegerField()  # Good enough for just over plus-or-minus 89 year difference in days.


class DayYear(Transform):
    """date1: Date -> int. Returns a number 1 to 366 as the day of the year for the given date or datetime input. """
    lookup_name = 'dayyear'
    function = 'DAYOFYEAR'

    @property
    def output_field(self):
        return SmallIntegerField()


class NumDay(Transform):
    """date1: Date -> int. Returns number of days since 0 date ('0000-00-00') for the given date or datetime input. """
    lookup_name = 'numday'
    function = 'TO_DAYS'

    @property
    def output_field(self):
        return PositiveIntegerField()


class DateFromNum(Transform):
    """Given a number of days since 0 date ('0000-00-00'), returns a date. The opposite of 'numday'. """
    lookup_name = 'datefromnum'
    function = 'FROM_DAYS'

    @property
    def output_field(self):
        return DateField()


class MakeDate(Transform):
    """year: int, day: int -> Date. Returns a Date for the given 4-digit year and day integer (1 to 366). """
    lookup_name = 'makedate'
    function = 'MAKEDATE'

    @property
    def output_field(self):
        return DateField()


class DateToday(Transform):
    """Returns the date portion, without any information about the time, of the current day. """
    lookup_name = 'today'
    function = 'CURDATE'

    @property
    def output_field(self):
        return DateField()


class StartClassDate(Transform):
    lookup_name = 'datestart'

    @property
    def output_field(self):
        return DateField()


DateField.register_lookup(AddDate)
DateTimeField.register_lookup(AddDate)
DateField.register_lookup(DateDiff)
DateTimeField.register_lookup(DateDiff)
DateField.register_lookup(DayYear)
DateTimeField.register_lookup(DayYear)
DateField.register_lookup(NumDay)
DateTimeField.register_lookup(NumDay)

SmallIntegerField.register_lookup(DateFromNum)
PositiveIntegerField.register_lookup(DateFromNum)
IntegerField.register_lookup(DateFromNum)
# AddDate, DateDiff, DayYear, NumDay, DateFromNum, MakeDate, DateToday

# Find the difference between two dates, may span over some years.
# Create a new date by adding or subtracting an integer of days. date1: datetime, num: integer -> datetime
# Determine if a date is before or after another date.
# Transform with my special rules for determining the start date of a given classoffer
#   date1: datetime, day: integer for day of the week, shift: integer for direction and max to go in that direction.
#   From the day of the week of date1, try to go in the direction of shift to get to day.
#       If that requires going beyond the range of shift, then go the opposite direction.
#       Thus, the new date is computed for before or after the date1 and returned as a DateField
