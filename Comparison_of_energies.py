import time
from pprint import pprint

import numpy as np
from numpy import sum, exp, min, max
from numpy.polynomial import polynomial
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy import linalg
from glob import glob
import re
from tqdm import tqdm

from dat_opener import read_dat


def create_hash_map(main_txt_folder: str, main_dat_folder: str, datafolder: str,
                    shift: str, frequence: str, num_SiPl: str, energies: dict) -> np.array:

    folder_txt = f'{main_txt_folder}/{datafolder}'
    folder_dat = f'{main_dat_folder}/{datafolder}'

    files = glob(f'{folder_txt}/*.txt')

    energies[datafolder] = {'nums': {},
                            'shift': shift,
                            'frequence': frequence,
                            'num_SiPl': num_SiPl,
                            'total_files': len(files)}

    for file in files:
        num = re.search(r'_\d{6,7}del', file).group().replace('_', '').replace('del', '')
        energies[datafolder]['nums'][num] = {'osc': get_energy_from_txt(file)}

    files = glob(f'{folder_dat}/*.dat')

    for file in files:
        num = re.search(r'\d{6,7}del', file).group().replace('del', '')

        data, _, _ = read_dat(file)
        data -= min(data)
        if f'{int(num) - 1}' in energies[datafolder]['nums'].keys():
            energies[datafolder]['nums'][f'{int(num) - 1}']['camera'] = sum(data)

    keys_for_deleting = []
    for key in energies[datafolder]['nums'].keys():
        if len(energies[datafolder]['nums'][key].keys()) == 1:
            keys_for_deleting.append(key)

    for key in keys_for_deleting:
        del energies[datafolder]['nums'][key]

    return energies


def get_energy_from_txt(filename: str):
    energy = np.loadtxt(filename, dtype='float64')
    energy_record = energy[:, 1]
    peaks = find_peaks(energy_record, distance=1000)
    return max(energy_record[:peaks[0][0] + 400])


# Это основные папки, в которых лежат папки с данными
main_txt_folder = '1_en_txt'
main_dat_folder = '1_en_dat'

folders = glob(f'{main_txt_folder}/*')
folders = [x.replace(f'{main_txt_folder}\\', '') for x in folders]

for frequence in ['0.1 THz', '0.3 THz', '0.5 THz']:
    with open(f'{frequence}.txt', mode='w+', encoding='utf-8') as f:
        f.write(f'Сдвиг\tSiPl\tАмплитуда\tПогрешность\tВсего файлов\tОсталось файлов\n')

# folders = folders[:2]

energies = {}
pbar = tqdm(total=len(folders))
for folder in folders:
    pbar.set_description(f'Считаем данные из папки {folder}')

    shift = re.search(pattern=r'[-+]?\d{1,2}cm', string=folder).group().replace('cm', '')
    frequence = re.search(pattern=r'0.\dTHz', string=folder).group().replace('THz', '')
    num_sipl = re.search(pattern=r'\d{1,2}SiPl', string=folder).group().replace('SiPl', '')

    energies |= create_hash_map(main_txt_folder=main_txt_folder, main_dat_folder=main_dat_folder, datafolder=folder,
                                shift=shift, frequence=frequence, num_SiPl=num_sipl, energies=energies)

    pbar.update(1)

# Если нужно будет сдвинуть линию, заместо False пишем новый уроверь линии PG - (4046421.5 * x + 173253)
# Single (3091380.5 * x + 2555419), x = energy [mJ]
level_for_points = 4046421.5 * 6 + 173253
bandwidth = 0.2

# x_old и y_old нужны, чтобы показать на графике точки из всех файлов
y = []
x_old = []
for folder in folders:
    for num in energies[folder]['nums'].keys():
        y.append(energies[folder]['nums'][num]['camera'])
        x_old.append(int(num))

x_old = np.array(x_old)
y = np.array(y)
y_old = np.copy(y)
mid_value = level_for_points if level_for_points else np.mean(y)
print(f'\nСреднее значение: {2.46e-7 * mid_value + 0.01449}')

if level_for_points:
    mid_value = level_for_points


# Помечаем те номера пакетов, которые выходят за границы полосы
key_for_delete = []
for folder in tqdm(folders, desc='Ищем точки вне полосы', total=len(folders)):
    for num in energies[folder]['nums'].keys():
        _ = 2.46e-7 * energies[folder]['nums'][num]['camera'] + 0.01449
        if _ < 2.46e-7 * mid_value + 0.01449 - 1 or _ > 2.46e-7 * mid_value + 0.01449 + 1:
            key_for_delete.append({'folder': folder,
                                   'num': num})

# Удаляем все пакеты за пределами полосы
for data in key_for_delete:
    del energies[data['folder']]['nums'][data['num']]

y = []
x = []
for folder in folders:
    for num in energies[folder]['nums'].keys():
        x.append(int(num))
        y.append(energies[folder]['nums'][num]['camera'])

x = np.array(x)
y = np.array(y)

plt.scatter(x_old, 2.46e-7 * y_old + 0.01449, color='red')
plt.scatter(x, 2.46e-7 * y + 0.01449, color='green')
plt.grid()
plt.show()

for folder in tqdm(folders, desc='Записываем в файл', total=len(folders)):
    files_left = len(energies[folder]['nums'].keys())

    frequence = energies[folder]['frequence']
    shift = energies[folder]['shift']
    num_sipl = energies[folder]['num_SiPl']

    amplitudes = []
    for num in energies[folder]['nums'].keys():
        amplitudes.append(energies[folder]['nums'][num]['osc'])

    amplitudes = np.array(amplitudes)

    with open(f'{frequence} THz.txt', mode='a+', encoding='utf-8') as f:
        f.write(f'{shift}cm\t')
        f.write(f'{num_sipl}SiPl\t')
        f.write(f'{np.mean(amplitudes)}\t')
        f.write(f'{np.var(amplitudes, ddof=1)}\t')
        f.write(f'{energies[folder]['total_files']}\t')
        f.write(f'{files_left}\n')
