# Test for gRPC Server

## Create an environment for executing gRPC client/server

This guide gets you started with gRPC in Python with a simple working example.

Prerequisites
1. Python 3.7 or higher
2. pip version 9.0.1 or higher

If necessary, upgrade your version of pip:
```
$ python -m pip install --upgrade pip
```
If you cannot upgrade pip due to a system-owned installation, you can run the example in a virtualenv:
```
$ python -m pip install virtualenv
$ virtualenv venv
$ source venv/bin/activate
$ python -m pip install --upgrade pip
```
gRPC 
Install gRPC:
```
$ python -m pip install grpcio
```
Or, to install it system wide:
```
$ sudo python -m pip install 
```

## Our work

Work type & Approaches
1. Unit Test
2. Fuzzing

Test target : Server/client architecture using gRPC.
Expected result
* Unit Test : 
    * The service works fine in different situations and returns expected results.
    * This includes verifying that the gRPC code handles input and output correctly and handles exceptions.
* Fuzzing :
    * Expected fuzz testing will use a variety of different inputs, including invalid, abnormal, and unexpected inputs, to check whether gRPC services can handle these situations correctly and respond to errors appropriately.
