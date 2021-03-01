## Misbehaviour and Solutions for Windows

- Make sure that you are not in any other virtual env (anaconda, ...):

```
(ohsome-quality-analyst) C:\Users\user\ohsome-quality-analyst> deactivate
C:\Users\user\ohsome-quality-analyst>
```

- Error: `ModuleNotFoundError: No module named 'ohsome_quality_analyst'`
    - Make sure virtual environment is activated: `poetry shell`

- Connection to the database fails
    - Make sure you are in the `VPN` of the university
    - Check if the variables are in your environment. Try the following code:

```python
import os 
print(os.getenv("POSTGRES_HOST"))
print(os.getenv("POSTGRES_PORT"))
print(os.getenv("POSTGRES_DB"))
print(os.getenv("POSTGRES_USER"))
print(os.environ["POSTGRES_PASSWORD"])
```

If the variables are not as expected, make sure your system updated access (close command line and open a new one and enter the lines again / restart pycharm).
