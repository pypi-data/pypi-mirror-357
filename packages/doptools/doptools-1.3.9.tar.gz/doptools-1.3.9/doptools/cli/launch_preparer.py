#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Copyright 2022-2025 Pavel Sidorov <pavel.o.sidorov@gmail.com> This
#  file is part of DOPTools repository.
#
#  DOPtools is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.

import argparse
import os
import pickle
import warnings
import multiprocessing as mp
import json
from itertools import product, combinations
import logging

import numpy as np
import pandas as pd
from chython import smiles
from sklearn.datasets import dump_svmlight_file

from doptools.chem.chem_features import ComplexFragmentor, PassThrough
from doptools.chem.solvents import SolventVectorizer
from doptools.optimizer.config import get_raw_calculator
from doptools.optimizer.preparer import *

logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)

basic_params = {
    "circus": True, 
    "circus_min": [0], 
    "circus_max": [2, 3, 4], 
    "linear": True, 
    "linear_min": [2], 
    "linear_max": [5, 6, 7, 8], 
    "morgan": True, 
    "morgan_nBits": [1024], 
    "morgan_radius": [2, 3, 4], 
    "morganfeatures": True, 
    "morganfeatures_nBits": [1024], 
    "morganfeatures_radius": [2, 3, 4], 
    "rdkfp": True, 
    "rdkfp_nBits": [1024], 
    "rdkfp_length": [2,3,4], 
    "rdkfplinear": True, 
    "rdkfplinear_nBits": [1024], 
    "rdkfplinear_length": [5,6,7,8], 
    "layered": True, 
    "layered_nBits": [1024], 
    "layered_length": [5,6,7,8], 
    "avalon": True, 
    "avalon_nBits": [1024], 
    "atompairs": True, 
    "atompairs_nBits": [1024], 
    "torsion": True, 
    "torsion_nBits": [1024], 
    "separate_folders": True,
    "save":True,
    "standardize": True
}

def _calculate_and_output(input_params):
    calculator, data, prop, prop_name, output_folder, pickles, fmt = input_params
    desc = calculator.fit_transform(data)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)  # exist_ok is useful when several processes try to create the folder at the same time
        logging.info("The output directory {} created".format(output_folder))
        print('The output directory {} created'.format(output_folder))
    else:
        logging.warning('The output directory {} already exists. The data will be overwritten'.format(output_folder))
        
    if pickles:
        fragmentor_name = os.path.join(output_folder, '.'.join([prop_name, calculator.short_name, 'pkl']))
        with open(fragmentor_name, 'wb') as f:
            pickle.dump(calculator, f, pickle.HIGHEST_PROTOCOL)

    output_name = os.path.join(output_folder, '.'.join([prop_name, calculator.short_name, fmt]))
    if fmt == "csv":
        desc = pd.concat([pd.Series(prop, name=prop_name), desc], axis=1, sort=False)
        desc.to_csv(output_name, index=False)
    else:
        dump_svmlight_file(np.array(desc, dtype="float32"), prop, output_name, zero_based=False)
    

