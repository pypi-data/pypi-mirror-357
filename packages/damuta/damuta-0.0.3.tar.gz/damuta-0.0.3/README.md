# DAMUTA
**D**irichlet **a**llocation of **muta**tions in cancer 

[![Documentation Status](https://readthedocs.org/projects/damuta/badge/?version=latest)](https://damuta.readthedocs.io/en/latest/?badge=latest)
      

![image](https://user-images.githubusercontent.com/23587234/140100948-98f10395-2bdb-4cf5-ac8b-fd66396d8d7f.png)


# install

## most recent build

DAMUTA is available 

## development version
Clone this repo `git clone https://github.com/morrislab/damuta`
Install requirements `pip install -r damuta/requirements.txt`
Install damuta `pip install -e damuta`


# theanorc

To use the GPU, `~/.theanorc` should contain the following:

```
[global]
floatX = float64
device = cuda
```

Otherwise, device will default to CPU. 

