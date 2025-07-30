import os
from pycdlib import PyCdlib

def create_iso(input_path: str, output_path: str):
    iso = PyCdlib()
    iso.new(interchange_level=3)

    if os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, input_path).replace("\\", "/").upper()
                iso_path = f'/{rel_path};1'
                try:
                    iso.add_file(full_path, iso_path)
                except Exception as e:
                    print(f"[IsoFier] Error on : {iso_path} : {e}")
    elif os.path.isfile(input_path):
        filename = os.path.basename(input_path).upper()
        iso.add_file(input_path, iso_path=f'/{filename};1')
    else:
        raise FileNotFoundError(f"[IsoFier] Unknow path : {input_path}")

    iso.write(output_path)
    iso.close()
    print(f"[IsoFier] Iso Created : {output_path}")
