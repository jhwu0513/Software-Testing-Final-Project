# Fuzzing testing e-Voting Server

In this section, we will be using [protofuzz](https://github.com/trailofbits/protofuzz) and [fuzzdb](https://github.com/fuzzdb-project/fuzzdb) to perform fuzzing tests on gRPC. The following will describe the usage.

## Usage

### Install protofuzz

- `git clone https://github.com/trailofbits/protofuzz.git`
- `cd protofuzz`
- `python3 setup.py install`

### Install fuzzdb

After install the protofuzz package, we need to download fuzzdb to specsific directory.

- Preferred method is to check out sources via git, new payloads are added frequently

  - git clone https://github.com/fuzzdb-project/fuzzdb.git --depth 1

- While in the FuzzDB dir, you can update your local repo with the command
  - git pull

After downloading and installing the required packages, the directory structure will be as shown in the figure.

![image](https://github.com/sheway/PChome-AutoBuy/assets/67420772/82aa28da-c7ac-43d4-b668-5ed1cd2f7691)

### Debugging

If you encounter the error message:

- protofuzz.pbimport.ProtocNotFound: Protobuf compiler not found
  - `sudo apt update `
  - `sudo apt install protobuf-compiler`
- RuntimeError: Could not import fuzzdb dependency files.
  - `export FUZZDB_DIR=/path/to/your/fuzzdb`

## Experiment result

The experimental results are as follows: for each sent gRPC packet, after inputting it in the specified format, the program uses fuzzdb to generate test data and performs fuzzing on the protocol buffer.

![image](https://github.com/sheway/PChome-AutoBuy/assets/67420772/ccc0b909-64e7-41ef-9aa5-18685e05a4f1)
