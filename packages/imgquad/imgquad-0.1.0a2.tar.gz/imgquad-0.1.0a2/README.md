# IMaGe QUality Assessment for Digitisation batches

## What is imgquad?

Imgquad is a simple tool for automated quality assessment of images in digitisation batches against a user-defined technical profile. It uses [Pillow](https://pillow.readthedocs.io/) to extract the relevant technical properties.

These properties are serialized to a simple XML structure, which is then evaluated against [Schematron rules](http://en.wikipedia.org/wiki/Schematron) that define the expected/required technical characteristics.


## Installation

Install the software with the [pip package manager](https://en.wikipedia.org/wiki/Pip_(package_manager)):

```
pip install imgquad
```

Then run imgquad once:

```
imgquad
```

Depending on your system, imgquad will create a folder named *imgquad* in one of the following locations: 

- For Linux, it will use the location defined by environment variable *$XDG_CONFIG_HOME*. If this variable is not set, it will use the *.config* directory in the user's home folder (e.g. `/home/johan/.config/imgquad`). Note that the *.config* directory is hidden by default.
- For Windows, it will use the *AppData\Local* folder (e.g. `C:\Users\johan\AppData\Local\imgquad`).

The folder contains two subdirectories named *profiles* and *schemas*, which are explained in the "Profiles" and "Schemas" sections below.

## Command-line syntax

The general syntax of imgquad is:

```
usage: imgquad [-h] [--version] {process,list,copyps} ...
```

Imgquad has three sub-commands:

|Command|Description|
|:-----|:--|
|process|Process a batch.|
|list|List available profiles and schemas.|
|copyps|Copy default profiles and schemas to user directory.|

### process command

Run imgquad with the *process* command to process a batch. The syntax is:

```
usage: imgquad process [-h] [--maxfiles MAXFILES] [--prefixout PREFIXOUT]
                       [--outdir OUTDIR] [--verbose]
                       profile batchDir
```

The *process* command expects the following positional arguments: 

|Argument|Description|
|:-----|:--|
|profile|This defines the validation profile. Note that any file paths entered here will be ignored, as Imgquad only accepts  profiles from the profiles directory. You can just enter the file name without the path. Use the *list* command to list all available profiles.|
|batchDir|This defines the batch directory that will be analyzed.|

In addition, the following optional arguments are available:

|Argument|Description|
|:-----|:--|
|--maxfiles, -x|This defines the maximum number of images that are reported in each output XML file (default: 1000).|
|--prefixout, -p|This defines a text prefix on which the names of the output files are based (default: "pq").|
|--outdir, -o|This defines the directory where output is written (default: current working directory from which imgquad is launched).|
|--verbose, -b|This tells imgquad to report Schematron output in verbose format.|

In the simplest case, we can call imgquad with the profile and the batch directory as the only arguments:

```
imgquad process beeldstudio-retro.xml ./mybatch
```

Imgquad will now recursively traverse all directories and files inside the "mybatch" directory, and analyse all image files (based on a file extension match).

### list command

Run imgquad with the *list* command to get a list of the available profiles and schemas, as well as their locations. For example:

```
imgquad list
```

Results in:

```
Available profiles (directory /home/johan/.config/imgquad/profiles):
  - beeldstudio-retro.xml
Available schemas (directory /home/johan/.config/imgquad/schemas):
  - beeldstudio-retro.sch
```

### copyps command

If you run imgquad with the *copyps* command, it will copy the default profiles and schemas that are included in the installation over to your user directory.

**Warning:** any changes you made to the default profiles or schemas will be lost after this operation, so proceed with caution! If you want to keep any of these files, just make a copy and save them under a different name before running the *copyps* command.

## Profiles

A profile is an XML file that defines how a digitisation batch is evaluated. Here's an example:

```xml
<?xml version="1.0"?>

<profile>

<!-- File extensions that will be processed (case insensitive) -->
<extension>tif</extension>
<extension>tiff</extension>
<extension>jpg</extension>
<extension>jpeg</extension>

<!-- Properties that are written to summary file -->
<summaryProperty>properties/image/format</summaryProperty>
<summaryProperty>properties/image/exif/Compression</summaryProperty>
<summaryProperty>properties/image/components</summaryProperty>
<summaryProperty>properties/image/bpc</summaryProperty>
<summaryProperty>properties/image/icc_profile_name</summaryProperty>
<summaryProperty>properties/image/exif/ColorSpace</summaryProperty>
<summaryProperty>properties/image/exif/XResolution</summaryProperty>
<summaryProperty>properties/image/exif/YResolution</summaryProperty>
<summaryProperty>properties/image/exif/Make</summaryProperty>
<summaryProperty>properties/image/exif/Model</summaryProperty>
<summaryProperty>properties/image/exif/LensMake</summaryProperty>
<summaryProperty>properties/image/exif/LensSpecification</summaryProperty>
<summaryProperty>properties/image/exif/LensModel</summaryProperty>
<summaryProperty>properties/image/exif/LensSerialNumber</summaryProperty>
<summaryProperty>properties/image/exif/ExposureTime</summaryProperty>
<summaryProperty>properties/image/exif/FNumber</summaryProperty>
<summaryProperty>properties/image/exif/ISOSpeedRatings</summaryProperty>
<summaryProperty>properties/image/exif/WhiteBalance</summaryProperty>
<summaryProperty>properties/image/exif/Software</summaryProperty>

<!-- Schematron schema definition -->
<schema>beeldstudio-retro.sch</schema>

</profile>
```

The profile is made up of the following components:

1. One or more *extension* elements, which tell imgquad what file extensions to look for. Imgquad handles file extensions in a case-insensitive way, so *tif* covers both "rubbish.tif" and "rubbish.TIF".
2. One or more *summaryProperty* elements. These define the properties that are written to the summary file (see below).
3. One or more *schema* elements, that each link a file or directory naming pattern to a Schematron file (explained in the next section).

In the example, there's only one  *schema* element, which is used for all processed images. Optionally, each *schema* element may contain *type*, *match* and *pattern* attributes, which define how a schema is linked to file or directory names inside the batch:

- If **type** is "fileName", the matching is based on the naming of an image. In case of "parentDirName" the matching uses the naming of the direct parent directory of an image.
- The **match** attribute defines whether the matching pattern with the file or directory name is exact ("is") or partial ("startswith", "endswith", "contains".)
- The **pattern** attribute defines a text string that is used for the match.

See the [pdfquad documentation](https://github.com/KBNLresearch/pdfquad#profiles) for an example of how these attributes are used.

### Available profiles

Currently the following profiles are included:

|Profile|Description|
|:--|:--|
|beeldstudio-retro.xml|Profile for KB Beeldstudio retro batches of digitised medieval manuscripts.|

## Schemas

Schemas contain the Schematron rules on which the quality assessment is based. Some background information about this type of rule-based validation can be found in [this blog post](https://www.bitsgalore.org/2012/09/04/automated-assessment-jp2-against-technical-profile). Currently the following schemas are included:

### beeldstudio-retro.sch

This is a schema for KB Beeldstudio retro batches of digitised medieval manuscripts.

<!--
TODO, add description

It includes the following checks:

|Check|Value|
|:---|:---|
|||
|||
|||
|||

-->

## Output

Imgquad reports the following output:

### Comprehensive output file (XML)

Imgquad generates one or more comprehensive output files in XML format. For each image, these contain all extracted properties, as well a the Schematron report and the assessment status. <!-- TODO add example file [Here's an example file](./examples/pq_batchtest_001.xml).-->

Since these files can get really large, Imgquad splits the results across multiple output files, using the following naming convention:

- iq_mybatch_001.xml
- iq_mybatch_002.xml
- etcetera

By default Imgquad limits the number of reported images for each output file to 1000, after which it creates a new file. This behaviour can be changed by using the *--maxfiles* (alias *-x*) option. For example, the command below will limit the number of images per output file to 1 (so each image will have its dedicated output file):

```
imgquad process beeldstudio-retro.xml ./mybatch -x 1
```

### Summary file (CSV)

This is a comma-delimited text file that summarises the analysis. At the minimum, Imgquad reports the following columns for each image:

|Column|Description|
|:-----|:--|
|file|Full path to the image file.|
|validationSuccess|Flag with value *True* if Schematron validation was succesful, and *False* if not. A value *False* indicates that the file could not be validated (e.g. because no matching schema was found, or the validation resulted in an unexpected exception)|
|validationOutcome|The outcome of the Schematron validation/assessment. Value is *Pass* if file passed all tests, and *Fail* otherwise. Note that it is automatically set to *Fail* if the Schematron validation was unsuccessful (i.e. "validationSuccess" is *False*)|
|fileOut|Corresponding comprehensive output file with full output for this image.|

In addition, the summary file contains additional columns with the properties that are defined by the *summaryProperty* elements in the profile.

<!-- TODO add example

Here's an example:

``` csv
```

-->

## Licensing

Imgquad is released under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).

## Useful links

- [Schematron](http://en.wikipedia.org/wiki/Schematron)


