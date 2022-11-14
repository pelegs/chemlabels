from pubchempy import get_compounds, Compound
from mol2chemfigPy3 import mol2chemfig as smiles2chemfig
from subprocess import check_output
from sys import argv
from subprocess import run
from numpy.random import randint

if argv[1] == 'random':
    CID = randint(2000000)
else:
    CID = argv[1]
chemical = Compound.from_cid(CID)
print(dir(chemical))


# chemfig = smiles2chemfig(smiles)
# with open('mol.tex', 'w') as f:
#     f.write(chemfig)
# pdflatex_cmd = 'pdflatex template'
# run(pdflatex_cmd, shell=True)
# del_cmd = 'rm mol.tex'
# run(del_cmd, shell=True)
