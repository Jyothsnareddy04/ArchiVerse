import json

FILE_PATH = r"C:\Users\jyoth\Desktop\Major-Project\Backend\datasets\raw\Interior\3D-FRONT\00110bde-f580-40be-b8bb-88715b338a2a.json"

with open(FILE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

print("\n================ TOP LEVEL =================\n")

for k, v in data.items():

    print(f"\nKEY : {k}")
    print(f"TYPE: {type(v)}")

    if isinstance(v, list):
        print(f"LENGTH: {len(v)}")

        if len(v) > 0:
            print("\nFIRST ITEM:\n")
            print(v[0])

    elif isinstance(v, dict):

        print("\nDICT KEYS:\n")
        print(v.keys())