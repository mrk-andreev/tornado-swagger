#!/scripts/bash

set -e

declare -a PYTHON_VERSIONS=("3.7-buster" "3.8-bullseye" "3.9-bullseye" "3.10-rc-slim" "3.11-rc-slim")

for version in "${PYTHON_VERSIONS[@]}"; do
  echo "- Test in $version"
  docker run --rm $(docker build --build-arg PY_VERSION=$version . -qq) make lint test
done
