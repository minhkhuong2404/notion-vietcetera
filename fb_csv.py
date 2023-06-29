import pandas as pd
df = pd.read_json("./vi_VN.jsonl")

df.to_csv("./data.csv", index=None)
