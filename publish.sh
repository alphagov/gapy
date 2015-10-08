#!/bin/bash

function pretty() {
  local blue="\033[34m"
  local reset="\033[0m"
  while read line; do
    echo -e "${blue}[publishing]${reset} ${line}"
  done
}

function get_sha(){
    REF=$(git log -n 1 -- performanceplatform/collector/__init__.py --name-only)
    SHA=$(echo $REF | awk '{ print $2 }')

    echo "checking out ${SHA}" | pretty

    git checkout $SHA
}

function get_version(){
    VERSION=$(python setup.py --version)
    echo "latest version is ${VERSION}" | pretty
}

function publish_or_die(){
    TAG_EXISTS=$(git tag | grep -G "^${VERSION}$")
    if [ "$TAG_EXISTS" ]; then
        echo "Tag already exists, exiting" | pretty
        exit 0
    else
        pypi_check $VERSION
    fi
}

function pypi_check(){
    python setup.py sdist register -r pypitest
    python setup.py sdist upload -r pypitest
    echo "Testing upload to PyPI test server" | pretty
    publish
}

function publish(){
    git tag -a $VERSION -m "Automatically published from jenkins"
    echo "Pushing tags to github and publishing ${VERSION} to PyPI" | pretty
    git push origin --tags
    python setup.py register -r pypi
    python setup.py sdist upload -r pypi
}

function main(){
    get_sha
    get_version
    publish_or_die
}

main
