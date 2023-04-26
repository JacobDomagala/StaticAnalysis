# Compile Result

The Compile Result GitHub action parses build output for C/C++ based applications and creates a comment on the pull request with any issues found. The generated comment includes code snippets alongside descriptions of the identified issues. When this action runs for the first time, it creates a comment with the initial results for the current pull request. Subsequent runs will edit this comment to update the status.

## Output Example
![output](https://github.com/JacobDomagala/CompileResult/wiki/example_output.png)

## Workflow Example

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

| Name                    | Required | Description                                          | Default value          |
|-------------------------|----------|------------------------------------------------------|:----------------------:|
| `compile_result_file`   | TRUE     | The file containing the compilation results          | `empty`                |
| `compiler`              | TRUE     | The compiler used to produce the output (MSVC/GNU/CLANG) | `GNU`                |
| `token`                 | TRUE     | GITHUB_TOKEN or a repo-scoped PAT                    | `${{github.token}}`    |
| `work_dir`              | TRUE     | The action work directory                            | `${{github.workspace}}`|
| `exclude_dir`           | FALSE    | The full path to the directory to be ignored         | `<empty>`              |
| `pull_request_number`   | TRUE     | The GitHub Pull Request number                       | `${{github.event.pull_request.number}}`|
| `comment_title`         | TRUE     | The comment title displayed at the top of the comment. It is also used to determine whether the comment already exists and should be edited or not. | `COMPILE RESULT` |
| `num_lines_to_display`  | FALSE    | The number of lines for the code snippet displayed for each error/warning | `5` |
