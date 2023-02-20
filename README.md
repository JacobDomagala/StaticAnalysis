[![Linter](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/linter.yml/badge.svg?branch=master)](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/linter.yml?query=branch%3Amaster)
[![Test Action](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/test_action.yml/badge.svg?branch=master)](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/test_action.yml?query=branch%3Amaster)
[![Unit Tests](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/unit_tests.yml/badge.svg?branch=master)](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/unit_tests.yml?query=branch%3Amaster)

# Static Analysis

GitHub action for C++ project, that runs [cppcheck](http://cppcheck.sourceforge.net/) and [clang-tidy](https://clang.llvm.org/extra/clang-tidy/). This action works on both push and pull requests.

It's recommended that your project is CMake based, but it's not required (see **Inputs** section below). Also it's recommended to use ```.clang-tidy``` file, which should be located in your root directory. If your project requires some additional packages to be installed, you can use `apt_pckgs` and/or `init_script` input variables to install them (see the **Workflow example** or **Inputs** sections below). Also, if your repository should allow contribiutions from forks, then it's required to use this Action with `pull_request_target` trigger event, otherwise the GitHub API won't allow to create PR comments.

- **cppcheck** will run with the following default flags: </br>
```--enable=all --suppress=missingInclude --inline-suppr --inconclusive```
You can use `cppcheck_args` input to set your flags.

- **clang-tidy** will look for the ```.clang-tidy``` file in your repository, or you can set checks via `clang_tidy_args` input.

## Pull Request comment

Created comment will contain code snippets with the issue description. When this action is run for the first time, the comment with the initial result will be created for current Pull Request. Consecutive runs will edit this comment with updated status.

Note that it's possible that the amount of issues detected can make the comment's body to be greater than the GitHub's character limit per PR comment (which is 65536). In that case, the created comment will contain only the isues found up to that point, and the information that the limit of characters was reached.

### Output example
![output](https://github.com/JacobDomagala/StaticAnalysis/wiki/output_example.png)

## Non Pull Request

For non Pull Requests, the output will be printed to GitHub's output console. This behaviour can also be forced via `force_console_print` input.

### Output example
![output](https://github.com/JacobDomagala/StaticAnalysis/wiki/console_output_example.png)

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

| Name                    |Required| Description                        | Default value |
|-------------------------|--------|------------------------------------|:---------------:|
| `github_token`          | FALSE  | Github token used for Github API requests |`${{github.token}}`|
| `pr_num`                | FALSE  | Pull request number for which the comment will be created |`${{github.event.pull_request.number}}`|
| `comment_title`         | FALSE  | Title for comment with the raport. This should be an unique name | `Static analysis result` |
| `exclude_dir`           | FALSE  | Directory which should be excluded from the raport | `<empty>` |
| `apt_pckgs`             | FALSE  | Additional (space separated) packages that need to be installed in order for project to compile | `<empty>` |
| `init_script`           | FALSE  | Optional shell script that will be run before configuring project (i.e. running CMake command). This should be used, when the project requires some environmental set-up beforehand. Script will be run with 2 arguments: `root_dir`(root directory of user's code) and `build_dir`(build directory created for running SA). Note. `apt_pckgs` will run before this script, just in case you need some packages installed. Also this script will be run in the root of the project (`root_dir`) | `<empty>` |
| `cppcheck_args`         | FALSE  | Cppcheck (space separated) arguments that will be used |`--enable=all --suppress=missingInclude --inline-suppr --inconclusive`|
| `clang_tidy_args`       | FALSE  | clang-tidy arguments that will be used (example: `-checks='*,fuchsia-*,google-*,zircon-*'` |`<empty>`|
| `report_pr_changes_only`| FALSE  | Only post the issues found within the changes introduced in this Pull Request. This means that only the issues found within the changed lines will po posted. Any other issues caused by these changes in the repository, won't be reported, so in general you should run static analysis on entire code base  |`false`|
| `use_cmake`             | FALSE  | Determines wether CMake should be used to generate compile_commands.json file | `true` |
| `cmake_args`            | FALSE  | Additional CMake arguments |`<empty>`|
| `force_console_print`   | FALSE  | Output the action result to console, instead of creating the comment |`false`|



### **NOTE: `apt_pckgs` will run before `init_script`, just in case you need some packages installed before running the script**
