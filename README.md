# Study Sea Ice (SSI)

!["mypy" GitHub Action Status](https://github.com/Guymer/ssi/actions/workflows/mypy.yaml/badge.svg) !["pylint" GitHub Action Status](https://github.com/Guymer/ssi/actions/workflows/pylint.yaml/badge.svg)

This project aims to map the behaviour of sea ice.

The following three sea ice datasets from the [Copernicus Marine Environment Monitoring Service](https://marine.copernicus.eu/) are each less than 10 GiB.

* [SEAICE_ANT_SEAICE_L4_NRT_OBSERVATIONS_011_012](https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=SEAICE_ANT_SEAICE_L4_NRT_OBSERVATIONS_011_012) is "Antarctic Ocean - Sea Ice Edge from SAR".
* [SEAICE_ARC_SEAICE_L3_NRT_OBSERVATIONS_011_014](https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=SEAICE_ARC_SEAICE_L3_NRT_OBSERVATIONS_011_014) is "Sea Ice Thickness derived from merging CryoSat-2 and SMOS ice thickness".
* [SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004](https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004) is "Baltic Sea - Sea Ice Concentration and Thickness Charts".
    * The [User Manual](https://documentation.marine.copernicus.eu/PUM/CMEMS-SEAICE-PUM-011-004-011.pdf) states that "The SAR-based products have an individual grid depending on the source SAR data. The ice chart grid-based products have a fixed grid of 1223 (x) by 1445 (y) grid points, int latlong coordinate system. The upper left corner is (x,y)=(9.0,66.2) degrees, and the resolution is (dx,dy)=(0.018,0.009) degrees. The reference ellipsoid is WGS84". This statement **does** agree with the values in the NetCDF (but only if you don't care about sub-percentage level differences).
    * The [User Manual](https://documentation.marine.copernicus.eu/PUM/CMEMS-SEAICE-PUM-011-004-011.pdf) states that: "Geographical coverage = Baltic Sea 9°E 🡪 30°30’E ; 53°40’N 🡪 66°N" and "Horizontal resolution = 1km". This statement **does not** agree with the values in the NetCDF.
    * The [User Manual](https://documentation.marine.copernicus.eu/PUM/CMEMS-SEAICE-PUM-011-004-011.pdf) states that: "The nominal resolution is about 1km".
    * The [User Manual](https://documentation.marine.copernicus.eu/PUM/CMEMS-SEAICE-PUM-011-004-011.pdf) states that the NetCDF schema is:
    ```
dimensions:
    time = 1 ;
    xc = 3812 ;
    yc = 2980 ;

variables:
    int time(time) ;
        time:long_name = "reference time of sea ice file" ;
        time:units = "seconds since 1981-01-01 00:00:00" ;
    float yc(yc) ;
        yc:axis = "Y" ;
        yc:long_name = "y-coordinate in Cartesian system" ;
        yc:units = "m" ;
    float xc(xc) ;
        xc:axis = "X" ;
        xc:long_name = "x-coordinate in Cartesian system" ;
        xc:units = "m" ;
    float lat(yc, xc) ;
        lat:long_name = "latitude" ;
        lat:units = "degrees_north" ;
    float lon(yc, xc) ;
        lon:long_name = "longitude" ;
        lon:units = "degrees_east" ;
    char crs ;
        crs:grid_mapping_name = "polar_stereographic" ;
        crs:straight_vertical_longitude_from_pole = 0.f ;
        crs:latitude_of_projection_origin = 90.f ;
        crs:standard_parallel = 90.f ;
        crs:false_easting = 0.f ;
        crs:false_northing = 0.f ;
        crs:proj4_string = "+proj=stere lon_0=0.0 lat_ts=90.0 lat_0=90.0 a=6371000.0 b=6371000.0" ;
    short ice_concentration(time, yc, xc) ;
        ice_concentration:long_name = "sea ice concentration" ;
        ice_concentration:standard_name = "sea_ice_area_fraction" ;
        ice_concentration:units = "%" ;
        ice_concentration:coordinates = "lon lat" ;
        ice_concentration:grid_mapping = "crs" ;
        ice_concentration:source = "met.no" ;
        ice_concentration:_FillValue = -99s ;
        ice_concentration:scale_factor = 1.f ;
        ice_concentration:add_offset = 0.f ;
    short concentration_range(time, yc, xc) ;
        concentration_range:long_name = "concentration range" ;
        concentration_range:units = "%" ;
        concentration_range:coordinates = "lon lat" ;
        concentration_range:grid_mapping = "crs" ;
        concentration_range:_FillValue = -99s ;
        concentration_range:comments = "Range of the analyzed ice concentration value" ;
    ```

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
* [shapely](https://pypi.org/project/Shapely/)
