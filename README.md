# Study Sea Ice (SSI)

!["mypy" GitHub Action Status](https://github.com/Guymer/ssi/actions/workflows/mypy.yaml/badge.svg) !["pylint" GitHub Action Status](https://github.com/Guymer/ssi/actions/workflows/pylint.yaml/badge.svg)

This project aims to map the behaviour of sea ice.

The following three sea ice datasets from the [Copernicus Marine Environment Monitoring Service](https://marine.copernicus.eu/) are each less than 10 GiB.

* [SEAICE_ANT_SEAICE_L4_NRT_OBSERVATIONS_011_012](https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=SEAICE_ANT_SEAICE_L4_NRT_OBSERVATIONS_011_012) is "Antarctic Ocean - Sea Ice Edge from SAR".
* [SEAICE_ARC_SEAICE_L3_NRT_OBSERVATIONS_011_014](https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=SEAICE_ARC_SEAICE_L3_NRT_OBSERVATIONS_011_014) is "Sea Ice Thickness derived from merging CryoSat-2 and SMOS ice thickness".
* [SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004](https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004) is "Baltic Sea - Sea Ice Concentration and Thickness Charts".

If you register for a free account at [Copernicus Marine Environment Monitoring Service](https://marine.copernicus.eu/) you can then put your account information in a file called "~/.netrc" using the format `machine nrt.cmems-du.eu login USERNAME password PASSWORD`. Then, after installing [lftp](https://lftp.yar.ru/), you can download datasets with a command along the lines of `lftp -c "open --user USERNAME ftp://nrt.cmems-du.eu; mirror -ep Core/SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004/ Copernicus/SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004/"`. This command can be repeated later to just update your local mirror with new files.

## Workflow

1. Download the entire [SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004](https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004) dataset (by running [lftp](https://lftp.yar.ru/) as outlined above)
2. Create PNG maps of Baltic Sea sea ice concentration (by running [studyBalticConcentration_step1.py](studyBalticConcentration_step1.py))
3. Create CSV histograms of Baltic Sea sea ice concentration (by running [studyBalticConcentration_step2.py](studyBalticConcentration_step2.py))
4. Create PNG plots of Baltic Sea sea ice concentration (by running [studyBalticConcentration_step3.py](studyBalticConcentration_step3.py))
5. Create PNG frames *and* MP4 video *and* WEBP animations of Baltic Sea sea ice concentration (by running [studyBalticConcentration_step4.py](studyBalticConcentration_step4.py))

## Output

The output of [studyBalticConcentration_step2.py](studyBalticConcentration_step2.py) is:

```
Summarising ...
The highest single non-zero occurrence is 84,569 km².
The highest 100%-concentration equivalent occurrence is 166,898.7 km².
Saving trends ...
2018 = 9,334,863.9 km².day
2019 = 6,020,943.4 km².day
2020 = 2,251,272.7 km².day
2021 = 6,345,430.9 km².day
2022 = 7,316,733.1 km².day
2023 = 6,213,928.5 km².day
```

## Dependencies

SSI requires the following Python modules to be installed and available in your `PYTHONPATH`.

* [matplotlib](https://pypi.org/project/matplotlib/)
* [numpy](https://pypi.org/project/numpy/)
* [PIL](https://pypi.org/project/Pillow/)
* [pyguymer3](https://github.com/Guymer/PyGuymer3)
* [scipy](https://pypi.org/project/scipy/)
