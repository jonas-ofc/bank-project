#!/bin/sh

pylama .
pip-audit
djlint .
find . -type f \( -name '*.sh' -o -name '*.bash' -o -name '*.ksh' -o -name '*.bashrc' -o -name '*.bash_profile' -o -name '*.bash_login' -o -name '*.bash_logout' \) \
 -exec shellcheck {} +
find . -type f \( -name '*.yml' \) \
 -exec yamllint {} +