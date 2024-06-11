import json
import sys

filename = sys.argv[1]

layout_dict = {}

with open(filename,"r") as file:
    layout_dict = json.load(file)

def format(dict, indent="    "):
    result = []
    for key,value in dict.items():
        line = f'{indent}    "{key}": '
        if type(value) == type({}):
            line += format(value,indent+"    ")
        elif type(value) == type([]):
            line += "[\n"
            line += ",\n".join(indent+"        "+str(elem) for elem in value)
            line += "\n"+indent+"    ]"
        else:
            line += '"'+str(value)+'"'
        result.append(line)
    result = ",\n".join(result)
    return f"{{\n{result}\n{indent}}}"

with open(filename[:-5]+".formatted.json","w") as file:
    file.write(format(layout_dict))
