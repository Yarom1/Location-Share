path = "app/src/main/java/com/locationshare/MainActivity.kt"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("=== כל שורות ה-import ===")
for i, line in enumerate(lines):
    if line.strip().startswith("import "):
        print(f"{i+1}: {line.rstrip()}")

print("\n=== מכיל 'android.content.Intent'? ===")
print(any("android.content.Intent" in l for l in lines))

print("\n=== מכיל 'runOnUiThread'? ===")
content = "".join(lines)
print("runOnUiThread" in content)
