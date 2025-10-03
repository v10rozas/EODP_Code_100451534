from common.io.writeToa import writeToa, readToa

def check_criteria(toa, my_toa, threshold=0.0001, sigma_threshold=0.997):
    if len(toa) != len(my_toa):
        raise ValueError("TOAs Y-dimension must be the same.")

    num_total_points = 0
    num_correct_points = 0

    for row_toa, row_my_toa in zip(toa, my_toa):
        if len(row_toa) != len(row_my_toa):
            raise ValueError("TOAs X-dimension must be the same.")

        for point_toa, point_my_toa in zip(row_toa, row_my_toa):
            num_total_points += 1
            if point_toa == 0 and point_my_toa == 0: # Avoid division by 0
                rel_diff = 0
            elif point_toa == 0 or point_my_toa == 0: # Avoid division by 0. It counts as failure.
                rel_diff = float('inf')
            else:
                rel_diff = abs(point_toa - point_my_toa) / abs(point_toa)

            if rel_diff < threshold:
                num_correct_points += 1

    correct_ratio = num_correct_points / num_total_points
    return correct_ratio >= sigma_threshold

# Outputs directories
output_dir = "/Users/victordr02/Library/CloudStorage/GoogleDrive-vdiezrozasoficial@gmail.com/Mi unidad/UC3M/MUIT 2º Curso/1º Cuatrimestre/Procesado de datos/Proyecto/EODP-TS-ISM/output"
my_output_dir = "/Users/victordr02/Library/CloudStorage/GoogleDrive-vdiezrozasoficial@gmail.com/Mi unidad/UC3M/MUIT 2º Curso/1º Cuatrimestre/Procesado de datos/Proyecto/EODP-TS-ISM/my_own_output"

for num_band in range(0, 4):
    # Retrieve TOAs for a specific band
    toa_filename = "ism_toa_optical_VNIR-" + str(num_band) + ".nc"
    toa = readToa(output_dir, toa_filename)
    my_toa = readToa(my_output_dir, toa_filename)
    # Check criteria for a specific band
    print(f"VNIR-{num_band} pass criteria: {check_criteria(toa, my_toa)}")
