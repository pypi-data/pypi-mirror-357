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

import pandas as pd
from pandas import DataFrame
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from chython import smiles, CGRContainer, MoleculeContainer, ReactionContainer
from typing import Optional, List, Dict, Tuple, Iterable
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolDescriptors
from rdkit.Avalon import pyAvalonTools
#from mordred import Calculator, descriptors
from doptools.chem.utils import _add_stereo_substructure
from functools import partialmethod

from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')

# disabling the mordred tqdm log
from tqdm import tqdm
tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)


class DescriptorCalculator:
    """
    An abstract class for the descriptor calculatiors in this library.
    Made for utility functions, such as retrieveing the name, size, or
    features of the calculator.
    """
    def __init__(self, name: str, size: Tuple[int]):
        self._name = name
        self._size = size
        self._short_name = name
        self.feature_names = []

    @property
    def size(self) -> Tuple[int]:
        """
        Returns the size of the calculator as a tuple of integers.
        """
        
        return self._size

    @property
    def name(self) -> str:
        """
        Returns the name of the calculator as string.
        """
        return self._name

    @property
    def short_name(self):
        return self._short_name
    

    def get_feature_names(self) -> List[str]:
        """
        Returns the list of features as strings.
        """
        return self.feature_names
    

class ChythonCircus(DescriptorCalculator, BaseEstimator, TransformerMixin):
    """
    ChythonCircus class is a scikit-learn compatible transformer that
    calculates the fragment features from molecules and Condensed
    Graphs of Reaction (CGR). The features are augmented
    substructures - atom-centered fragments that take into account atom
    and its environment. Implementation-wise, this takes all atoms in
    the molecule/CGR, and builds topological neighborhood spheres
    around them. All atoms and bonds that are in a sphere of certain
    radius (1 bond, 2 bonds, etc) are taken into the substructure. The
    features are stored as hashes of these substructures for faster
    search. When the transform is called, the similar procedure will
    occur for the test set molecules, and the hashes that were found
    within the features of the calcualtor, will be updated. No new
    features will be added in transform!

    The implementation is similar to Morgan counts, although some
    differences (specifically, the representation of rings) are present
    due to different library requirements.

    The parameters of the calcualtor are the lower and the upper limits
    of the radius. By default, both are set to 0, which means only the
    count of atoms. Additionally, only_dynamic flag indicates of only
    fragments that contain a dynamic bond or atom will be considered
    (only works in case of CGRs). fmt parameter defines the format in
    which the molecules are given to the calculator. "mol" if they are
    in a chython MoleculeContainer or CGRContainer, "smiles" if they are
    in SMILES.
    """

    def __init__(self, lower: int = 0, upper: int = 0, only_dynamic: bool = False, 
                 on_bond: bool = False, fmt: str = "mol", keep_stereo = 'no'):
        """
        Circus descriptor calculator constructor.

        :param lower: lower limit of the radius.
        :type lower: int

        :param upper: upper limit of the radius.
        :type upper: int

        :param only_dynamic: toggle for calculating only fragments with dynamic items.
        :type only_dynamic: bool

        :param on_bond: toggle for calculating fragments centering on bonds.
        :type on_bond: bool

        param fmt: format of the molecules for input ('mol' for MoleculeContainers, 'smiles' for strings).
        :type fmt: str

        param keep_stereo: ("yes", "no", or "both") applicable for reactions to generate stereo-keeping CGR fragments.
        :type keep_stereo: str
        """
        self.feature_names = []
        self.lower = lower 
        self.upper = upper
        self.only_dynamic = only_dynamic
        self.fmt = fmt
        self.on_bond = on_bond
        self._name = "circus"
        self._size = (lower, upper)
        self.keep_stereo = keep_stereo
        all_params = ["C", str(lower), str(upper)]
        if on_bond:
            all_params += ["B"]
        if only_dynamic:
            all_params += ["D"]
        if keep_stereo == "yes":
            all_params += ["KS"]
        elif keep_stereo == "both":
            all_params += ["BS"]
        self._short_name = "-".join(all_params)
    
    def fit(self, X: DataFrame, y: Optional[List] = None):
        """
        Fits the calculator - finds all possible substructures in the
        given array of molecules/CGRs.

        :param X: the array/list/... of molecules/CGRs to train the augmentor.
            Collects all possible substructures.
        :type X: array-like, [MoleculeContainers, CGRContainers]

        :param y: required by default by scikit-learn standards, but
            doesn't change the function at all.
        :type y: None
        """
        self.feature_names = []
        for i, mol in enumerate(X):
            reac = None
            if self.fmt == "smiles":
                mol = smiles(mol)
            if isinstance(mol, ReactionContainer):
                reac = mol
                mol = reac.compose()
            for length in range(self.lower, self.upper+1):
                if not self.on_bond:
                    for atom in mol._atoms:
                        # deep is the radius of the neighborhood sphere in bonds
                        sub = mol.augmented_substructure([atom], deep=length)
                        sub_smiles = str(sub)
                        if self.keep_stereo=='yes' and isinstance(mol, CGRContainer):
                            sub_smiles = _add_stereo_substructure(sub, reac)
                        if sub_smiles not in self.feature_names:
                            # if dynamic_only is on, skip all non-dynamic fragments
                            if self.only_dynamic and ">" not in sub_smiles:
                                continue
                            self.feature_names.append(sub_smiles)
                        if self.keep_stereo=='both' and isinstance(mol, CGRContainer):
                            sub_smiles = _add_stereo_substructure(sub, reac)
                            if sub_smiles not in self.feature_names:
                            # if dynamic_only is on, skip all non-dynamic fragments
                                if self.only_dynamic and ">" not in sub_smiles:
                                    continue
                                self.feature_names.append(sub_smiles)
                else:
                    for bond in mol.bonds():
                        # deep is the radius of the neighborhood sphere in bonds
                        sub = mol.augmented_substructure([bond[0], bond[1]], deep=length)
                        sub_smiles = str(sub)
                        if self.keep_stereo=='yes' and isinstance(mol, CGRContainer):
                            sub_smiles = _add_stereo_substructure(sub, reac)
                        if sub_smiles not in self.feature_names:
                            # if dynamic_only is on, skip all non-dynamic fragments
                            if self.only_dynamic and ">" not in sub_smiles:
                                continue
                            self.feature_names.append(sub_smiles)
                        if self.keep_stereo=='both' and isinstance(mol, CGRContainer):
                            sub_smiles = _add_stereo_substructure(sub, reac)
                            if sub_smiles not in self.feature_names:
                            # if dynamic_only is on, skip all non-dynamic fragments
                                if self.only_dynamic and ">" not in sub_smiles:
                                    continue
                                self.feature_names.append(sub_smiles)
        return self

    def transform(self, X: Iterable, y: Optional[List] = None) -> DataFrame:
        """
        Transforms the given array of molecules/CGRs to a data frame
        with features and their values.

        :param X: the array/list/... of molecules/CGRs to transform to feature table
            using trained feature list.
        :type X: array-like, [MoleculeContainers, CGRContainers]

        :param y: required by default by scikit-learn standards, but
            doesn't change the function at all.
        :type y: None
        """
        table = pd.DataFrame(columns=self.feature_names)
        for i, mol in enumerate(X):
            visited_substructures = []
            reac = None
            if self.fmt == "smiles":
                mol = smiles(mol)
            if isinstance(mol, ReactionContainer):
                reac = mol
                mol = reac.compose()
            table.loc[len(table)] = 0
            for length in range(self.lower, self.upper+1):
                if not self.on_bond:
                    for atom in mol._atoms:
                        # deep is the radius of the neighborhood sphere in bonds
                        sub = mol.augmented_substructure([atom], deep=length)
                        sub_set = set([a for a in mol.augmented_substructure([atom], deep=length)._atoms.keys()])
                        sub_smiles = str(sub)
                        if self.keep_stereo=='yes' and isinstance(mol, CGRContainer):
                            sub_smiles = _add_stereo_substructure(sub, reac)
                        if sub_smiles in self.feature_names and sub_set not in visited_substructures:
                            visited_substructures.append(sub_set)
                            table.iloc[i, self.feature_names.index(sub_smiles)] += 1
                        if self.keep_stereo=='both' and isinstance(mol, CGRContainer):
                            sub_smiles = _add_stereo_substructure(sub, reac)
                            if sub_smiles in self.feature_names:
                                table.iloc[i, self.feature_names.index(sub_smiles)] += 1
                        
                else:
                    for bond in mol.bonds():
                        # deep is the radius of the neighborhood sphere in bonds
                        sub = mol.augmented_substructure([bond[0], bond[1]], deep=length)
                        sub_set = set([a for a in mol.augmented_substructure([bond[0], bond[1]], deep=length)._atoms.keys()])
                        sub_smiles = str(sub)
                        if self.keep_stereo=='yes' and isinstance(mol, CGRContainer):
                            sub_smiles = _add_stereo_substructure(sub, reac)
                        if sub_smiles in self.feature_names and sub_set not in visited_substructures:
                            visited_substructures.append(sub_set)
                            table.iloc[i, self.feature_names.index(sub_smiles)] += 1
                        if self.keep_stereo=='both' and isinstance(mol, CGRContainer):
                            sub_smiles = _add_stereo_substructure(sub, reac)
                            if sub_smiles in self.feature_names:
                                table.iloc[i, self.feature_names.index(sub_smiles)] += 1
        return table
    

