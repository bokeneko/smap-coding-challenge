# SMAP Python Developer Challenge

This is bokeneko's inplementation for [SMAP Python Developer Challenge](https://github.com/camenergydatalab/smap-coding-challenge)

## Requirements

- docker
- make (Maybe you already have it)

## How to start service

To start service, just execute following command:

```
make up
```

For first time you build service, you need to execute following command to initialize DB and import data:

```
make initdb
```

Now you can access to the service by following url:

```
http://localhost:8989/
```

## How to stop service

To stop service, execute following command:

```
make down
```

## How to clear image and volume

To clear all, execute following command:

```
make clean
make clean-none # Be careful. This will remove all 'none' image.
make clean-volume
```

## How to test

To test, execute following command:

```
make test
```
