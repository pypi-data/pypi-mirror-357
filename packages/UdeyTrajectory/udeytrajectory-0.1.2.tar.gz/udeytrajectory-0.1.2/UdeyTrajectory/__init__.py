import json
from importlib.resources import files

def get_trajectory(index):
    path = files("UdeyTrajectory").joinpath(f"pattern{index}.json")
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

data = get_trajectory(1)
print(data)