class ChythonLinear(DescriptorCalculator, BaseEstimator, TransformerMixin):
    """
    ChythonLinear class is a scikit-learn compatible transformer that
    calculates the linear fragment features from molecules and
    Condensed Graphs of Reaction (CGR). Implementation-wise, this uses
    the linear fingeprints features from chython library. The features
    are stored as hashes of these substructures for faster search. When
    the transform is called, the similar procedure will occur for the
    test set molecules, and the hashes that were found within the
    features of the calcualtor, will be updated. No new features will
    be added in transform!

    The parameters of the calculator are the lower and the upper limits
    of the radius. By default, both are set to 0, which means only the
    count of atoms. Additionally, only_dynamic flag indicates of only
    fragments that contain a dynamic bond or atom will be considered
    (only works in case of CGRs). fmt parameter defines the format in
    which the molecules are given to the calculator. "mol" if they are
    in a chython MoleculeContainer or CGRContainer, "smiles" if they are
    in SMILES.
    """
    def __init__(self, lower: int = 0, upper: int = 0, only_dynamic: bool = False, fmt: str = "mol"):
        self.feature_names = []
        self.lower = lower 
        self.upper = upper
        self.only_dynamic = only_dynamic
        self.fmt = fmt
        self._name = "chyline"
        self._size = (lower, upper)
        all_params = ["H", str(lower), str(upper)]
        if only_dynamic:
            all_params += ["D"]
        self._short_name = "-".join(all_params)

    def fit(self, X: DataFrame, y: Optional[List] = None):
        """
        Fits the calculator - finds all possible substructures in the
        given array of molecules/CGRs.

        :param X: the array/list/... of molecules/CGRs to train the augmentor.
            Collects all possible substructures.
        :type X: array-like, [MoleculeContainers, CGRContainers]

        :param y: required by default by scikit-learn standards, but
            doesn't change the function at all.
        :type y: None
        """
        self.feature_names = []
        output = []
        for i, mol in enumerate(X):
            if self.fmt == "smiles":
                mol = smiles(mol)
            if isinstance(mol, ReactionContainer):
                reac = mol
                mol = reac.compose()
            output.append(mol.linear_smiles_hash(self.lower, self.upper, number_bit_pairs=0))
        self.feature_names = pd.DataFrame(output).columns
        return self

    def transform(self, X: DataFrame, y: Optional[List] = None):
        """
        Transforms the given array of molecules/CGRs to a data frame
        with features and their values.

        :param X: the array/list/... of molecules/CGRs to transform to feature table
            using trained feature list.
        :type X: array-like, [MoleculeContainers, CGRContainers]

        :param y: required by default by scikit-learn standards, but
            doesn't change the function at all.
        :type y: None
        """
        df = pd.DataFrame(columns=self.feature_names, dtype=int)

        output = []
        for m in X:
            if self.fmt == "smiles":
                m = smiles(m)
            if isinstance(m, ReactionContainer):
                reac = m
                m = reac.compose()
            output.append(m.linear_smiles_hash(self.lower, self.upper, number_bit_pairs=0))
        output = pd.DataFrame(output)
        output = output.map(lambda x: len(x) if isinstance(x, list) else 0)
        
        output2 = output[output.columns.intersection(df.columns)]
        df = pd.concat([df, output2])
        df = df.fillna(0)
        return df


