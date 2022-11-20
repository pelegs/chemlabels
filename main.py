from funcs import Chemical, pictogram_dict
from subprocess import run
from sys import argv
from mol2chemfigPy3 import mol2chemfig as smiles2chemfig


if __name__ == "__main__":
    CIDs = [x.strip() for x in argv[1].split(",")]

    for CID in CIDs:
        C = Chemical(CID)

        # NFPA
        NFPA = C.NFPA704_diamond
        # print(NFPA)
        # exit()
        if NFPA:
            if len(NFPA) == 4:
                extra = NFPA[3]
            else:
                extra = ""
            NFPA704_cmd = f'lualatex --jobname=NFPA704_{CID} --output-directory=parts "\\def\\health{{{NFPA[0]}}}\\def\\fire{{{NFPA[1]}}}\\def\\react{{{NFPA[2]}}}\\def\\extra{{{extra}}}\\input{{parts/NFPA704_diamond.tex}}"'
            run(NFPA704_cmd, shell=True)

        # GHS Pictograms
        pictograms = C.GHS_pictograms
        if pictograms:
            pictograms_tex = "".join(
                [f"\\ghspic[scale=2.5]{{{pictogram_dict[p]}}}" for p in pictograms]
            )
        else:
            pictograms_tex = ""

        # SMILEs to chemfig
        chemfig = smiles2chemfig(C.SMILES).replace("\n", "").replace("%", "")
        # print(chemfig)
        # exit()

        # Create label
        label_cmd = f'lualatex --jobname=label_{CID} --output-directory=. "\\def\\cid{{{CID}}}\\def\\Name{{{C.name}}}\\def\\CAS{{{C.CAS}}}\\def\\formula{{\\ce{{{C.molecular_formula}}}}}\\def\\GHSpictograms{{{pictograms_tex}}}\\def\\cf{{{chemfig}}}\\input{{templates/label.tex}}"'
        print(label_cmd)
        run(label_cmd, shell=True)
