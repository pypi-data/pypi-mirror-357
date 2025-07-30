from rdworks import Mol
from rdworks.xtb.wrapper import GFN2xTB
from rdworks.testdata import drugs

from pathlib import Path


# In ASE, the default energy unit is eV (electron volt).
# It will be converted to kcal/mol
# CODATA 2018 energy conversion factor
hartree2ev = 27.211386245988
hartree2kcalpermol = 627.50947337481
ev2kcalpermol = 23.060547830619026


datadir = Path(__file__).parent.resolve() / "data"
workdir = Path(__file__).parent.resolve() / "outfiles"

workdir.mkdir(exist_ok=True)

name = 'Atorvastatin'
testmol = Mol(drugs[name], name).make_confs(n=50).optimize_confs()
testmol = testmol.drop_confs(similar=True, verbose=True).sort_confs()


def test_xtb_wrapper():
    from rdworks.xtb.wrapper import GFN2xTB
    assert GFN2xTB.is_xtb_ready() == True
    assert GFN2xTB.is_cpx_ready() == True
    assert GFN2xTB.is_cpcmx_ready() == True
    assert GFN2xTB.is_ready() == True
    assert GFN2xTB.version() is not None


def test_singlepoint():        
    mol = testmol.copy()

    print("number of conformers=", mol.count())
    print("number of atoms=", mol.confs[0].natoms)

    gfn2xtb = GFN2xTB(mol.confs[0].rdmol)

    print("GFN2xTB.singlepoint()")
    outdict = gfn2xtb.singlepoint()
    print(outdict)
    print()

    print("GFN2xTB.singlepoint(water='gbsa')")
    outdict = gfn2xtb.singlepoint(water='gbsa')
    print(outdict)
    print()

    print("GFN2xTB.singlepoint(water='alpb')")
    outdict = gfn2xtb.singlepoint(water='alpb')
    print(outdict)
    print()

    print("GFN2xTB.singlepoint(water='cpcmx')")
    outdict = gfn2xtb.singlepoint(water='cpcmx')
    print(outdict)
    print()


def test_optimize():
    mol = testmol.copy()
    print("number of conformers=", mol.count())
    print("GFN2xTB.optimize()")
    outdict = GFN2xTB(mol.confs[0].rdmol).optimize(verbose=True)
    print(outdict)
    print()


def test_state_generate():
    import rdworks
    import numpy as np
    import os

    task_queue = 'xtb'

    kT = 0.001987 * 300.0 # (kcal/mol K)

    smiles =  'CCCCNC(=O)[C@@H]1CCCN1[C@@H](CC)c1nnc(Cc2ccc(C)cc2)o1'
    n = 50
    method = 'ETKDG'

    standardized = rdworks.Mol(smiles)
    libr = rdworks.complete_tautomers(standardized)

    PE = []
    for mol in libr:
        mol = mol.make_confs(n=n, method=method, verbose=True)
        mol = mol.optimize_confs(calculator='MMFF94', verbose=True)
        mol = mol.drop_confs(similar=True, similar_rmsd=0.3, verbose=True)
        mol = mol.sort_confs(calculator='xTB', verbose=True)
        mol = mol.drop_confs(k=10, window=15.0, verbose=True) # enforcing both conditions
        _PE = []
        for conf in mol.confs:
            conf = conf.optimize(calculator='xTB', verbose=True)
            # GFN2xTB requires 3D coordinates
            xtb = GFN2xTB(conf.rdmol).singlepoint(water='cpcmx', verbose=True)
            _PE.append(xtb.PE)
        # SimpleNamespace(
        #             PE = datadict['total energy'] * hartree2kcalpermol,
        #             Gsolv = Gsolv,
        #             charges = datadict['partial charges'],
        #             wbo = Wiberg_bond_orders,
        #             )
        PE.append(_PE)
        print(_PE)
    
    # calculate population
    PE = np.array(PE)
    PE = PE - np.min(PE)
    Boltzmann_factors = np.exp(-PE/kT)
    # partition function
    Z = np.sum(Boltzmann_factors)
    # population
    p = np.sum(Boltzmann_factors/Z, axis=1)

    sorted_indices = sorted(list(enumerate(p)), key=lambda x: x[1], reverse=True) # [(0,p0), (1,p1), ...]

    molecular_states = []
    for idx, population in sorted_indices:
        if population < 0.05:
            continue

        # state.keys() = ['rdmol','smiles','charge','population','pKa', 'qikprop']

        state_mol = libr[idx].rename(f'state.{idx+1}').qed(
            properties=['QED', 'MolWt', 'LogP', 'TPSA', 'HBD', 'HBA'])
        
        basic_properties = {
            'QED'      : round(state_mol.props['QED'],   2),
            'MolWt'    : round(state_mol.props['MolWt'], 2),
            'LogP'     : round(state_mol.props['LogP'],  2),
            'TPSA'     : round(state_mol.props['TPSA'],  2),
            'HBD'      : state_mol.props['HBD'],
            'HBA'      : state_mol.props['HBA'],
            }
        
        state_props = {
            'method': task_queue,
            'PE(kcal/mol)': state_mol.confs[0].props['E_tot(kcal/mol)'],
            'population' : round(float(population), 3),
            'basic_properties': basic_properties,
            'rdkit_version': rdworks.__rdkit_version__,
            'rdworks_version': rdworks.__version__,
        }
        
        molecular_states.append((state_mol.serialize(compressed=True), state_props))
    
    print(molecular_states)



if __name__ == '__main__':
    test_xtb_wrapper()
    test_singlepoint()
    test_optimize()
    test_state_generate()
