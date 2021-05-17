# Computer Vision Data Format Converter

This script can be used to convert our standard annotation format into various computer vision formats.

# Delimiter Separated Values Writer

The DSV writer can be configured by loading a YAML file.

## Configuration

There are multiple configuration options.

- **delimiter**: Separation character between annotation values.
- **lineTerminator**: Separation between lines or annotations if `annotationPerLine` is `true`.
- **ignoreEmptyClass**: No space is occupied of this is set to `true`.
- **defaultClass**: Placed if class is empty and `ignoreEmptyClass` was set to `false`.
- **classAtEnd**: Defines if the class is placed at the beginning or before the annotation values.
- **quoting**: Defines if values should be quoted if there are spaces or delimiters within the string.
- **quoteChar**: Character used to quote fields containing spaces or delimiters, if `quoting` is `true`.
- **withPath**: If images path should be inserted to the annotation.
- **pathAtEnd**: Defines if the path is placed in front or at the beginning of the annotation values.
- **defaultPath**: Default path to the image if no path is defined.
- **annotationPerLine**: If annotations of an image are saved in a single line.
- **annotationDelimiter**: Character between annotations.
- **filePerImage**: If image annotations are saved in separate file.
- **outputFolder**: Folder in which the files are saved if `filePerImage` is `true`.
- **fileExtension**: File extensions of the saved files if `filePerImage` is `true`.
- **outputFile**: File path for all images if `filePerImage` is `false`.
- **boundingBox**: Output annotation format for bounding boxes.
    - Possible values: `coco`, `voc`, `center`, `relativeCoco`, `relativeVoc`, `relativeCenter`
- **classMapping**: Contains key-value pairs that maps a class name to the defined value,
  with the use of nested collections.
  
#### Class mapping example:
```yaml
classMapping:
  Cat: 0
  Dog: 1
  Horse: 2
```


### Default Config

This is the standard configuration.

```yaml
delimiter: ','
lineTerminator: "\r\n"
ignoreEmptyClass: false
classAtEnd: true
defaultClass: 'unk'
withPath: true
pathAtEnd: false
defaultPath: ''
annotationPerLine: true
annotationDelimiter: ' '
filePerImage: false
outputFolder: /cvdfc/
fileExtension: txt
outputFile: /cvdfc/all.txt
boundingBox: coco
```

### Loader Config
The config file for DSV loader needs three more field.
```yaml
imageExtension: null
imageWidth: null
imageHeight: null
```

It also has to be mentioned that the class mapping needs to be reversed. For example:
```yaml
classMapping:
  0: Cat
  1: Dog
  2: Horse
```

## Scripts Help Menu
- Standard to DSV: `main -h`
- DSV to Standard: `dsv -h`