class Fingerprinter(DescriptorCalculator, BaseEstimator, TransformerMixin):
    """
    Fingeprinter class is a scikit-learn compatible transformer that
    calculates various fingerprints implemented in the RDkit library
    for molecules. The feature names are stored as indices. When the
    transform is called, the fingperints are calculated based on the
    the parameters used during training.

    The parameters of the calculator are the type of fingerprints, the
    length of the vector (nBits), radius (used for Morgan FP and RDkit
    FP), and any addiitonal parameters that the RDkit FP type can
    take.
    """
    def __init__(self, fp_type, nBits: int = 1024, radius=None, params=None, fmt="mol", chirality=False):
        if params is None:
            params = {}
        self.fp_type = fp_type
        self.nBits = nBits
        self.fmt = fmt
        if radius is None:
            self._size = (nBits,)
        else:
            self._size = (radius, nBits)
        self.radius = radius
        self.params = params
        self.chirality = chirality
        self.info = dict([(i, []) for i in range(self.nBits)])
        self.feature_names = dict([(i, []) for i in range(self.nBits)])
        self.feature_names_chython = dict([(i, []) for i in range(self.nBits)])
        if fp_type == "morgan" and 'useFeatures' in params.keys() and params["useFeatures"]==True:
            self._name = "morganfeatures"
            self._short_name = "-".join(["MF", str(nBits), str(radius)])
        elif fp_type == "rdkfp" and 'branchedPaths' in params.keys() and params["branchedPaths"]==False:
            self._name = "rdkfplinear"
            self._short_name = "-".join(["RL", str(nBits), str(radius)])
        else:
            self._name = fp_type
            sh_name = {"atompairs":"AP", "avalon": "V", "morgan":"M",
                       "layered":"L", "torsion":"T", "rdkfp":"R"}
            all_params = [sh_name[fp_type], str(nBits)]
            if radius is not None:
                all_params.append(str(radius))
            self._short_name = "-".join(all_params)
        
    def fit(self, X: DataFrame, y=None):
        """
        Fits the fingerprint calculator.

        :param X: the array/list/... of molecules to train the calculator.
        :type X: array-like, [MoleculeContainers]

        :param y: required by default by scikit-learn standards, but
            doesn't change the function at all.
        :type y: None
        """
        
        return self
        
    def get_features(self, x, output="smiles"):

        features = dict([(i, []) for i in range(self.nBits)])
        if self.fmt == "smiles":
            m = Chem.MolFromSmiles(x)
        else:
            m = Chem.MolFromSmiles(str(x))
        if self.fp_type == 'avalon':
            pass
        elif self.fp_type == 'layered':
            pass
        elif self.fp_type == 'atompairs':
            pass
        elif self.fp_type == 'torsion':
            pass

        elif self.fp_type == "morgan":
            if "useFeatures" not in self.params:
                frg = Chem.rdFingerprintGenerator.GetMorganGenerator(radius=self.radius, 
                                                                    includeChirality=self.chirality, 
                                                                    fpSize=self.nBits)
            elif not self.params["useFeatures"]:
                frg = Chem.rdFingerprintGenerator.GetMorganGenerator(radius=self.radius, 
                                                                    includeChirality=self.chirality, 
                                                                    fpSize=self.nBits)
            else:
                feat_gen = Chem.rdFingerprintGenerator.GetMorganFeatureAtomInvGen()
                frg = Chem.rdFingerprintGenerator.GetMorganGenerator(radius=self.radius, 
                                                                    includeChirality=self.chirality, 
                                                                    fpSize=self.nBits, 
                                                                    atomInvariantsGenerator=feat_gen)
            ao = AllChem.AdditionalOutput()
            ao.CollectBitInfoMap()
            desc = frg.GetFingerprintAsNumPy(m, additionalOutput=ao)
            bmap = ao.GetBitInfoMap()
            for k, v in bmap.items():
                for i in v:
                    if i[1] > 0:
                        env = Chem.FindAtomEnvironmentOfRadiusN(m, i[1], i[0])
                        amap = {}
                        submol = Chem.PathToSubmol(m, env, atomMap=amap)
                        if output=="smiles":
                            features[k].append(Chem.MolToSmiles(submol, canonical=True))
                        elif output=="mapping":
                            features[k].append(tuple(amap.keys()))
                        else:
                            features[k] = bmap
                    else:
                        if output=="smiles":
                            features[k].append(m.GetAtomWithIdx(i[0]).GetSymbol())
                        elif output=="mapping":
                            features[k].append(tuple([i[0]]))
                        else:
                            features[k] = bmap
            for k, v in features.items():
                vt = [item for item in v if item != '']
                features[k] = set(vt)

                features = bmap
        elif self.fp_type == "rdkfp":
            frg = Chem.rdFingerprintGenerator.GetRDKitFPGenerator(maxPath=self.radius, 
                                                                    useHs=False, 
                                                                    fpSize=self.nBits,
                                                                    **self.params)
            ao = AllChem.AdditionalOutput()
            ao.CollectBitPaths()
            desc = frg.GetFingerprintAsNumPy(m, additionalOutput=ao)
            bmap = ao.GetBitPaths()
            for k, v in bmap.items():
                for i in v:
                    if output=="smiles":
                        features[k].append(Chem.MolFragmentToSmiles(m, 
                                                                atomsToUse=set(sum([[m.GetBondWithIdx(b).GetBeginAtomIdx(),
                                                                                    m.GetBondWithIdx(b).GetEndAtomIdx()] for b in i], [])),
                                                                bondsToUse=i))
                    elif output=="mapping":
                        features[k].append(tuple(set(sum([[m.GetBondWithIdx(b).GetBeginAtomIdx(),
                                                     m.GetBondWithIdx(b).GetEndAtomIdx()] for b in i], []))))
                    else:
                        features[k] = bmap                  
            for k, v in features.items():
                vt = [item for item in v if item != '']
                features[k] = set(vt)
        return features

    def get_feature_names(self) -> List[str]:
        return [str(i) for i in range(self.nBits)]
                                       
    def transform(self, X, y=None):
        """
        Transforms the given array of molecules to a data frame
        with features and their values.

        :param X: the array/list/... of molecules to transform to feature table
            using trained feature list.
        :type X: array-like, [MoleculeContainers]

        :param y: required by default by scikit-learn standards, but
            doesn't change the function at all.
        :type y: None
        """
        res = []
        for x in X:
            if self.fmt == "smiles":
                m = Chem.MolFromSmiles(x)
            else:
                m = Chem.MolFromSmiles(str(x))
            if self.fp_type == 'avalon':
                res.append(pyAvalonTools.GetAvalonFP(m, nBits=self.nBits))
            elif self.fp_type == 'layered':
                res.append(Chem.LayeredFingerprint(m, fpSize=self.nBits,
                                                   maxPath=self.size[0], **self.params))
            else:
                if self.fp_type == "atompairs":
                    frg = Chem.rdFingerprintGenerator.GetAtomPairGenerator(includeChirality=self.chirality,
                                                                     fpSize=self.nBits)
                if self.fp_type == 'morgan':
                    if "useFeatures" not in self.params:
                        frg = Chem.rdFingerprintGenerator.GetMorganGenerator(radius=self.radius, 
                                                                                           includeChirality=self.chirality, 
                                                                                           fpSize=self.nBits)
                    elif not self.params["useFeatures"]:
                        frg = Chem.rdFingerprintGenerator.GetMorganGenerator(radius=self.radius, 
                                                                                           includeChirality=self.chirality, 
                                                                                           fpSize=self.nBits)
                    else:
                        feat_gen = Chem.rdFingerprintGenerator.GetMorganFeatureAtomInvGen()
                        frg = Chem.rdFingerprintGenerator.GetMorganGenerator(radius=self.radius, 
                                                                                           includeChirality=self.chirality, 
                                                                                           fpSize=self.nBits, 
                                                                                           atomInvariantsGenerator=feat_gen)
                if self.fp_type == 'torsion':
                    frg = Chem.rdFingerprintGenerator.GetTopologicalTorsionGenerator(includeChirality=self.chirality, 
                                                                               fpSize=self.nBits)
                if self.fp_type == 'rdkfp':
                    frg = Chem.rdFingerprintGenerator.GetRDKitFPGenerator(maxPath=self.radius, 
                                                                                         useHs=False, 
                                                                                         fpSize=self.nBits,
                                                                                         **self.params)
                res.append(frg.GetFingerprintAsNumPy(m))
        return pd.DataFrame(np.array(res), columns=[str(i) for i in range(self.nBits)])


