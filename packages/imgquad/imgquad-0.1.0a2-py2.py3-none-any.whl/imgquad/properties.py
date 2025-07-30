#! /usr/bin/env python3

"""ImagGe Quality Assessment for Digitisation batches

Johan van der Knijff

Copyright 2025, KB/National Library of the Netherlands

Image properties extraction module

"""
import os
import sys #remove, test only
import io
import logging
import base64
from lxml import etree
import PIL
from PIL import ImageCms
from PIL.ExifTags import TAGS, GPSTAGS, IFD
from . import jpegquality


def dictionaryToElt(name, dictionary):
    """Create Element object from dictionary"""
    elt = etree.Element(name)
    for key, value in dictionary.items():
        child = etree.Element(key)
        child.text = str(value)
        elt.append(child)
    return elt


def dictionaryToEltNew(name, dictionary):
    """Create Element object from dictionary, with recursion
    TODO doesn't work yet!"""
    elt = etree.Element(name)

    for k, v in dictionary.items():
        child = etree.Element(k)
        if isinstance(v, dict):
            dictionaryToEltNew(str(k),v)
            cChild = etree.Element(k)
            child.append(cChild)
        else:
            child.text = str(v)
        elt.append(child)

    return elt


def getBPC(image):
    """Return Bits per Component as a function of mode and components values"""
    mode_to_bpp = {"1": 1,
                   "L": 8,
                   "P": 8,
                   "RGB": 24,
                   "RGBA": 32,
                   "CMYK": 32,
                   "YCbCr": 24,
                   "LAB": 24,
                   "HSV": 24,
                   "I": 32,
                   "F": 32}

    bitsPerPixel = mode_to_bpp[image.mode]
    noComponents = len(image.getbands())

    if noComponents != 0  and isinstance(bitsPerPixel, int):
        bpc = int(bitsPerPixel/noComponents)
    else:
        bpc = -9999

    return bpc


def getProperties(file):
    """Extract properties and return result as Element object"""

    # Create element object to store all properties
    propertiesElt = etree.Element("properties")

    # Element to store exceptions at file level
    exceptionsFileElt = etree.Element("exceptions")

    # Create and fill descriptive elements
    fPathElt = etree.Element("filePath")
    fPathElt.text = file
    fNameElt = etree.Element("fileName")
    fNameElt.text = os.path.basename(file)
    fSizeElt = etree.Element("fileSize")
    fSizeElt.text = str(os.path.getsize(file))

    # Add to properies element
    propertiesElt.append(fPathElt)
    propertiesElt.append(fNameElt)
    propertiesElt.append(fSizeElt)

    # Read image
    try:
        im = PIL.Image.open(file)
        im.load()
        propsImageElt = getImageProperties(im)
        propertiesElt.append(propsImageElt)

    except Exception  as e:
        ex = etree.SubElement(exceptionsFileElt,'exception')
        ex.text = str(e)
        propertiesElt.append(exceptionsFileElt)
        logging.warning(("while opening image: {}").format(str(e)))
        return propertiesElt

    return propertiesElt


def getImageProperties(image):
    """Extract image properties and return result as Element object"""

    # Dictionary for storing image properties
    propsImage = {}
    # Element for storing image-level exceptions
    exceptionsImageElt = etree.Element("exceptions")

    propsImage['format'] = image.format
    width = image.size[0]
    height = image.size[1]
    propsImage['width'] = width
    propsImage['height'] = height
    propsImage['mode'] = image.mode
    noComponents = len(image.getbands())
    propsImage['components']= noComponents
    bitsPerComponent = getBPC(image)
    propsImage['bpc'] = bitsPerComponent

    if image.format == "JPEG":
        try:
            # Estimate JPEG quality using least squares matching
            # against standard quantization tables
            quality, rmsError, nse = jpegquality.computeJPEGQuality(image)
            propsImage['JPEGQuality'] = quality
            propsImage['NSE_JPEGQuality'] = nse
        except Exception as e:
            ex = etree.SubElement(exceptionsImageElt,'exception')
            ex.text = str(e)
            logging.warning(("while estimating JPEG quality from image: {}").format(str(e)))

    for key, value in image.info.items():
        if key == 'exif':
            # Skip any exif elements as Exif tags are added later
            pass
        elif key == 'photoshop':
            # Skip photoshop elements, because they tend to be large and I don't know how to
            # properly decode them
            pass
        elif isinstance(value, bytes):
            propsImage[key] = 'bytestream'
        elif key == 'dpi' and isinstance(value, tuple):
            propsImage['ppi_x'] = value[0]
            propsImage['ppi_y'] = value[1]
        elif key == 'jfif_density' and isinstance(value, tuple):
            propsImage['jfif_density_x'] = value[0]
            propsImage['jfif_density_y'] = value[1]
        elif isinstance(value, tuple):
            # Skip any other properties that return tuples
            pass
        else:
            propsImage[key] = value

    # ICC profile name and description
    iccFlag = False
    try:
        icc = image.info['icc_profile']
        iccFlag = True
    except KeyError:
        pass

    if iccFlag:
        try:
            iccProfile = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            propsImage['icc_profile_name'] = ImageCms.getProfileName(iccProfile).strip()
            propsImage['icc_profile_description'] = ImageCms.getProfileDescription(iccProfile).strip()
        except Exception as e:
            ex = etree.SubElement(exceptionsImageElt,'exception')
            ex.text = str(e)
            logging.warning(("while extracting ICC profile properties from image: {}").format(str(e)))

    # Exif tags
    propsExif = image.getexif()

    # Create element object to store Exif tags
    propsExifElt = etree.Element("exif")

    # Iterate over various Exif tags, code adapted from:
    # https://stackoverflow.com/a/75357594/1209004

    for k, v in propsExif.items():
        tag = TAGS.get(k, k)
        exifElt = etree.Element(str(tag))
        exifElt.text = str(v)
        if tag == 'XMLPacket':
            # Skip XMLPacket tag, which contains raw XMP metadata
            pass
        else:
            propsExifElt.append(exifElt)

    for ifd_id in IFD:
        # Iterate over image file directories
        # NOTE: this can result in duplicate Exif Tags. Example: Thumbnail image is implemented as 
        # separate IFD, with XResolution / YResolution tags whose values are different from
        # main resolution tags. Currently these are all lumped together in the output.
        try:
            ifd = propsExif.get_ifd(ifd_id)

            if ifd_id == IFD.GPSInfo:
                resolve = GPSTAGS
            else:
                resolve = TAGS

            for k, v in ifd.items():
                tag = resolve.get(k, k)
                exifElt = etree.Element(str(tag))
                exifElt.text = str(v)
                propsExifElt.append(exifElt)
        except KeyError:
            pass
    

    # XMP metadata (returns dictionary)
    # TODO not supported right now, might add this later
    # xmp = image.getxmp()

    # Dictionary to element
    # propsXMPElt = dictionaryToEltNew('xmp', xmp)

    propsImageElt = dictionaryToElt('image', propsImage)
    propsImageElt.append(propsExifElt)
    #propsImageElt.append(propsXMPElt)
    propsImageElt.append(exceptionsImageElt)

    return propsImageElt