def _perform_fullconfig(fullconfig):
    calculators = {}

    if fullconfig["input_file"].endswith(".csv"):
        data = pd.read_table(fullconfig["input_file"], sep=",")
    elif fullconfig["input_file"].endswith(".xlsx"):
        data = pd.read_excel(fullconfig["input_file"])

    for s in fullconfig["structures"].keys():
        
        # standardization
        if fullconfig["standardize"]:
            struct = [smiles(m) for m in data[s]]
            # this is magic, gives an error if done otherwise...
            for m in struct:
                try:
                    m.canonicalize(fix_tautomers=False) 
                except:
                    m.canonicalize(fix_tautomers=False)
            data[s] = [str(m) for m in struct]

    y = data[fullconfig["property"]]
    indices = y[pd.notnull(y)].index
    if len(indices) < len(data):
        print(f"'{p}' column warning: only {len(indices)} out of {len(data)} instances have the property.")
        print(f"Molecules that don't have the property will be discarded from the set.")
    y = y.iloc[indices]
    data = data.iloc[indices]

    if "numerical" in fullconfig.keys() or "solvent" in fullconfig.keys() or len(fullconfig["structures"].keys())>1:
        data_x = data
        
        fullconfig["separate_folders"] = False
        
        associators = []
        for s in fullconfig["structures"].keys():
            associators.append([])
            for t, d in fullconfig["structures"][s].items():
                if fullconfig["chiral"]:
                    if t in ["morgan", "torsion", "atompairs"]:
                        d["chirality"] = [True]
                d["fmt"] = ["smiles"]
                param_values = list(d.values())
                for p in [dict(zip(list(d.keys()), i)) for i in product(*param_values)]:
                    associators[-1].append((s, get_raw_calculator(t, p)))
    
        if "solvent" in fullconfig.keys():
            associators.append([(fullconfig["solvent"], SolventVectorizer())])
    
        if "numerical" in fullconfig.keys():
            associators.append([("numerical", PassThrough(fullconfig["numerical"]))])
    
        for p in product(*associators):
            cf = ComplexFragmentor(associator=p, structure_columns=list(fullconfig["structures"].keys()))
            calculators[cf.short_name] = cf
    else:
        data_x = data[list(fullconfig["structures"].keys())[0]]
        for s in fullconfig["structures"].keys():
            for t, d in fullconfig["structures"][s].items():
                d["fmt"] = ["smiles"]
                param_values = list(d.values())
                for p in [dict(zip(list(d.keys()), i)) for i in product(*param_values)]:
                    calc = get_raw_calculator(t, p)
                    calculators[calc.short_name] = calc

    pool = mp.Pool(processes=fullconfig["parallel"] if fullconfig["parallel"] > 0 else 1)
    # non_mordred_descriptors = [desc for desc in descriptor_dictionary.keys() if 'mordred2d' not in desc]
    # Use pool.map to apply the calculate_and_output function to each set of arguments in parallel
    # The arguments are tuples containing (inpt, descriptor, descriptor_params, output_params)
    pool.map(_calculate_and_output, [(calc, 
                                      data_x, 
                                      y, 
                                      fullconfig["property_name"], 
                                      fullconfig["output_folder"], 
                                      fullconfig["save"], 
                                      fullconfig["output_fmt"]) for calc in calculators.values()])
    pool.close() # Close the pool and prevent any more tasks from being submitted
    pool.join() # Wait for all the tasks to complete

def _set_default(argument, default_values):
    if len(argument) > 0:
        return list(set(argument))
    else:
        return default_values


