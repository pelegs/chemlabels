from funcs import Chemical, pictogram_dict
from subprocess import run
from sys import argv


if __name__ == "__main__":
    CIDs = [x.strip() for x in argv[1].split(',')]

    for CID in CIDs:
        C = Chemical(CID)

        # NFPA
        NFPA = C.NFPA704_diamond
        if NFPA:
            if len(NFPA) == 4:
                extra = NFPA[3]
            else:
                extra = ""
            NFPA704_cmd = f'lualatex --jobname=NFPA_test{CID} --output-directory=parts "\\def\\health{{{NFPA[0]}}}\\def\\fire{{{NFPA[1]}}}\\def\\react{{{NFPA[2]}}}\\def\\extra{{{extra}}}\\input{{parts/NFPA704_diamond.tex}}"'
            run(NFPA704_cmd, shell=True)

        # GHS Pictograms
        pictograms = C.GHS_pictograms
        if pictograms:
            pictograms_tex = ''.join([
                f"\\ghspic{{{pictogram_dict[p]}}}" for p in pictograms
            ])
            pictograms_cmd = f'pdflatex --jobname=pictogram_test{CID} --output-directory=parts "\\def\\ghcpictograms{{{pictograms_tex}}}\\input{{parts/Pictograms.tex}}"'
            print(pictograms_cmd)
            run(pictograms_cmd, shell=True)
