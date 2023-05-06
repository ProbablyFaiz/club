# Club

Club is a small CLI library for making local Google Apps Script development
a bit easier. Specifically, Club provides a way of managing and pushing
to multiple remotes for a single Clasp project without manually editing
`.clasp.json` files.

```
Usage: club [OPTIONS] COMMAND [ARGS]...

  A small counterpart CLI for Google Apps Script's clasp.

Options:
  --help  Show this message and exit.

Commands:
  init    Initialize the current directory as a club project.
  list    List the remote destinations for the project in the current directory.
  push    Push the project in the current directory to the remote destination(s).
  remove  Remove a remote destination for the project in the current directory.
  set     Add a remote destination for the project in the current directory.
```

## Installation

Club requires Python 3.6 or higher. To install, run:

```bash
git clone https://github.com/ProbablyFaiz/club
cd club
python3 -m pip install .
```

## Usage

At the top level of your project, run `club init` to initialize the project's Club configuration.
If you have a `scriptId` set in your `.clasp.json` file, Club will automatically set that as the
default remote, `main`. Otherwise, you can create any remote you want with `club set <remote> <scriptId>`.

Once you have a remote set, you can push to it with `club push <remote>`. If you don't specify a remote,
Club will push to the default remote, `main`, or the only remote if there is only one. To push to all
remotes simultaneously, use `club push --all`. To push to one or more remotes of your choice, use
`club push <remote1> <remote2> ...`.

To see all usage information and options, run `club <command> --help`.
