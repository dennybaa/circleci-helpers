[![Build Status](https://travis-ci.org/dennybaa/circleci-helpers.svg?branch=master)](https://travis-ci.org/dennybaa/circleci-helpers) ![Coverage Status](https://coveralls.io/repos/github/dennybaa/circleci-helpers/badge.svg?branch=master) ![python versions](https://img.shields.io/pypi/pyversions/circleci-helpers.svg) ![pypi version](https://img.shields.io/pypi/v/circleci-helpers.svg)

# Circle CI helpers

Project is intended to bring handy tools to make use of the Circle CI a bit more pleasant.

## circle-matrix

The big difference of Circle CI from Travis is the lack of Matrix builds support. This sometimes is really painful because the `circle.yml` becomes clumsy and hard to read. Just creating a matrix based on some environment variables turns into `if-bashery` with *$CIRCLE_NODE_INDEX* checks, readability degrades almost to zero.

**circle-matrix** is a helper which can be used to create one-dimensional environment matrices using travis like syntax. For example:

```yaml
dependencies:
  pre:
    - sudo -H pip install --upgrade pip
    - sudo -H pip install circleci-helpers
test:
  override:
    - ? | 
          circle-matrix <<"EHD"
            env:
              - VERSION=centos6
              - VERSION=centos7
              - VERSION=fedora22
              - VERSION=fedora23

            before_script:
              - env | sort
              - cd "$VERSION"
              - export image="$IMAGE:$VERSION"

            script:
              - test "$(head -n1 Dockerfile)" = "FROM $image-scm"
                && test "$(head -n1 scm/Dockerfile)" = "FROM $image-curl"
                && [[ "$(head -n1 curl/Dockerfile)" == 'FROM centos:'*
                   || "$(head -n1 curl/Dockerfile)" == 'FROM fedora:'* ]]
              - docker build -t "$image-curl" curl
              - docker build -t "$image-scm" scm
              - docker build -t "$image" .
              - ~/official-images/test/run.sh "$image"

            after_script:
              - docker images
          EHD
      :
        parallel: true
```

So as much as above. It's also worth saying that circle-matrix reads *circle-matrix.yml* if it presents, otherwise falls back to reading from **STDIN**. For information how to specify another configuration file please check help (`circle-matrix --help`).

### Running on Circle CI

Matrix runs are automatically distributed between available number of Circle CI nodes (*$CIRCLE_NODE_TOTAL*). However please don't forget to use the above syntax for the **test** section (`parallel: true`) if you are using *circle-matrix* in this section (the only one which is executed sequentially). 

### What circle-matrix is and what is not

It's **purely environment variables** matrix and it's one-dimensional. It can't be used as travis multi-dimensional matrices for example *env* and *python* grouped together. It supports travis like execution and the following configuration subset:

**Script batches (in execution order)**:

- before_script
- script
- after_success | after_failure
- after_script

**Configuration**:

- env - environment list of matrix variables.
- matrix.allow_failures - list of env mappings (`env: FOO=foo BAR=bar`).


# License and Authors

Licensed under MIT (https://opensource.org/licenses/MIT)

* Author:: Denis Baryshev (dennybaa@gmail.com)