class ComplexFragmentor(DescriptorCalculator, BaseEstimator, TransformerMixin):
    """
    ComplexFragmentor class is a scikit-learn compatible transformer that concatenates the features 
    according to specified associations. The most important argument is the "associator" - a list of tuples
    that establishes the correspondence between a column in a data frame X and the transformer 
    that is trained on it (similarly to how sklearn Pipeline works).

    For example, say you have a data frame with molecules/CGRs in one column ("molecules"), and 
    solvents in another ("solvent"). You want to generate a feture table that includes both structural 
    and solvent descriptors. You would define a ComplexFragmentor class with associator as a list of tuples,
    where each tuple is a pair of column names and the corresponding feature generators. In this case, e.g.,

        associator = [("molecules", Augmentor(lower=a, upper=b)),
                      ("solvent":SolventVectorizer())]  # see CIMTools library for solvent features

    ComplexFragmentor assumes that one of the types of features will be structural, thus, 
    "structure_column" parameter defines the column of the data frame where structures are found.
    """
    def __init__(self, associator: List[Tuple[str, object]], structure_columns=None):
        self.structure_columns = [] if structure_columns is None else structure_columns
        self.associator = associator
        #self.fragmentor = self.associator[self.structure_column]
        self.feature_names = []
        self._name = "ComplexFragmentor"
        self._short_name = ".".join([c[1].short_name for c in associator])
    
    def fit(self, x: DataFrame, y: Optional[List] = None):
        """
        Fits the calculator - finds all possible substructures in the
        given array of molecules/CGRs.

        :param x: the dataframe with the columns containing structures or solvents.
            Trains each calculator separately on the corresponding column.
        :type x: DataFrame

        :param y: required by default by scikit-learn standards, but
            doesn't change the function at all.
        :type y: None
        """
        self.feature_names = []
        for k, v in self.associator:
            if k == "numerical":
                v.fit(x)
            else:
                v.fit(x[k])
            self.feature_names += [k+'::'+f for f in v.get_feature_names()]
        return self

    def transform(self, x: DataFrame, y: Optional[List] = None) -> DataFrame:
        """
        Transforms the given data frame to a data frame of features
        with their values. Applies each feature generator
        separately, then concatenates them.

        :param x: the data frame to transform to feature table using
            trained feature list. Must contain columns indicated in the
            associator.
        :type x: DataFrame

        :param y: required by default by scikit-learn standards, but
            doesn't change the function at all.
        :type y: None
        """
        concat = []
        if not isinstance(x, DataFrame) and isinstance(x, (dict, list, pd.Series)):
            x = pd.DataFrame(x if isinstance(x, list) else [x])
        for k, v in self.associator:
            if len(x.shape) == 1:
                if k == "numerical":
                    concat.append(v.transform(x.iloc[:1]))
                else:
                    concat.append(v.transform([x.iloc[:1][k]]))

            else:
                if k == "numerical":
                    concat.append(v.transform(x))
                else:
                    concat.append(v.transform(x[k]))
        res = pd.concat(concat, axis=1, sort=False)
        res.columns = self.feature_names
        return res


