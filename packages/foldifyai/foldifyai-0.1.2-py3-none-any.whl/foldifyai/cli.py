"""Command-line interface entrypoint for the `foldifyai` package."""
from __future__ import annotations

import pathlib
import sys

import requests

foldifyai_ENDPOINT = "https://gpu1.foldify.org/fold?seq="


def _usage() -> None:
    """Print a short help message using the actual executable name."""
    prog = pathlib.Path(sys.argv[0]).name or "foldify"
    print(f"Usage: {prog} <path_to_file.fasta>", file=sys.stderr)


#from foldifyai import fold
#fold('cofactors/')
# write out .a3m file and .pdb file 

# change to do chunks 12->42 in bfd and 12->42 in uniref? 60 chunks. so ~45% slower. 
# perhaps do 0,2,4,8,...50 in both?

import time 
import json 
from rdkit import Chem
from rdkit.Chem import AllChem
import urllib
from foldifyai.utils import get_type
def compute_3d_conformer(mol, version: str = "v3") -> bool:
    if version == "v3":
        options = AllChem.ETKDGv3()
    elif version == "v2":
        options = AllChem.ETKDGv2()
    else:
        options = AllChem.ETKDGv2()

    options.clearConfs = False
    conf_id = -1

    try:
        conf_id = AllChem.EmbedMolecule(mol, options)

        if conf_id == -1:
            print(
                f"WARNING: RDKit ETKDGv3 failed to generate a conformer for molecule "
                f"{Chem.MolToSmiles(AllChem.RemoveHs(mol))}, so the program will start with random coordinates. "
                f"Note that the performance of the model under this behaviour was not tested."
            )
            options.useRandomCoords = True
            conf_id = AllChem.EmbedMolecule(mol, options)

        #AllChem.UFFOptimizeMolecule(mol, confId=conf_id, maxIters=1000)
        # i set the maxIters=33 to skip more aggressively.
        AllChem.UFFOptimizeMolecule(mol, confId=conf_id, maxIters=33)

    except RuntimeError:
        pass  # Force field issue here
    except ValueError:
        pass  # sanitization issue here

    if conf_id != -1:
        conformer = mol.GetConformer(conf_id)
        conformer.SetProp("name", "Computed")
        conformer.SetProp("coord_generation", f"ETKDG{version}")

        return True

    return False

def test(seq, affinity=False):
    try:
        mol = AllChem.MolFromSmiles(seq)
        mol = AllChem.AddHs(mol)

        # Set atom names
        canonical_order = AllChem.CanonicalRankAtoms(mol)
        for atom, can_idx in zip(mol.GetAtoms(), canonical_order):
            atom_name = atom.GetSymbol().upper() + str(can_idx + 1)
            if len(atom_name) > 4:
                msg = (
                    f"{seq} has an atom with a name longer than "
                    f"4 characters: {atom_name}."
                )
                raise ValueError(msg)
            atom.SetProp("name", atom_name)

        success = compute_3d_conformer(mol)
        if not success:
            msg = f"Failed to compute 3D conformer for {seq}"
            raise ValueError(msg)

        mol_no_h = AllChem.RemoveHs(mol, sanitize=False)
        affinity_mw = AllChem.Descriptors.MolWt(mol_no_h) if affinity else None
        return True
    except Exception as e:
        print(e, seq)
        return False 

def fold(folder):
    from pathlib import Path
    from tqdm import tqdm
    import os 

    files = [a for a in Path(folder).rglob("*.fasta")]
    files = sorted(files, key=lambda p: os.path.getsize(str(p)))
    files = [str(a) for a in files]

    for p in tqdm(files):
        p = str(p)
        new_path = p.replace('.fasta','_raw.pdb')
        if os.path.exists(new_path): continue 
        content = open(p).read()
        if len(content) > 1000: continue 

        for line in content.split('\n'):
            if line.startswith('>'): continue 
            if line == '': continue 
            if get_type(line) == 'SMILES': 
                if not test(line): 
                    print(f"Skipping {p}. RDKit didn't like {line}. ")
                    continue 

        encoded = urllib.parse.quote(content, safe="")
        url = f"https://gpu1.foldify.org/fold?immediate_msa=True&seq={encoded}"
        
        # Open connection with progress reporting
        response = urllib.request.urlopen(url)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc=f"Streaming foldifyaing results {p}")
        
        result = ''
        while True:
            data = response.read(block_size)
            if not data:
                break
            result += data.decode('utf-8')
            progress_bar.update(len(data))
        progress_bar.close()
        
        with open(new_path, 'w') as f: f.write(result)

        jsons = [json.loads(a) for a in result.split('\n@\n') if a != '']
        msa = [a for a in jsons if a['type'] == 'data_msa']
        pdbs = [a for a in jsons if a['type'] == 'data_pdb']

        for num, (msa_id, msa_data) in enumerate(msa[0]['data'].items()):
            open(new_path.replace('_raw.pdb',f'_{num}.a3m'), 'w').write(msa_data)

        open(new_path.replace('_raw.pdb','.pdb'), 'w').write(pdbs[-1]['data'])

        time.sleep(1)


def main() -> None:  # pragma: no cover
    if len(sys.argv) != 2:
        _usage()
        raise SystemExit(1)
    fold(sys.argv[1])

    

if __name__ == "__main__":  # pragma: no cover
    sys.argv = ['foldifyai','cofactors/']
    main() 