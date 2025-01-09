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
