# # High-Performance Integrated hydrodynamic Modelling System ***hybrid***
# @author: Jiaheng Zhao (Hemlab)
# @license: (C) Copyright 2020-2025. 2025~ Apache Licence 2.0
# @contact: j.zhao@lboro.ac.uk
# @software: hipims_hybrid
# @time: 07.01.2021
# This is a beta version inhouse code of Hemlab used for high-performance flooding simulation.
# Feel free to use and extend if you are a ***member of hemlab***.
import os

print("         Welcome to the HiPIMS! ")

dir_path = os.path.dirname(os.path.realpath(__file__))

f = open(os.path.join(dir_path, 'banner.txt'), 'r', encoding='utf-8')

file_contents = f.read()
print(file_contents)
f.close()