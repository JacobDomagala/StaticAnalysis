## <p align="center"><b> :zap: SA CMake output :zap: </b></p>

<details> <summary> <b> :red_circle: cppcheck found 6 issues! Click here to see details. </b> </summary> <br>

https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L9-L14
```diff
!Line: 9 - warning: Class 'Example' does not have a copy constructor which is recommended since it has dynamic memory/resource allocation(s). [noCopyConstructor]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L9-L14
```diff
!Line: 9 - warning: Class 'Example' does not have a operator= which is recommended since it has dynamic memory/resource allocation(s). [noOperatorEq]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L36-L41
```diff
!Line: 36 - error: Null pointer dereference: ptr [nullPointer]

!Line: 35 - note: Assignment 'ptr=nullptr', assigned value is 0
!Line: 36 - note: Null pointer dereference
```



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L35-L40
```diff
!Line: 35 - style: Variable 'ptr' can be declared as pointer to const [constVariablePointer]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L39-L44
```diff
!Line: 39 - error: Out of bounds access in expression 'vec[10]' because 'vec' is empty. [containerOutOfBounds]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L41-L44
```diff
!Line: 41 - style: Unused variable: unusedvec [unusedVariable]

```
 <br>
 </details>

 ***
<details> <summary> <b> :red_circle: clang-tidy found 21 issues! Click here to see details. </b> </summary> <br>

https://github.com/JacobDomagala/TestRepo/blob/<SHA>/another_source.cpp#L1-L3
```diff
!Line: 1 - error: function 'do_nothing' can be made static or moved into an anonymous namespace to enforce internal linkage [misc-use-internal-linkage,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L2-L7
```diff
!Line: 2 - error: included header string is not used directly [misc-include-cleaner,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L5-L10
```diff
!Line: 5 - error: class 'Example' defines a non-default destructor but does not define a copy constructor, a copy assignment operator, a move constructor or a move assignment operator [cppcoreguidelines-special-member-functions,hicpp-special-member-functions,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L9-L14
```diff
!Line: 9 - error: 42 is a magic number; consider replacing it with a named constant [cppcoreguidelines-avoid-magic-numbers,readability-magic-numbers,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L11-L16
```diff
!Line: 11 - error: parameter name 'p' is too short, expected at least 3 characters [readability-identifier-length,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L21-L26
```diff
!Line: 21 - error: function 'divide' can be made static or moved into an anonymous namespace to enforce internal linkage [misc-use-internal-linkage,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L21-L26
```diff
!Line: 21 - error: parameter name 'a' is too short, expected at least 3 characters [readability-identifier-length,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L21-L26
```diff
!Line: 21 - error: parameter name 'b' is too short, expected at least 3 characters [readability-identifier-length,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L23-L28
```diff
!Line: 23 - error: do not use 'std::endl' with streams; use '\n' instead [performance-avoid-endl,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L30-L35
```diff
!Line: 30 - error: variable 'ex' of type 'Example' can be declared 'const' [misc-const-correctness,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L30-L35
```diff
!Line: 30 - error: variable name 'ex' is too short, expected at least 3 characters [readability-identifier-length,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L31-L36
```diff
!Line: 31 - error: variable 'x' of type 'int' can be declared 'const' [misc-const-correctness,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L31-L36
```diff
!Line: 31 - error: variable name 'x' is too short, expected at least 3 characters [readability-identifier-length,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L31-L36
```diff
!Line: 31 - error: 10 is a magic number; consider replacing it with a named constant [cppcoreguidelines-avoid-magic-numbers,readability-magic-numbers,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L32-L37
```diff
!Line: 32 - error: variable 'y' of type 'int' can be declared 'const' [misc-const-correctness,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L32-L37
```diff
!Line: 32 - error: variable name 'y' is too short, expected at least 3 characters [readability-identifier-length,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L33-L38
```diff
!Line: 33 - error: do not use 'std::endl' with streams; use '\n' instead [performance-avoid-endl,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L36-L41
```diff
!Line: 36 - error: do not use 'std::endl' with streams; use '\n' instead [performance-avoid-endl,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L39-L44
```diff
!Line: 39 - error: 10 is a magic number; consider replacing it with a named constant [cppcoreguidelines-avoid-magic-numbers,readability-magic-numbers,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L39-L44
```diff
!Line: 39 - error: do not use 'std::endl' with streams; use '\n' instead [performance-avoid-endl,-warnings-as-errors]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L41-L44
```diff
!Line: 41 - error: variable 'unusedvec' of type 'std::vector<int>' can be declared 'const' [misc-const-correctness,-warnings-as-errors]

```
 <br>
 </details><br>
