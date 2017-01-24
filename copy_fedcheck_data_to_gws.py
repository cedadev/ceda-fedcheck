#!/usr/bin/env python
"""
This program is for the ESGF fedcheck data, which is being performed in preparation for CMIP6.
The purpose is to copy CMIP5 data from the CEDA archive to the ESGF fedcheck group workspace while
changing the data reference syntax from the CMIP5 structure to the CMIP6 structure.

Initially using data under /badc/cmip5/data/cmip5/output1/MOHC/HadGEM2-ES/esmControl
Destination: /group_workspaces/jasmin/esgf_fedcheck/archive

CMIP5 DRS: <project>.<product>.<institute>.<model>.<frequency>.<realm>.<table>.<ensemble>.<version>
CMIP6 DRS: <project>.<product>.<institute>.<model>.<frequency>.<realm>.<table>.<ensemble>.<variable>.<version>

At /badc/cmip5/data/<project>/<output>/<institute>/<model>/<frequency>/<realm>/<table>/<ensemble>/
There are directories
/files
/latest
/vYYYYMMDD
/vYYYYMMDD
"""


import os, sys, re, glob, time, datetime
import shutil

def parse_filename(filename):
    """
    Routine to parse CMIP5 filename into consituent facets

    :param filename: CMIP5 filename
    :returns: realm, table, ensemble, folder, variable, ncfile
    """

    file = filename.split('/')
    realm = file[10].strip()
    table = file[11].strip()
    ensemble = file[12].strip()
    folder = file[13].strip()
    variable = file[14].strip()
    ncfile = file[15].strip()

    return realm, table, ensemble, folder, variable, ncfile



def copy_files(source_basedir, dest_basedir):
    """
    Routine that copies all archive esgf-fedcheck CMIP5 data to the gws
    Changes to the CMIP6 data reference syntax
    Reconstructs symbolic links and versioning

    :param source_basedir: Source data up to experiment in DRS
    :param dest_basedir: ESGF-fedcheck gws archive replica
    """

    project = source_basedir.split('/')[4].strip()
    product = source_basedir.split('/')[5].strip()
    institute = source_basedir.split('/')[6].strip()
    model = source_basedir.split('/')[7].strip()
    experiment = source_basedir.split('/')[8].strip()
    frequency = source_basedir.split('/')[9].strip()

    for path, dirs, files in os.walk(source_basedir):
        for file in files:
            if not os.path.islink(os.path.join(path, file)):

                # Original file in archive
                source_file = os.path.join(path, file)

                # Get CMIP5 facets from file name
                realm, table, ensemble, folder, variable, ncfile = parse_filename(os.path.join(path, file))

                # Name destination file in esgf-fedcheck gws files/ folder
                dest_file = os.path.join(dest_basedir, project, product, institute, model, experiment,
                                             frequency, realm, table, ensemble, variable, folder, ncfile)

                print "COPY:" + source_file
                print "DEST:" + dest_file

                # Get version folder from variable name
                var = variable.split('_')[0].strip()
                version = 'v' + variable.split('_')[1].strip()

                # VERSIONING
                # Create the version folder if it doesn't exist
                dest_version_dir = os.path.join(dest_basedir, project, product, institute, model, experiment,
                                             frequency, realm, table, ensemble, var, version)

                if not os.path.exists(dest_version_dir):
                    print "MAKE DIR: " + dest_version_dir
                    # os.makedirs(dest_version_dir)


                # file to symlink to
                symblink_file = os.path.join(dest_version_dir, ncfile)
                # os.symlink(symblink_file, dest_file)


                # LATEST
                # Make latest dir if it doesn't exist
                latest_dir = os.path.join(dest_basedir, project, product, institute, model, experiment,
                                             frequency, realm, table, ensemble, var, 'latest')

                if not os.path.exists(latest_dir):
                    print "MAKE DIR: " + latest_dir
                    # os.makedirs(latest_dir)

                # Populate the version folder with symlinks to the data

                # DECIDE ON WHICH IS LATEST
                latest_file = os.path.join(latest_dir, ncfile)

                if not os.path.isfile(os.path.join(latest_dir, ncfile)):
                    # get current version
                    currentf_year = int(variable.split('_')[1].strip()[:4])
                    currentf_mon = int(variable.split('_')[1].strip()[4:6])
                    currentf_day = int(variable.split('_')[1].strip()[6:])
                    current_version = datetime.datetime(currentf_year, currentf_mon, currentf_day)

                    # get symlink version
#                    symlink_file = os.path.realpath(latest_file)

                    dest_file_var = dest_file.split('/')[16]
                    dest_file_year = int(dest_file_var.split('_')[1].strip()[:4])
                    dest_file_mon = int(dest_file_var.split('_')[1].strip()[4:6])
                    dest_file_day = int(dest_file_var.split('_')[1].strip()[6:])
                    symlink_version = datetime.datetime(dest_file_year, dest_file_mon, dest_file_day)

                    if current_version > symlink_version:
                        print "REPLACING SYMLINK SOURCE: " + latest_file
                        print "REPLACING SYMLINK DESTIN: " + dest_file
                        # os.symlink(latest_file, dest_file)
                else:
                    print "MAKE LATEST SYMLINK SOURCE: " + latest_file
                    print "MAKE LATEST SYMLINK DESTIN: " + dest_file
                    # make symbolic links
                    # os.symlink(latest_file, dest_file)

if __name__ == "__main__":
    source_basedir = '/badc/cmip5/data/cmip5/output1/MOHC/HadGEM2-ES/esmControl/mon'
    dest_basedir = '/group_workspaces/jasmin/esgf_fedcheck/archive/cmip5/data/'
    dest_file = copy_files(source_basedir, dest_basedir)

