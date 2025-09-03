import vr1

my_mat = '''
13027.00c -0.9353353
25055.00c -0.002999189
12024.00c -0.03894506
12025.00c -0.005135806
12026.00c -0.005880707
24050.00c -4.17238E-05
24052.00c -0.000836786
24053.00c -9.67094E-05
24054.00c -2.45272E-05
29063.00c -0.0006848
29065.00c -0.000314914
26054.00c -0.00011288
26056.00c -0.00183761
26057.00c -4.31962E-05
26058.00c -5.84949E-06
16032.00c -0.005400523
16033.00c -4.45872E-05
16034.00c -0.00025931
16036.00c -1.28002E-06
30064.00c -0.000485768
30066.00c -0.000278866
30067.00c -4.09805E-05
30068.00c -0.00018791
30070.00c -5.99714E-06
22046.00c -7.91718E-05
22047.00c -7.29506E-05
22048.00c -0.000738218
22049.00c -5.53035E-05
22050.00c -5.4033E-05
'''


def mat_s2open(s2mat: str):
    """Convert the Serpent 2 material input string to OpenMC material input format.
    Parameters:
        - s2mat (str): The Serpent 2 material string representing isotopic composition and atomic weights.
    Returns:
        - None: The function prints the OpenMC formatted material dictionary entries to the console."""
    for line in s2mat.splitlines():
        if line == '':
            continue
        # print(l)
        (zaid, wostr) = line.split(' ')
        wo = -1. * float(wostr)
        (za, lib_id) = zaid.split('.')
        A = int(za[-3:])
        Z = int(za[0:-3])
        # print(za, Z, A, vr1.ELEMENTS[Z], wo)
        ele = f'{vr1.ELEMENTS[Z]}'.capitalize() + str(A)
        print(f'"{ele}": {wo},')

import os
import subprocess

def plot_vr1():
    subprocess.run(["openmc-plotter"])

if __name__ == '__main__':
    mat_s2open(my_mat)
