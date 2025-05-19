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

We provide a script to run FuzzLi.

```
cd EmbeddedFuzzer
python main.py
```

The core functionality resides in the run method. FuzzLi performs the following steps:

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



## Core Files/Folders

| Module                  | Path                                                         |
| ----------------------- | ------------------------------------------------------------ |
| configuration           | fuzzli_tool\EmbeddedFuzzer\resources\config.json             |
| seed program generation | fuzzli_tool\EmbeddedFuzzer\src\Postprocessor\callable_processor.py |
| mutation                | fuzzli_tool\EmbeddedFuzzer\src\Mutator                       |
| differential testing    | fuzzli_tool\EmbeddedFuzzer\src\Harness.py                    |
| reducer                 | fuzzli_tool\EmbeddedFuzzer\src\Reducer                       |



## Bug List

Following double-blind reviewing, we are not sharing our bug list now. It will be made available after the paper is submitted.
