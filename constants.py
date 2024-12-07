import re

GITHUB_LINE_NUMBER_URL_REGEX = re.compile(
    r"""
    (?:                                 # Discard any match not proceded by
        (?<!\S)                         # a non-space character
        | (?<=<)                        # a "<" character
        | (?<=\|\|)                     # a "||"
    )
    https?://github\.com/               
    (?P<owner>[\w\-.]+)/                # Repo owner
    (?P<repo>[\w\-.]+)/                 # Repo name
    blob/(?P<branch>[\w\-.]+)/          # Branch name or hash
    (?P<file_path>.+?)                  # File path
    (?:\.(?P<file_ext>\w+))?            # Optional file extension
    (?:\?.+)?                           # Optional query string
    \#L(?P<l1>[0-9]+)                   # Line number
    (?:-L(?P<l2>[0-9]+))?               # Optional ending line number
    (?:                                 # Discard any match not followed by
        (?!\S)                          # a non-space character
        | (?=>)                         # a ">" character
        | (?=\|\|)                      # a "||"
    )
    """,
    flags=re.VERBOSE
)

DISCORD_MESSAGE_URL_REGEX = re.compile(
    r"""
    (?:
        (?<!\S)                         # Discard any match proceded by a non-space character
        |                               # Or
        (?<=<)                          # Discard any match not proceded by a "<" character
    )
    https://
    (?:ptb\.|canary\.)?                 # Optional PTB or Canary subdomain
    discord.com/channels/
    ([0-9]+)/                           # Guild ID
    ([0-9]+)/                           # Channel ID
    ([0-9]+)                            # Message ID
    /?
    (?:
        (?!\S)                          # Discard any match followed by a non-space character
        |                               # Or
        (?=>)                           # Discard any match not followed by a ">" character
    )
    """,
    flags=re.VERBOSE
)