def _enumerate_parameters(args):
    def _make_name(iterable):
        return '_'.join([str(i) for i in iterable])

    param_dict = {}
    if args.morgan:
        for nb in _set_default(args.morgan_nBits, [1024]):
            for mr in _set_default(args.morgan_radius, [2]):
                param_dict[_make_name(('morgan', nb, mr))] = {'nBits': nb, 'radius': mr}
    if args.morganfeatures:
        for nb in _set_default(args.morganfeatures_nBits, [1024]):
            for mr in _set_default(args.morganfeatures_radius, [2]):
                param_dict[_make_name(('morganfeatures', nb, mr))] = {'nBits': nb, 'radius': mr}
    if args.rdkfp:
        for nb in _set_default(args.rdkfp_nBits, [1024]):
            for rl in _set_default(args.rdkfp_length, [3]):
                param_dict[_make_name(('rdkfp', nb, rl))] = {'nBits': nb, 'radius': rl}
    if args.rdkfplinear:
        for nb in _set_default(args.rdkfplinear_nBits, [1024]):
            for rl in _set_default(args.rdkfplinear_length, [3]):
                param_dict[_make_name(('rdkfplinear', nb, rl))] = {'nBits': nb, 'radius': rl}
    if args.layered:
        for nb in _set_default(args.layered_nBits, [1024]):
            for rl in _set_default(args.layered_length, [3]):
                param_dict[_make_name(('layered', nb, rl))] = {'nBits': nb, 'radius': rl}
    if args.avalon:
        for nb in _set_default(args.avalon_nBits, [1024]):
            param_dict[_make_name(('avalon', nb))] = {'nBits': nb}
    if args.torsion:
        for nb in _set_default(args.torsion_nBits, [1024]):
            param_dict[_make_name(('torsion', nb))] = {'nBits': nb}
    if args.atompairs:
        for nb in _set_default(args.atompairs_nBits, [1024]):
            param_dict[_make_name(('atompairs', nb))] = {'nBits': nb}
    if args.circus:
        for lower in _set_default(args.circus_min, [1]):
            for upper in _set_default(args.circus_max, [2]):
                if int(lower) <= int(upper):
                    if args.onbond:
                        param_dict[_make_name(('circus_b', lower, upper))] = {'lower': lower, 'upper': upper, 'on_bond': True}
                    else:
                        param_dict[_make_name(('circus', lower, upper))] = {'lower': lower, 'upper': upper}
    if args.linear:
        for lower in _set_default(args.linear_min, [2]):
            for upper in _set_default(args.linear_max, [5]):
                if int(lower) <= int(upper):
                    param_dict[_make_name(('chyline', lower, upper))] = {'lower': lower, 'upper': upper}
    #if args.mordred2d:
    #    param_dict[_make_name(('mordred2d',))] = {}
    return param_dict


def _pickle_descriptors(output_dir, fragmentor, prop_name, desc_name):
    fragmentor_name = os.path.join(output_dir, '.'.join([prop_name, desc_name, 'pkl']))
    with open(fragmentor_name, 'wb') as f:
        pickle.dump(fragmentor, f, pickle.HIGHEST_PROTOCOL)

