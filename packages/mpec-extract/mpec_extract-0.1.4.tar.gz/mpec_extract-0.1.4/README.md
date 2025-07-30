
Note: make sure that twine distribution is <= 6.0.1 to be compatible with pyproject.toml.

Note: out_data files need to be regenerated with the current library structure in place (i.e. the module, class, and 
function definitions). So the library needs to be created then used to generate new out_data files, before others can 
use it. (I have already done this for the current library structure, but if it changes, the out_data might need to be 
regenerated.)

-----

### Commands to build 

Remember to update the version number in the pyproject.toml file, and delete any old distributions. The twine upload 
will not work if there's any old versions around.

``` py -m build ```

This should create a dist folder with a tar.gz and a wheel build. 

### Commands to upload to PyPi or TestPyPi

``` py -m twine upload --repository testpypi dist/*```

``` py -m twine upload --repository pypi dist/*```

Note you'll need to create a PyPi and/or TestPyPi account and an API access token, and provide the token to twine, either via the 
commandline or via a .pypirc file. PyPi and TestPyPi are separate: they will require separate accounts and separate access tokens. 

If you choose to use a .pypirc file, an example is provided in this repo, but it needs to be placed in your local home 
directory, not the project directory!

### Commands to install the package

In general, you can find the correct command easily on the package webpage: 
- TestPyPi: https://test.pypi.org/project/mpec-extract/
- PyPi: https://pypi.org/project/mpec-extract/

The command should be something like: 

- Test PyPi: ``` pip install -i https://test.pypi.org/simple/ mpec-extract ```

- PyPi: ``` pip install mpec-extract ```
