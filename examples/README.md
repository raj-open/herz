# Examples #

This folder contains example runs of the code on artificial data.

## Structure ##

```text
examples
│
├── setup
│   └── config.yaml
│
├── data
│   └── *.csv
│
├── output # will be generated
│   ├── *.html
│   └── *.png
│
└── README.md
```

In the setup folder, the application is configured
to deal with the data sets stored in the [examples/data](data/) folder.
These files must be in **\*.csv** format.

## Execution ##

Open up a bash terminal and execute

```bash
just build
```

and (ensuring no errors occcurred in this process) run

```bash
just run examples/setup/config.yaml
```

## Output ##

This will result in the files in the output folder.
Depending upon the settings in [examples/setup/config.yaml](setup/config.yaml),
either **.html** or **.png** graphics will be generated.
To view html-outputs, simply drag them into a web browser.
These are self-contained files
(i.e. they contain their own javascript and style definitions
and do not rely on external files).
