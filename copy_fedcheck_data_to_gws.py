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

    file_parts = [part.strip() for part in filename.split("/")]
    realm, table, ensemble, folder, variable, ncfile = file_parts[10:]

    return realm, table, ensemble, folder, variable, ncfile



def copy_files(source_basedir, dest_basedir):
    """
    Routine that copies all archive esgf-fedcheck CMIP5 data to the gws
    Changes to the CMIP6 data reference syntax
    Reconstructs symbolic links and versioning

    :param source_basedir: Source data up to experiment in DRS
    :param dest_basedir: ESGF-fedcheck gws archive replica
    """

    split_basedir = [part.strip() for part in source_basedir.split('/')]
    product, institute, model, experiment, frequency = split_basedir[5:10]
    project = 'cmip6'

    for path, dirs, files in os.walk(source_basedir):
        for file in files:
            if not os.path.islink(os.path.join(path, file)):

                # Original file in archive
                source_file = os.path.join(path, file)

                # Get CMIP5 facets from file name
                realm, table, ensemble, files_folder, var_date, ncfile = parse_filename(os.path.join(path, file))

                # Get version folder from var_date name
                variable, date = [part.strip() for part in var_date.split('_')]

                # Name destination file in esgf-fedcheck gws files/ folder
                dest_dir = os.path.join(dest_basedir, project, product, institute, model, experiment,
                                             frequency, realm, table, ensemble, variable, files_folder, var_date)

                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)

                dest_file = os.path.join(dest_dir, ncfile)
                shutil.copy(source_file, dest_file)

                print "COPY:" + source_file
                print "DEST:" + dest_file

                # VERSIONING
                # Create the version folder if it doesn't exist
                version = 'v' + date
                dest_version_dir = os.path.join(dest_basedir, project, product, institute, model, experiment,
                                             frequency, realm, table, ensemble, variable, version)
                if not os.path.exists(dest_version_dir):
                    print "MAKE DIR: " + dest_version_dir
                    os.makedirs(dest_version_dir)

                # Change dir to make relative symlinks
                print "PWD: " + dest_version_dir
                os.chdir(dest_version_dir)

                # file to symlink to
#                link_target = os.path.join('../files/d%/s%') % (version, ncfile)
                link_target = os.path.join('../files/' + var_date + '/' + ncfile)
                link_src = os.path.join(dest_version_dir, ncfile)
                # MAKE LINK
                print "LINKING: " + link_target
                print "WITH   : " + link_src
                os.symlink(link_target, link_src)

                # CREATE "latest" DIRECTORY SYMLINK

                # Make latest dir if it doesn't exist
                latest_dir = os.path.join(dest_basedir, project, product, institute, model, experiment,
                                             frequency, realm, table, ensemble, variable, 'latest')

                if not os.path.exists(latest_dir):
                    print "SYMLINK LATEST: " + dest_version_dir
                    print "WITH    LATEST: " + latest_dir
                    os.symlink(dest_version_dir, latest_dir)
                else:
                    # DECIDE ON WHICH IS LATEST
                    # get current version
                    existing_dir_date = os.readlink(latest_dir)[-8:]
                    date_ints = [int(item) for item in (existing_dir_date[:4], existing_dir_date[4:6], existing_dir_date[6:8])]
                    existing_version = datetime.datetime(*date_ints)
                    date_ints = [int(item) for item in (date[:4], date[4:6], date[6:8])]
                    current_version = datetime.datetime(*date_ints)
                    print existing_version
                    print current_version

                    if current_version > existing_version:
                        # REPLACE SYMLINK
                        print "REPLACING SYMLINK SOURCE: " + dest_version_dir
                        print "REPLACING SYMLINK DESTIN: " + latest_dir
                        os.symlink(dest_version_dir, latest_dir)

if __name__ == "__main__":

    source_basedir = '/badc/cmip5/data/cmip5/output1/MOHC/HadGEM2-ES/esmControl/mon'
    dest_basedir = '/group_workspaces/jasmin/esgf_fedcheck/archive/badc/cmip6/data'
    dest_file = copy_files(source_basedir, dest_basedir)

