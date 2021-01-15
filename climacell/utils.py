from dateutil import parser


def join_fields(fields):
    """
    Joins the provided fields with a comma and returns the result

    :param list[str] fields:
    :return: a string with fields joined by comma
    :rtype: str
    """
    return ",".join(fields)


def check_datetime_str(datetime_str):
    """
    Tries to parse the datetime string to a datetime object. If it fails,
    it will return False

    :param str datetime_str:
    :return: returns True or False depending on the validity of the datetime string
    :rtype: bool
    """
    try:
        parse_datetime_str(datetime_str)
        return True
    except ValueError:
        return False


def parse_datetime_str(datetime_str):
    return parser.parse(datetime_str)
