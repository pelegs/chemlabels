from subprocess import run
from sys import argv
from mol2chemfigPy3 import mol2chemfig as smiles2chemfig
import argparse
from funcs import Chemical, pictogram_dict, format_temperature_range


parser = argparse.ArgumentParser(
    description="Automatically generate chemical label from CID number"
)
parser.add_argument("-c", "--cid", help="CID number", required=True)
parser.add_argument(
    "-n", "--nfpa704", help="Manually enter NFPA704 values", required=False
)
args = vars(parser.parse_args())

if __name__ == "__main__":
    CIDs = [x.strip() for x in args["cid"].split(",")]

    for CID in CIDs:
        C = Chemical(CID)

        # NFPA
        NFPA = C.NFPA704_diamond
        # print(NFPA)
        # exit()
        if NFPA:
            NFPA_list = NFPA
        else:
            NFPA_list = args["nfpa704"].split("-")
        print(f"NFPA704 list: {NFPA_list}")
        if len(NFPA_list) == 4:
            extra = NFPA_list[3]
        else:
            extra = ""
        NFPA_cmd= f'lualatex --jobname=NFPA704_{CID} --output-directory=parts "\\def\\health{{{NFPA_list[0]}}}\\def\\fire{{{NFPA_list[1]}}}\\def\\react{{{NFPA_list[2]}}}\\def\\extra{{{extra}}}\\input{{parts/NFPA704_diamond.tex}}"'
        run(NFPA_cmd, shell=True)

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
        chemfig_cmd = f'lualatex --jobname=molecule_{CID} --output-directory=parts "\\def\\molecule{{{chemfig}}}\\input{{parts/draw_molecule.tex}}"'
        run(chemfig_cmd, shell=True)

        # Physical properties
        BP = format_temperature_range(C.bp)
        MP = format_temperature_range(C.mp)

        # Create label
        label_cmd = f'lualatex --jobname=label_{CID} --output-directory=. "\\def\\cid{{{CID}}}\\def\\Name{{{C.name}}}\\def\\CAS{{{C.CAS}}}\\def\\IUPACname{{{C.IUPAC_name}}}\\def\\formula{{\\ce{{{C.molecular_formula}}}}}\\def\\GHSpictograms{{{pictograms_tex}}}\\def\\cf{{{chemfig}}}\\def\\MW{{{C.MW}}}\\def\\BP{{{BP}}}\\def\\MP{{{MP}}}\\input{{templates/label.tex}}"'
        print(label_cmd)
        run(label_cmd, shell=True)
