import os

LOADGPS_setvar = (
    "C",
    "DOC",
    "PAN",
    "MODEL",
    "CONFIG",
    "D",
    "P",
    "S",
    "U",
    "T",
)

root = "__ab__"

for env_var in LOADGPS_setvar:
    os.environ[env_var] = os.path.join(root, env_var)
