## <p align="center"><b> :zap: SA non-CMake output :zap: </b></p>

<details> <summary> <b> :red_circle: cppcheck found 6 issues! Click here to see details. </b> </summary> <br>

https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L9-L14
```diff
!Line: 9 - warning: Class 'Example' does not have a copy constructor which is recommended since it has dynamic memory/resource management. [noCopyConstructor]

```
 <br>



https://github.com/JacobDomagala/TestRepo/blob/<SHA>/source.cpp#L9-L14
```diff
!Line: 9 - warning: Class 'Example' does not have a operator= which is recommended since it has dynamic memory/resource management. [noOperatorEq]

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
