import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import re
from tqdm import tqdm

global_folder = '1'
filename = "20-52-19.494550.txt"

level = 0.5
folders = glob('1/*')


def get_info_from_all_folders():

    folders = glob('1/*')
    empty_folders = 0

    for folder in tqdm(folders, total=len(folders)-1):
        shift = re.search(pattern=r'[-+]?\d{1,2}cm', string=folder).group().replace('cm', '')
        frequence = float(re.search(pattern=r'0.\dTHz', string=folder).group().replace('THz', ''))
        num_sipl = int(re.search(pattern=r'\d{1,2}SiPl', string=folder).group().replace('SiPl', ''))

        files = glob(f'{folder}/*.txt')

        durations = np.array([])
        amplitudes = np.array([])

        for file in files:
            data = np.genfromtxt(file)
            time = data[:, 0]
            signal = data[:, 1]

            amplitudes = np.append(amplitudes, np.max(signal))

            # Находим индексы, в которых сигнал больше заданного уровня, и смотрим,
            # какому времени эти индексы соотвутствуют
            pulse_timings = time[np.argwhere(signal > np.max(signal) * level)]
            pulse_timings = np.reshape(pulse_timings, -1)
            pulse_duration = pulse_timings[-1] - pulse_timings[0]

            durations = np.append(durations, pulse_duration)

        if amplitudes.size > 0:
            with open(f'{frequence} THz.txt', mode='a+', encoding='utf-8') as f:
                f.write(f'{shift}cm\t{num_sipl}SiPl\t{np.mean(amplitudes)}\t{np.var(amplitudes, ddof=1)}\n')
        else:
            empty_folders += 1

    print(f'Я нашёл {empty_folders} пустых папок')


single_file = True
all_files = True

# if single_file:
#     get_info_from_single_file()

if all_files:
    get_info_from_all_folders()
