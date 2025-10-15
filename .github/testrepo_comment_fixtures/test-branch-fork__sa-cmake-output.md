## <p align="center"><b> :zap: SA CMake output :zap: </b></p>

<details> <summary> <b> :red_circle: cppcheck found 12 issues! Click here to see details. </b> </summary> <br>

------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/another.cpp](https://github.com/JacobDTest/TestRepo/blob/<SHA>/another.cpp#L1)
```c++
#include <stdio.h> <---- HERE

int evaluate(int x) {
    // Create a large number of branches.

```

```diff
!Line: 0 - information: Limiting analysis of branches. Use --check-level=exhaustive to analyze all branches. [normalCheckLevelMaxBranches]

```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/new_file.cpp](https://github.com/JacobDTest/TestRepo/blob/<SHA>/new_file.cpp#L30)
```c++
    int getElement(int index) { <---- HERE
        // Improper bounds checking: if index is invalid, returns -1.
        // A static analyzer might flag this for potential misuse.
        if (index < 0 || index >= size_) {
            return -1;

```

```diff
!Line: 30 - style: inconclusive: Technically the member function 'DataProcessor::getElement' can be const. [functionConst]

```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/new_file.cpp](https://github.com/JacobDTest/TestRepo/blob/<SHA>/new_file.cpp#L9)
```c++
        data_ = new int[size_];  // Dynamic allocation (potential memory leak) <---- HERE
    }

    // Destructor intentionally missing delete[] to trigger memory leak warning.
    ~DataProcessor() {

```

```diff
!Line: 9 - warning: Class 'DataProcessor' does not have a copy constructor which is recommended since it has dynamic memory/resource allocation(s). [noCopyConstructor]

```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/new_file.cpp](https://github.com/JacobDTest/TestRepo/blob/<SHA>/new_file.cpp#L9)
```c++
        data_ = new int[size_];  // Dynamic allocation (potential memory leak) <---- HERE
    }

    // Destructor intentionally missing delete[] to trigger memory leak warning.
    ~DataProcessor() {

```

```diff
!Line: 9 - warning: Class 'DataProcessor' does not have a operator= which is recommended since it has dynamic memory/resource allocation(s). [noOperatorEq]

```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/new_file.cpp](https://github.com/JacobDTest/TestRepo/blob/<SHA>/new_file.cpp#L8)
```c++
    DataProcessor(int size) : size_(size) { <---- HERE
        data_ = new int[size_];  // Dynamic allocation (potential memory leak)
    }

    // Destructor intentionally missing delete[] to trigger memory leak warning.

```

```diff
!Line: 8 - style: Class 'DataProcessor' has a constructor with 1 argument that is not explicit. [noExplicitConstructor]

```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/new_file.cpp](https://github.com/JacobDTest/TestRepo/blob/<SHA>/new_file.cpp#L40)
```c++
    int* data_; <---- HERE
    int size_;
};

int main() {

```

```diff
!Line: 40 - style: Class 'DataProcessor' is unsafe, 'DataProcessor::data_' can leak by wrong usage. [unsafeClassCanLeak]

```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/new_file.cpp](https://github.com/JacobDTest/TestRepo/blob/<SHA>/new_file.cpp#L59)
```c++
    if (b == 0) { <---- HERE
        std::cerr << "Warning: Division by zero avoided" << std::endl;
    } else {
        std::cout << "Division result: " << a / b << std::endl;
    }

```

```diff
!Line: 59 - style: The comparison 'b == 0' is always true. [knownConditionTrueFalse]

!Line: 58 - note: 'b' is assigned value '0' here.
!Line: 59 - note: The comparison 'b == 0' is always true.
```



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/new_file.cpp](https://github.com/JacobDTest/TestRepo/blob/<SHA>/new_file.cpp#L58)
```c++
    int a = 10, b = 0; <---- HERE
    if (b == 0) {
        std::cerr << "Warning: Division by zero avoided" << std::endl;
    } else {
        std::cout << "Division result: " << a / b << std::endl;

```

```diff
!Line: 58 - style: The scope of the variable 'a' can be reduced. [variableScope]

```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/new_file.cpp](https://github.com/JacobDTest/TestRepo/blob/<SHA>/new_file.cpp#L55)
```c++
    std::cout << "Uninitialized value: " << uninitialized << std::endl; <---- HERE

    // Intentional potential division by zero.
    int a = 10, b = 0;
    if (b == 0) {

```

```diff
!Line: 55 - error: Uninitialized variable: uninitialized [uninitvar]

```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/new_file.cpp](https://github.com/JacobDTest/TestRepo/blob/<SHA>/new_file.cpp#L54)
```c++
    int uninitialized; <---- HERE
    std::cout << "Uninitialized value: " << uninitialized << std::endl;

    // Intentional potential division by zero.
    int a = 10, b = 0;

```

```diff
!Line: 54 - style: Variable 'uninitialized' is not assigned a value. [unassignedVariable]

```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/source.cpp](https://github.com/JacobDTest/TestRepo/blob/<SHA>/source.cpp#L2)
```c++
    int anotherUnused; <---- HERE
}

int main(int /*argc*/, char** argv){
    int unused = 0;

```

```diff
!Line: 2 - style: Unused variable: anotherUnused [unusedVariable]

```
 <br>



------

 <b><i>Issue found in file</b></i> [JacobDTest/TestRepo/source.cpp](https://github.com/JacobDTest/TestRepo/blob/<SHA>/source.cpp#L6)
```c++
    int unused = 0; <---- HERE
    return 0;

```

```diff
!Line: 6 - style: Variable 'unused' is assigned a value that is never used. [unreadVariable]

```
 <br>
 </details>

 ***
