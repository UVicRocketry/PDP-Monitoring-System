# Installation Guide

## Comms Setup
The communication network of the system uses a websocket server over a local wifi network delivered by 2 TP-link CPE-710. Please check [comms setup](comms.md#setup) for more information.

## Server Installation

## Client Installation
[Ground Support Repository](https://github.com/UVicRocketry/Ground-Support)



# Style Guide

## Best Practices
`⚠️ 4 tab indentation ⚠️` Please change your IDE setting to match or I will hunt you down.
- **Code Readability**: Space out your code, look at the rest of the codebase and emulate the style.
- **Comments**: Do not over comment. Keep most of your comment to the doc string. The key to being a good programmer is to write code that is self-explanatory. After you write your code read it over and see if you can understand it without the comments. If you can't, rename variable, worst case add comments.
- **Function Length**: Keep functions short and to the point. If a function is longer than 50 lines, consider breaking it up into smaller functions.

### Modules
- **Imports**: Import modules at the top of the file. Use the following order:
    1. Standard Library Imports
    2. Related Third Party Imports
    3. Local Application/Library Specific Imports
- **Module Level Dunder Variables**: Place module level dunder variables at the top of the file.
    ```python
    __author__ = "Author Name"
    __version__ = "0.0.1"
    __name__ = "ModuleName"
    ```
- **Main Guard**: Use a main guard to protect the code that is run when the script is executed.
    ```python
    if __name__ == "ModuleName":
        # Code to run when the script is executed.
    ```
- **Doc String**: Include a docstring at the top of the file that describes the purpose of the module.
    ```python
    """
    Description of the module.
    """
    ```

## Naming Conventions

- **Variables**: `snake_case` - for variable names.
- **Functions**: `snake_case`- for function names.
- **Classes**: `PascalCase` - for class names.
- **Constants**: `UPPER_SNAKE_CASE` - for constants.

### Classes

- **Public Attributes**: `self.public` - named like any other variable.
- **Private Attributes**: `self.__private` - named with a 2 leading underscore.
- **Protected Attributes**: `self._protected` - named with a leading underscore.

- **Public Methods**: `def method_name(self):` - named like any other function.
- **Private Methods**: `def __method_name(self):` - named with a 2 leading underscore.
- **Protected Methods**: `def _method_name(self):` - named with a leading underscore.
- **Doc String**: Always include a docstring for every class and function. The docstring should be in the following format:
    ```python
    def function_name(arg1, arg2):
        """
        Description of the function.

        Args:
            arg1: Description of arg1.
            arg2: Description of arg2.

        Returns:
            Description of the return value.
        """
    ```
- **API Docs**: Create an API doc for each module that describes the purpose of the module, the classes and functions it contains, and how to use them.

# Developer Guide

## Serial Interface

A serial connection is used to communicate with both the controls system. The controls system uses a USB to connect to the arduino which starts stepper motors and solenoids which controls the valves. This document explains the commands that the arduino can receive and the response it will give and useful debugging strategies.

## Websocket Interface

## Testing Suite

