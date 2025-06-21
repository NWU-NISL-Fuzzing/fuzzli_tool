# FuzzLi

This is a fuzzer for lightweight JavaScript engines.



## Installment

1. Create a Docker image.

```
docker build -t fuzzli .
```

2. Create a Docker container.

```
docker run -d -it -p xxxx:22 --name fuzzli fuzzli:v1.0
```



## Usage

### Configuration

The configuration file is located at `resources/config.json`. You typically do not need to modify this file unless you want to customize the default settings.

### Running FuzzLi

We provide a script to run FuzzLi. Users can choose to execute it all at once or step by step.

To run FuzzLi in one go:

```
cd EmbeddedFuzzer
python main.py --step=0 --size=[INPUT A NUMBER]
```

To run FuzzLi step by step:

```
cd EmbeddedFuzzer
// 1. Obtain seed programs and mutate.
python main.py --step=1 --size=[INPUT A NUMBER]
// 2. Execute differential testing.
python main.py --step=2 --size=[INPUT A NUMBER]
// 3. Reduce anomalies.
python main.py --step=3 --size=[INPUT A NUMBER]
```

_**NOTE.** The `--size` parameter is optional. If omitted, the default value is `100`. If the input size exceeds the number of available results in the database, the program will use only the available results._

### Observing the Results

You can find the results for each step of FuzzLi in the database file you specified in the [configuration file](EmbeddedFuzzer/resources/config.json).


| Table Name | Description |
| ----------- | ----------- |
| Corpus | Extracted code fragments |
| DifferentialTestResults | Results of differential testing |
| Engines | Information of the tested JS engines |
| OriginalTestcases | Seed programs |
| Outputs | Execution results of test cases |
| Testcases | Mutated test cases |



## Introduction of Implementation of FuzzLi

For users interested in the internal workings of FuzzLi, we provide a brief overview of its implementation.

The entry point is `main.py`, where the core logic is handled by the `step0` method.

FuzzLi first generates seed programs using:

```
original_test_case = self.config.callable_processor.get_self_calling(simple)
```

It then mutates the seed program to produce a list of test cases:

```
mutated_test_case_list = self.mutationByFlag(flag, original_test_case)
```

The third step is differential testing.

```
differential_test_result = Result.differential_test(harness_result)
```

Finally, anomalies are simplified using the reducer:

```
simplified_test_case = self.config.reducer.reduce(harness_result)
```

The core modules are shown below.

| Module                  | Path                                                         |
| ----------------------- | ------------------------------------------------------------ |
| configuration           | EmbeddedFuzzer\resources\config.json             |
| seed program generation | EmbeddedFuzzer\src\Postprocessor\callable_processor.py |
| mutation                | EmbeddedFuzzer\src\Mutator                       |
| differential testing    | EmbeddedFuzzer\src\Harness.py                    |
| reducer                 | EmbeddedFuzzer\src\Reducer                       |



## Bug List

Following double-blind reviewing, we are not sharing our bug list now. It will be made available after the paper is accepted.
