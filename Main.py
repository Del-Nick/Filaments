import numpy as np
import matplotlib.pyplot as plt
from glob import glob

folder = '1/0cm_0.3THz_682mm_10SiPl'
filename = "20-52-19.494550.txt"

level = 0.5


# def get_info_from_single_file():
#     data = np.genfromtxt(f'{folder}/{filename}')
#     time = data[:, 0]
#     # УКАЗАТЬ СТОЛБЕЦ С ДАННЫМИ НИЖЕ !!!!!!!!!!!!!!!!!!!!!!!!!
#     signal = data[:, 1]
#
#     pulse_timings = time[np.argwhere(signal > np.max(signal) * level)]
#     pulse_timings = np.reshape(pulse_timings, -1)
#     pulse_duration = pulse_timings[-1] - pulse_timings[0]
#     print(f'Длительность импульса {pulse_duration * 1e6} мкс\n'
#           f'Амплитуда импульса {np.max(signal)} В')
#
#     plt.plot(time * 1e6, signal, label="Signal")
#     plt.legend()
#     plt.grid()
#     plt.xlim(.6, .7)
#     plt.xlabel("time, мкc")
#     plt.ylabel("amp, В")


def get_info_from_all_files():
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

    # np.mean - нахождение среднего от массива
    # np.var - нахождение дисперсии. По умолчанию нормировка на N. Параметр ddof
    # показывает, на сколько нужно уменьшить N. То есть при ddof=1 нормировка на 1/(N-1)
    print(f'Длительность импульса {np.mean(durations) * 1e6} ± {np.var(durations, ddof=1) * 1e6} мкс\n'
          f'Амплитуда импульса {np.mean(amplitudes)} ± {np.var(amplitudes, ddof=1)}')

    plt.figure(figsize=(12, 6))
    ax = plt.subplot(1, 2, 1)
    ax.set_title('Длительности всех импульсов по номерам')
    plt.scatter(np.arange(durations.size), durations * 1e6)
    plt.ylabel('Длительность, мкс')
    plt.xlabel('Номер импульса')
    plt.grid()

    ax2 = plt.subplot(1, 2, 2)
    ax2.set_title('Амплитуды всех импульсов по номерам')
    plt.scatter(np.arange(amplitudes.size), amplitudes)
    plt.ylabel('Амплитуда, В')
    plt.xlabel('Номер импульса')
    plt.grid()

    plt.show()


single_file = True
all_files = True

# if single_file:
#     get_info_from_single_file()

if all_files:
    get_info_from_all_files()
