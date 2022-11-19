from funcs import Chemical
from subprocess import run
from sys import argv


if __name__ == "__main__":
    CID = (argv[1])
    C = Chemical(CID)
    NFPA = C.NFPA704_diamond
    if NFPA:
        if len(NFPA) == 4:
            extra = NFPA[3]
        else:
            extra = ""
        cmd = f'lualatex --jobname=NFPA_test1 --output-directory=parts "\\def\\health{{{NFPA[0]}}}\\def\\fire{{{NFPA[1]}}}\\def\\react{{{NFPA[2]}}}\\def\\extra{{{extra}}}\\input{{parts/NFPA704_diamond.tex}}"'
        print(cmd)
        run(cmd, shell=True)
