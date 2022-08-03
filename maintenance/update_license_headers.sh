#! /bin/sh
# Updates all Python files with license taken from LICENSE.md and copyright information obtained from the git log.

for fn in setup.py $(find dtool_config_generator -name "*.py"); do
  echo $fn
  python maintenance/copyright.py $fn | cat - LICENSE.md | python maintenance/replace_header.py $fn
done
