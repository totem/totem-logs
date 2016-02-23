# About
Command line interface (node based) to tail logs from log service.

# Installation
## Requirements
- nodejs (0.10.30+)

## Dependencies

```
npm install argparse ws
```

# Running

## Help (All options) 
```
node tail --help
```

## Example
Following command tails logs for fleet daemon:

```
node tail -u ws://<cluster-url> -s true -p fleetd
```

