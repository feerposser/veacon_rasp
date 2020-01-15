
dicionario = {
    'a': [3,2,1]
}

for i in dicionario.keys():
    print(i, '-', dicionario[i])

dicionario['a'] = sorted(dicionario['a'])
print(dicionario)
dicionario.pop('a')
print(dicionario)