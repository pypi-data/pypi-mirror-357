import pytest
import os
import warnings
import numpy as np
import json
import ARTmie

class AccuracyWarning(Warning):
    def __init__(self,message):
        self.message = message


def load_test_data(file_name,inner_path):
    '''
      loads test data directly from json-file on the fly
    '''
    folder = os.path.abspath(os.path.dirname(__file__))
    jsonfile = os.path.join(folder, file_name)
    with open(jsonfile) as file:
        content = json.load(file)
        tokens = inner_path.split(',')
        for token in tokens:
            content = content[token]
        if 'bessel' in tokens:
            print('uses bessel test data')
            data = [ (item['nu'],item['z'][0]+item['z'][1]*1j,item['res'][0]+item['res'][1]*1j) for item in content ]
            return data
        if 'single' in tokens:
            if 'homog' in token:
                print('uses data for single particles')
                data = [ (item['m'][0]+item['m'][1]*1j,item['d'],item['wl'],item['exp']) for item in content ]
                return data
            if 'coat' in token:
                print('uses data for single particles')
                data = [ (item['mc'][0]+item['mc'][1]*1j,item['ms'][0]+item['ms'][1]*1j,item['dc'],item['cf'],item['wl'],item['exp']) for item in content ]
                return data
        data = [ item for item in content ]
        return data


@pytest.mark.parametrize("nu,z,expectation", load_test_data('testdata_bessel.json','bessel,J'))
def test_besselj(nu,z,expectation):
    if np.abs(expectation) < 0.0001:
        assert np.abs(ARTmie.besselj(nu,z+0j)-expectation)<1.0e-8
    else:
        assert np.abs(ARTmie.besselj(nu,z+0j)/expectation-1.0)<1.0e-8


@pytest.mark.parametrize("nu,z,expectation", load_test_data('testdata_bessel.json','bessel,Y'))
def test_bessely(nu,z,expectation):
    if np.abs(expectation) < 0.0001:
        assert np.abs(ARTmie.bessely(nu,z+0j)-expectation)<1.0e-8
    else:
        assert np.abs(ARTmie.bessely(nu,z+0j)/expectation-1.0)<1.0e-8


@pytest.mark.parametrize("nu,z,expectation", load_test_data('testdata_bessel.json','bessel,H'))
def test_hankel(nu,z,expectation):
    if np.abs(expectation) < 0.0001:
        assert np.abs(ARTmie.hankel(nu,z+0j,1)-expectation)<1.0e-8
    else:
        assert np.abs(ARTmie.hankel(nu,z+0j,1)/expectation-1.0)<1.0e-8


@pytest.mark.parametrize("m,d,wl,expectation", load_test_data('testdata_single_mie.json','single,homog'))
def test_homogeneous(m,d,wl,expectation):
    q = ARTmie.MieQ(m,d,wl, asDict=True)
    keys = ['Qext','Qsca','Qabs','Qback','Qratio','Qpr','g']
    for k in keys:
        if np.abs(expectation[k])<1.0e-14:
            assert np.abs(q[k]-expectation[k])<1.0e-14
        else:
            assert np.abs(q[k]/expectation[k]-1.0)<1.0e-5
            delta = np.abs(q[k]/expectation[k]-1.0)
            if delta>=1.0e-8:
                warnings.warn(f'Somewhat significant difference ({delta}) between ARTmie and used reference: PyMieScatt.', AccuracyWarning)


@pytest.mark.parametrize("mc,ms,dc,cf,wl,expectation", load_test_data('testdata_single_mie.json','single,coat'))
def test_coated(mc,ms,dc,cf,wl,expectation):
    q = ARTmie.MieCoatedQ(mc,dc,ms,dc*(1+cf),wl, asDict=True)
    keys = ['Qext','Qsca','Qabs','Qback','Qratio','Qpr','g']
    for k in keys:
        if np.abs(expectation[k])<1.0e-8:
            assert np.abs(q[k]-expectation[k])<1.0e-8
        else:
            assert np.abs(q[k]/expectation[k]-1.0)<7.5e-3
            delta = np.abs(q[k]/expectation[k]-1.0)
            if delta>=1.0e-8:
                warnings.warn(f'Somewhat significant difference ({delta}) between ARTmie and used reference: PyMieScatt.', AccuracyWarning)
