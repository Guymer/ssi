# Study Sea Ice (SSI)

This project aims to map the behaviour of sea ice.

The following three sea ice datasets are less than 10 GiB from the [Copernicus Marine Environment Monitoring Service](https://marine.copernicus.eu/).

* [SEAICE_ANT_SEAICE_L4_NRT_OBSERVATIONS_011_012](https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=SEAICE_ANT_SEAICE_L4_NRT_OBSERVATIONS_011_012) is "Antarctic Ocean - Sea Ice Edge from SAR".
* [SEAICE_ARC_SEAICE_L3_NRT_OBSERVATIONS_011_014](https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=SEAICE_ARC_SEAICE_L3_NRT_OBSERVATIONS_011_014) is "Sea Ice Thickness derived from merging CryoSat-2 and SMOS ice thickness".
* [SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004](https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004) is "Baltic Sea - Sea Ice Concentration and Thickness Charts".

If you register for a free account at [Copernicus Marine Environment Monitoring Service](https://marine.copernicus.eu/) you can then put your account information in a file called "~/.netrc" using the format `machine nrt.cmems-du.eu login USERNAME password PASSWORD`. Then, after installing [lftp](https://lftp.yar.ru/), you can download datasets with a command along the lines of `lftp -c "open --user USERNAME ftp://nrt.cmems-du.eu; mirror -ep Core/SEAICE_ANT_SEAICE_L4_NRT_OBSERVATIONS_011_012/ Copernicus/SEAICE_ANT_SEAICE_L4_NRT_OBSERVATIONS_011_012/"`. The command can be repeated later to just update your local mirror with new files.
