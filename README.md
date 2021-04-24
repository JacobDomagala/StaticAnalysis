# Static Analysis

GitHub action for CMake based C++ project, that runs cppcheck and clang-tidy, and creates comment for PR with any issues found. Created comment will contain code snippets with the issue description. When this action is run for the first time, the comment with the initial result will be created for current Pull Request. Consecutive runs will edit this comment with updated status.


Note that it's possible that the amount of issues detected can make the comment's body to be greater than the GitHub's character limit per PR comment (which is 65536). In that case, the created comment will contain only the isues found to that point and the information that the limit of characters was reached.


In order for this action to work properly, your project has to be CMake based and also include ```.clang-tidy``` file in your root directory. If your projects requires some additional packages to be installed, you can use `apt_pckgs` and/or `init_script` input variables to install them (see the **Workflow example** or **Inputs** sections below)


The **CPPCHECK** will run with the following default flags: </br>
```--enable=all --suppress=missingInclude --inline-suppr --inconclusive```
You can use `cppcheck_args` input to set your flags.

**clang-tidy** will look for the ```.clang-tidy``` file in your repository.

## Workflow example

```yml
name: Static analysis

on: [pull_request]

jobs:
  static analysis:
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
        exclude_dir: lib
        apt_pckgs: software-properties-common
        init_script: init_script.sh
```

## Inputs

| Name                    |Required| Description                        | Default value |
|-------------------------|--------|------------------------------------|:---------------:|
| `github_token`          | TRUE   | Github token used for Github API requests |`${{github.token}}`|
| `pr_num`                | TRUE   | Pull request number for which the comment will be created |`${{github.event.pull_request.number}}`|
| `comment_title`         | TRUE   | Title for comment with the raport. This should be an unique name | `Static analysis result` |
| `exclude_dir`           | FALSE  | Directory which should be excluded from the raport | `<empty>` |
| `apt_pckgs`             | FALSE  | Additional (comma separated) packages that need to be installed in order for project to compile | `<empty>` |
| `init_script`           | FALSE  | Optional shell script that will be run before running CMake command. This should be used, when the project requires some environmental set-up beforehand. | `<empty>` |
| `cppcheck_args`         | TRUE   | CPPCHECK (space separated) arguments that will be used |`--enable=all --suppress=missingInclude --inline-suppr --inconclusive`|



### **NOTE: `apt_pckgs` will run before `init_script`, just in case you need some packages installed before running the script**
