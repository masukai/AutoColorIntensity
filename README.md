This document was written by Kaito Masuda (masukai9612kf@gmail.com)

---

# AutoColorIntensity

This **AutoColorIntensity** can calculate something's area and color intensities (gradations) in each picture repeatedly by Python 3 (3.8.6) instead of [ImageJ](https://imagej.nih.gov/ij/).
**AutoColorIntensity** is the Additional version of [AutoArea](https://github.com/masukai/AutoArea) and [AutoArea-GUI](https://github.com/masukai/AutoArea-GUI).

## Dependencies

- Numpy (1.19.5)
- OpenCV2 (4.5.1)
- Matplotlib (3.1.1)

## Install

```
git clone https://github.com/masukai/AutoColorIntensity.git
```

If you do not install Python 3, Numpy and OpenCV2, please install them, following below.

- [Python 3](https://www.python.org/downloads/)
- Numpy, OpenCV2 and Matplotlib

```
pip(3) install numpy
pip(3) install opencv-python
pip(3) install matplotlib
```

If you need "(3)" to use Python 3, not Python 2, please add it.

## Usage

### First Step

please set your pictures in which you want to calculate areas in the **photo(YOU CAN CHANGE THE NAME)** folder.
I saved a sample picture. If you want to calculate your data (pictures), please delete my sample.

### Second Step

Move to _AutoColorIntensity_ directory and type below,

```
python(3) main.py
```

If you use the GUI mode, please type below.

```
python(3) gui.py
```

then, the GUI will open.

### Third Step

_Making now. Please wait._

## CAUSION

- **An environment of taking pictures is the most important.**
  Please take pictures or images in the almost same environment.

- See [AutoArea](https://github.com/masukai/AutoArea) for the effect of the parameters.

- This program has been checked by MacOS 12.1 (2021.12.21).
  If you find some bugs, please tell me about them.

## REFERENCES

- AutoArea, 2020. https://github.com/masukai/AutoArea.

- Yamazaki, Y. 2021. Python でグレースケール(grayscale)化. https://qiita.com/yoya/items/dba7c40b31f832e9bc2a.
