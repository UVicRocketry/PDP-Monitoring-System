# Installation Guide

## Comms Setup
The communication network of the system uses a websocket server over a local wifi network delivered by 2 TP-link CPE-710. Please check [comms setup](comms.md#setup) for more information on how to setup the system.

## Server Installation

Should be installed on the mini PC at the valve cart. For development purposes first clone this repository and install the dependencies. 

```bash
git clone https://github.com/UVicRocketry/PDP-Monitoring-System.git
cd PDP-Monitoring-System
pip install -r requirements.txt
```

You require python 3.11 (any version above should do) to run the server. If you don't have python 3.11.x go to the python website and download version 3.11.x. **Make sure to add python to your path.**

you can now start the server by running the following command:

```bash
cd VC/ && python3 main.py
```

## Client Installation
[Ground Support Repository](https://github.com/UVicRocketry/Ground-Support)

# Startup Guide

First connect over ssh to the mini PC [ssh info](comms.md#ssh-credentials). you'll need two terminals one for client (Ground-Support) and the other for the server (PDP-Monitoring-System). Then navigate to `~/Documents/Github` directory.  

In the first ssh terminal run the following commands to start the monitoring system:
```bash
cd /Documents/Github/
sh start_cart.sh
```

In the first ssh terminal run the following commands to start the monitoring system:

```bash
cd /Documents/Github/
sh start_valve.sh
```

The system is now running and can be accessed by connecting to the `UVR-PDP` network. The client can be accessed by going to `192.168.0.1:3000`.

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

A serial connection is used to communicate with both the controls system. The controls system uses a USB to connect to the arduino which starts stepper motors and solenoids which controls the valves. This section explains the commands that the arduino can receive and the response it will give and useful debugging strategies.

You can find the api documentation [here](serial-api.md).

## Websocket Interface
The websocket interface is used to communicate with the client. The client is a web service that displays the status of the valves and allows the user to control the valves. This section explains how to develop the websocket interface and how to test it.

You can find the api documentation [here](ws-api.md).

## Testing Suite

The testing framework has two types of tests, unit tests and feature tests. feature test are defined by a test case table and accomplish requirements tied with features. While unit tests, test integration points, and edge cases within the actual code. Test cases are either automated or physically done by the system. All unit tests are automated and done using the `unittest` built in python framework. 

All tests are prioritized. The prioritizes are used to determine the $/zeta$ index, which is the percentage which a given test accomplishes it's feature. Simply put the $/zeta$ index is a weighted average that takes into account prioritizes. Please check the [testing legend]("Docs/test-case-legend.pdf") for more details. 

You can run a testing suite through the following command. 

One Test Suite
```bash
python -m unittest tests/test_module.py
```

All the tests in the `tests` directory can be run using the following command. 
```bash
python -m unittest discover -s tests -p '*_test.py'
```

You can compute the zeta index for a given test suite given that the `test-completion-matrix-1.#.csv` for the corresponding feature is defined. using the following labels.

| Test Case ID | Priority type | Priority Importance |
|--------------|---------------|---------------------|

If you are unsure how how to name the labels check the [testing legend]("Docs/test-case-legend.pdf").

To generate the zetas run 

```bash
cd VC/tests && python feature_compeletion.py
```
### Automated Testing
A Automated testing script which will generate all the zetas for and attach the results from a given test suite to the `test-completion-matrix-1.#.csv` can be used with the following command.

TODO:
```bash
cd VC/tests && python automated_testing.py
```

### Creating A Feature Test Case

To create a test first you need to create a test case table. The test case table should follow the [testing legend]("Docs/test-case-legend.pdf").

Next create a corresponding `csv` file for the results of the test case. The `csv` file should be named `test-completion-matrix-1.#.csv` where `#` is the feature number.

Next you need to create a test case in the `tests` directory. The test case should be named `test_module.py` where `module` is the module you are testing.

Now you can write your test case. The test case should be a class that inherits from `unittest.TestCase`. Each test case should have a `setUp` method that initializes the test case and a `tearDown` method that cleans up after the test case. Each test case should have a `test` method that tests a specific feature of the module.

```python
import unittest

class TestModule(unittest.TestCase):
    def setUp(self):
        # Initialize the test case.
        pass

    def tearDown(self):
        # Clean up after the test case.
        pass

    def test_feature(self):
        # Test a specific feature of the module.
        pass
```

### Creating A Unit Test Case
all you need is to add test case IDs to the `test-completion-matrix-1.#.csv` file.

next you need to create a test case in the `tests` directory. The test case should be named `test_module.py` where `module` is the module you are testing.

Add your unit test to the feature test case. 

```python
import unittest

class TestModule(unittest.TestCase):
    def setUp(self):
        # Initialize the test case.
        pass

    def tearDown(self):
        # Clean up after the test case.
        pass

    def test_feature(self):
        # Test a specific feature of the module.
        pass

    def test_unit(self): <--- Add this
        # Test a specific feature of the module.
        pass
```