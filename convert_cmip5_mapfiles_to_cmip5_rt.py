#!/usr/bin/env python

import string
import re
import sys
import os

"""
Takes one or more mapfiles (paths on the command line) which
correspond to an ESGF cmip5 dataset, and turns each mapfile into
a set of mapfiles in which the variable name has been added as 
last element of the DRS, the output map files being saved under
a separate top level directory
"""

def read_file(fn):
    with open(fn) as f:
        lines = f.readlines()
    return lines

def is_version(st):
    return re.match("v[0-9]+$", st)

def molest_line(line):
    "return revised line, and the new dataset ID"
    bits = line.split()
    dsid_orig = bits[0]
    path = bits[2]
    path_bits = path.split("/")
    version = path_bits[-3]
    assert is_version(version)
    varname = path_bits[-2]
    ds_bits = dsid_orig.split(".")
    assert len(ds_bits) == 9
    assert ds_bits[0] == "cmip5"
    ds_bits.append(varname)
    ds_bits[0] = "cmip5_rt"    
    dsid_new = string.join(ds_bits, ".")
    bits[0] = dsid_new
    line_new = string.join(bits, " ")
    return dsid_new, line_new
    
def get_output_path(fn, dsid, version, outroot): 
    origdir = os.path.dirname(fn)
    newdir = os.path.join(outroot, origdir.replace("/cmip5/", "/cmip5_rt/"))
    dsid_with_version = "%s.%s" % (dsid, version)
    return os.path.join(newdir, dsid_with_version)
    
def write_file(path, lines):
    dname = os.path.dirname(path)
    if not os.path.isdir(dname):
        os.makedirs(dname)
    with open(path, "w") as f:
        for line in lines:
            f.write(line)

def molest_mapfile(fn, outroot):
    lines = read_file(fn)
    dss = {}
    version = fn.split(".")[-1]
    assert is_version(version)
    for line in lines:
        dsid_new, line_new = molest_line(line)        
        if dsid_new not in dss:
            dss[dsid_new] = []
        dss[dsid_new].append(line_new)

    for dsid in dss:
        output_file = get_output_path(fn, dsid, version, outroot)
        print output_file
        write_file(output_file, dss[dsid])
        

if __name__ == '__main__':
    files = sys.argv[1:]
    for file in files:
        molest_mapfile(file, "with_var")
    

