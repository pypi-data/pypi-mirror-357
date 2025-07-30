# brickproof-cli
CLI extension of Brickproof

## Installation

```sh
pip install brickproof-cli
```

## Useage

### Initialize Project

To initialize a brickproof project, run:

```sh
brickproof init
```

This will create a new `brickproof.toml` file, which you will edit for your own usecase. Running the `init` command multiple times will not overwrite your `brickproof.toml` file.


### Configre Databricks Connection

To configure connection credentials to your Databricks workspace, run:

```sh

brickproof configure

```

This command will prompt you to enter your databricks workspace url, personal access token, and profile name. These
will be written out to a `.bprc` file in your local directory. 

### Run Brickproof

To run a brickproof testing event, run:

```sh
brickproof run
```

To run with a specific configured profile, run:

```sh
brickproof run --p <MY_PROFILE>
```

### Version

To get the version of your brickproof instance, run:

```sh
brickproof version

```
