# AstroHelper
AstroHelper is a tool created to provide for clean, easy to understand and comprehensive help to observational astronomy.

## Introduction
This code has been developed to help amateur astronomers easily find the best observable objects at their location and at the best observation time. We (the creators) are physics/astronomy students ourselves as well as amateur astronomers. We have found it inconvenient to always have to pull up Stellarium or other sky viewing programs/apps to view one object at a time. Our project has the goal to create a somewhat simpler and versatile tool to help amateur astronomers, especially astrophotographers.

## How to install AstroHelper

To install AstroHelper you just need to run the pip command:
```bash
pip install astrohelper
```

## Concept
This package functions on the basis of a data array. You can either create your own list of elements and then run ```Simbad_extraction_with_ned()```to collect all data for your objects. There are lists of NGC, IC and Messier objects with all the data provided with this project. We encourage using these as it saves time. Before continuing please set your telescope data by using the function ```TelescopeData()```. To plot objects which are most viable for observation at your location and time use the function ```PlotBestObjects()```. There are many arguments you can set, they are listed in the documentation. The output is a plot of the best objects determined by the function, followed by single plots for each of the top 10 (this number is variable) objects. There you will see the altitude and azimuth as a function of time, aswell as the appearance and the expected luminosity in your telescope FOV.

### Future
Future projects are a community photo upload which can then be shown with the singular plots. A larger project is a GUI.

## Documentation
Full documentation of the functions can be found on the [wiki](https://github.com/DP0604/AstroHelper/wiki/Overview).

## Contributing
We welcome contributions to develop the code further and create a better tool for the users. If you want to contribute pull requests are welcome. For pull requests please use the template!

## License
This project falls under the MIT license.