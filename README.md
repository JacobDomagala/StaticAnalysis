[![Linter](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/linter.yml/badge.svg?branch=master)](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/linter.yml?query=branch%3Amaster)
[![Test Action](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/test_action.yml/badge.svg?branch=master)](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/test_action.yml?query=branch%3Amaster)
[![Unit Tests](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/unit_tests.yml/badge.svg?branch=master)](https://github.com/JacobDomagala/StaticAnalysis/actions/workflows/unit_tests.yml?query=branch%3Amaster)

# Static Analysis

This GitHub Action is designed for **C++ and Python projects** and performs static analysis using:
* [cppcheck](http://cppcheck.sourceforge.net/) and [clang-tidy](https://clang.llvm.org/extra/clang-tidy/) for C++
* [pylint](https://pylint.readthedocs.io/en/latest/index.html) for Python

It can be triggered by push and pull requests.

For further information and guidance on setup and various inputs, please see the sections dedicated to each language ([**C++**](https://github.com/JacobDomagala/StaticAnalysis?tab=readme-ov-file#c) and [**Python**](https://github.com/JacobDomagala/StaticAnalysis?tab=readme-ov-file#python)).

---

## Pull Request Comment

The created comment will include code snippets and issue descriptions. When this action runs for the first time on a pull request, it creates a comment with the initial analysis results. Subsequent runs will update this same comment with the latest status.

Note that the number of detected issues might cause the comment's body to exceed GitHub's character limit (currently 65,536 characters) per PR comment. If this occurs, the comment will contain issues up to the limit and indicate that the character limit was reached.

---

## Output Example (C++)
![output](https://github.com/JacobDomagala/StaticAnalysis/wiki/output_example.png)

---

## Non-Pull Request Events

For non-pull request events, the output will be printed directly to the GitHub Actions console. This behavior can also be forced using the `force_console_print` input.

---

## Output Example (C++)
![output](https://github.com/JacobDomagala/StaticAnalysis/wiki/console_output_example.png)

---

# C++

While it's recommended that your project is CMake-based, it's not strictly required (see the [**Inputs**](https://github.com/JacobDomagala/StaticAnalysis#inputs) section below). We also recommend using a `.clang-tidy` file in your repository's root directory. If your project requires additional packages, you can install them using the `apt_pckgs` and/or `init_script` input variables (see the [**Workflow example**](https://github.com/JacobDomagala/StaticAnalysis#workflow-example) or [**Inputs**](https://github.com/JacobDomagala/StaticAnalysis#inputs) sections below). If your repository allows contributions from forks, you must use this Action with the `pull_request_target` trigger event, as the GitHub API won't allow PR comments otherwise.

By default, **cppcheck** runs with the following flags:
```--enable=all --suppress=missingIncludeSystem --inline-suppr --inconclusive```
You can use the `cppcheck_args` input to set your own flags.

**Clang-Tidy** looks for a `.clang-tidy` file in your repository, but you can also specify checks using the `clang_tidy_args` input.

---

## Using a Custom `compile_commands.json` File

You can use a pre-generated `compile_commands.json` file with the `compile_commands` input. This is incredibly useful when you need **more control over your compilation database**, whether you're working with a complex build system, have a specific build configuration, or simply want to reuse a file generated elsewhere.

When using a custom `compile_commands.json` with this GitHub Action, you'll encounter a common technical challenge: a **mismatch between the directory where the file was originally generated and the path used by this GitHub Action** (specifically, inside its Docker container). This means the source file paths listed in your `compile_commands.json` might not be valid from the container's perspective.

To resolve this, you have two main options:

* **Manually replace the prefixes** in your `compile_commands.json` file (for example, change `/original/path/to/repo` to `/github/workspace`). This method gives you complete control over the path adjustments.
* **Let the action try to replace the prefixes for you.** For simpler directory structures, you can enable this convenient feature using the `compile_commands_replace_prefix` input.

---

Beyond path adjustments, another important consideration when using a custom `compile_commands.json` file is **dependency resolution** for your static analysis tools. `clang-tidy` performs deep semantic analysis, which means it requires all necessary include files and headers to be found and accessible during its run. If these dependencies are missing or incorrectly referenced, `clang-tidy` may stop analyzing the affected file, leading to incomplete results. In contrast, `cppcheck` is generally more resilient to missing include paths, as it primarily focuses on lexical and syntactic analysis rather than full semantic parsing.

---

## Workflow Example

```yml
name: Static Analysis

on:
  # Runs on 'push' events to specified branches. Output will be printed to the console.
  push:
    branches:
      - develop
      - master
      - main

  # Uses 'pull_request_target' to allow analysis of forked repositories.
  # Output will be shown in PR comments (unless 'force_console_print' is used).
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
        apt update && apt upgrade -y
        apt install -y libvulkan1 mesa-vulkan-drivers vulkan-utils" > init_script.sh

    - name: Run Static Analysis
      uses: JacobDomagala/StaticAnalysis@master
      with:
        language: c++

        # Exclude any issues found in ${Project_root_dir}/lib
        exclude_dir: lib

        use_cmake: true

        # Additional apt packages required before running CMake
        apt_pckgs: software-properties-common libglu1-mesa-dev freeglut3-dev mesa-common-dev

        # Optional shell script that runs AFTER 'apt_pckgs' and before CMake
        init_script: init_script.sh

        # Optional Clang-Tidy arguments
        clang_tidy_args: -checks='*,fuchsia-*,google-*,zircon-*,abseil-*,modernize-use-trailing-return-type'

        # Optional Cppcheck arguments
        cppcheck_args: --enable=all --suppress=missingIncludeSystem
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
| `cppcheck_args`         | Cppcheck (space separated) arguments that will be used |`--enable=all --suppress=missingIncludeSystem --inline-suppr --inconclusive`|
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
