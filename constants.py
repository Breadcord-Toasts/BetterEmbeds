import re

GITHUB_LINE_NUMBER_URL_REGEX = re.compile(
    r"""
    (?<!\S)                             # Discard any match proceded by a non-space character
    https?://github\.com/               
    (?P<owner>\w+)/                     # Repo owner
    (?P<repo>\w+)/                      # Repo name
    blob/(?P<branch>\w+)/               # Branch name or hash
    (?P<file_path>.+?)                  # File path
                                        # Please PR some propper matching for this, 'cause I sure won't do it
    (?:\.(?P<file_ext>\w+))?            # Optional file extension
    \#L(?P<l1>\d+)                      # Line number. # is escaped due to it being seen as a comment otherwise
    (?:-L(?P<l2>\d+))?                  # Optional ending line number
    (?!\S)                              # Discard any match followed by a non-space character
    """,
    flags=re.VERBOSE
)



