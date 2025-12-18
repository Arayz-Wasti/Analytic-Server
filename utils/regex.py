import re

PASSWORD_REGEX = re.compile(
    r"""
    ^                           # start
    (?=.*[a-z])                # at least one lowercase
    (?=.*[A-Z])                # at least one uppercase
    (?=.*\d)                   # at least one digit
    (?=.*[@$!%*?&^#()_\-+=])   # at least one special char
    [A-Za-z\d@$!%*?&^#()_\-+=]{8,}  # minimum length 8
    $                           # end
    """,
    re.VERBOSE
)
