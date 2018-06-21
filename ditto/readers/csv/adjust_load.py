from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

try:
    import pandas as pd
except ImportError as e:
    print(
        "Pandas is not installed, please ensure that you install all of DiTTo's dependencies. Check the documentation for more information."
    )
    raise e

df = pd.read_csv("rnm_load.csv")
df["Load.phase_loads[0].phase"] = ""
df["Load.phase_loads[1].phase"] = ""
df["Load.phase_loads[2].phase"] = ""
df.loc[df.phases == 3, "Load.phase_loads[0].phase"] = "A"
df.loc[df.phases == 3, "Load.phase_loads[1].phase"] = "B"
df.loc[df.phases == 3, "Load.phase_loads[2].phase"] = "C"
df = df.drop("phases", 1)
df.to_csv("rnm_load_updated.csv", index=False)
