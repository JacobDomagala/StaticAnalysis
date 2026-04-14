## <p align="center"><b> :zap: Python :zap: </b></p>

<details> <summary> <b> :red_circle: PyLint found 6 issues! Click here to see details. </b> </summary> <br>

------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/file_with_errors.py](https://github.com/JacobDTest/TestRepo/blob/<SHA>/file_with_errors.py#L19)
```python
     <---- HERE
    # Run pylint on the provided files
    # You can adjust the options list below as needed
    args = files
    results = lint.Run(args, reporter=reporter, exit=False)

```

```diff
!Line: 19 - C0303: Trailing whitespace (trailing-whitespace)
```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/file_with_errors.py](https://github.com/JacobDTest/TestRepo/blob/<SHA>/file_with_errors.py#L24)
```python
     <---- HERE
    # Get the output as a string
    output_str = output.getvalue()
    output.close()
    return results.linter.msg_status, output_str

```

```diff
!Line: 24 - C0303: Trailing whitespace (trailing-whitespace)
```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/file_with_errors.py](https://github.com/JacobDTest/TestRepo/blob/<SHA>/file_with_errors.py#L41)
```python
     <---- HERE
    # Exit with the pylint status code to reflect analysis result
    sys.exit(exit_code)

if __name__ == "__main__":

```

```diff
!Line: 41 - C0303: Trailing whitespace (trailing-whitespace)
```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/file_with_errors.py](https://github.com/JacobDTest/TestRepo/blob/<SHA>/file_with_errors.py#L30)
```python
def main(): <---- HERE
    if len(sys.argv) < 2:
        print("Usage: {} <python_file.py> [<python_file2.py> ...]".format(sys.argv[0]))
        sys.exit(1)


```

```diff
!Line: 30 - C0116: Missing function or method docstring (missing-function-docstring)
```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/file_with_errors.py](https://github.com/JacobDTest/TestRepo/blob/<SHA>/file_with_errors.py#L32)
```python
        print("Usage: {} <python_file.py> [<python_file2.py> ...]".format(sys.argv[0])) <---- HERE
        sys.exit(1)

    files = sys.argv[1:]
    exit_code, report = run_pylint(files)

```

```diff
!Line: 32 - C0209: Formatting a regular string which could be an f-string (consider-using-f-string)
```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/file_with_errors.py](https://github.com/JacobDTest/TestRepo/blob/<SHA>/file_with_errors.py#L12)
```python
import io <---- HERE

def run_pylint(files):
    """Run pylint on the list of files and capture the output."""
    # Capture the output in a string buffer

```

```diff
!Line: 12 - C0411: standard import "io" should be placed before third party imports "pylint.lint", "pylint.reporters.text.TextReporter" (wrong-import-order)
```
 <br>
 </details>

 ***
