#!/usr/bin/env python

# plots results of small file test
# to run, system needs to have pandas installed 
# check here for how to do that 
# http://git.app.eng.bos.redhat.com/git/perf-dept.git/tree/docker/openshift/beaker/container-jmeter-run/Performance/Jmeter-runs-for-container-performance/runtest.sh
# and function panas_setup from there

# prepare environment and import modules
# try to import pandas and matplotlib, in most cases these modules are not installed by default

import subprocess 

try:
    import matplotlib as mpl

    mpl.use('Agg')

    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np

except ImportError:
    print("modules not installed...getting them")
    print("Trying to install necessary modules")
    subprocess.call(['rpm', '-ihv', 'https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm'])
    subprocess.call(['yum', 'install', '-y', 'gcc', 'gcc-c++', 'libgcc', 'python-pip', 'python-devel', 'numpy',
                     'python-matplotlib'])
    subprocess.call(['pip', 'install', 'pandas'])
    subprocess.call(['pip', 'install', 'prettytable'])

import getopt
import matplotlib as mpl
import os
import sys

mpl.use('Agg')
import pandas as pd
import numpy as np


def usage():
    print("drawresult.py will draw smallfile test resutls\n")
    print("it takes below parameters")
    print("-r [,str], --resultfile=[,str] - result file where results are saved")
    print("-i [,str], --interimfile=[,str] - interim file name - we need this to configure results properly")
    print("-o [,str], --outputfile=[,str] - png file - the name of output .png file")
    print("-t [,str], --title=[,str] - title describing results")
    print("-p [,str], --plottype=[,str] -- plot tipe, it can be 'bars' or 'lines' ")
    print("-x [,str], --xlab=[,str] -- label for X axis")
    print("-y [,str], --ylab=[,str] -- label for Y axis")
    print("-s [,int], --series=[int] -- how many series of test were executed")


def main():
    try:
        options, args = getopt.getopt(sys.argv[1:], "r:i:o:t:p:x:y:s:h",
                                      ["resultfile=", "interimfile=", "outputfile=", "title=", "plottype=", "xlab=",
                                       "ylab=","series=", "help"])

        if len(options) < 5:
            print("Check input parameters\n")
            usage()
            sys.exit(0)

        else:
            for opt, arg in options:

                if opt in ("-r", "--resultfile"):
                    resultfile = str(arg)

                elif opt in ("-i", "--interimfile"):
                    interimfile = str(arg)

                elif opt in ("-o", "--outputfile"):
                    outputfile = str(arg)

                elif opt in ("-t", "--title"):
                    title = str(arg)

                elif opt in ("-p", "--plottype"):
                    plottype = str(arg)

                elif opt in ("-x", "--xlab"):
                    xlab = str(arg)

                elif opt in ("-y", "--ylab"):
                    ylab = str(arg)
                
                elif opt in ("-s", "--series"):
                    series = int(arg)

                elif opt in ("-h", "--help"):
                    usage()

    except getopt.GetoptError, err:
        print(str(err))
        sys.exit()

    with open(resultfile, 'r') as inputfile:
        with open(interimfile, 'w') as finalfile:
            for line in inputfile:
                if not (line.startswith('instances') or line.startswith('\n')):
                    finalfile.write(line)

    defaultdeletechars = set("""~!@#$%^&*()=+~\|]}[{';: /?.>,<""")
    dataArray = np.genfromtxt(interimfile, delimiter=',', dtype=None,  autostrip=1, case_sensitive=True, names=True,
                              deletechars="""~!@#$%^&*()=+~\|]}[{';: /?>,<""")
    # dtype=None
    # names=True
    # usecols = (1,10)
    # read http://docs.scipy.org/doc/numpy/reference/generated/numpy.genfromtxt.html
    # check this usecol parameter - possible to draw all in one run

    result = pd.DataFrame(dataArray, index= [x for x in range(1,series+1)]) 
    #result.set_axis_bgcolor("lightslategray")
    # check index https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.plot.line.html

    if plottype == "bars":
        result.plot(kind='bar') # ,color="green")
    elif plottype == "lines":
        result.plot()
    else:
        print
        "Something is broken in state of Denmark"

    plt.legend(loc="upper right", ncol=1, prop={'size': 8}, bbox_to_anchor=(1.6, 1))
    plt.xticks(rotation=0)

    plt.title(title) 
    plt.xlabel(xlab, fontsize=10)
    plt.ylabel(ylab)
    plt.savefig(outputfile, bbox_inches="tight", format=None)
    os.remove(interimfile)
    sys.exit()


if __name__ == "__main__":
    main()
