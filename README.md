# Compile Result

The Compile Result GitHub action parses the build output for C/C++ based applications and creates a comment for the pull request with any issues found. The created comment will contain code snippets with a description of the issues found. When this action is run for the first time, the comment with the initial result will be created for the current pull request. Subsequent runs will edit this comment with an updated status.

## Output example
![output](https://github.com/JacobDomagala/CompileResult/wiki/example_output.png)

## Workflow example

```yml
name: Build on Ubuntu

on: [pull_request]

jobs:
  Compile:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Setup
      shell: bash
      run: cmake -E make_directory ${{runner.workspace}}/build
    - name: Build
      working-directory: ${{runner.workspace}}/build
      shell: bash
      run: |
        cmake $GITHUB_WORKSPACE
        cmake --build . 2> >(tee "output.txt")
    - name: Post PR comment for warnings/errors
      if: always()
      uses: JacobDomagala/CompileResult@master
      with:
        comment_title: UBUNTU COMPILE RESULT
        compile_result_file: ${{runner.workspace}}/build/output.txt
```

## Inputs

| Name                    |Required| Description                        | Default value |
|-------------------------|--------|------------------------------------|:---------------:|
| `compile_result_file`   | TRUE   | The file that contains the compilation result | `empty` |
| `compiler`              | TRUE   | The compiler that was used to produce the output (MSVC/GNU/CLANG) | `GNU` |
| `token`                 | TRUE   | GITHUB_TOKEN or a repo scoped PAT | `${{github.token}}` |
| `work_dir`              | TRUE   | The action work directory | `${{github.workspace}}` |
| `exclude_dir`           | FALSE  | The full path to the directory that should be ignored | `<empty>` |
| `pull_request_number`   | TRUE   | The Github Pull Request number | `${{github.event.pull_request.number}}` |
| `comment_title`         | TRUE   | The comment title that will be displayed on top of the comment. It is also used to determine whether the comment already exists and should be edited or not. | `COMPILE RESULT` |
| `num_lines_to_display`  | FALSE  | The number of lines for the code snippet that will be displayed for each error/warning | `5` |



