# Static Analysis

GitHub action for CMake based C++ project, that runs [Cppcheck](http://cppcheck.sourceforge.net/) and [clang-tidy](https://clang.llvm.org/extra/clang-tidy/), and creates comment for PR with any issues found. Created comment will contain code snippets with the issue description. When this action is run for the first time, the comment with the initial result will be created for current Pull Request. Consecutive runs will edit this comment with updated status.


Note that it's possible that the amount of issues detected can make the comment's body to be greater than the GitHub's character limit per PR comment (which is 65536). In that case, the created comment will contain only the isues found up to that point, and the information that the limit of characters was reached.


In order for this action to work properly, your project has to be CMake based and also include ```.clang-tidy``` file in your root directory. If your project requires some additional packages to be installed, you can use `apt_pckgs` and/or `init_script` input variables to install them (see the **Workflow example** or **Inputs** sections below)


- **Cppcheck** will run with the following default flags: </br>
```--enable=all --suppress=missingInclude --inline-suppr --inconclusive```
You can use `cppcheck_args` input to set your flags.

- **clang-tidy** will look for the ```.clang-tidy``` file in your repository.

## Workflow example

```yml
name: Static analysis

on: [pull_request]

jobs:
  static_analysis:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: setup init_script
      shell: bash
      run: |
        echo "#!/bin/bash
        add-apt-repository ppa:oibaf/graphics-drivers
        apt update
        apt upgrade
        apt install -y libvulkan1 mesa-vulkan-drivers vulkan-utils" > init_script.sh

    - name: Run static analysis
      uses: JacobDomagala/StaticAnalysis@master
      with:
        # Exclude any issues found in ${Project_root_dir}/lib
        exclude_dir: lib

        # Additional apt packages that need to be installed before running Cmake
        apt_pckgs: software-properties-common libglu1-mesa-dev freeglut3-dev mesa-common-dev

        # Additional script that will be run (sourced) AFTER 'apt_pckgs' and before running Cmake
        init_script: init_script.sh
```

## Inputs

| Name                    |Required| Description                        | Default value |
|-------------------------|--------|------------------------------------|:---------------:|
| `github_token`          | TRUE   | Github token used for Github API requests |`${{github.token}}`|
| `pr_num`                | TRUE   | Pull request number for which the comment will be created |`${{github.event.pull_request.number}}`|
| `comment_title`         | TRUE   | Title for comment with the raport. This should be an unique name | `Static analysis result` |
| `exclude_dir`           | FALSE  | Directory which should be excluded from the raport | `<empty>` |
| `apt_pckgs`             | FALSE  | Additional (space separated) packages that need to be installed in order for project to compile | `<empty>` |
| `init_script`           | FALSE  | Optional shell script that will be run before running CMake command. This should be used, when the project requires some environmental set-up beforehand. | `<empty>` |
| `cppcheck_args`         | TRUE   | Cppcheck (space separated) arguments that will be used |`--enable=all --suppress=missingInclude --inline-suppr --inconclusive`|
| `report_pr_changes_only`| FALSE  | Only post the issues found within the changes introduced in this Pull Request. This means that only the issues found within the changed lines will po posted. Any other issues caused by these changes in the repository, won't be reported, so in general you should run static analysis on entire code base  |`false`|



### **NOTE: `apt_pckgs` will run before `init_script`, just in case you need some packages installed before running the script**
