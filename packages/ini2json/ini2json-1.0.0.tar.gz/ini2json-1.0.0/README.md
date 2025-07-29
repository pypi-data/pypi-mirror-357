# ini2json

**@readwithai** - [X](https://x.com/readwithai) - [blog](https://readwithai.substack.com/) - [machine-aided reading](https://www.reddit.com/r/machineAidedReading/) - [📖](https://readwithai.substack.com/p/what-is-reading-broadly-defined) [⚡️](https://readwithai.substack.com/s/technical-miscellany) [🖋️](https://readwithai.substack.com/p/note-taking-with-obsidian-much-of)

**ini2json** is a command-line tool to convert between INI files and JSON and back again (via **json2ini**)

You can use this together with other tooling to programmatically process and modify configuration files.

## Motivation

JSON is a widely used standard with a lot of tooling. Tools like [`gron`](https://github.com/tomnomnom/gron) and [`jq`](https://stedolan.github.io/jq/) make it quite easy to filter, grep, modify, and understand JSON from the command line. Many tools use INI-style configuration files for simplicity and readability — however, there is not as good tooling for INI files.

Instead of recreating tooling specifically for INI, ini2json translates INI files to and from JSON so you can leverage existing, powerful JSON tools.

The original motivation came when I wanted to run a program with a tweaked configuration file rather than copying the file by hand.

## Alternatives and prior work

I briefly searched GitHub and PyPI for similar tools. The ones I found were mostly written in C (making distribution more difficult) or did not provide a reverse command to convert JSON back to INI.

The idea of using paired commands for forward and reverse transformations was partly inspired by the `gron` and `ungron` commands in `gron`. This concept also echoes a notion in group theory in mathematics called conjugation.

[Git](https://git-scm.com/) provides tools to edit an INI-based config file from the command line via [`git config`](https://git-scm.com/docs/git-config).

## Installation
You can install ini2json using [pipx](https://github.com/pypa/pipx)

```bash
pipx install ini2json
```


## Usage
Convert an INI file to JSON

```bash
ini2json path/to/config.ini
```

Convert JSON back to INI:
```bash
json2ini path/to/config.json
```
Both programs will read from standard in with no arguments.


You can use these tool with Bash [process substitution](https://www.gnu.org/software/bash/manual/bash.html#Process-Substitution) feature `<()` to modify an ini configuration while a program is running.


```bash
program -f <(ini2json config.ini | jq '.parent.key1 = "newvalue"' | json2ini)
```


## License

[MIT](LICENSE)

## About me
I am **@readwithai**. I create tools for reading, research and agency sometimes using the markdown editor [Obsidian](https://readwithai.substack.com/p/what-exactly-is-obsidian).

I also create a [stream of tools](https://readwithai.substack.com/p/my-productivity-tools) that are related to carrying out my work. You might like to check some of them out if you like this tool.

I write about lots of things - including tools like this - on [X](https://x.com/readwithai).
My [blog](https://readwithai.substack.com/) is more about reading and research and agency.
*
