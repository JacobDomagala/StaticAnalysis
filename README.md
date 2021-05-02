# Compile Result

GitHub action parses the build output for C/C++ based application and creates comment for PR with any issues found. Created comment will contain code snippets with the issue description. When this action is run for the first time, the comment with the initial result will be created for current Pull Request. Consecutive runs will edit this comment with updated status.

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
| `compile_result_file`   | TRUE   | File which contains compilation result | `empty` |
| `compiler`              | TRUE   | Which compiler was used to produce the output. MSVC/GNU/CLANG | `GNU` |
| `token`                 | TRUE   | GITHUB_TOKEN or a repo scoped PAT | `${{github.token}}` |
| `work_dir`              | TRUE   | Action work directory | `${{github.workspace}}` |
| `exclude_dir`           | FALSE  | Full path to the directory that should be ignored | `<empty>` |
| `pull_request_number`   | TRUE   | Github Pull Request number | `${{github.event.pull_request.number}}` |
| `comment_title`         | TRUE   | Comment title that will be displayed on top of the comment. Used also to determine whether comment already exists and should be edited or not | `COMPILE RESULT` |
| `num_lines_to_display`  | FALSE  |Number of lines for code snippet which will be displayed for each error/warning | `5` |



