with open("extensions.html", "r") as f:
    content = f.read()

extensions = []

for line in content.split("\n"):
    if '<span class="ext tag" data-ext="' in line:
        extension = line.split('data-ext="')[1].split('"')[0]
        extensions.append(extension)

with open("extensions.json", "w") as f:
    f.write(json.dumps(extensions))
