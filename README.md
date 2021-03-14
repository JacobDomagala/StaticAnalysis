# static-analysis-action

GitHub action for CMake based C++ project, that runs cppcheck and clang-tidy and creates comment for PR with any issues found.

## Workflow example

```yml
name: Static analysis

on: [pull_request]

jobs:
  graph:
    runs-on: ubuntu-latest
    steps:
    - name: Run static analysis
      uses: JacobDomagala/StaticAnalysis@master
      with:
        exclude_dir: dependencies
```

## Inputs

Following inputs can be used to customize the graph

| Name                    |Required| Description                        | Default value |
|-------------------------|--------|------------------------------------|---------------|
| `github_token`          | TRUE   | Github token used for Github API requests | ${{ github.token }} |
| `pr_num`                | TRUE   | Pull request number for which the comment will be created | ${{ github.event.pull_request.number }} |
| `comment_title`         | TRUE   | Title for comment with the raport. This should be an unique name | Static analysis result |
| `exclude_dir`           | FALSE  | Directory which should be excluded from the raport | <empty> |
