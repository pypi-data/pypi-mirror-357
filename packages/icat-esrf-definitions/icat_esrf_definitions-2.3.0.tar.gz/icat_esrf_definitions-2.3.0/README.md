# HDF5 Master config

This repository contains the XML file that describes the mapping between ICAT database and the master file in HDF5 format. It also contains a set of [tools](#tools) that will help with the maintenance of it.

:warning: The file `hdf5_cfg.xml` is not longer updated and only exists for backward compatibility with `pyicat-plus<=0.1.7`.
The new definitions file is `src/icat_esrf_definitions/hdf5_cfg.xml`. Changes should be applied to the new file only.

# Techniques

1. TOMO
2. FLUO
3. KMAP
4. MX
5. BIOSAXS
6. PTYCHO
7. MRT


# Tools

## Requirements

### Proxy 

In case of need a proxy should be well setup:
```
export https_proxy=https://proxy.esrf.fr:3128
```
### python-icat

Some tools will need python-icat version 0.12.0  and version 0.13.1 will not work

#### Installing python-icat

Go to the URL :
```
https://icatproject.org/user-documentation/python-icat/
```
and download file called python-icat-0.12.0.tar.gz:
```
-rw-r--r-- 1 blissadm bliss 272576 Oct 10  2016 python-icat-0.12.0.tar.gz
c9034ad2a725ba1317a911940c577a8b  python-icat-0.12.0.tar.gz
```
This file can be found on:
```
/segfs/bliss/projects/ICAT/python-icat
-rw-r--r-- 1 homsrego soft 272576 Feb 12 16:48 python-icat-0.12.0.tar.gz


```

Uncompress and install the tar by using pip:
```
cd Downloads
tar -xvzf python-icat-0.12.0.tar.gz
cd python-icat-0.12.0
pip install .
```

Test:
```
~/icat/python-icat % python 
Python 2.7.9 (default, Jun 29 2016, 13:08:31) 
[GCC 4.9.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import icat
>>> icat.__version__
'0.12.0'
```


## List of tools

Set of tools to validate the XML file

1. [XML Syntax Validation](#XML-syntax-validation): Checks if XML is well formed
2. [Parameters list](#parameters-list): Prints a list of parameters from XML
3. [ICAT Parameter list](#icat-parameter-list): Prints a list of parameters from ICAT DB
4. [Metadata Status](#metadata-status): Compares both metadata parameters from XML file and DB
5. [Add parameters](#add-parameters): It reads the xml file and proposes to create the missing parameters in ICAT. Missing parameters are the params defined in the XML that are not in the ICAT DB
6. [List techniques](#list-techniques): It reads the xml file are returns all the subentries that correspond to the techniques

## XML Syntax Validation
	
This tool checks the syntax of the hdf5_cfg.xml file. It will raise an error if the XML is not well formed

### How to run it?

```
python tools/xml/validate.py hdf5_cfg.xml 
```

#### Example

	Success:
	```
	lindemaria:~/Software/metadata/hdf5-master-config % python tools/validate.py hdf5_cfg.xml 
	[PASSED] hdf5_cfg.xml is well-formed
	```

	Error:
	```
	lindemaria:~/Software/metadata/hdf5-master-config % python tools/validate.py hdf5_cfg.xml 
	[ERROR] hdf5_cfg.xml is mismatched tag: line 84, column 3
	```



## Parameters list

This tool prints in the standard output the list of parameters set in the hdf5_cgf.xml file

### How to run it?

```
cd tools
python -m list.list ../hdf5_cfg.xml
```

#### Example

```
scanName
scanNumber
proposal
scanType
[..]
```

## ICAT Parameter list

This tool prints in the standard output the list of parameters set in ICAT. 

### Configuration Files

icat.cfg should exist on this location:
```
./tools/icat/icat.cfg
```

It is the file that contains the connection string to ICAT. 
An example of such file you can find icat.cfg.example where password has been hidden
	
```
[ovm-icat2]
url = https://ovm-icat2.esrf.fr/ICATService/ICAT?wsdl
auth = db
username = root
password = ************
idsurl = https://ovm-icat2:8181/ids
# uncomment, if your server does not have a trusted certificate
checkCert = No
```
	
Note that auth is a controlled value list of: db | esrf
    


### How to run it?
```
cd tools/icat/list
python list.py -s ovm-icat2 --no-check-certificate -c ../icat.cfg --https-proxy ""
```


## Metadata Status

This tool will look for the parameters on ICAT DB and then will compare with the parameters defined in the xml making a summary of the current status

### Configuration

	icat.cfg should exist that it is the file that contains the connection string to ICAT.
	An example of such file is icat.cfg.example where password has been hidden

### How to run it?
```
cd tools/icat/status
python status.py  -s ovm-icat2 --no-check-certificate -c ../icat.cfg --https-proxy ""
```
### Example
```
lindemaria:tools/icat/status % python status.py  -s ovm-icat2 --no-check-certificate -c ../icat.cfg --https-proxy ""


[ERROR] These parameters exists in ../../../hdf5_cfg.xml but not in the DB

MRT_beamHeight
MRT_beamSize
MRT_dose
MRT_expoSpeed
MRT_expoStart


[INFO] -----------------------------------------------------------------------------------------------------------
[INFO] Summary of metadata on https://icat.esrf.fr/ICATService/ICAT?wsdl database and ../../../hdf5_cfg.xml file
[INFO] Total 267 parameters defined in the XML file
[INFO] Total 387 parameters defined in the ICAT DB
[INFO] -----------------------------------------------------------------------------------------------------------
```

### Add parameters

### Configuration

	icat.cfg should exist that it is the file that contains the connection string to ICAT.
	An example of such file is icat.cfg.example where password has been hidden

### How to run it?
```
cd tools/icat/addParameters
python addParameters.py  -s ovm-icat2 --no-check-certificate -c ../icat.cfg --https-proxy ""
```

### List techniques
### How to run it?
```
lindemaria:~/Software/metadata/hdf5-master-config % python tools/xml/getTechniques.py hdf5_cfg.xml 
['SAXS', 'MX', 'PTYCHO', 'TOMO', 'MRT', 'HOLO', 'WAXS']
```
```

