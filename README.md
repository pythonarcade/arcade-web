# Welcome to arcade-web

arcade-web is a reimplementation of the [Arcade](https://github.com/pythonarcade/arcade) library which allows running games inside web browsers. This is made possible thanks to [Pyodide](https://github.com/pyodide/pyodide).

Currently, arcade-web exists as a separate package to Arcade, and the intention is to install one or the other. You would use the main Arcade package when running in a desktop environment(Windows, Mac, or Linux) and arcade-web when running in a browser via Pyodide. As of now, the two libraries should not be installed alongside each other, you will encounter problems if they are.

For more information on Arcade and it's usage, please visit the main [Arcade](https://github.com/pythonarcade/arcade) repo. arcade-web makes a currently best effort approach to maintain full API compatibility with Arcade.

## Current Status

Currently arcade-web is in the very early stages of development, and is not ready for general consumption by users. As such, it is not available on pypi yet, you may download a zip of this repository and install it into a pyodide environment manually if you wish to test out the library. You can also checkout the [experiments](https://github.com/pythonarcade/arcade-web-experiments) repository for some examples of how to include and use arcade-web in the meantime.

We do not currently have a solid timeline or roadmap of when a general release will be ready. In the meantime if you want to try out arcade-web, the experiments repo linked above is the best starting point to see how to use it in it's current form.

The library is currently under very rapid development and it's core structure is still very fluid, so nothing represented in either this repo or the experiments repo at this time should be taken as an indicator of how the final general release will be.