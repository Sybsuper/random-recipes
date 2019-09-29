import os
import random
import io
import zipfile
import json
import sys

if len(sys.argv) >= 2:
	try:
		seed = int(sys.argv[1])
	except Exception:
		print('The seed "{}" is not an integer.'.format(sys.argv[1]))
		exit()
	random.seed(seed)
	datapack_name = 'random_recipes_{}'.format(seed)
	datapack_desc = 'Loot Table Randomizer, Seed: {}'.format(seed)
else:
	print('If you want to use a specific randomizer seed integer, use: "python randomize.py <seed>"')
	datapack_name = 'random_recipes'
	datapack_desc = 'Recipe Randomizer'

datapack_filename = datapack_name + '.zip'

print('Generating datapack...')

file_list = []
results = []

for dirpath, dirnames, filenames in os.walk('recipes'):
	for filename in filenames:
		file_list.append(os.path.join(dirpath, filename))
		with open(os.path.join(dirpath, filename)) as file:
			res = json.loads(file.read())
			if "result" in res:
				results.append(res["result"])


file_dict = {}
for file in file_list:
	if len(results) > 0:
		i = random.randint(0, len(results)-1)
		file_dict[file] = results[i]
		del results[i]

zipbytes = io.BytesIO()
zip = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)

for from_file in file_dict:
	with open(from_file) as file:
		contents = json.loads(file.read())
	contents["result"] = file_dict[from_file]
	if contents["type"] == "minecraft:smelting" or contents["type"] == "minecraft:blasting" or contents["type"] == "minecraft:campfire_cooking" or contents["type"] == "minecraft:smoking" or contents["type"] == "minecraft:stonecutting":
		if  str(type(file_dict[from_file]))=="<class 'dict'>":
			if contents["type"] == "minecraft:stonecutting" and "count" in contents["result"]:
				contents["count"] = contents["result"]["count"]
			contents["result"] = contents["result"]["item"]
	elif contents["type"]=="minecraft:crafting_shapeless" or contents["type"]=="minecraft:crafting_shaped":
		if str(type(file_dict[from_file])) == "<class 'str'>":
			contents["result"] = {"item": file_dict[from_file], "count": 1}
	zip.writestr(os.path.join('data/minecraft/', from_file), json.dumps(contents))

zip.writestr('pack.mcmeta', json.dumps({'pack':{'pack_format':1, 'description':datapack_desc}}, indent=4))
zip.writestr('data/minecraft/tags/functions/load.json', json.dumps({'values':['{}:reset'.format(datapack_name)]}))
zip.writestr('data/{}/functions/reset.mcfunction'.format(datapack_name), 'tellraw @a {"text":"Recipe randomizer by Sybsuper","color":"gold"}')

zip.close()
with open(datapack_filename, 'wb') as file:
	file.write(zipbytes.getvalue())

print('Created datapack "{}"'.format(datapack_filename))
