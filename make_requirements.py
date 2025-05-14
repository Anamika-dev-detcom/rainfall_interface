packages = [
    "streamlit",
    "pandas",
    "xarray",
    "pydeck"
]

with open("requirements.txt", "w") as f:
    for pkg in packages:
        f.write(pkg + "\n")

print("requirements.txt created."

