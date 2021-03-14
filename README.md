# Static Analysis

GitHub action for CMake based C++ project, that runs cppcheck and clang-tidy, and creates comment for PR with any issues found. Created comment will contain code snippets with the issue description. When this action is run for the first time, the comment with the initial result will be created for current Pull Request. Consecutive runs will edit this comment with updated status.

Note that it's possible that the amount of issues detected can make the comment's body to be greater than the GitHub's character limit per PR comment (which is 65536). In that case, the created comment will contain only the isues found to that point and the information that the limit of characters was reached.

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

| Name                    |Required| Description                        | Default value |
|-------------------------|--------|------------------------------------|---------------|
| `github_token`          | TRUE   | Github token used for Github API requests | ${{ github.token }} |
| `pr_num`                | TRUE   | Pull request number for which the comment will be created | ${{ github.event.pull_request.number }} |
| `comment_title`         | TRUE   | Title for comment with the raport. This should be an unique name | `Static analysis result` |
| `exclude_dir`           | FALSE  | Directory which should be excluded from the raport | `empty` |