# class Mordred2DCalculator(DescriptorCalculator, BaseEstimator, TransformerMixin):
#     """
#     Mordred2DCalculator class is a scikit-learn compatible transformer that
#     calculates Mordred 2D descriptors.
#     """
#     def __init__(self):
#         self._size = ()
#         self._name = "mordred2D"
#         self.calculator = None
#         self._short_name = "M2"

#     def fit(self, X, y=None):
#         """
#         Fits the Mordred calculator.

#         :param X: the array/list/... of molecules to train the calculator.
#         :type X: array-like, [MoleculeContainers]

#         :param y: required by default by scikit-learn standards, but
#             doesn't change the function at all.
#         :type y: None
#         """
#         mols = [Chem.MolFromSmiles(str(x)) for x in X]
#         self.calculator = Calculator(descriptors, ignore_3D=True)
#         matrix = self.calculator.pandas(mols).select_dtypes(include='number')
#         self.feature_names = list(matrix.columns)
#         return self

#     def transform(self, X, y=None):
#         """
#         Transforms the given array of molecules to a data frame
#         with features and their values.

#         :param X: the array/list/... of molecules to transform to feature table
#             using trained feature list.
#         :type X: array-like, [MoleculeContainers]

#         :param y: required by default by scikit-learn standards, but
#             doesn't change the function at all.
#         :type y: None
#         """
#         mols = [Chem.MolFromSmiles(str(x)) for x in X]
#         matrix = self.calculator.pandas(mols).select_dtypes(include='number')
#         return matrix[self.feature_names]
        