def launch_preparer():
    parser = argparse.ArgumentParser(prog='Descriptor calculator', 
                                     description='Prepares the descriptor files for hyperparameter optimization launch.')
    
    # I/O arguments
    parser.add_argument('-i', '--input', 
                        help='Input file, requires csv or Excel format')
    parser.add_argument('--structure_col', action='store', type=str, default='SMILES',
                        help='Column name with molecular structures representations. Default = SMILES.')
    parser.add_argument('--concatenate', action='extend', type=str, nargs='+', default=[],
                        help='Additional column names with molecular structures representations to be concatenated with the primary structure column.')
    parser.add_argument('--property_col',  action='extend', type=str, nargs='+', default=[],
                        help='Column with properties to be used. Case sensitive.')
    parser.add_argument('--property_names', action='extend', type=str, nargs='+', default=[],
                        help='Alternative name for the property columns specified by --property_col.')
    parser.add_argument('--standardize', action='store_true', default=False,
                        help='Standardize the input structures? Default = False.')
    parser.add_argument('-o', '--output', 
                         help='Output folder where the descriptor files will be saved.')
    parser.add_argument('-f', '--format', action='store', type=str, default='svm', choices=['svm', 'csv'],
                        help='Descriptor files format. Default = svm.')
    parser.add_argument('-p', '--parallel', action='store', type=int, default=0,
                        help='Number of parallel processes to use. Default = 0')
    parser.add_argument('-s', '--save', action='store_true',
                        help='Save (pickle) the fragmentors for each descriptor type.')
    parser.add_argument('--separate_folders', action='store_true',
                        help='Save each descriptor type into a separate folders.')
    parser.add_argument('--load_config', action='store', type=str, default='',
                        help='Load descriptor configuration from a JSON file. JSON parameters are prioritized! Use "basic" to load default parameters')
    parser.add_argument('--full_config', action='store', type=str, default='',
                        help='Load preparer configuration from a JSON file. In this case, all the other parameters are ignored.')

    # Morgan fingerprints
    parser.add_argument('--morgan', action='store_true', 
                        help='Option to calculate Morgan fingerprints.')
    parser.add_argument('--morgan_nBits', nargs='+', action='extend', type=int, default=[],
                        help='Number of bits for Morgan FP. Allows several numbers, which will be stored separately. Default = 1024.')
    parser.add_argument('--morgan_radius', nargs='+', action='extend', type=int, default=[],
                        help='Maximum radius of Morgan FP. Allows several numbers, which will be stored separately. Default = 2.')

    # Morgan feature fingerprints
    parser.add_argument('--morganfeatures', action='store_true', 
                        help='Option to calculate Morgan feature fingerprints.')
    parser.add_argument('--morganfeatures_nBits', nargs='+', action='extend', type=int, default=[],
                        help='Number of bits for Morgan feature FP. Allows several numbers, which will be stored separately. Default = 1024.')
    parser.add_argument('--morganfeatures_radius', nargs='+', action='extend', type=int, default=[],
                        help='Maximum radius of Morgan feature FP. Allows several numbers, which will be stored separately. Default = 2.')

    # RDKit fingerprints
    parser.add_argument('--rdkfp', action='store_true', 
                        help='Option to calculate RDkit fingerprints.')
    parser.add_argument('--rdkfp_nBits', nargs='+', action='extend', type=int, default=[],
                        help='Number of bits for RDkit FP. Allows several numbers, which will be stored separately. Default = 1024.')
    parser.add_argument('--rdkfp_length', nargs='+', action='extend', type=int, default=[],
                        help='Maximum length of RDkit FP. Allows several numbers, which will be stored separately. Default = 3.')

    # RDKit linear fingerprints
    parser.add_argument('--rdkfplinear', action='store_true', 
                        help='Option to calculate RDkit linear fingerprints.')
    parser.add_argument('--rdkfplinear_nBits', nargs='+', action='extend', type=int, default=[],
                        help='Number of bits for RDkit linear FP. Allows several numbers, which will be stored separately. Default = 1024.')
    parser.add_argument('--rdkfplinear_length', nargs='+', action='extend', type=int, default=[],
                        help='Maximum length of RDkit linear FP. Allows several numbers, which will be stored separately. Default = 3.')

    # RDKit layered fingerprints
    parser.add_argument('--layered', action='store_true', 
                        help='Option to calculate RDkit layered fingerprints.')
    parser.add_argument('--layered_nBits', nargs='+', action='extend', type=int, default=[],
                        help='Number of bits for RDkit layered FP. Allows several numbers, which will be stored separately. Default = 1024.')
    parser.add_argument('--layered_length', nargs='+', action='extend', type=int, default=[],
                        help='Maximum length of RDkit layered FP. Allows several numbers, which will be stored separately. Default = 3.')

    # Avalon fingerprints
    parser.add_argument('--avalon', action='store_true', 
                        help='Option to calculate Avalon fingerprints.')
    parser.add_argument('--avalon_nBits', nargs='+', action='extend', type=int, default=[], 
                        help='Number of bits for Avalon FP. Allows several numbers, which will be stored separately. Default = 1024.')

    # Atom pair fingerprints
    parser.add_argument('--atompairs', action='store_true', 
                        help='Option to calculate atom pair fingerprints.')
    parser.add_argument('--atompairs_nBits', nargs='+', action='extend', type=int, default=[],
                        help='Number of bits for atom pair FP. Allows several numbers, which will be stored separately. Default = 1024.')

    # Topological torsion fingerprints
    parser.add_argument('--torsion', action='store_true', 
                        help='Option to calculate topological torsion fingerprints.')
    parser.add_argument('--torsion_nBits', nargs='+', action='extend', type=int, default=[], 
                        help='Number of bits for topological torsion FP. Allows several numbers, which will be stored separately. Default = 1024.')

    # Chython Linear fragments
    parser.add_argument('--linear', action='store_true', 
                        help='Option to calculate ChyLine fragments.')
    parser.add_argument('--linear_min', nargs='+', action='extend', type=int, default=[],
                        help='Minimum length of linear fragments. Allows several numbers, which will be stored separately. Default = 2.')
    parser.add_argument('--linear_max', nargs='+', action='extend', type=int, default=[],
                        help='Maximum length of linear fragments. Allows several numbers, which will be stored separately. Default = 5.')

    # CircuS (Circular Substructures) fragments
    parser.add_argument('--circus', action='store_true', 
                        help='Option to calculate CircuS fragments.')
    parser.add_argument('--circus_min', nargs='+', action='extend', type=int, default=[],
                        help='Minimum radius of CircuS fragments. Allows several numbers, which will be stored separately. Default = 1.')
    parser.add_argument('--circus_max', nargs='+', action='extend', type=int, default=[],
                        help='Maximum radius of CircuS fragments. Allows several numbers, which will be stored separately. Default = 2.')
    parser.add_argument('--onbond', action='store_true', 
                        help='Toggle the calculation of CircuS fragments on bonds. With this option the fragments will be bond-cetered, making a bond the minimal element.')

    # Mordred 2D fingerprints
    #parser.add_argument('--mordred2d', action='store_true', 
    #                    help='Option to calculate Mordred 2D descriptors.')
    # Solvents
    parser.add_argument('--solvent', type=str, action='store', default='',
                        help='Column that contains the solvents. Check the available solvents in the solvents.py script.')
    #parser.add_argument('--testset', nargs='+', action='extend', type=str, default=[],
    #                    help='Name(s) of the file(s) containing the test set(s) to calculate with the same descriptors')
    parser.add_argument("--logging", action="store", type=str, default="ERROR")

    args = parser.parse_args()

    if args.full_config:
        with open(args.full_config) as f:
            fconfig = json.load(f)
        _perform_fullconfig(fconfig)
    else:
        if args.load_config == "basic":
            vars(args).update(basic_params)
        elif args.load_config:
            with open(args.load_config) as f:
                p = json.load(f)
            vars(args).update(p)

        check_parameters(args)
        
        input_params = {
            'input_file': args.input,
            'structure_col': args.structure_col,
            'standardize': args.standardize,
            'property_col': args.property_col,
            'property_names': args.property_names,
            'concatenate': args.concatenate,
            'solvent': args.solvent
        }

        output_params = {
            'output': args.output,
            'separate': args.separate_folders,
            'format': args.format,
            'pickle': args.save,
            'write_output': True
        #    'test_sets':args.testset
        }
        create_output_dir(output_params['output'])

        inpt = create_input(input_params)

        descriptor_dictionary = _enumerate_parameters(args)
        # Create a multiprocessing pool (excluding mordred) with the specified number of processes
        # If args.parallel is 0 or negative, use the default number of processes
        pool = mp.Pool(processes=args.parallel if args.parallel > 0 else 1)
        non_mordred_descriptors = [desc for desc in descriptor_dictionary.keys() if 'mordred2d' not in desc]
        # Use pool.map to apply the calculate_and_output function to each set of arguments in parallel
        # The arguments are tuples containing (inpt, descriptor, descriptor_params, output_params)
        pool.map(calculate_and_output, [(inpt, desc, descriptor_dictionary[desc], output_params) for desc in non_mordred_descriptors])
        pool.close() # Close the pool and prevent any more tasks from being submitted
        pool.join() # Wait for all the tasks to complete

        # Serial mordred calculations
        #mordred_descriptors = [desc for desc in descriptor_dictionary.keys() if 'mordred2d' in desc]
        #for desc in mordred_descriptors:
        #    calculate_and_output((inpt, desc, descriptor_dictionary[desc], output_params))
