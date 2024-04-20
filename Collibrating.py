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


def create_hash_map(folder_txt: str, folder_dat: str) -> np.array:
    files_matching = {}

    files = glob(f'{folder_dat}/*.dat')

    for file in tqdm(files, desc=f'{folder_dat} Считаем энергии для камеры', total=len(files)):
        num = re.search(r'\d{6,7}del', file).group().replace('del', '')

        data, *_ = read_dat(file)
        data -= min(data)
        files_matching[num] = {'camera': sum(data)}

    files = glob(f'{folder_txt}/*.txt')

    for file in tqdm(files, desc=f'{folder_txt} Считаем энергии для осциллографа', total=len(files)):
        num = re.search(r'_\d{6,7}del', file).group().replace('_', '').replace('del', '')

        if num in files_matching.keys():
            try:
                files_matching[str(int(num)+1)]['osc'] = get_energy_from_txt(file)
            except KeyError:
                pass

    keys_for_deleting = []
    for key in files_matching.keys():
        if len(files_matching[key].keys()) == 1:
            keys_for_deleting.append(key)

    for key in keys_for_deleting:
        del files_matching[key]

    return files_matching


def get_energy_from_txt(filename: str):
    energy = np.loadtxt(filename, dtype='float64')
    energy_record = energy[:, 2]
    peaks = find_peaks(energy_record, distance=1000)
    return max(energy_record[:peaks[0][0] + 400] * 100)


# folders = ['5mJ', '15mJ', 'PG_10mJ']
folders = ['5mJ', '15mJ']

energies = {}
for folder in folders:
    energies |= create_hash_map(f'2_txt/{folder}', f'2_dat/{folder}')

energies_10mJ = create_hash_map(f'2_txt/PG_10mJ', f'2_dat/PG_10mJ')

keys = list(energies.keys())
keys_10mJ = list(energies_10mJ.keys())

with open('data.txt', mode='w+', encoding='utf-8') as f:
    f.write('Номер сигнала; Осциллятор; Камера\n')

    for key in tqdm(keys, desc='Записываем в файл', total=len(keys)):
        f.write(f'{key}; {energies[key]["osc"]}; {energies[key]["camera"]}\n')

with open('data_10mJ.txt', mode='w+', encoding='utf-8') as f:
    f.write('Номер сигнала; Осциллятор; Камера\n')

    for key in tqdm(keys_10mJ, desc='Записываем в файл', total=len(keys_10mJ)):
        f.write(f'{key}; {energies_10mJ[key]["osc"]}; {energies_10mJ[key]["camera"]}\n')

plt.ion()
plt.figure(num='38 попугаев', figsize=(12, 6))
for i in np.arange(len(keys)):
    plt.subplot(1, 2, 1)
    plt.title(keys[i])
    y = [energies[x]['camera'] for x in keys[:i]]
    x = [energies[y]['osc'] for y in keys[:i]]

    plt.xlabel('Energy, mJ')
    plt.ylabel(r'$Energy \cdot parrots$')

    plt.grid()
    plt.scatter(x, y)

    plt.subplot(1, 2, 2)
    plt.xlabel('Energy, mJ')
    plt.ylabel(r'$Energy \cdot parrots$')

    plt.grid()
    plt.plot(0, 0)

    plt.show(block=False)
    plt.pause(.01)

    plt.clf()

for i in np.arange(len(keys_10mJ)):
    plt.subplot(1, 2, 1)

    plt.title(keys[i])

    plt.xlabel('Energy, mJ')
    plt.ylabel(r'$Energy \cdot parrots$')

    plt.grid()
    plt.scatter(x, y)

    plt.subplot(1, 2, 2)
    plt.title(keys_10mJ[i])
    y_2 = [energies_10mJ[x]['camera'] for x in keys_10mJ[:i]]
    x_2 = [energies_10mJ[y]['osc'] for y in keys_10mJ[:i]]

    plt.xlabel('Energy, mJ')
    plt.ylabel(r'$Energy \cdot parrots$')

    plt.grid()
    plt.scatter(x_2, y_2)

    plt.show(block=False)
    plt.pause(.01)

    plt.clf()

plt.ioff()
y = [energies[x]['camera'] for x in keys]
x = [energies[y]['osc'] for y in keys]

approx_x = np.linspace(min(x) * .7, max(x) * 1.1, 100)
coef, stats = polynomial.polyfit(x, y, deg=1, full=True)

approx_x_10mJ = np.linspace(min(x) * .7, max(x) * 1.1, 100)
coef_10mJ, stats_10mJ = polynomial.polyfit(x_2, y_2, deg=1, full=True)

print(f'Зависимость: {coef[1]} * x + {coef[0]}')
if stats[0] > coef[1]:
    print('Зависимость очень плохая')

print(f'Зависимость 10mJ: {coef_10mJ[1]} * x + {coef_10mJ[0]}')
if stats_10mJ[0] > coef_10mJ[1]:
    print('Зависимость очень плохая')

plt.subplot(1, 2, 1)
plt.xlabel('Energy, mJ')
plt.ylabel(r'$Energy \cdot parrots$')

plt.grid()
plt.scatter(x, y)
plt.plot(approx_x, coef[1] * approx_x + coef[0])

plt.subplot(1, 2, 2)

plt.xlabel('Energy, mJ')
plt.ylabel(r'$Energy \cdot parrots$')

plt.grid()
plt.scatter(x_2, y_2)
plt.plot(approx_x_10mJ, coef_10mJ[1] * approx_x_10mJ + coef_10mJ[0])

plt.show()