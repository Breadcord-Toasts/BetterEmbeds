import re

GITHUB_LINE_NUMBER_URL_REGEX = re.compile(
    r"""
    (?:
        (?<!\S)                         # Discard any match proceded by a non-space character
        |                               # Or
        (?<=<)                          # Discard any match not proceded by a "<" character
    )
    https?://github\.com/               
    (?P<owner>[\w\-.]+)/                # Repo owner
    (?P<repo>[\w\-.]+)/                 # Repo name
    blob/(?P<branch>[\w\-.]+)/          # Branch name or hash
    (?P<file_path>.+?)                  # File path
    (?:\.(?P<file_ext>\w+))?            # Optional file extension
    (?:\?.+)?                           # Optional query string
    \#L(?P<l1>\d+)                      # Line number
    (?:-L(?P<l2>\d+))?                  # Optional ending line number
    (?:
        (?!\S)                          # Discard any match followed by a non-space character
        |                               # Or
        (?=>)                           # Discard any match not followed by a ">" character
    )
    """,
    flags=re.VERBOSE
)



