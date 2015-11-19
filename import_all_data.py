# coding: ascii
# Copyright (c) Mike Gibson
# Distributed under the terms of the MIT License.

"""
Uses materialsproject API to extract enthalpies of formation and 
compositions of compounds for comparison to Miedema values.
"""

__author__ = "Mike Gibson"
__credits__ = "Materials Project"
__copyright__ = "Copyright 2015, Mike Gibson"
__version__ = "1.0"
__maintainer__ = "Mike Gibson"
__email__ = "gibson.michael.a@gmail.com"
__date__ = "Nov 17, 2015"

# make this file happen in interactive: 
# execfile('import_all_data_as_qhull.py')
import csv
import os
from pymatgen.phasediagram.pdmaker import PhaseDiagram
from pymatgen.matproj.rest import MPRester
from pymatgen.core.composition import Composition
from pymatgen.core.periodic_table import get_el_sp, Element


elementsToTest = ['Sc',  'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu',
                  'Y',  'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag',
                  'La', 'Hf', 'Ta',  'W', 'Re', 'Os', 'Ir', 'Pt', 'Au']
startDirectory = "all_TM_Mixing_Data/"

with MPRester("JwiPQItBAT8z6Dgd") as m:
    for i in range(len(elementsToTest)):
        elem1 = elementsToTest[i]
        print "elem1 is: " + elem1
        for j in range(len(elementsToTest)):
            elem2 = elementsToTest[j]
            print "elem2 is: " + elem2
            directory = startDirectory + str(elem1) + str(elem2)
            if not os.path.exists(directory):
                os.makedirs(directory)
            chemSystem = m.get_entries_in_chemsys([elem1, elem2])
            pd = PhaseDiagram(chemSystem)
            compEnergyData = pd.qhull_data
            compEnergyDataList = compEnergyData.tolist()
            compEnergyList = []
            compEnergyRatios = []
            chemsSysEnergies = []
            for phase in chemSystem:
                if phase.data['nelements'] > 1:
                    name = phase.data['pretty_formula']
                    comp = phase.composition.get_atomic_fraction(Element(elem1))
                    deltaE = phase.data['formation_energy_per_atom']
                    compEnergyList.append([name, comp, deltaE])
                    if deltaE < 0 and type(deltaE) == float:
                        compEnergyRatios.append(deltaE/comp)
                        chemsSysEnergies.append(deltaE)
            # Write the raw data in two forms, the second of which should be more interpretable
            with open(directory + "/" + elem1 + 
                    elem2 + "compEnergyDataFromqhull.csv", 'wb') as csvfile:
                csvwriter = csv.writer(csvfile, dialect='excel')
                for phase in compEnergyDataList:
                    csvwriter.writerow(phase)
            with open(directory + "/" + elem1 + elem2 + "compEnergyData.csv", 'wb') as csvfile:
                csvwriter = csv.writer(csvfile, dialect='excel')
                for phase in compEnergyList:
                    csvwriter.writerow(phase)

            chemsSysEnergies.append(0)
            compEnergyRatios.append(0)
            minEnergy= min(chemsSysEnergies)
            minSlope = min(compEnergyRatios)
            if minEnergy >= 0: minEnergy = 9999
            if minSlope >= 0: minSlope = 9999
            with open("energiesAndSlopesAcrossSystems.csv",'ab') as csvfile:
                csvwriter = csv.writer(csvfile, dialect='excel')
                csvwriter.writerow([elem1 + elem2, minEnergy, minSlope])

