import os

from ab.pkg import bsw_env_vars


root = "__ab__"

for env_var in bsw_env_vars.read_text().splitlines():
    os.environ[env_var] = os.path.join(root, env_var)
