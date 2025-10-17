import matplotlib.pyplot as plt
from common.io.writeToa import writeToa, readToa

def plot_toa(isrf_toa, toa_without_eq, num_band):
    if len(isrf_toa) != len(toa_without_eq):
        raise ValueError("TOAs X-dimension must be the same.")

    plt.figure(figsize=(8, 6))
    plt.plot(range(0, len(isrf_toa)), isrf_toa, color='blue', label='TOA after the ISRF')
    plt.plot(range(0, len(toa_without_eq)), toa_without_eq, color='red', label='TOA L1B without eq and res')
    plt.title("Effect of the Non-Equalization and Non-Restoration for VNIR-" + str(num_band))
    plt.xlabel("ACT pixel [-]")
    plt.ylabel("TOA [mW/m2/sr]")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Outputs directories
isrf_output_dir = "/Users/victordr02/Library/CloudStorage/GoogleDrive-vdiezrozasoficial@gmail.com/Mi unidad/UC3M/MUIT 2º Curso/1º Cuatrimestre/Procesado de datos/Proyecto/EODP-TS-E2E/my_ism_own_output"
output_without_eq_dir = "/Users/victordr02/Library/CloudStorage/GoogleDrive-vdiezrozasoficial@gmail.com/Mi unidad/UC3M/MUIT 2º Curso/1º Cuatrimestre/Procesado de datos/Proyecto/EODP-TS-E2E/my_l1b_own_output"

for num_band in range(0, 4):
    # Retrieve TOAs for a specific band
    isrf_toa_filename = "ism_toa_isrf_VNIR-" + str(num_band) + ".nc"
    isrf_toa = readToa(isrf_output_dir, isrf_toa_filename)
    toa_filename = "l1b_toa_VNIR-" + str(num_band) + ".nc"
    toa_without_eq = readToa(output_without_eq_dir, toa_filename)

    # Retrieve central ALT position
    isrf_toa = isrf_toa[int(len(isrf_toa) / 2)]
    toa_without_eq = toa_without_eq[int(len(toa_without_eq)/2)]

    # Plot TOAs
    plot_toa(isrf_toa, toa_without_eq, num_band)
