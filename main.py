from src import preparar_ambiente, bigfile, bigfile_bkp
from gui.launcher import main

if __name__ == "__main__":
    preparar_ambiente(bigfile, bigfile_bkp)
    main()