class PassThrough(DescriptorCalculator, BaseEstimator, TransformerMixin):
    """
    PassThrough is a sklearn-compatible transformer that passes a column
    from a Dataframe into the feature Dataframe without any changes. It
    is functionally identical to sklearn.compose ColumnTransformer's
    passthrough function. Needed to be compatible with
    ComplexFragmentor.
    """
    def __init__(self, column_names: List[str]):
        self.column_names = column_names
        self.feature_names = self.column_names
        self._name = "numerical"
        self._short_name = "N"
        self._size = ()
    
    def fit(self, x: DataFrame, y=None):
        """
        Fits the calculator. Parameters are not necessary.
        """
        return self
    
    def transform(self, x: DataFrame, y: Optional[List] = None):
        """
        Returns the column without any transformation.

        :param x: dataframe from which the columns will be taken
        :type x: DataFrame

        :param y: required by default by scikit-learn standards, but
            doesn't change the function at all.
        :type y: None
        """
        return pd.DataFrame(x[self.column_names], columns=self.column_names)

    def get_feature_names(self):
        return self.feature_names


class ChythonCircusNonhash(BaseEstimator, TransformerMixin):
    """
    ChythonCircus class is a scikit-learn compatible transformer that
    calculates the fragment features from molecules and Condensed
    Graphs of Reaction (CGR). The features are augmented
    substructures - atom-centered fragments that take into account atom
    and its environment. Implementation-wise, this takes all atoms in
    the molecule/CGR, and builds topological neighborhood spheres
    around them. All atoms and bonds that are in a sphere of certain
    radius (1 bond, 2 bonds, etc) are taken into the substructure. All
    such substructures are detected and stored as distinct features.
    The substructures will keep any rings found within them. The value
    of the feature is the number of occurrence of such substructure in
    the given molecule. 

    OLD IMPLEMENTATION!!! This is the old implementation and requires
    quite a long time to perform.

    The parameters of the augmentor are the lower and the upper limits
    of the radius. By default, both are set to 0, which means only the
    count of atoms. Additionally, only_dynamic flag indicates of only
    fragments that contain a dynamic bond or atom will be considered
    (only works in case of CGRs). fmt parameter defines the format in
    which the molecules are given to the calculator. "mol" if they are
    in Chython MoleculeContainer or CGRContainer, "smiles" if they are
    in SMILES.
    """

    def __init__(self, lower: int = 0, upper: int = 0, only_dynamic: bool = False, fmt: str = "mol"):
        """
        Circus descriptor calculator constructor.

        :param lower: lower limit of the radius.
        :type lower: int

        :param upper: upper limit of the radius.
        :type upper: int

        :param only_dynamic: toggle for calculating only fragments with dynamic items.
        :type only_dynamic: bool

        param fmt: format of the molecules for input ('mol' for MoleculeContainers, 'smiles' for strings).
        :type fmt: str
        """
        self.feature_names = []
        self.features = []
        self.lower = lower 
        self.upper = upper
        self.only_dynamic = only_dynamic
        self.fmt = fmt
        self._name = "linear"
        self._size = (lower, upper)
    
    def fit(self, X: DataFrame, y: Optional[List] = None):
        """
        Fits the calculator - finds all possible substructures in the
        given array of molecules/CGRs.

        :param X: the array/list/... of molecules/CGRs to train the augmentor.
            Collects all possible substructures.
        :type X: array-like, [MoleculeContainers, CGRContainers]

        :param y: required by default by scikit-learn standards, but
            doesn't change the function at all.
        :type y: None
        """
        self.feature_names = []
        self.features = []
        for i, mol in enumerate(X):
            if self.fmt == "smiles":
                mol = smiles(mol)
            for length in range(self.lower, self.upper+1):
                for atom in mol.atoms():
                    # deep is the radius of the neighborhood sphere in bonds
                    sub = mol.augmented_substructure([atom[0]], deep=length)
                    if sub not in self.features:
                        # if dynamic_only is on, skip all non-dynamic fragments
                        if self.only_dynamic and ">" not in str(sub):
                            continue
                        self.feature_names.append(str(sub))
                        self.features.append(sub)
        return self

    def transform(self, X: DataFrame, y: Optional[List] = None) -> DataFrame:
        """
        Transforms the given array of molecules/CGRs to a data frame
        with features and their values.

        :param X: the array/list/... of molecules/CGRs to transform to feature table
            using trained feature list.
        :type X: array-like, [MoleculeContainers, CGRContainers]

        :param y: required by default by scikit-learn standards, but
            doesn't change the function at all.
        :type y: None
        """
        table = pd.DataFrame(columns=self.feature_names)
        for i, mol in enumerate(X):
            if self.fmt == "smiles":
                mol = smiles(mol)
            table.loc[len(table)] = 0
            for sub in self.features:
                # if CGRs are used, the transformation of the substructure to the CGRcontainer is needed
                mapping = list(sub.get_mapping(mol))
                # mapping is the list of all possible substructure mappings into the given molecule/CGR
                table.loc[i, str(sub)] = len(mapping)
        return table

    def get_feature_names(self):
        return self.feature_names


__all__ = ['ChythonCircus', 'ChythonCircusNonhash', 'ChythonLinear', 'ComplexFragmentor',
           'DescriptorCalculator', 'Fingerprinter', 'PassThrough']
