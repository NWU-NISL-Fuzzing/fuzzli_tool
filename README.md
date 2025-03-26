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

```
cd EmbeddedFuzzer
python main.py
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

In accordance with double-blind reviewing, we are not sharing our bug list at this time. It will be made available after the paper is submitted.
