import codecs
import json

leveldir = '../assets/levels/level1/prewalls.json'
checkpointdir = '../assets/levels/level1/precheckpoints.json'
outputdir = '../assets/levels/level1/level.json'

with codecs.open(leveldir, 'r', encoding='UTF-8') as f:
    walls_in = json.load(f)['level']

with codecs.open(checkpointdir, 'r', encoding='UTF-8') as f:
    checkpoints_in = json.load(f)['layers'][0]['paths']

wallpos = 0

level_out = {
    "walls": [[], []],
    "checkpoints": []
}

# Register walls
wallpos = 0
for c in walls_in:
    if len(c) == 1:
        wallpos = 1
        continue
    if c[0] == 'M' or c[0] == 'L':
        curpos = c[1:3]
        level_out['walls'][wallpos].append(curpos)
    elif c[0] == 'l':
        curpos = [curpos[0] + c[1], curpos[1] + c[2]]
        level_out['walls'][wallpos].append(curpos)

# Register checkpoints
for path in checkpoints_in:
    level_out['checkpoints'].append(path['points'])

input('Are you sure you want to write to {}? Ctrl+C to abort.'.format(outputdir))

with codecs.open(outputdir, 'w', encoding='UTF-8') as f:
    json.dump(level_out, f)
