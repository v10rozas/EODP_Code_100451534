
# MAIN FUNCTION TO CALL THE L1C MODULE

from l1c.src.l1c import l1c

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'/Users/victordr02/Library/CloudStorage/GoogleDrive-vdiezrozasoficial@gmail.com/Mi unidad/UC3M/MUIT 2º Curso/1º Cuatrimestre/Procesado de datos/Proyecto/EODP_Code_100451534/auxiliary'
# GM dir + L1B dir
indir = r'/Users/victordr02/Library/CloudStorage/GoogleDrive-vdiezrozasoficial@gmail.com/Mi unidad/UC3M/MUIT 2º Curso/1º Cuatrimestre/Procesado de datos/Proyecto/EODP-TS-L1C/input/gm_alt100_act_150,/Users/victordr02/Library/CloudStorage/GoogleDrive-vdiezrozasoficial@gmail.com/Mi unidad/UC3M/MUIT 2º Curso/1º Cuatrimestre/Procesado de datos/Proyecto/EODP-TS-L1C/input/l1b_output'
outdir = r"/Users/victordr02/Library/CloudStorage/GoogleDrive-vdiezrozasoficial@gmail.com/Mi unidad/UC3M/MUIT 2º Curso/1º Cuatrimestre/Procesado de datos/Proyecto/EODP-TS-L1C/my_own_output"

# Initialise the ISM
myL1c = l1c(auxdir, indir, outdir)
myL1c.processModule()
