## Miss behaviour and solutions for Windows

- Make sure that you are not in any other virtual env (anaconda, ..):

```
(ohsome-quality-tool) C:\Users\user\ohsome-quality-tool> deactivate
C:\Users\user\ohsome-quality-tool>
```

- Error: ModuleNotFoundError: No module named 'ohsome_quality_tool'
    - Make sure virtual environment is activated: `poetry shell`

- Connection to the database fails
    - Make sure you are in the `VPN` of the university
    - Check if the variables are in yur environment. Try following code:

```python
import os 
print(os.getenv("POSTGRES_HOST"))
print(os.getenv("POSTGRES_PORT"))
print(os.getenv("POSTGRES_DB"))
print(os.getenv("POSTGRES_USER"))
print(os.environ["POSTGRES_PASSWORD"])
```

If the variables are not as expected, make sure your system updated access (close command line and open a new one and enter the lines again / restart pycharm).
