[![Linter](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/linter.yml/badge.svg?branch=master)](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/linter.yml?query=branch%3Amaster)
[![Test Action](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/test_action.yml/badge.svg?branch=master)](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/test_action.yml?query=branch%3Amaster)
[![Unit Tests](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/unit_tests.yml/badge.svg?branch=master)](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/unit_tests.yml?query=branch%3Amaster)

# Static Analysis

This GitHub action is designed for C++/Python projects and performs static analysis using:
- [cppcheck](http://cppcheck.sourceforge.net/) and [clang-tidy](https://clang.llvm.org/extra/clang-tidy/) for C++
- [pylint](https://pylint.readthedocs.io/en/latest/index.html) for Python

It can be triggered by push and pull requests.

For further information and guidance about setup and various inputs, please see sections dedicated to each language ([**C++**](https://github.com/JacobDomagala/StaticAnalysis#c++) and [**Python**](https://github.com/JacobDomagala/StaticAnalysis#python))

## Pull Request comment

Created comment will contain code snippets with the issue description. When this action is run for the first time, the comment with the initial result will be created for current Pull Request. Consecutive runs will edit this comment with updated status.

Note that it's possible that the amount of issues detected can make the comment's body to be greater than the GitHub's character limit per PR comment (which is 65536). In that case, the created comment will contain only the isues found up to that point, and the information that the limit of characters was reached.

## Output example (C++)
![output](https://github.com/JacobDomagala/StaticAnalysis/wiki/output_example.png)

## Non Pull Request

For non Pull Requests, the output will be printed to GitHub's output console. This behaviour can also be forced via `force_console_print` input.

## Output example (C++)
![output](https://github.com/JacobDomagala/StaticAnalysis/wiki/console_output_example.png)


<br><br>

# C++
While it's recommended that your project is CMake-based, it's not required (see the [**Inputs**](https://github.com/JacobDomagala/StaticAnalysis#inputs) section below). We also recommend using a ```.clang-tidy``` file in your root directory. If your project requires additional packages to be installed, you can use the `apt_pckgs` and/or `init_script` input variables to install them (see the [**Workflow example**](https://github.com/JacobDomagala/StaticAnalysis#workflow-example) or [**Inputs**](https://github.com/JacobDomagala/StaticAnalysis#inputs) sections below). If your repository allows contributions from forks, you must use this Action with the `pull_request_target` trigger event, as the GitHub API won't allow PR comments otherwise.

By default, **cppcheck** runs with the following flags:
```--enable=all --suppress=missingInclude --inline-suppr --inconclusive```
You can use the `cppcheck_args` input to set your own flags.

**clang-tidy** looks for the ```.clang-tidy``` file in your repository, but you can also set checks using the `clang_tidy_args` input.


## Workflow example

```yml
name: Static analysis

on:
  # Will run on push when merging to 'branches'. The output will be shown in the console
  push:
    branches:
      - develop
      - master
      - main

  # 'pull_request_target' allows this Action to also run on forked repositories
  # The output will be shown in PR comments (unless the 'force_console_print' flag is used)
  pull_request_target:
    branches:
      - "*"

jobs:
  static_analysis:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: setup init_script
      shell: bash
      run: |
        echo "#!/bin/bash

        # Input args provided by StaticAnalysis action
        root_dir=\${1}
        build_dir=\${2}
        echo \"Hello from the init script! First arg=\${root_dir} second arg=\${build_dir}\"

        add-apt-repository ppa:oibaf/graphics-drivers
        apt update && apt upgrade
        apt install -y libvulkan1 mesa-vulkan-drivers vulkan-utils" > init_script.sh

    - name: Run static analysis
      uses: JacobDomagala/StaticAnalysis@master
      with:
        language: c++

        # Exclude any issues found in ${Project_root_dir}/lib
        exclude_dir: lib

        use_cmake: true

        # Additional apt packages that need to be installed before running Cmake
        apt_pckgs: software-properties-common libglu1-mesa-dev freeglut3-dev mesa-common-dev

        # Additional script that will be run (sourced) AFTER 'apt_pckgs' and before running Cmake
        init_script: init_script.sh

        # (Optional) clang-tidy args
        clang_tidy_args: -checks='*,fuchsia-*,google-*,zircon-*,abseil-*,modernize-use-trailing-return-type'

        # (Optional) cppcheck args
        cppcheck_args: --enable=all --suppress=missingInclude
```

## Inputs

| Name                    | Description                        | Default value |
|-------------------------|------------------------------------|---------------|
| `github_token`          | Github token used for Github API requests |`${{github.token}}`|
| `pr_num`                | Pull request number for which the comment will be created |`${{github.event.pull_request.number}}`|
| `comment_title`         | Title for comment with the raport. This should be an unique name | `Static analysis result` |
| `exclude_dir`           | Directory which should be excluded from the raport | `<empty>` |
| `apt_pckgs`             | Additional (space separated) packages that need to be installed in order for project to compile | `<empty>` |
| `init_script`           | Optional shell script that will be run before configuring project (i.e. running CMake command). This should be used, when the project requires some environmental set-up beforehand. Script will be run with 2 arguments: `root_dir`(root directory of user's code) and `build_dir`(build directory created for running SA). Note. `apt_pckgs` will run before this script, just in case you need some packages installed. Also this script will be run in the root of the project (`root_dir`) | `<empty>` |
| `cppcheck_args`         | Cppcheck (space separated) arguments that will be used |`--enable=all --suppress=missingInclude --inline-suppr --inconclusive`|
| `clang_tidy_args`       | clang-tidy arguments that will be used (example: `-checks='*,fuchsia-*,google-*,zircon-*'` |`<empty>`|
| `report_pr_changes_only`| Only post the issues found within the changes introduced in this Pull Request. This means that only the issues found within the changed lines will po posted. Any other issues caused by these changes in the repository, won't be reported, so in general you should run static analysis on entire code base  |`false`|
| `use_cmake`             | Determines wether CMake should be used to generate compile_commands.json file | `true` |
| `cmake_args`            | Additional CMake arguments |`<empty>`|
| `force_console_print`   | Output the action result to console, instead of creating the comment |`false`|

**NOTE: `apt_pckgs` will run before `init_script`, just in case you need some packages installed before running the script**

<br><br>

# Python


## Workflow example

```yml
name: Static analysis

on:
  push:
    branches:
      - master
  pull_request:

jobs:
  check:
    name: Run Linter
    runs-on: ubuntu-20.04
    steps:
      - uses: actions/checkout@v3

      - name: CodeQuality
        uses: JacobDomagala/StaticAnalysis@master
        with:
          language: "Python"
          pylint_args: "--rcfile=.pylintrc --recursive=true"
          python_dirs: "src test"
```

## Inputs

| Name                    | Description                        | Default value |
|-------------------------|------------------------------------|---------------|
| `github_token`          | Github token used for Github API requests |`${{github.token}}`|
| `pr_num`                | Pull request number for which the comment will be created |`${{github.event.pull_request.number}}`|
| `comment_title`         | Title for comment with the raport. This should be an unique name | `Static analysis result` |
| `exclude_dir`           | Directory which should be excluded from the raport | `<empty>` |
| `apt_pckgs`             | Additional (space separated) packages that need to be installed in order for project to compile | `<empty>` |
| `init_script`           | Optional shell script that will be run before configuring project (i.e. running CMake command). This should be used, when the project requires some environmental set-up beforehand. Script will be run with 2 arguments: `root_dir`(root directory of user's code) and `build_dir`(build directory created for running SA). Note. `apt_pckgs` will run before this script, just in case you need some packages installed. Also this script will be run in the root of the project (`root_dir`) | `<empty>` |
| `pylint_args`         | Pylint (space separated) arguments that will be used |`<empty>`|
| `python_dirs`     | Directories that contain python files to be checked | `<empty>` |
| `report_pr_changes_only`| Only post the issues found within the changes introduced in this Pull Request. This means that only the issues found within the changed lines will po posted. Any other issues caused by these changes in the repository, won't be reported, so in general you should run static analysis on entire code base  |`false`|
| `force_console_print`   | Output the action result to console, instead of creating the comment |`false`|

**NOTE: `apt_pckgs` will run before `init_script`, just in case you need some packages installed before running the script**
