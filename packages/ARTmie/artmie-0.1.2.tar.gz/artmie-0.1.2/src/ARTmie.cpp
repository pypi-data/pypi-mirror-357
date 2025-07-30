#define PY_SSIZE_T_CLEAN
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <numpy/ndarrayobject.h>
#include <numpy/npy_3kcompat.h>
#include <numpy/npy_math.h>
#include <string>
#include "cpp_amos/ARTmie_amos.cpp"



static const double EPS = 0.5e-8;
static const std::complex<double> cplxJ(0.0,1.0);


// **** Parser and basics

int parse_arrays(int arg_count, int dtype, PyObject **args, PyObject **arrs) {
    int i, e=0;

    for (i=0; i<arg_count; i++) {
        arrs[i] = PyArray_FROM_OTF(args[i], dtype, NPY_ARRAY_IN_ARRAY);
        if(arrs[i] == NULL) e++;
    }

    if( e>0 ) {
        for (i=0; i<arg_count; i++) {
            Py_XDECREF(arrs[i]);
        }
        PyErr_Clear();
        return 0; //some error occured
    }

    return 1; //no error
}

PyArrayObject* c2py_dblarr(int c_arr_len, double *c_arr) {
    npy_intp dims[1];
    dims[0] =  (npy_intp)c_arr_len;
    double *pydata;
    PyArrayObject *pyarr = (PyArrayObject *) PyArray_Zeros(1, dims, PyArray_DescrFromType(NPY_FLOAT64), 0);
    pydata = (double *) PyArray_DATA(pyarr);
    for(int idx=0; idx<c_arr_len; idx++) {
        pydata[idx] = c_arr[idx];
    }
    Py_INCREF(pyarr);
    return pyarr;
}
PyArrayObject* c2py_dblarr(int dim1_len, int dim2_len, double *c_arr) {
    npy_intp dims[2];
    dims[0] = (npy_intp)dim1_len;
    dims[1] = (npy_intp)dim2_len;
    PyArrayObject *pyarr = (PyArrayObject *) PyArray_Zeros(2, dims, PyArray_DescrFromType(NPY_DOUBLE), 0);

    PyArrayObject *op[1] = { pyarr };
    npy_uint32 op_flags[1] = { NPY_ITER_WRITEONLY };
    npy_uint32 flags = NPY_ITER_EXTERNAL_LOOP | NPY_ITER_BUFFERED | NPY_ITER_GROWINNER;
    NpyIter *iter = NpyIter_MultiNew(1, op, flags, NPY_KEEPORDER, NPY_NO_CASTING, op_flags, NULL);
    if( iter==NULL ) {
        Py_XDECREF(pyarr);
        return NULL;
    }
    NpyIter_IterNextFunc * iternext = NpyIter_GetIterNext(iter, NULL);
    if (iternext == NULL) {
        NpyIter_Deallocate(iter);
        Py_XDECREF(pyarr);
        return NULL;
    }

    // -- iterate ------------------
    npy_intp count;
    int idx=0;
    char ** dataptr = NpyIter_GetDataPtrArray(iter);
    npy_intp * strideptr = NpyIter_GetInnerStrideArray(iter);
    npy_intp * innersizeptr = NpyIter_GetInnerLoopSizePtr(iter);
    do {
        count = *innersizeptr;

        while(count--) {
            *(double *)dataptr[0] = c_arr[idx];

            dataptr[0] += strideptr[0];
            idx++;
        }
    } while (iternext(iter));

    if(NpyIter_Deallocate(iter) != NPY_SUCCEED) {
        Py_XDECREF(pyarr);
        return NULL;
    }

//    pydata = (double *) PyArray_DATA(pyarr);
//    for(int idx=0; idx<dim1_len*dim2_len; idx++) {
////        int j = idx/dim2_len;
////        int i = idx%dim2_len;
////        pydata[idx] = c_arr[j][i];
//        pydata[idx] = c_arr[idx];
//    }
//    Py_INCREF(pyarr);
    return pyarr;
}
void py2c_dblarr(PyArrayObject* pyarr, double *carr) {
    PyArrayObject* inarr = nullptr;
    if(PyArray_IS_C_CONTIGUOUS(pyarr)) {
        inarr = pyarr;
    } else {
        inarr = (PyArrayObject*)PyArray_NewCopy(pyarr, NPY_CORDER);
    }
    //inarr is C-contiguous, so we use the flat representation of the data
    int arr_len = (int) PyArray_SIZE(inarr);
    int dtype = PyArray_DTYPE(inarr)->type_num;
    int idx;
    if (dtype==NPY_FLOAT) {
        float *pydata = (float *) PyArray_DATA(inarr);
        for(idx=0; idx<arr_len; idx++)
            carr[idx] = (double)pydata[idx];
        return;
    }
    if (dtype==NPY_DOUBLE) {
        double *pydata = (double *) PyArray_DATA(inarr);
        for(idx=0; idx<arr_len; idx++)
            carr[idx] = pydata[idx];
        return;
    }
    for(idx=0; idx<arr_len; idx++)
        carr[idx] = std::numeric_limits<double>::quiet_NaN();
}

std::complex<double> py2c_cplx(Py_complex np_cplx) {
    std::complex<double> c_cplx(np_cplx.real, np_cplx.imag);
    return c_cplx;
}
Py_complex c2py_cplx(std::complex<double> c_cplx) {
    Py_complex np_cplx;
    np_cplx.real = c_cplx.real();
    np_cplx.imag = c_cplx.imag();
    return np_cplx;
}
Py_complex nanPyCplx() {
    Py_complex py_cplx;
    py_cplx.real = std::numeric_limits<double>::quiet_NaN();
    py_cplx.imag = std::numeric_limits<double>::quiet_NaN();
    return py_cplx;
}
PyArrayObject* c2py_cplxarr(int c_arr_len, std::complex<double> *c_arr) {
    npy_intp dims[1];
    dims[0] =  (npy_intp)c_arr_len;
    Py_complex *pydata;
    PyArrayObject *pyarr = (PyArrayObject *) PyArray_Zeros(1, dims, PyArray_DescrFromType(NPY_COMPLEX128), 0);
    pydata = (Py_complex *) PyArray_DATA(pyarr);
    for(int idx=0; idx<c_arr_len; idx++) {
        pydata[idx].real = c_arr[idx].real();
        pydata[idx].imag = c_arr[idx].imag();
    }
    Py_INCREF(pyarr);
    return pyarr;
}
int py2c_cplxarr(PyArrayObject* pyarr, std::complex<double> *carr) {
    PyArrayObject* inarr = nullptr;
    if(PyArray_IS_C_CONTIGUOUS(pyarr)) {
        inarr = pyarr;
    } else {
        inarr = (PyArrayObject*)PyArray_NewCopy(pyarr, NPY_CORDER);
    }
//    int dtype = PyArray_DTYPE(inarr)->type_num;
//    //if(!(dtype==NPY_FLOAT || dtype==NPY_DOUBLE || dtype==NPY_COMPLEX64 || dtype==NPY_COMPLEX128)) {
//    //    inarr = (PyArrayObject*)PyArray_Cast(inarr, NPY_COMPLEX128);
//    //    return 0;
//    //}
    int arr_len = (int) PyArray_SIZE(inarr);
    int idx;
//    if(dtype==NPY_FLOAT) {
//        float* pydata = (float *) PyArray_DATA(inarr);
//        for(idx=0; idx<arr_len; idx++)
//            carr[idx] = std::complex<double>((double)pydata[idx], 0.0);
//        return 1;
//    }
//    if(dtype==NPY_DOUBLE) {
//        double* pydata = (double *) PyArray_DATA(inarr);
//        for(idx=0; idx<arr_len; idx++)
//            carr[idx] = std::complex<double>(pydata[idx], 0.0);
//        return 1;
//    }
//    if(dtype==NPY_COMPLEX64 || dtype==NPY_COMPLEX128) {
        Py_complex *pydata = (Py_complex *) PyArray_DATA(inarr);
        for(idx=0; idx<arr_len; idx++)
            carr[idx] = std::complex<double>(pydata[idx].real, pydata[idx].imag);
        return 1;
//    }
//    for(idx=0; idx<arr_len; idx++)
//        carr[idx] = std::complex<double>(
//                std::numeric_limits<double>::quiet_NaN(),
//                std::numeric_limits<double>::quiet_NaN());
//    return 1;
}

const char* shape2str(int ndim, npy_intp* shape) {
    std::string s = "(";
    for(int i=0; i<ndim; i++) {
        if(i>0)
            s += ",";
        s += std::to_string((long)shape[i]);
    }
    return (s+")").c_str();
}


// **** Gamma function

#define gm_docstring "gamma(x)\n\n\
Calculates the gamma function\n\n\
Parameters\n----------\n\
x : scalar, floating point number\n    argument\n\n\
Returns\n-------\n\
g : scalar, floating point number\n    result of the gamma function"
PyObject* mie_art_gamma(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"x", NULL };

    //use function for integer array and integer value
    double valueX;
    if(PyArg_ParseTupleAndKeywords(args, kwds, "d", kwlist, &valueX)) {
    } else {
        PyErr_SetString(
            PyExc_TypeError,
            "The arguments dtypes do not match, expected (float)"
        );
        return NULL;
    }
    PyObject *res = Py_BuildValue("d",0.0+ std::exp(dgamln(valueX)));
    return res;
}


// **** Bessel functions

#define bj_docstring "besselj(v, z, /, es=False)\n\n\
Calculates the Bessel function of the first kind\n\n\
Parameters\n----------\n\
v : scalar, float\n    order of the Bessel function\n\
z : scalar or array-like, complex\n    the argument/location, where the Bessel function has to be evaluated\n\
es : scalar, boolean, optional\n    exponentially scales the result by exp(2/3*z**1.5) if set to True, default: False\n\n\
Returns\n-------\n\
r : scalar or array-like, complex\n    result of the Bessel function of the first kind and order v at complex value z, same shape as z"
PyObject* mie_art_besselj(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"v", (char*)"z", (char*)"es", (char*)"debug", NULL };

    int valueExpScl = false;
    int valueDebug = false;
    double valueV;
    Py_complex valueNpZ;

    PyObject* arr_cplx_ptr[1] = { NULL };
    PyObject* array_cplx[1]   = { NULL };

    int numArrs = -1;
    int ctype = -1;

    if(PyArg_ParseTupleAndKeywords(args, kwds, "dD|pp", kwlist, &valueV, &valueNpZ, &valueExpScl, &valueDebug)) {
        numArrs = 0;
    } else {
        PyErr_Clear();
    }

    if(numArrs < 0) {
        if(PyArg_ParseTupleAndKeywords(args, kwds, "dO|pp", kwlist, &valueV, &arr_cplx_ptr[0], &valueExpScl, &valueDebug)) {
            if(parse_arrays(1, NPY_COMPLEX64, arr_cplx_ptr, array_cplx))
                ctype = NPY_COMPLEX64;
            if(ctype<0)
            if(parse_arrays(1, NPY_COMPLEX128, arr_cplx_ptr, array_cplx))
                ctype = NPY_COMPLEX128;
            if(ctype<0) {
                PyErr_SetString(
                    PyExc_TypeError,
                    "The z array has to be of type float, double or complex."
                );
                return NULL;
            }
            numArrs = 1;
        } else {
            PyErr_Clear();
        }
    }

    if(numArrs < 0) {
        PyErr_SetString(
            PyExc_TypeError,
            "The arguments dtypes do not match, expected (float,complex)"
        );
        return NULL;
    }
    double bjr[1], bji[1];
    int nz, idum;

    PyObject* res = NULL;
    if(numArrs == 0) {
        std::complex<double> valueZ = py2c_cplx(valueNpZ);
        PySys_WriteStdout("Bessel J: nu=%f  z=%f+i*%f  expscl=%i\n",valueV,valueZ.real(),valueZ.imag(),valueExpScl);
        zbesj(valueZ.real(), valueZ.imag(), valueV, 1+valueExpScl, 1, bjr, bji, &nz, &idum, &valueDebug);
        if(nz>=0 && (idum==0 || idum==3)) {
            valueZ = std::complex<double>(bjr[0],bji[0]);
        } else {
            valueZ = std::complex<double>(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN());
        }
        res = Py_BuildValue("O", PyComplex_FromDoubles(valueZ.real(),valueZ.imag()));
    }

    if(numArrs > 0) {
        int       ndimZ  = PyArray_NDIM( (PyArrayObject*)array_cplx[0]);
        npy_intp* shapeZ = PyArray_SHAPE((PyArrayObject*)array_cplx[0]);
        npy_intp  flatDims[1];
        flatDims[0]      = PyArray_SIZE( (PyArrayObject*)array_cplx[0]);
        int       a_len  = (int) flatDims[0];
        std::complex<double> valuesZ[a_len];
        if(ndimZ==1) {
            py2c_cplxarr((PyArrayObject*)array_cplx[0], valuesZ);
        } else {
            PyArray_Dims flatShp = { nullptr, 0 };
            flatShp.ptr = flatDims;
            flatShp.len = 1;
            py2c_cplxarr((PyArrayObject*)PyArray_Newshape((PyArrayObject*)array_cplx[0], &flatShp, NPY_CORDER), valuesZ);
        }
        for(int i=0; i<a_len; i++) {
            PySys_WriteStdout("Bessel J: nu=%f  z=%f+i*%f  expscl=%i\n",valueV,valuesZ[i].real(),valuesZ[i].imag(),valueExpScl);
            zbesj(valuesZ[i].real(), valuesZ[i].imag(), valueV, 1+valueExpScl, 1, bjr, bji, &nz, &idum, &valueDebug);
            if(nz>=0 && (idum==0 || idum==3)) {
                valuesZ[i] = std::complex<double>(bjr[0],bji[0]);
            } else {
                valuesZ[i] = std::complex<double>(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN());
            }
        }
        if(ndimZ==1) {
            res = Py_BuildValue("O", c2py_cplxarr(a_len, valuesZ));
        } else {
            PyArray_Dims outShp = { nullptr, 0 };
            outShp.ptr = shapeZ;
            outShp.len = ndimZ;
            res = Py_BuildValue("O", PyArray_Newshape(c2py_cplxarr(a_len, valuesZ), &outShp, NPY_CORDER));
        }
    }

    return res;
}
#define by_docstring "bessely(v, z, /, es=False)\n\n\
Calculates the Bessel function of the second kind\n\n\
Parameters\n----------\n\
v : scalar, float\n    order of the Bessel function\n\
z : scalar or array-like, complex\n    the argument/location, where the Bessel function has to be evaluated\n\
es : scalar, boolean, optional\n    exponentially scales the result by exp(2/3*z**1.5) if set to True, default: False\n\n\
Returns\n-------\n\
r : scalar or array-like, complex number\n    result of the Bessel function of the second kind and order v at complex value z, same shape as z"
PyObject* mie_art_bessely(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"v", (char*)"z", (char*)"es", (char*)"debug", NULL };

    int valueExpScl = false;
    int valueDebug = false;
    double valueV;
    Py_complex valueNpZ;

    PyObject* arr_cplx_ptr[1] = { NULL };
    PyObject* array_cplx[1]   = { NULL };

    int numArrs = -1;
    int ctype = -1;

    if(PyArg_ParseTupleAndKeywords(args, kwds, "dD|pp", kwlist, &valueV, &valueNpZ, &valueExpScl, &valueDebug)) {
        numArrs = 0;
    } else {
        PyErr_Clear();
    }

    if(numArrs < 0) {
        if(PyArg_ParseTupleAndKeywords(args, kwds, "dO|pp", kwlist, &valueV, &arr_cplx_ptr[0], &valueExpScl, &valueDebug)) {
            if(parse_arrays(1, NPY_COMPLEX64, arr_cplx_ptr, array_cplx))
                ctype = NPY_COMPLEX64;
            if(ctype<0)
            if(parse_arrays(1, NPY_COMPLEX128, arr_cplx_ptr, array_cplx))
                ctype = NPY_COMPLEX128;
            if(ctype<0) {
                PyErr_SetString(
                    PyExc_TypeError,
                    "The z array has to be of type float, double or complex."
                );
                return NULL;
            }
            numArrs = 1;
        } else {
            PyErr_Clear();
        }
    }

    if(numArrs < 0) {
        PyErr_SetString(
            PyExc_TypeError,
            "The arguments dtypes do not match, expected (float,complex)"
        );
        return NULL;
    }

    double byr[1], byi[1], cwr[1], cwi[1];
    int nz, idum;

    PyObject* res = NULL;
    if(numArrs == 0) {
        zbesy(valueNpZ.real, valueNpZ.imag, valueV, 1+valueExpScl, 1, byr, byi, &nz, cwr, cwi, &idum, &valueDebug);
        std::complex<double> valueZ;
        if(nz>=0 && (idum==0 || idum==3)) {
            valueZ = std::complex<double>(byr[0],byi[0]);
        } else {
            valueZ = std::complex<double>(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN());
        }
        res = Py_BuildValue("O", PyComplex_FromDoubles(valueZ.real(),valueZ.imag()));
    }

    if(numArrs > 0) {
        int       ndimZ  = PyArray_NDIM( (PyArrayObject*)array_cplx[0]);
        npy_intp* shapeZ = PyArray_SHAPE((PyArrayObject*)array_cplx[0]);
        npy_intp  flatDims[1];
        flatDims[0]      = PyArray_SIZE( (PyArrayObject*)array_cplx[0]);
        int       a_len  = (int) flatDims[0];
        std::complex<double> valuesZ[a_len];
        if(ndimZ==1) {
            py2c_cplxarr((PyArrayObject*)array_cplx[0], valuesZ);
        } else {
            PyArray_Dims flatShp = { nullptr, 0 };
            flatShp.ptr = flatDims;
            flatShp.len = 1;
            py2c_cplxarr((PyArrayObject*)PyArray_Newshape((PyArrayObject*)array_cplx[0], &flatShp, NPY_CORDER), valuesZ);
        }
        for(int i=0; i<a_len; i++) {
            zbesy(valuesZ[i].real(), valuesZ[i].imag(), valueV, 1+valueExpScl, 1, byr, byi, &nz, cwr, cwi, &idum, &valueDebug);
            if(nz>=0 && (idum==0 || idum==3)) {
                valuesZ[i] = std::complex<double>(byr[0],byi[0]);
            } else {
                valuesZ[i] = std::complex<double>(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN());
            }
        }
        if(ndimZ==1) {
            res = Py_BuildValue("O", c2py_cplxarr(a_len, valuesZ));
        } else {
            PyArray_Dims outShp = { nullptr, 0 };
            outShp.ptr = shapeZ;
            outShp.len = ndimZ;
            res = Py_BuildValue("O", PyArray_Newshape(c2py_cplxarr(a_len, valuesZ), &outShp, NPY_CORDER));
        }
    }

    return res;
}
#define hv_docstring "hankel(v, z, m, /, es=False)\n\n\
Calculates the Bessel function of the third kind, also known as Hankel function\n\n\
Parameters\n----------\n\
v : scalar, float\n    order of the Bessel function\n\
z : scalar or array-like, complex\n    the argument/location, where the Bessel function has to be evaluated\n\
m : scalar, integer\n    kind of the Hankel function, possible values: 1, 2\n\
es : scalar, boolean, optional\n    exponentially scales the result by exp(2/3*z**1.5) if set to True, default: False\n\n\
Returns\n-------\n\
r : scalar or array-like, complex\n    result of the bessel function of the second kind and order v at complex value z, same shape as z"
PyObject* mie_art_hankel(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"v", (char*)"z", (char*)"m", (char*)"es", (char*)"debug", NULL };

    int valueExpScl = false;
    int valueDebug = false;
    int valueM;
    double valueV;
    Py_complex valueNpZ;

    PyObject* arr_cplx_ptr[1] = { NULL };
    PyObject* array_cplx[1]   = { NULL };

    int numArrs = -1;
    int ctype = -1;

    if(PyArg_ParseTupleAndKeywords(args, kwds, "dDi|pp", kwlist, &valueV, &valueNpZ, &valueM, &valueExpScl, &valueDebug)) {
        numArrs = 0;
    } else {
        PyErr_Clear();
    }

    if(numArrs < 0) {
        if(PyArg_ParseTupleAndKeywords(args, kwds, "dOi|pp", kwlist, &valueV, &arr_cplx_ptr[0], &valueM, &valueExpScl, &valueDebug)) {
            if(parse_arrays(1, NPY_COMPLEX64, arr_cplx_ptr, array_cplx))
                ctype = NPY_COMPLEX64;
            if(ctype<0)
            if(parse_arrays(1, NPY_COMPLEX128, arr_cplx_ptr, array_cplx))
                ctype = NPY_COMPLEX128;
            if(ctype<0) {
                PyErr_SetString(
                    PyExc_TypeError,
                    "The z array has to be of type float, double or complex."
                );
                return NULL;
            }
            numArrs = 1;
        } else {
            PyErr_Clear();
        }
    }

    double bhr[1], bhi[1];
    int nz, idum;

    PyObject* res = NULL;
    if(numArrs == 0) {
    	zbesh(valueNpZ.real,valueNpZ.imag, valueV, 1+valueExpScl, valueM, 1, bhr,bhi, &nz, &idum, &valueDebug);
        std::complex<double> valueZ;
        if(nz>=0 && (idum==0 || idum==3)) {
            valueZ = std::complex<double>(bhr[0],bhi[0]);
        } else {
            valueZ = std::complex<double>(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN());
        }
        res = Py_BuildValue("O", PyComplex_FromDoubles(valueZ.real(),valueZ.imag()));
    }

    if(numArrs > 0) {
        int       ndimZ  = PyArray_NDIM( (PyArrayObject*)array_cplx[0]);
        npy_intp* shapeZ = PyArray_SHAPE((PyArrayObject*)array_cplx[0]);
        npy_intp  flatDims[1];
        flatDims[0]      = PyArray_SIZE( (PyArrayObject*)array_cplx[0]);
        int       a_len  = (int) flatDims[0];
        std::complex<double> valuesZ[a_len];
        if(ndimZ==1) {
            py2c_cplxarr((PyArrayObject*)array_cplx[0], valuesZ);
        } else {
            PyArray_Dims flatShp = { nullptr, 0 };
            flatShp.ptr = flatDims;
            flatShp.len = 1;
            py2c_cplxarr((PyArrayObject*)PyArray_Newshape((PyArrayObject*)array_cplx[0], &flatShp, NPY_CORDER), valuesZ);
        }
        for(int i=0; i<a_len; i++) {
            zbesh(valuesZ[i].real(),valuesZ[i].imag(), valueV, 1+valueExpScl, valueM, 1, bhr,bhi, &nz, &idum, &valueDebug);
            if(nz>=0 && (idum==0 || idum==3)) {
                valuesZ[i] = std::complex<double>(bhr[0],bhi[0]);
            } else {
                valuesZ[i] = std::complex<double>(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN());
            }
        }
        if(ndimZ==1) {
            res = Py_BuildValue("O", c2py_cplxarr(a_len, valuesZ));
        } else {
            PyArray_Dims outShp = { nullptr, 0 };
            outShp.ptr = shapeZ;
            outShp.len = ndimZ;
            res = Py_BuildValue("O", PyArray_Newshape(c2py_cplxarr(a_len, valuesZ), &outShp, NPY_CORDER));
        }
    }

    return res;
}

#define bi_docstring "besseli(v, z, m, /, es=False)\n\n\
Calculates the modified Bessel function of the first kind\n\n\
Parameters\n----------\n\
v : scalar, floating point number\n    order of the Bessel function\n\
z : scalar, complex number\n    the argument/location, where the Bessel function has to be evaluated\n\
es : scalar, boolean, optional\n    exponentially scales the result by exp(2/3*z**1.5) if set to True, default: False\n\n\
Returns\n-------\n\
r : scalar, complex number\n    result of the modified Bessel function of the first kind and order v at complex value z"
PyObject* mie_art_besseli(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"v", (char*)"z", (char*)"es", (char*)"debug", NULL };

    //use function for integer array and integer value
    int valueExpScl = false;
    int valueDebug = false;
    double valueV;
    Py_complex valueNpZ;
    if(PyArg_ParseTupleAndKeywords(args, kwds, "dD|pp", kwlist, &valueV, &valueNpZ, &valueExpScl, &valueDebug)) {
    } else {
        PyErr_SetString(
            PyExc_TypeError,
            "The arguments dtypes do not match, expected (float,complex)"
        );
        return NULL;
    }

    double bir[1], bii[1];
    std::complex<double> bi = std::complex<double>(
            std::numeric_limits<double>::quiet_NaN(),
            std::numeric_limits<double>::quiet_NaN());;
    int nz, idum;
    zbesi(valueNpZ.real, valueNpZ.imag, valueV, 1+valueExpScl, 1, bir, bii, &nz, &idum, &valueDebug);
    if(nz>=0 && (idum==0 || idum==3)) {
        bi = std::complex<double>(bir[0], bii[0]);
    }
    PyObject *res = Py_BuildValue("O", PyComplex_FromDoubles(bi.real(),bi.imag()));
    return res;
}
#define bk_docstring "besselk(v, z, m, /, es=False)\n\n\
Calculates the modified Bessel function of the second kind\n\n\
Parameters\n----------\n\
v : scalar, floating point number\n    order of the Bessel function\n\
z : scalar, complex number\n    the argument/location, where the Bessel function has to be evaluated\n\
es : scalar, boolean, optional\n    exponentially scales the result by exp(2/3*z**1.5) if set to True, default: False\n\n\
Returns\n-------\n\
r : scalar, complex number\n    result of the modified Bessel function of the second kind and order v at complex value z"
PyObject* mie_art_besselk(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"v", (char*)"z", (char*)"es", (char*)"debug", NULL };

    //use function for integer array and integer value
    int valueExpScl = false;
    int valueDebug = false;
    double valueV;
    Py_complex valueNpZ;
    if(PyArg_ParseTupleAndKeywords(args, kwds, "dD|pp", kwlist, &valueV, &valueNpZ, &valueExpScl, &valueDebug)) {
    } else {
        PyErr_SetString(
            PyExc_TypeError,
            "The arguments dtypes do not match, expected (float,complex)"
        );
        return NULL;
    }

    double bkr[1], bki[1];
    std::complex<double> bk = std::complex<double>(
            std::numeric_limits<double>::quiet_NaN(),
            std::numeric_limits<double>::quiet_NaN());;
    int nz, idum;
    zbesk(valueNpZ.real, valueNpZ.imag, valueV, 1+valueExpScl, 1, bkr, bki, &nz, &idum, &valueDebug);
    if(nz>=0 && (idum==0 || idum==3)) {
        bk = std::complex<double>(bkr[0], bki[0]);
    }
    PyObject *res = Py_BuildValue("O", PyComplex_FromDoubles(bk.real(),bk.imag()));
    return res;
}


// **** Airy function

#define ai_docstring "airy(z, /, es=False)\n\n\
Calculates the Airy function\n\n\
Parameters\n----------\n\
z : scalar, complex number\n    the argument/location, where the airy function has to be evaluated\n\
es : scalar, boolean, optional\n    exponentially scales the result by exp(2/3*z**1.5) if set to True, default: False\n\n\
Returns\n-------\n\
r : scalar, complex number\n    result of the Airy function at complex value z"
PyObject* mie_art_airy(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"z", (char*)"es", (char*)"debug", NULL };

    //use function for integer array and integer value
    int valueExpScl = false;
    int valueDebug = false;
    Py_complex valueNpZ;
    PyObject* arr_ptr[1] = { NULL };
    PyObject* array[1] =   { NULL };
    int numArrs = -5;

    if(PyArg_ParseTupleAndKeywords(args, kwds, "D|pp", kwlist, &valueNpZ, &valueExpScl, &valueDebug)) {
        numArrs = 0;
    } else {
        PyErr_Clear();
    }
    if(numArrs<0) {
        if(PyArg_ParseTupleAndKeywords(args, kwds, "O|pp", kwlist, &arr_ptr[0], &valueExpScl, &valueDebug)) {
            int dtype = -1;
            if(parse_arrays(1, NPY_COMPLEX64, arr_ptr, array))
                dtype = NPY_COMPLEX64;
            if(dtype<0)
            if(parse_arrays(1, NPY_COMPLEX128, arr_ptr, array))
                dtype = NPY_COMPLEX128;
            if(dtype<0) {
                PyErr_SetString(
                    PyExc_TypeError,
                    "z is expected to be of type complex."
                );
                return NULL;
            }
            numArrs = 1;
        } else {
            PyErr_Clear();
        }
    }

    if(numArrs<0) {
        PyErr_SetString(
            PyExc_TypeError,
            "Arguments do not match function defintion: airy(z, /, es=False)");
        return NULL;
    }

    PyObject* res = NULL;
    if(numArrs==0) {
        double air[1], aii[1];
        std::complex<double> ai = std::complex<double>(
                std::numeric_limits<double>::quiet_NaN(),
                std::numeric_limits<double>::quiet_NaN());
        int nz, idum;
        zairy(valueNpZ.real, valueNpZ.imag, 0, 1+valueExpScl, air, aii, &nz, &idum, &valueDebug);
        if(nz>=0 && (idum==0 || idum==3)) {
            ai = std::complex<double>(air[0], aii[0]);
        }
        res = Py_BuildValue("O", PyComplex_FromDoubles(ai.real(),ai.imag()));
    }
    if(numArrs==1) {
        npy_intp flatDims[1];
        flatDims[0] = PyArray_SIZE((PyArrayObject*)array[0]);
        int a_len = (int) flatDims[0];
        PyArray_Dims flatShp = { nullptr, 0 };
        flatShp.ptr = flatDims;
        flatShp.len = 1;

        std::complex<double> valuesZ[a_len];
        py2c_cplxarr((PyArrayObject*)PyArray_Newshape((PyArrayObject*)array[0], &flatShp, NPY_CORDER), valuesZ);
        double air[1], aii[1];
        int nz, idum;
        for(int i=0; i<a_len; i++) {
            zairy(valuesZ[i].real(),valuesZ[i].imag(), 0, 1+valueExpScl, air, aii, &nz, &idum, &valueDebug);
            if(nz>=0 && (idum==0 || idum==3)) {
                valuesZ[i] = std::complex<double>(air[0], aii[0]);
            } else {
                valuesZ[i] = std::complex<double>(
                        std::numeric_limits<double>::quiet_NaN(),
                        std::numeric_limits<double>::quiet_NaN());
            }
        }
        PyArray_Dims outShp = { nullptr, 0 };
        outShp.ptr = PyArray_SHAPE((PyArrayObject*)array[0]);
        outShp.len = PyArray_NDIM((PyArrayObject*)array[0]);
        res = Py_BuildValue("O", PyArray_Newshape(c2py_cplxarr(a_len, valuesZ), &outShp, NPY_CORDER));
    }
    return res;
}


// **** Mie field coefficients

static int calc_nmax(double x) {
    return (int)(x + 4.0*std::cbrt(x) + 2.5);
}

#define mieab_docstring "Mie_ab(m, x)\n\n\
Computes external field coefficients $a_n$ and $b_n$ based on inputs of refractive index $m$ and size parameter $x=\\pi\\,d_p/\\lambda$.\n\n\
Parameters\n----------\n\
m : scalar, complex number\n    refractive index of the particle reduced by the refractive index of the surrounding medium\n\
x : scalar, floating point number\n    size parameter of the particle\n\n\
Returns\n-------\n\
an : array-like, 1dimensional, complex numbers\n    external field coefficients $a_n$\n\
bn : array-like, 1dimensional, complex numbers\n    external field coefficients $b_n$"
void mie_ab(std::complex<double> m, double x, std::complex<double> *an, std::complex<double> *bn) {
    int nmax = calc_nmax(x);
    std::complex<double> mx = m*x;
    int nmx  = 16 + std::max(nmax, (int)(std::abs(mx)+0.5));
    double sx = std::sqrt(HPI*x);
    int idx;

    std::complex<double> Dn[nmx];
    Dn[nmx-1] = std::complex<double>(0.0,0.0);
    for(idx=nmx-2; idx>=0; idx--) {
        std::complex<double> invM = (2.0+idx) / mx;
        Dn[idx] = invM - 1.0/(Dn[idx+1] + invM);
    }

    std::complex<double> jv[nmax];
    std::complex<double> yv[nmax];

    double jvr[1], jvi[1], yvr[1], yvi[1], cwr[1], cwi[1];
    double v_start = 1.5;
    int success, ierr;
    int debug = false;
    for(idx=0; idx<nmax; idx++) {
        double nu = v_start+idx;
        zbesj(x, 0.0, nu, 1, 1, jvr, jvi, &success,           &ierr, &debug);
        zbesy(x, 0.0, nu, 1, 1, yvr, yvi, &success, cwr, cwi, &ierr, &debug);
        jv[idx] = std::complex<double>(jvr[0],jvi[0]);
        yv[idx] = std::complex<double>(yvr[0],yvi[0]);
    }

    std::complex<double> cx(x,0.0);
    std::complex<double> p1x(std::sin(x),0.0);
    std::complex<double> ch1x(std::cos(x),0.0);

    for(idx=0; idx<nmax; idx++) {
        std::complex<double> px   =  sx*jv[idx];
        std::complex<double> chx  = -sx*yv[idx];
        std::complex<double> gsx  = px - chx*cplxJ;
        std::complex<double> gs1x = p1x - ch1x*cplxJ;
        std::complex<double> af   = Dn[idx]/m + (1.0+idx)/x;
        std::complex<double> bf   = m*Dn[idx] + (1.0+idx)/x;

        an[idx] = (px*af-p1x) / (gsx*af-gs1x);
        bn[idx] = (px*bf-p1x) / (gsx*bf-gs1x);

        p1x  = px;
        ch1x = chx;
    }
}
PyObject* mie_art_mieab(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"m", (char*)"x", NULL };

    //use function for integer array and integer value
    Py_complex valueNpM;
    double valueX;
    if(PyArg_ParseTupleAndKeywords(args, kwds, "Dd", kwlist, &valueNpM, &valueX)) {
    } else {
        PyErr_SetString(
            PyExc_TypeError,
            "The arguments dtypes do not match, expected (complex,float)"
        );
        return NULL;
    }
    int nmax = calc_nmax(valueX);
    std::complex<double> valueM = py2c_cplx(valueNpM);
    std::complex<double> an[nmax];
    std::complex<double> bn[nmax];
    mie_ab(valueM, valueX, an, bn);
    PyArrayObject *pyan = c2py_cplxarr(nmax, an);
    PyArrayObject *pybn = c2py_cplxarr(nmax, bn);
    PyObject *res = Py_BuildValue("OO", pyan, pybn);
    return res;
}

#define miecoatedab_docstring "MieCoated_ab(m_core, x_core, m_shell, x_shell)\n\n\
Computes external field coefficients $a_n$ and $b_n$ based on inputs of refractive indices $m_core$ and $m_shell$,\n\
and size parameters $x_core=\\pi\\,d_core/\\lambda$ and $x_shell=\\pi\\,d_shell/\\lambda$.\n\n\
Parameters\n----------\n\
m_core : scalar, complex number\n    refractive index of the particle reduced by the refractive index of the surrounding medium\n\
x_core : scalar, floating point number\n    size parameter of the particle's core without coating\n\
m_shell : scalar, complex number\n    refractive index of the particle's coating reduced by the refractive index of the surrounding medium\n\
x_shell : scalar, floating point number\n    size parameter of the particle including the coating shell\n\n\
Returns\n-------\n\
an : array-like, 1dimensional, complex numbers\n    external field coefficients $a_n$\n\
bn : array-like, 1dimensional, complex numbers\n    external field coefficients $b_n$"
void miecoated_ab(std::complex<double> m_core, double x_core, std::complex<double> m_shell, double x_shell, std::complex<double> *an, std::complex<double> *bn) {
    int nmax = calc_nmax(x_shell);
    std::complex<double> cx_shell(x_shell,0.0);
    std::complex<double> m = m_shell / m_core;
    std::complex<double> u = m_core * x_core; // #arguments for the Bessel functions
    std::complex<double> v = m_shell * x_core;
    std::complex<double> w = m_shell * x_shell;
    double mx = std::max(std::abs(m_core)*x_shell, std::abs(m_shell)*x_shell);
    int nmx  = 16 + std::max(nmax, (int)(mx+0.5));
    int idx;

    std::complex<double> dnu[nmx];
    std::complex<double> dnv[nmx];
    std::complex<double> dnw[nmx];
    dnu[nmx-1] = std::complex<double>(0.0,0.0);
    dnv[nmx-1] = std::complex<double>(0.0,0.0);
    dnw[nmx-1] = std::complex<double>(0.0,0.0);
    dnu[nmx-2] = std::complex<double>(0.0,0.0);
    dnv[nmx-2] = std::complex<double>(0.0,0.0);
    dnw[nmx-2] = std::complex<double>(0.0,0.0);
    for(idx=nmx-3; idx>=0; idx--) {
        std::complex<double> invU = (2.0+idx)/u;
        std::complex<double> invV = (2.0+idx)/v;
        std::complex<double> invW = (2.0+idx)/w;
        dnu[idx] = invU - 1.0/(dnu[idx+1]+invU);
        dnv[idx] = invV - 1.0/(dnv[idx+1]+invV);
        dnw[idx] = invW - 1.0/(dnw[idx+1]+invW);
    }

    std::complex<double> sv = std::sqrt(HPI*v);
    std::complex<double> sw = std::sqrt(HPI*w);
    std::complex<double> sy(std::sqrt(HPI*x_shell),0.0);
    std::complex<double> p1y(std::sin(x_shell),0.0);
    std::complex<double> ch1y(std::cos(x_shell),0.0);
    std::complex<double> gs1y(0.0,0.0);

    std::complex<double> jv[nmax];
    std::complex<double> yv[nmax];
    std::complex<double> jw[nmax];
    std::complex<double> yw[nmax];
    std::complex<double> jy[nmax];
    std::complex<double> yy[nmax];

    double jvr[1], jvi[1], yvr[1], yvi[1], cwr[1], cwi[1];
    double v_start = 1.5;
    int success, ierrj, ierry;
    int debug = false;
    for(idx=0; idx<nmax; idx++) {
        double nu = v_start+idx;
        zbesj(v.real(),v.imag(), nu, 2, 1, jvr, jvi, &success,           &ierrj, &debug);
        zbesy(v.real(),v.imag(), nu, 2, 1, yvr, yvi, &success, cwr, cwi, &ierry, &debug);
        jv[idx] = std::complex<double>(jvr[0],jvi[0]);
        yv[idx] = std::complex<double>(yvr[0],yvi[0]);
        zbesj(w.real(),w.imag(), nu, 2, 1, jvr, jvi, &success,           &ierrj, &debug);
        zbesy(w.real(),w.imag(), nu, 2, 1, yvr, yvi, &success, cwr, cwi, &ierry, &debug);
        jw[idx] = std::complex<double>(jvr[0],jvi[0]);
        yw[idx] = std::complex<double>(yvr[0],yvi[0]);
        zbesj(x_shell,0.0, nu, 1, 1, jvr, jvi, &success,           &ierrj, &debug);
        zbesy(x_shell,0.0, nu, 1, 1, yvr, yvi, &success, cwr, cwi, &ierry, &debug);
        jy[idx] = std::complex<double>(jvr[0],jvi[0]);
        yy[idx] = std::complex<double>(yvr[0],yvi[0]);
    }
    double aiv = std::abs(v.imag());
    double aiw = std::abs(w.imag());
    double ewvv = std::exp(aiw-aiv-aiv);
    double ew   = std::exp(aiw);

    for(idx=0; idx<nmax; idx++) {
        std::complex<double> pv   = jv[idx]*sv;
        std::complex<double> pw   = jw[idx]*sw;
        std::complex<double> py   = jy[idx]*sy;
        std::complex<double> chv  = -yv[idx]*sv;
        std::complex<double> chw  = -yw[idx]*sw;
        std::complex<double> chy  = -yy[idx]*sy;
        std::complex<double> gsy  = py - chy*cplxJ;
        std::complex<double> gs1y = p1y - ch1y*cplxJ;

        std::complex<double> uu   = dnu[idx]*m - dnv[idx];
        std::complex<double> vv   = dnu[idx]/m - dnv[idx];
        std::complex<double> fv   = pv/chv;
        std::complex<double> pw_chw_fv = (pw-chw*fv)*ew;
        std::complex<double> pw_pv_chv = pw/(pv*chv)*ewvv;
        std::complex<double> ku1  = (uu*fv/pw)/ew;
        std::complex<double> kv1  = (vv*fv/pw)/ew;
        std::complex<double> ku2  = uu*pw_chw_fv + pw_pv_chv;
        std::complex<double> kv2  = vv*pw_chw_fv + pw_pv_chv;
        std::complex<double> dns  = ku1 / ku2 + dnw[idx];
        std::complex<double> gns  = kv1 / kv2 + dnw[idx];

        std::complex<double> af   = dns/m_shell + (1.0+idx)/x_shell;
        std::complex<double> bf   = gns*m_shell + (1.0+idx)/x_shell;
        an[idx] = (py*af-p1y) / (gsy*af-gs1y);
        bn[idx] = (py*bf-p1y) / (gsy*bf-gs1y);

        p1y = py;
        ch1y = chy;
    }
}
PyObject* mie_art_miecoatedab(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"m_core", (char*)"x_core", (char*)"m_shell", (char*)"x_shell", NULL };

    //use function for integer array and integer value
    Py_complex valueNpMcore;
    Py_complex valueNpMshell;
    double valueXcore;
    double valueXshell;
    if(PyArg_ParseTupleAndKeywords(args, kwds, "DdDd", kwlist, &valueNpMcore, &valueXcore, &valueNpMshell, &valueXshell)) {
    } else {
        PyErr_SetString(
            PyExc_TypeError,
            "The arguments dtypes do not match, expected (complex,float,complex,float)"
        );
        return NULL;
    }
    int nmax = calc_nmax(valueXshell);
    std::complex<double> valueMcore = py2c_cplx(valueNpMcore);
    std::complex<double> valueMshell = py2c_cplx(valueNpMshell);
    std::complex<double> an[nmax];
    std::complex<double> bn[nmax];
    miecoated_ab(valueMcore, valueXcore, valueMshell, valueXshell, an, bn);
    PyArrayObject *pyan = c2py_cplxarr(nmax, an);
    PyArrayObject *pybn = c2py_cplxarr(nmax, bn);
    PyObject *res = Py_BuildValue("OO", pyan, pybn);
    return res;
}

#define miecd_docstring "Mie_cd(m, x)\n\n\
Computes internal field coefficients $c_n$ and $d_n$ based on inputs of refractive index $m$ and size parameter $x=\\pi\\,d_p/\\lambda$.\n\n\
Parameters\n----------\n\
m : scalar, complex number\n    refractive index of the particle reduced by the refractive index of the surrounding medium\n\
x : scalar, floating point number\n    size parameter of the particle\n\n\
Returns\n-------\n\
cn : array-like, 1dimensional, complex numbers\n    internal field coefficients $c_n$\n\
dn : array-like, 1dimensional, complex numbers\n    internal field coefficients $d_n$"
void mie_cd(std::complex<double> m, double x, std::complex<double> *cn, std::complex<double> *dn) {
    std::complex<double> cx(x,0.0);
    std::complex<double> mx = m*x;
    std::complex<double> m2 = m*m;
    std::complex<double> mx2 = mx*mx;
    int nmax = calc_nmax(x);
    int nmx  = 16+std::max(nmax, (int)(std::abs(mx)+0.5));
    int idx;

    std::complex<double> cnx[nmx];
    cnx[nmx-1] = std::complex<double>(0.0,0.0);
    for(idx=nmx; idx>1; idx--) {
        cnx[idx-1] = (double)idx - mx2/(cnx[idx]+(double)idx);
    }

    double rx1 = std::sqrt(HPI/x);
    std::complex<double> rx2 = std::sqrt(mx/HPI);
    std::complex<double> b1x(std::sin(x)/x,0.0);
    std::complex<double> y1x(std::cos(x)/x,0.0);

    std::complex<double> jv[nmax];
    std::complex<double> yv[nmax];
    double jvr[1], jvi[1], yvr[1], yvi[1], cwr[1], cwi[1];
    double v_start = 1.5;
    int success, ierr;
    int  debug = false;
    for(idx=0; idx<nmax; idx++) {
        double nu = v_start + idx;
        zbesj(x,0.0, nu, 1, 1, jvr, jvi, &success,           &ierr, &debug);
        zbesy(x,0.0, nu, 1, 1, yvr, yvi, &success, cwr, cwi, &ierr, &debug);
        jv[idx] = std::complex<double>(jvr[0],jvi[0]);
        yv[idx] = std::complex<double>(yvr[0],yvi[0]);
    }
    for(idx=0; idx<nmax; idx++) {
        std::complex<double> jnx  = rx1*jv[idx];
        std::complex<double> jnmx = rx2/jv[idx];
        std::complex<double> yx   = rx1*yv[idx];
        std::complex<double> hx   = jnx + yx*cplxJ;
        std::complex<double> hn1x = b1x + y1x*cplxJ;
        std::complex<double> ax   = b1x*x - jnx*(1.0+idx);
        std::complex<double> ahx  = hn1x*x - hx*(1.0*idx);
        std::complex<double> numerator = jnx*ahx - hx*ax;
        std::complex<double> c_denom =   ahx - hx*cnx[idx];
        std::complex<double> d_denom =   m2*ahx - hx*cnx[idx];

        cn[idx] = jnmx * numerator/c_denom;
        dn[idx] = jnmx*m *numerator/d_denom;

        b1x = jnx;
        y1x = yx;
    }
}
PyObject* mie_art_miecd(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"m", (char*)"x", NULL };

    //use function for integer array and integer value
    Py_complex valueNpM;
    double valueX;
    if(PyArg_ParseTupleAndKeywords(args, kwds, "Dd", kwlist, &valueNpM, &valueX)) {
    } else {
        PyErr_SetString(
            PyExc_TypeError,
            "The arguments dtypes do not match, expected (complex,float)"
        );
        return NULL;
    }
    int nmax = calc_nmax(valueX);
    std::complex<double> valueM = py2c_cplx(valueNpM);
    std::complex<double> cn[nmax];
    std::complex<double> dn[nmax];
    mie_cd(valueM, valueX, cn, dn);
    PyArrayObject *pycn = c2py_cplxarr(nmax, cn);
    PyArrayObject *pydn = c2py_cplxarr(nmax, dn);
    PyObject *res = Py_BuildValue("OO", pycn, pydn);
    return res;
}

#define miepitau_docstring "Mie_pitau(theta, nmax)\n\n\
Calculates angular functions $\\pi_n$ and $\\tau_n$.\n\n\
Parameters\n----------\n\
theta : scalar or array-like (1dimensional), floating point number\n    the scattering angle(s) $\\theta$\n\
nmax : scalar, integer\n    the maximum number of coefficients to compute.\n    Typically, $nmax = floor\\left(2+x+4x^{1/3}\\right)$, but can be given any integer.\n\n\
Returns\n-------\n\
pin : array-like, floating point numbers\n    coefficient series $\\pi_n$\n    1dimensional if a single value for $\\theta$ was given, else 2dimensional\n\
taun : array-like, floating point numbers\n    coefficient series $\\tau_n$\n    1dimensional if a single value for $\\theta$ was given, else 2dimensional"
void mie_pitau(double theta, int nmax, double *pin, double *taun) {
    double mu = std::cos(theta);
    pin[0] = 1.0;
    pin[1] = 3*mu;
    taun[0] = mu;
    taun[1] = 3*std::cos(2*theta);
    int idx;
    for(idx=2; idx<nmax; idx++) {
        pin[idx]  = ((2.0*idx+1.0)*mu*pin[idx-1] - (1.0+idx)*pin[idx-2]) / idx;
        taun[idx] = (1.0+idx)*mu*pin[idx] - (2.0+idx)*pin[idx-1];
    }
}
void mie_pitau(int nang, double *theta, int nmax, double *pin, double *taun) {
    int a,n;
    double sub_pi[nmax];
    double sub_tau[nmax];
    for(a=0; a<nang; a++) {
        mie_pitau(theta[a], nmax, sub_pi, sub_tau);
        int off = a*nmax;
        for(n=0; n<nmax; n++) {
            pin[off+n]  = sub_pi[n];
            taun[off+n] = sub_tau[n];
        }
    }
}
PyObject* mie_art_miepitau(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"theta", (char*)"nmax", NULL };

    //use function for integer array and integer value
    double valueTheta;
    int valueNmax;
    if(PyArg_ParseTupleAndKeywords(args, kwds, "di", kwlist, &valueTheta, &valueNmax)) {
        double pin[valueNmax];
        double taun[valueNmax];
        mie_pitau(valueTheta, valueNmax, pin, taun);
        PyArrayObject *pypin = c2py_dblarr(valueNmax, pin);
        PyArrayObject *pytaun = c2py_dblarr(valueNmax, taun);
        PyObject *res = Py_BuildValue("OO", pypin, pytaun);
        return res;
    } else {
        PyErr_Clear();
    }

    PyObject* arr_ptr[] = { NULL };
    PyObject* array[]   = { NULL };
    int dtype = -1;
    if(PyArg_ParseTupleAndKeywords(args, kwds, "Oi", kwlist, &arr_ptr[0], &valueNmax)) {
        {
            if(parse_arrays(1, NPY_FLOAT, arr_ptr, array)) {
                dtype = NPY_FLOAT;
            }
        }
        if(dtype==-1) {
            if (parse_arrays(1, NPY_DOUBLE, arr_ptr, array)) {
                dtype = NPY_DOUBLE;
            }
        }
    } else {
        PyErr_Clear();
    }

    if(dtype<0) {
        PyErr_SetString(
            PyExc_TypeError,
            "The arguments dtypes do not match, expected (float,int), (double,int), (float[],int) or (double[],int)"
        );
        return NULL;
    }
    int ndimT = PyArray_NDIM((PyArrayObject *)array[0]);
    if(ndimT!=1) {
        PyErr_SetString( PyExc_TypeError, "First argument must be scalar or one-dimensional!");
        Py_XDECREF(array[0]);
        return NULL;
    }
    int nang = PyArray_SIZE((PyArrayObject *)array[0]);
    double theta[nang];
    py2c_dblarr((PyArrayObject *)array[0], theta);
    int arr_len = nang*valueNmax;
    double *pin = new double[arr_len];
    double *taun = new double[arr_len];
    mie_pitau(nang, theta, valueNmax, pin, taun);
    PyArrayObject *pypin = c2py_dblarr(nang, valueNmax, pin);
    PyArrayObject *pytaun = c2py_dblarr(nang, valueNmax, taun);
    PyObject *res = Py_BuildValue("OO", pypin, pytaun);
    Py_DECREF(array[0]);
    delete[] pin;
    delete[] taun;
    return res;
}




// **** Mie for single particle

struct MieResult {
    double qext;
    double qsca;
    double qabs;
    double qback;
    double qpr;
    double qg;
    double qratio;
};

#define abtomie_docstring "ab2mie(an, bn, wavelength, diameter, /, asCrossSection=False, asDict=False)\n\n\
Parameters\n----------\n\
an : array-like, 1dimensional, complex numbers\n    external field coefficients $a_n$\n\
bn : array-like, 1dimensional, complex numbers\n    external field coefficients $b_n$\n\
wavelength : scalar, floating point number\n    the wavelength of incident light, in nm\n\
diameter : scalar, floating point number\n    the diameter of the whole particle, in nm\n\
asCrossSection : scalar, bool, optional\n    if specified and set to True, returns the results as optical cross-sections with units of nm$^2$.\n\
asDict : scalar, bool, optional\n    if specified and set to True, returns the results as a dictionary.\n\n\
Returns\n-------\n\
qext,qsca,qabs,qback,qratio,qpr,g :\n    scalars, floating point numbers\n    Mie efficiencies as described in MieQ()\n\
qext,qsca,qabs,qback,qratio,qpr,g :\n    scalars, floating point numbers\n    Mie efficiencies as optical cross sections, if asCrossSection set to True\n\
q : dict\n   dictionary of the Mie efficiencies, if asDict is set to True\n\
c : dict\n   dictionary of Mie efficiencies as optical cross sections, if asDict and asCrossSection are both set to True"
MieResult ab2mie(int nmax, std::complex<double> an[], std::complex<double> bn[], double wavelength, double diameter, int asCrossSection) {
    MieResult res;
    res.qext = 0.0;
    res.qsca = 0.0;
    res.qg   = 0.0;
    std::complex<double> qbck(0.0,0.0);
    int idx;

    for(idx=1; idx<=nmax; idx++) {
        double i = 1.0 - 2.0*(idx&1);
        double f = 2.0*idx+1.0;
        std::complex<double> a = an[idx-1];
        std::complex<double> b = bn[idx-1];
        std::complex<double> ap(0.0,0.0);
        std::complex<double> bp(0.0,0.0);
        if(idx<nmax) {
            ap = an[idx];
            bp = bn[idx];
        }
        res.qext += f*(a.real() + b.real());
        res.qsca += f*(a.real()*a.real()+a.imag()*a.imag() + b.real()*b.real()+b.imag()*b.imag());
        qbck +=     (a-b)*f*i;
        res.qg +=   (idx*idx+2.0*idx)*(a.real()*ap.real() + a.imag()*ap.imag() + b.real()*bp.real() + b.imag()*bp.imag())/(idx+1.0);
        res.qg +=   f*(a.real()*b.real() + a.imag()*b.imag())/(idx*idx+idx);
    }

    double sizeParam = _PI_ * diameter / wavelength;
    double ix2 = 1.0 / (sizeParam*sizeParam);
    double qbabs2 = qbck.real()*qbck.real()+qbck.imag()*qbck.imag();
    res.qpr    = 2.0*ix2*(res.qext - 2.0*res.qg);
    res.qg    *= 2.0/res.qsca;
    res.qback  = ix2*qbabs2;
    res.qratio = 0.5*qbabs2/res.qsca;
    res.qext  *= 2.0*ix2;
    res.qsca  *= 2.0*ix2;
    res.qabs   = res.qext - res.qsca;

    if(asCrossSection>0) {
        double css = 0.25*_PI_*diameter*diameter;
        res.qext  *= css;
        res.qsca  *= css;
        res.qabs  *= css;
        res.qback *= css;
        res.qpr   *= css;
    }

    return res;
}
PyObject* mie_art_ab2mie(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"an", (char*)"bn", (char*)"wavelength", (char*)"diameter", (char*)"asCrossSection", (char*)"asDict", NULL };

    PyObject *arr_ptr[2] = { NULL, NULL };
    PyObject *array[2] = { NULL, NULL };
    double valueW;
    double valueD;
    int valueCSS  = false;
    int valueDict = false;

    int dtype = -1;
    if(PyArg_ParseTupleAndKeywords(args, kwds, "OOdd|pp", kwlist,
                &arr_ptr[0], &arr_ptr[1], &valueW, &valueD, &valueCSS, &valueDict)) {
        if (parse_arrays(2, NPY_COMPLEX64, arr_ptr, array)) {
            dtype = NPY_COMPLEX64;
        }
        if (dtype<0)
        if (parse_arrays(2, NPY_COMPLEX128, arr_ptr, array)) {
            dtype = NPY_COMPLEX128;
        }
    } else {
        PyErr_Clear();
    }
    if (dtype<0) {
        PyErr_SetString(
            PyExc_TypeError,
            "The arguments dtypes do not match, expected (complex[:],complex[:],float,float[,bool,bool]) or (float64[:],float64[:],float64,int32[,int32,int32])"
        );
        return NULL;
    }
    int ndim1 = PyArray_NDIM((PyArrayObject*)array[0]);
    int ndim2 = PyArray_NDIM((PyArrayObject*)array[1]);
    if (ndim1!=1 || ndim2!=1) {
        Py_XDECREF(array[0]);
        Py_XDECREF(array[1]);
        PyErr_SetString(PyExc_TypeError, "Arrays must be one-dimensional.");
        return NULL;
    }
    int a_len = (int) PyArray_SIZE((PyArrayObject*)array[0]);
    int b_len = (int) PyArray_SIZE((PyArrayObject*)array[1]);
    if (a_len!=b_len) {
        Py_XDECREF(array[0]);
        Py_XDECREF(array[1]);
        PyErr_SetString(PyExc_TypeError, "Arrays have to be of the same length!");
        return NULL;
    }

    std::complex<double> an[a_len];
    std::complex<double> bn[b_len];
    py2c_cplxarr((PyArrayObject*)array[0], an);
    py2c_cplxarr((PyArrayObject*)array[1], bn);
    MieResult mr = ab2mie(a_len, an, bn, valueW, valueD, valueCSS);

    PyObject *res;
    if(valueDict>0) {
        if(valueCSS>0) {
            res = Py_BuildValue("{s:d,s:d,s:d,s:d,s:d,s:d,s:d}",
                                "Cext",mr.qext, "Csca",mr.qsca, "Cabs",mr.qabs, "Cback",mr.qback,
                                "Cratio",mr.qratio, "Cpr",mr.qpr, "g",mr.qg);
        } else {
            res = Py_BuildValue("{s:d,s:d,s:d,s:d,s:d,s:d,s:d}",
                                "Qext",mr.qext, "Qsca",mr.qsca, "Qabs",mr.qabs, "Qback",mr.qback,
                                "Qratio",mr.qratio, "Qpr",mr.qpr, "g",mr.qg);
        }
    } else {
        res = Py_BuildValue("ddddddd",mr.qext,mr.qsca,mr.qabs,mr.qback,mr.qratio,mr.qpr,mr.qg);
    }

    Py_DECREF(array[0]);
    Py_DECREF(array[1]);
    return res;
}

#define mieq_docstring "MieQ(m, diam, wavelength, /, nMedium=1.0, asCrossSection=False, asDict=False)\n\n\
Computes extinction, scattering, backscattering and absorption efficiencies, radiation pressure and asymmetry parameter\n\n\
Parameters\n----------\n\
m : scalar or array-like, complex number\n    refractive index of the particle reduced by the refractive index of the surrounding medium\n\
diam : scalar, floating point number\n    the diameter of the whole particle, in nm\n\
wavelength : scalar or array-like, floating point number\n    the wavelength of incident light, in nm\n    has to be of the same shape as m\n\
nMedium : scalar, floating point number, optional\n    the refractive index of the surrounding medium without the extinction part\n\
asCrossSection : scalar, bool, optional\n    if specified and set to True, returns the results as optical cross-sections with units of nm$^2$.\n\
asDict : scalar, bool, optional\n    if specified and set to True, returns the results as a dictionary\n\n\
Returns\n-------\n\
qext,qsca,qabs,qback,qratio,qpr,g :\n    scalars or array-like, floating point numbers, same shape as m\n    Mie efficiencies: extinction, scattering, absorption, backscattering, and backscatter-ratio, radiation pressure and asymmetry parameter\n\
cext,csca,cabs,cback,cratio,cpr,g :\n    scalars or array-like, floating point numbers, same shape as m\n    Mie efficiencies as optical cross sections, if asCrossSection set to True\n\
q : dict\n    dictionary of the Mie efficiencies, if asDict is set to True\n    entries have the same shape as m (scalar or array-like)\n\
c : dict\n    dictionary of Mie efficiencies as optical cross sections, if asDict and asCrossSection are both set to True\n    entries have the same shape as m (scalar or array-like)"
PyObject* mie_art_mieq(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"m", (char*)"diam", (char*)"wavelength", (char*)"nMedium", (char*)"asCrossSection", (char*)"asDict", NULL };

    Py_complex valueNpM;
    double valueW;
    double valueD;
    double valueNmedium = 1.0;
    int valueCSS = false;
    int valueDict = false;

    PyObject* arr_ptr[1] =      { NULL };
    PyObject* array[1] =        { NULL };
    PyObject* arr_cplx_ptr[1] = { NULL };
    PyObject* array_cplx[1] =   { NULL };

    int numArrs = -1;
    int ctype = -1;
    int dtype = -1;

    if(PyArg_ParseTupleAndKeywords(args, kwds, "Ddd|dpp", kwlist, &valueNpM, &valueD, &valueW, &valueNmedium, &valueCSS, &valueDict)) {
        numArrs = 0;
    } else {
        PyErr_Clear();
    }

    if(numArrs<0) {
        if(PyArg_ParseTupleAndKeywords(args, kwds, "OdO|dpp", kwlist, &arr_cplx_ptr[0], &valueD, &arr_ptr[0], &valueNmedium, &valueCSS, &valueDict)) {
            if(parse_arrays(1, NPY_COMPLEX64, arr_cplx_ptr, array_cplx))
                ctype = NPY_COMPLEX64;
            if(ctype<0)
            if(parse_arrays(1, NPY_COMPLEX128, arr_cplx_ptr, array_cplx))
                ctype = NPY_COMPLEX128;
            if(ctype<0) {
                PyErr_SetString(
                    PyExc_TypeError,
                    "The m array has to be of type float, double or complex."
                );
                return NULL;
            }
            if(parse_arrays(1, NPY_FLOAT, arr_ptr, array))
                dtype = NPY_FLOAT;
            if(dtype<0)
            if(parse_arrays(1, NPY_DOUBLE, arr_ptr, array))
                dtype = NPY_DOUBLE;
            if(dtype<0) {
                PyErr_SetString(
                    PyExc_TypeError,
                    "The wavelengths have to be an array of type float or double."
                );
                return NULL;
            }
            numArrs = 2;
        } else {
            PyErr_Clear();
        }
    }

    if(numArrs<0) {
        PyErr_SetString(
            PyExc_TypeError,
            "Arguments do not match function definition: MieQ(m, diameter, wavelength, /, nMedium=1.0, asCrossSection=False, asDict=False)"
        );
    }

    PyObject* res = NULL;
    if(numArrs==0) {
        std::complex<double> valueM = py2c_cplx(valueNpM) / valueNmedium;
        double x = _PI_*valueD/valueW;
        int nmax = calc_nmax(x);
        std::complex<double> an[nmax];
        std::complex<double> bn[nmax];
        mie_ab(valueM, x, an, bn);
        MieResult mr = ab2mie(nmax, an, bn, valueW, valueD, valueCSS);

        if(valueDict>0) {
            if(valueCSS>0) {
                res = Py_BuildValue("{s:d,s:d,s:d,s:d,s:d,s:d,s:d}",
                                    "Cext",mr.qext, "Csca",mr.qsca, "Cabs",mr.qabs, "Cback",mr.qback,
                                    "Cratio",mr.qratio, "Cpr",mr.qpr, "g",mr.qg);
            } else {
                res = Py_BuildValue("{s:d,s:d,s:d,s:d,s:d,s:d,s:d}",
                                    "Qext",mr.qext, "Qsca",mr.qsca, "Qabs",mr.qabs, "Qback",mr.qback,
                                    "Qratio",mr.qratio, "Qpr",mr.qpr, "g",mr.qg);
            }
        } else {
            res = Py_BuildValue("ddddddd",mr.qext,mr.qsca,mr.qabs,mr.qback,mr.qratio,mr.qpr,mr.qg);
        }
    }
    if(numArrs>1) {
        int ndimM = PyArray_NDIM((PyArrayObject*)array_cplx[0]);
        int ndimW = PyArray_NDIM((PyArrayObject*)array[0]);
        npy_intp* shapeM = PyArray_SHAPE((PyArrayObject*)array_cplx[0]);
        npy_intp* shapeW = PyArray_SHAPE((PyArrayObject*)array[0]);
        int mw_same = true;
        if(ndimM==ndimW) {
            for(int i=0; i<ndimM && mw_same; i++)
                mw_same = (shapeM[i]==shapeW[i]);
        } else {
            mw_same = false;
        }

        if(!mw_same) {
            Py_XDECREF(array_cplx[0]);
            Py_XDECREF(array[0]);
            PyErr_SetString(
                PyExc_IndexError,
                "m and wavelength have to be of the same shape!"
            );
            return res;
        }

        npy_intp flatDims[1];
        flatDims[0] = PyArray_SIZE((PyArrayObject*)array_cplx[0]);
        int a_len = (int) flatDims[0];
        PyArray_Dims flatShp = { nullptr, 0 };
        flatShp.ptr = flatDims;
        flatShp.len = 1;

        std::complex<double> valuesM[a_len];
        double valuesW[a_len];
        if(ndimW==1) {
            py2c_cplxarr((PyArrayObject*)array_cplx[0], valuesM);
            py2c_dblarr( (PyArrayObject*)array[0],      valuesW);
        } else {
            py2c_cplxarr((PyArrayObject*)PyArray_Newshape((PyArrayObject*)array_cplx[0], &flatShp, NPY_CORDER), valuesM);
            py2c_dblarr( (PyArrayObject*)PyArray_Newshape((PyArrayObject*)array[0],      &flatShp, NPY_CORDER), valuesW);
        }

        double bext[a_len];
        double bsca[a_len];
        double babs[a_len];
        double bbck[a_len];
        double brat[a_len];
        double bpr[a_len];
        double bg[a_len];
        for(int i=0; i<a_len; i++) {
            double x = _PI_*valueD/valuesW[i];
            int nmax = calc_nmax(x);
            std::complex<double> an[nmax];
            std::complex<double> bn[nmax];
            mie_ab(valuesM[i], x, an, bn);
            MieResult mr = ab2mie(nmax, an, bn, valuesW[i], valueD, valueCSS);
            bext[i] = mr.qext;
            bsca[i] = mr.qsca;
            babs[i] = mr.qabs;
            bbck[i] = mr.qback;
            brat[i] = mr.qratio;
            bpr[i]  = mr.qpr;
            bg[i]   = mr.qg;
        }

        PyArray_Dims outShp = { nullptr, 0 };
        outShp.ptr = shapeM;
        outShp.len = ndimM;
        PyObject* pyext_arr = NULL;
        PyObject* pysca_arr = NULL;
        PyObject* pyabs_arr = NULL;
        PyObject* pybck_arr = NULL;
        PyObject* pyrat_arr = NULL;
        PyObject* pypr_arr  = NULL;
        PyObject* pyasy_arr = NULL;
        if(ndimW==1) {
            pyext_arr = (PyObject*)c2py_dblarr(a_len, bext);
            pysca_arr = (PyObject*)c2py_dblarr(a_len, bsca);
            pyabs_arr = (PyObject*)c2py_dblarr(a_len, babs);
            pybck_arr = (PyObject*)c2py_dblarr(a_len, bbck);
            pyrat_arr = (PyObject*)c2py_dblarr(a_len, brat);
            pypr_arr  = (PyObject*)c2py_dblarr(a_len, bpr);
            pyasy_arr = (PyObject*)c2py_dblarr(a_len, bg);
        } else {
            pyext_arr = PyArray_Newshape(c2py_dblarr(a_len, bext), &outShp, NPY_CORDER);
            pysca_arr = PyArray_Newshape(c2py_dblarr(a_len, bsca), &outShp, NPY_CORDER);
            pyabs_arr = PyArray_Newshape(c2py_dblarr(a_len, babs), &outShp, NPY_CORDER);
            pybck_arr = PyArray_Newshape(c2py_dblarr(a_len, bbck), &outShp, NPY_CORDER);
            pyrat_arr = PyArray_Newshape(c2py_dblarr(a_len, brat), &outShp, NPY_CORDER);
            pypr_arr  = PyArray_Newshape(c2py_dblarr(a_len, bpr),  &outShp, NPY_CORDER);
            pyasy_arr = PyArray_Newshape(c2py_dblarr(a_len, bg),   &outShp, NPY_CORDER);
        }
        if(valueDict>0) {
            if(valueCSS>0) {
                res = Py_BuildValue("{s:O,s:O,s:O,s:O,s:O,s:O,s:O}",
                                    "Cext",pyext_arr, "Csca",pysca_arr, "Cabs",pyabs_arr, "Cback",pybck_arr,
                                    "Cratio",pyrat_arr, "Cpr",pypr_arr, "g",pyasy_arr);
            } else {
                res = Py_BuildValue("{s:O,s:O,s:O,s:O,s:O,s:O,s:O}",
                                    "Qext",pyext_arr, "Qsca",pysca_arr, "Qabs",pyabs_arr, "Qback",pybck_arr,
                                    "Qratio",pyrat_arr, "Qpr",pypr_arr, "g",pyasy_arr);
            }
        } else {
            res = Py_BuildValue("OOOOOOO",
                                pyext_arr, pysca_arr, pyabs_arr,pybck_arr,
                                pyrat_arr, pypr_arr, pyasy_arr);
        }
    }

    return res;
}

#define miecoatedq_docstring "MieCoatedQ(m_core, diam_core, m_shell, diam_shell, wavelength, /, nMedium=1.0, asCrossSection=False, asDict=False)\n\n\
As MieQ() but for coated particles\n\n\
Parameters\n----------\n\
m_core : scalar or array-like, complex number\n    refractive index of the particle's core\n\
diam_core : scalar, floating point number\n    the diameter of the particle's core, in nanometers\n\
m_shell : scalar or array-like, complex number\n    refractive index of the coating\n    same shape as m_core\n\
diam_shell : scalar, floating point number\n    the diameter of the particle and its coating, in nanometers\n\
wavelength : scalar or array-like, floating point number\n    the wavelength of incident light, in nanometers\n    same shape as m_core\n\
nMedium : scalar, floating point number, optional\n    the refractive index of the surrounding medium without the extinction part\n\
asCrossSection : scalar, bool, optional\n    if specified and set to True, returns the results as optical cross-sections with units of nm$^2$.\n\
asDict : scalar, bool, optional\n    if specified and set to True, returns the results as a dictionary.\n\n\
Returns\n-------\n\
qext,qsca,qabs,qback,qratio,qpr,g :\n    scalars or array-like, floating point numbers, same shape as m_core\n    Mie efficiencies as described in MieQ()\n\
qext,qsca,qabs,qback,qratio,qpr,g :\n    scalars or array-like, floating point numbers, same shape as m_core\n    Mie efficiencies as optical cross sections, if asCrossSection set to True\n\
q : dict\n    dictionary of the Mie efficiencies, if asDict is set to True\n    entries have the same shape as m_core (scalar or array-like)\n\
c : dict\n    dictionary of Mie efficiencies as optical cross sections, if asDict and asCrossSection are both set to True\n    entries have the same shape as m_core (scalar or array-like)"
PyObject* mie_art_miecoatedq(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"m_core", (char*)"diam_core", (char*)"m_shell", (char*)"diam_shell", (char*)"wavelength", (char*)"nMedium", (char*)"asCrossSection", (char*)"asDict", NULL };

    Py_complex valueNpMcore;
    Py_complex valueNpMshell;
    double valueW;
    double valueDcore;
    double valueDshell;
    double valueNmedium = 1.0;
    int valueCSS = false;
    int valueDict = false;

    PyObject* arr_ptr[1] =      { NULL };
    PyObject* array[1] =        { NULL };
    PyObject* arr_cplx_ptr[2] = { NULL, NULL };
    PyObject* array_cplx[2] =   { NULL, NULL };

    int numArrs = -1;
    int ctype = -1;
    int dtype = -1;

    if(PyArg_ParseTupleAndKeywords(args, kwds, "DdDdd|dpp", kwlist, &valueNpMcore, &valueDcore, &valueNpMshell, &valueDshell, &valueW, &valueNmedium, &valueCSS, &valueDict)) {
        numArrs = 0;
    } else {
        PyErr_Clear();
    }

    if(numArrs<0) {
        if(PyArg_ParseTupleAndKeywords(args, kwds, "OdOdO|dpp", kwlist, &arr_cplx_ptr[0], &valueDcore, &arr_cplx_ptr[1], &valueDshell, &arr_ptr[0], &valueNmedium, &valueCSS, &valueDict)) {
            if(parse_arrays(2, NPY_COMPLEX64, arr_cplx_ptr, array_cplx))
                ctype = NPY_COMPLEX64;
            if(ctype<0)
            if(parse_arrays(2, NPY_COMPLEX128, arr_cplx_ptr, array_cplx))
                ctype = NPY_COMPLEX128;
            if(ctype<0) {
                PyErr_SetString(
                    PyExc_TypeError,
                    "The arrays m_core and m_shell have to be of type float, double or complex."
                );
                return NULL;
            }
            if(parse_arrays(1, NPY_FLOAT, arr_ptr, array))
                dtype = NPY_FLOAT;
            if(dtype<0)
            if(parse_arrays(1, NPY_DOUBLE, arr_ptr, array))
                dtype = NPY_DOUBLE;
            if(dtype<0) {
                PyErr_SetString(
                    PyExc_TypeError,
                    "The wavelengths have to be an array of type float or double."
                );
                return NULL;
            }
            numArrs = 3;
        } else {
            PyErr_Clear();
        }
    }

    if(numArrs<0) {
        PyErr_SetString(
            PyExc_TypeError,
            "Arguments do not match function definition: MieCoatedQ(m_core, diam_core, m_shell, diam_shell, wavelength, /, nMedium=1.0, asCrossSection=False, asDict=False)"
        );
    }

    PyObject* res = NULL;
    if(numArrs==0) {
        std::complex<double> valueMcore = py2c_cplx(valueNpMcore) / valueNmedium;
        std::complex<double> valueMshell = py2c_cplx(valueNpMshell) / valueNmedium;
        double x = _PI_*valueDcore/valueW;
        double y = _PI_*valueDshell/valueW;
        int nmax = calc_nmax(y);
        std::complex<double> an[nmax];
        std::complex<double> bn[nmax];
        miecoated_ab(valueMcore, x, valueMshell, y, an, bn);
        MieResult mr = ab2mie(nmax, an, bn, valueW, valueDshell, valueCSS);

        if(valueDict>0) {
            if(valueCSS>0) {
                res = Py_BuildValue("{s:d,s:d,s:d,s:d,s:d,s:d,s:d}",
                                    "Cext",mr.qext, "Csca",mr.qsca, "Cabs",mr.qabs, "Cback",mr.qback,
                                    "Cratio",mr.qratio, "Cpr",mr.qpr, "g",mr.qg);
            } else {
                res = Py_BuildValue("{s:d,s:d,s:d,s:d,s:d,s:d,s:d}",
                                    "Qext",mr.qext, "Qsca",mr.qsca, "Qabs",mr.qabs, "Qback",mr.qback,
                                    "Qratio",mr.qratio, "Qpr",mr.qpr, "g",mr.qg);
            }
        } else {
            res = Py_BuildValue("ddddddd",mr.qext,mr.qsca,mr.qabs,mr.qback,mr.qratio,mr.qpr,mr.qg);
        }
    }
    if(numArrs>1) {
        int ndimMc = PyArray_NDIM((PyArrayObject*)array_cplx[0]);
        int ndimMs = PyArray_NDIM((PyArrayObject*)array_cplx[1]);
        int ndimW = PyArray_NDIM((PyArrayObject*)array[0]);
        npy_intp* shapeMc = PyArray_SHAPE((PyArrayObject*)array_cplx[0]);
        npy_intp* shapeMs = PyArray_SHAPE((PyArrayObject*)array_cplx[1]);
        npy_intp* shapeW = PyArray_SHAPE((PyArrayObject*)array[0]);
        int mw_same = (ndimMc==ndimMs && ndimMc==ndimW);
        if(mw_same) {
            for(int i=0; i<ndimMc && mw_same; i++)
                mw_same = (shapeMc[i]==shapeMs[i] && shapeMc[i]==shapeW[i]);
        }

        if(!mw_same) {
            Py_XDECREF(array_cplx[0]);
            Py_XDECREF(array_cplx[1]);
            Py_XDECREF(array[0]);
            PyErr_Format(
                PyExc_ValueError,
                "m_core, m_shell and wavelength cannot be broadcast together, found shapes %s, %s and %s.",
                shape2str(ndimMc,shapeMc), shape2str(ndimMs,shapeMs), shape2str(ndimW,shapeW)
            );
            return res;
        }

        npy_intp flatDims[1];
        flatDims[0] = PyArray_SIZE((PyArrayObject*)array_cplx[0]);
        int a_len = (int) flatDims[0];
        PyArray_Dims flatShp = { nullptr, 0 };
        flatShp.ptr = flatDims;
        flatShp.len = 1;

        std::complex<double> valuesMcore[a_len];
        std::complex<double> valuesMshell[a_len];
        double valuesW[a_len];
        if(ndimW==1) {
            py2c_cplxarr((PyArrayObject*)array_cplx[0], valuesMcore);
            py2c_cplxarr((PyArrayObject*)array_cplx[1], valuesMshell);
            py2c_dblarr( (PyArrayObject*)array[0],      valuesW);
        } else {
            py2c_cplxarr((PyArrayObject*)PyArray_Newshape((PyArrayObject*)array_cplx[0], &flatShp, NPY_CORDER), valuesMcore);
            py2c_cplxarr((PyArrayObject*)PyArray_Newshape((PyArrayObject*)array_cplx[1], &flatShp, NPY_CORDER), valuesMshell);
            py2c_dblarr( (PyArrayObject*)PyArray_Newshape((PyArrayObject*)array[0],      &flatShp, NPY_CORDER), valuesW);
        }

        double bext[a_len];
        double bsca[a_len];
        double babs[a_len];
        double bbck[a_len];
        double brat[a_len];
        double bpr[a_len];
        double bg[a_len];
        for(int i=0; i<a_len; i++) {
            valuesMcore[i]  /= valueNmedium;
            valuesMshell[i] /= valueNmedium;
            double x = _PI_*valueDcore/valuesW[i];
            double y = _PI_*valueDshell/valuesW[i];
            int nmax = calc_nmax(y);
            std::complex<double> an[nmax];
            std::complex<double> bn[nmax];
            miecoated_ab(valuesMcore[i], x, valuesMshell[i], y, an, bn);
            MieResult mr = ab2mie(nmax, an, bn, valuesW[i], valueDshell, valueCSS);
            bext[i] = mr.qext;
            bsca[i] = mr.qsca;
            babs[i] = mr.qabs;
            bbck[i] = mr.qback;
            brat[i] = mr.qratio;
            bpr[i]  = mr.qpr;
            bg[i]   = mr.qg;
        }

        PyArray_Dims outShp = { nullptr, 0 };
        outShp.ptr = shapeMc;
        outShp.len = ndimMc;
        PyObject* pyext_arr = NULL;
        PyObject* pysca_arr = NULL;
        PyObject* pyabs_arr = NULL;
        PyObject* pybck_arr = NULL;
        PyObject* pyrat_arr = NULL;
        PyObject* pypr_arr  = NULL;
        PyObject* pyasy_arr = NULL;
        if(ndimW==1) {
            pyext_arr = (PyObject*)c2py_dblarr(a_len, bext);
            pysca_arr = (PyObject*)c2py_dblarr(a_len, bsca);
            pyabs_arr = (PyObject*)c2py_dblarr(a_len, babs);
            pybck_arr = (PyObject*)c2py_dblarr(a_len, bbck);
            pyrat_arr = (PyObject*)c2py_dblarr(a_len, brat);
            pypr_arr  = (PyObject*)c2py_dblarr(a_len, bpr);
            pyasy_arr = (PyObject*)c2py_dblarr(a_len, bg);
        } else {
            pyext_arr = PyArray_Newshape(c2py_dblarr(a_len, bext), &outShp, NPY_CORDER);
            pysca_arr = PyArray_Newshape(c2py_dblarr(a_len, bsca), &outShp, NPY_CORDER);
            pyabs_arr = PyArray_Newshape(c2py_dblarr(a_len, babs), &outShp, NPY_CORDER);
            pybck_arr = PyArray_Newshape(c2py_dblarr(a_len, bbck), &outShp, NPY_CORDER);
            pyrat_arr = PyArray_Newshape(c2py_dblarr(a_len, brat), &outShp, NPY_CORDER);
            pypr_arr  = PyArray_Newshape(c2py_dblarr(a_len, bpr),  &outShp, NPY_CORDER);
            pyasy_arr = PyArray_Newshape(c2py_dblarr(a_len, bg),   &outShp, NPY_CORDER);
        }
        if(valueDict>0) {
            if(valueCSS>0) {
                res = Py_BuildValue("{s:O,s:O,s:O,s:O,s:O,s:O,s:O}",
                                    "Cext",pyext_arr, "Csca",pysca_arr, "Cabs",pyabs_arr, "Cback",pybck_arr,
                                    "Cratio",pyrat_arr, "Cpr",pypr_arr, "g",pyasy_arr);
            } else {
                res = Py_BuildValue("{s:O,s:O,s:O,s:O,s:O,s:O,s:O}",
                                    "Qext",pyext_arr, "Qsca",pysca_arr, "Qabs",pyabs_arr, "Qback",pybck_arr,
                                    "Qratio",pyrat_arr, "Qpr",pypr_arr, "g",pyasy_arr);
            }
        } else {
            res = Py_BuildValue("OOOOOOO",
                                pyext_arr, pysca_arr, pyabs_arr, pybck_arr,
                                pyrat_arr, pypr_arr, pyasy_arr);
        }
    }

    return res;
}

#define scatfunc_docstring "ScatteringFunction(m, diam, wavelength, theta, /, m_shell=m, fcoat=0.0)\n\n\
Calculates the angle-dependent scattering intensities for parallel, perpendicular polarized and unpolarized light.\n\n\
Parameters\n----------\n\
m : scalar, complex number\n    complex refractive index of the particle (its core, when a coating is given)\n\
diam : scalar, floating point number\n    the diameter of the particle (its core) in nm\n\
wavelength : scalar, floating point number\n    the wavelength of the incident light in nm\n\
theta : array-like, 1dimensional, floating point numbers\n    array of the scattering angles in radians\n\
m_shell : scalar, complex number, optional\n    complex refractive index of the particles coating, defaults to the core's refractive index\n\
fcoat : scalar, floating point number, optional\n    coating fraction as ratio of diameters, default 0.0\n\n\
Results\n-------\n\
sl : array-like, 1dimensional, floating point numbers\n    scattering intensities of perpendicular polarized light\n\
sr : array-like, 1dimensional, floating point numbers\n    scattering intensities of parallel polarized light\n\
su : array-like, 1dimensional, floating point numbers\n    scattering intensities of unpolarized light"
void scattering_function(int anbn_len, std::complex<double> *an, std::complex<double> *bn, int nang, double *theta, int nmax, double *pin, double *taun, double *sl, double *sr, double *su) {
    int a,n,t;
    for(a=0; a<nang; a++) {
        std::complex<double> S1(0.0,0.0);
        std::complex<double> S2(0.0,0.0);
        t = a*nmax-1;
        for(n=anbn_len; n>0; n--) {
            double n2 = (2.0+1.0/n)/(n+1.0);
            std::complex<double> s1 = an[n-1]*pin[t+n] + bn[n-1]*taun[t+n];
            std::complex<double> s2 = an[n-1]*taun[t+n] + bn[n-1]*pin[t+n];
            S1 = S1 + n2*s1;
            S2 = S2 + n2*s2;
        }
        sl[a] = S1.real()*S1.real() + S1.imag()*S1.imag();
        sr[a] = S2.real()*S2.real() + S2.imag()*S2.imag();
        su[a] = 0.5*(sl[a]+sr[a]);
    }
}
PyObject* mie_art_scatfunc(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"m", (char*)"diam", (char*)"wavelength", (char*)"theta", (char*)"m_shell", (char*)"fcoat", NULL };

    Py_complex valueNpMcore;
    Py_complex valueNpMshell = nanPyCplx();
    double valueD;
    double valueW;
    double valueFcoat = 0.0;
    PyObject *th_ptr[] = { NULL };
    PyObject *th_arr[] = { NULL };
    int dtype_th = -1;
    if(PyArg_ParseTupleAndKeywords(args, kwds, "DddO|Dd", kwlist, &valueNpMcore, &valueD, &valueW, &th_ptr, &valueNpMshell, &valueFcoat)) {
        {
            if(parse_arrays(1, NPY_FLOAT, th_ptr, th_arr)) dtype_th = NPY_FLOAT;
        }
        if(dtype_th<0) {
            if(parse_arrays(1, NPY_DOUBLE, th_ptr, th_arr)) dtype_th = NPY_DOUBLE;
        }
    } else {
        PyErr_Clear();
    }

    if(dtype_th<0) {
        PyErr_SetString(
            PyExc_TypeError,
            "The arguments dtypes do not match, expected m and m_shell to be complex, dia, wavelength and fcoat to be float or double, theta to be of the type float[] or double[]"
        );
        Py_XDECREF(th_arr[0]);
        return NULL;
    }

    int ndimH = PyArray_NDIM((PyArrayObject *)th_arr[0]);
    if(ndimH!=1) {
        PyErr_SetString(
            PyExc_IndexError,
            "Theta has to be 1dimensional"
        );
        Py_XDECREF(th_arr[0]);
        return NULL;
    }
    int nang = PyArray_SIZE((PyArrayObject *)th_arr[0]);

    std::complex<double> m_core  = py2c_cplx(valueNpMcore);
    std::complex<double> m_shell = py2c_cplx(valueNpMshell);
    if(std::isnan(valueNpMshell.real) || std::isnan(valueNpMshell.imag)) {
        m_shell = py2c_cplx(valueNpMcore);
    }
    double xval = valueD*_PI_/valueW;
    double yval = valueD*(1.0+valueFcoat)*_PI_/valueW;
    int nmax = calc_nmax(yval);
    std::complex<double> an[nmax];
    std::complex<double> bn[nmax];

    int is_coated = (valueFcoat>EPS && (m_core!=m_shell));

    if (is_coated) {
        miecoated_ab(m_core, xval, m_shell, yval, an, bn);
    } else {
        mie_ab(m_core, yval, an, bn);
    }

    double theta[nang];
    py2c_dblarr((PyArrayObject *)th_arr[0], theta);

    int pitau_len = nang*nmax;
    double *pin = new double[pitau_len];
    double *taun = new double[pitau_len];
    mie_pitau(nang, theta, nmax, pin, taun);

    double outSL[nang];
    double outSR[nang];
    double outSU[nang];
    scattering_function(nmax, an, bn, nang, theta, nmax, pin, taun, outSL, outSR, outSU);

    PyObject *res = Py_BuildValue("OOO",
        c2py_dblarr(nang, outSL),
        c2py_dblarr(nang, outSR),
        c2py_dblarr(nang, outSU)
        );
    Py_DECREF(th_arr[0]);
    return res;
}



// **** Mie for particle size distributions

#define clnd_docstring "createLogNormalDistribution(mean_diam, stdev_diam, /, fcoat=0.0, res=0.0, norm2core=False, norm2volume=True)\n\n\
Calculates the parameters regarding the log-normal particle size distribution needed internally by Size_Distribution_Optics and Size_Distribution_Phase_Function\n\n\
Parameters\n----------\n\
mean_diam : scalar, floating point number\n    the median count diameter of the particles in nanometers\n\
stdev_diam : scalar, floating point number\n    the geometric standard deviation of the particle size distribution\n\
fcoat : scalar, floating point number, optional\n    the coating fraction, default 0.0\n\
res : scalar, floating point number, optional\n    resolution of the particle size distribution, default 1.0\n\
dens : scalar, floating point number, optional\n    the density, default 1.0\n\
norm2core : scalar, bool, optional\n    normalize the pdf to the particles' core, default False\n\
norm2volume: scalar, bool, optional\n    normalize the pdf to the particles' volume, default True\n\n\
Returns\n-------\n\
x_range : array-like, 1dimensional, floating point numbers\n    diameters of the particle cores\n\
y_range : array-like, 1dimensional, floating point numbers\n    diameters of the particles including the coating\n\
crossArea : array-like, 1dimensional, floating point numbers\n    scaled particle cross section areas\n\
normWeight : scalar, floating point number\n    normalization weight"
int calc_diam_count(double mean_diam, double std_diam, double res) {
    double dlogd = std::min(res*1.0, std::log10(std_diam)*0.25);
    int limit = (int)(3.0*std::log(std_diam)/dlogd);
    return 2*limit;
}
void LogNormal_pdf_dexp(int arrlen, double diams[], double mean_diam, double std_diam,
        double /*out*/ pdf[], double /*out*/ dexp[]) {
    double loggsd =   std::log10(std_diam);
    double lgg2 = 2.0*loggsd*loggsd;
    double ln10 = std::log(10.0);
    double constant = loggsd * std::sqrt(2.0*_PI_);
    int idx;
    for(idx=0; idx<arrlen; idx++) {
        double x =   diams[idx] / mean_diam;
        double lnx = std::log(x);
        double lgx = lnx / ln10;
        pdf[idx] =  std::exp(-lgx*lgx/lgg2) / constant;
        dexp[idx] = std::exp(-lnx*lnx/lgg2) / (diams[idx]*constant);
    }
}
void createLogNormalDistribution(double d_gn, double sigma_g, double fcoat, double res, double dens, int norm2core, int norm2volume, double *x_range, double *y_range, double *pdf, double *crossArea, double *normWeight) {
    //Helper function: createLogNormalDistribution
    //Input
    //  d_gn, sigma_g = cound median diameter, geometric standart deviation
    //  fcoat = coating fraction for coated particles
    //  res = resolution of the particle size distribution
    //  dens = particle density in g/cm3
    int dcount = calc_diam_count(d_gn, sigma_g, res);
    int limit = dcount/2;
    double dlogd = std::min(res, std::log10(sigma_g)*0.25);
    double ln10 = std::log(10.0);
    double cfp1 = 1.0+fcoat;
    int idx;

    for(idx=0; idx<dcount; idx++) {
        double dx = (idx-limit)*dlogd;
        x_range[idx] = d_gn * std::exp(ln10*dx);
        y_range[idx] = cfp1*x_range[idx];
    }

    double dexp[dcount];
    LogNormal_pdf_dexp(dcount, x_range, d_gn, sigma_g, pdf, dexp);

//    double dDp[dcount];
//    for(idx=1; idx<dcount-1; idx++) {
//        dDp[idx] = 0.5*(x_range[idx+1]-x_range[idx-1]);
//    }
//    dDp[0] = x_range[1] - x_range[0];
//    dDp[dcount-1] = x_range[dcount-1] - x_range[dcount-2];

    double vol_tot = 0.0;
    if(norm2core>0) {
        for(idx=0; idx<dcount; idx++) {
            vol_tot += x_range[idx]*x_range[idx]*x_range[idx]*pdf[idx];
        }
    } else {
        for(idx=0; idx<dcount; idx++) {
            vol_tot += y_range[idx]*y_range[idx]*y_range[idx]*pdf[idx];
        }
    }
    vol_tot *= _PI_/6.0 * dlogd;

    for(idx=0; idx<dcount; idx++) {
        double y_area = 0.25*_PI_*y_range[idx]*y_range[idx];
        crossArea[idx] = y_area*pdf[idx]*dlogd;
    }

    if(norm2volume>0) {
        *normWeight = 1.0/vol_tot * 1000.0/dens;
    } else {
        *normWeight = 1.0e-6;
    }
}
PyObject* mie_art_createLgNormDist(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"mean_diam", (char*)"stdev_diam", (char*)"fcoat", (char*)"res", (char*)"norm2core", (char*)"norm2volume", NULL };

    double valueMu;
    double valueStd;
    double valueFcoat = 0.0;
    double valueRes =   1.0;
    int valueN2core =   false;
    int valueN2vol =    true;
    if(PyArg_ParseTupleAndKeywords(args, kwds, "dd|ddpp", kwlist, &valueMu, &valueStd, &valueFcoat, &valueRes, &valueN2core, &valueN2vol)) {
    } else {
        PyErr_SetString(
            PyExc_TypeError,
            "The arguments dtypes do not match, expected (float,float[,float,float,bool,bool])"
        );
        return NULL;
    }

    int dcount = calc_diam_count(valueMu, valueStd, valueRes);
    double core_diams[dcount];
    double shell_diams[dcount];
    double pdf[dcount];
    double crossArea[dcount];
    double normWeight;
    double density = 1.0;
    createLogNormalDistribution(valueMu, valueStd, valueFcoat, valueRes, density, valueN2core, valueN2vol, core_diams, shell_diams, pdf, crossArea, &normWeight);

    PyObject *res = Py_BuildValue("OOOOd",
                                  c2py_dblarr(dcount, core_diams),
                                  c2py_dblarr(dcount, shell_diams),
                                  c2py_dblarr(dcount, pdf),
                                  c2py_dblarr(dcount, crossArea),
                                  normWeight);
    return res;
}

#define cbs_docstring "calcBackscattering(x, an, bn, theta, dtheta, scatwts, pin, taun)\n\n\
Calculates the scattering angle weighted Mie backscattering efficiency.\n\n\
Parameters\n----------\n\
x : scalar, floating point value\n    size parameter of the whole particle\n\
an : array-like, 1dimensional, complex numbers\n    external field coefficients $a_n$\n\
bn : array-like, 1dimensional, complex numbers\n    external field coefficients $b_n$\n\
theta : array-like, 1dimensional, floating point numbers\n    all angels $\\theta$, for which the scattering function is calculated\n\
dtheta : array-like, 1dimensional, floating point numbers\n    angle step size for each angle $\\theta$\n\
scatwgts : array-like, 1dimensional, floating point numbers\n    angel dependent scattering weights\n\
pin : array-like, 2dimensional, floating point numbers\n    field coefficients $\\pi_n$ for every angle and every corresponding external field coefficient $a_n$\n\
taun : array-like, 2dimensional, floating point numbers\n    field coefficients $\\tau_n$ for every angle and every corresponding external field coefficient $a_n$\n\n\
Returns\n-------\n\
s : scalar, floating point number\n    backscatter coefficient\n    It is not the same as the provided one through MieQ() or ab2mie()!"
int calc_angles_count(double angres) {
    return 1 + (int) (180.0 / angres + EPS);
}
void scattering_weights(double angres, double *theta, double *dtheta, double *scatwgts) {
    int nang = calc_angles_count(angres);
    double ares = angres*_PI_/180.0; // convert from degrees to radians
    int idx;
    for(idx=0; idx<nang; idx++) {
        theta[idx]  = idx*ares;
        dtheta[idx] = (idx==0 || idx==nang-1) ? 0.5*ares : ares;
        double bsflag = 2*idx<nang ? 0.0 : 2*idx>nang ? 1.0 : 0.5;
        double wgt = std::sin(theta[idx]);
        scatwgts[idx] = wgt*bsflag;
    }
}
double calcBackscattering(double x, int anbn_len, std::complex<double> *an, std::complex<double> *bn, int nang, double *theta, double *dtheta, double *scatwgts, int nmax, double *pin, double *taun) {
    //an,bn are complex[anbn_len]
    //theta,dtheta,scatwgts are double[nang]
    //pin,taun are double[nang][nmax] flattened into double[nang*nmax]
    double ssq = 0.0;
    int a,n,t;
    for(a=0; a<nang; a++) {
        std::complex<double> S1(0.0,0.0);
        std::complex<double> S2(0.0,0.0);
        t = a*nmax;
        for(n=anbn_len-1; n>=0; n--) {
            double n2 = (2.0+1.0/(n+1))/(n+2.0);
            std::complex<double> s1 = an[n]*pin[t+n] + bn[n]*taun[t+n];
            std::complex<double> s2 = an[n]*taun[t+n] + bn[n]*pin[t+n];
            S1 = S1 + n2*s1;
            S2 = S2 + n2*s2;
        }
        double S1mag2 = S1.real()*S1.real() + S1.imag()*S1.imag();
        double S2mag2 = S2.real()*S2.real() + S2.imag()*S2.imag();
        ssq += (S1mag2+S2mag2) * dtheta[a] * scatwgts[a];
    }
    return ssq/(x*x);
}
PyObject* mie_art_calcBackScat(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"x", (char*)"an", (char*)"bn", (char*)"theta", (char*)"dtheta", (char*)"scatwgts", (char*)"pin", (char*)"taun", NULL };

    double valueX;
    PyObject *ab_ptr[] = { NULL, NULL };
    PyObject *th_ptr[] = { NULL, NULL, NULL };
    PyObject *pt_ptr[] = { NULL, NULL };
    PyObject *ab_array[] = { NULL, NULL };
    PyObject *th_array[] = { NULL, NULL, NULL };
    PyObject *pt_array[] = { NULL, NULL };
    int dtype_ab = -1;
    int dtype_th = -1;
    int dtype_pt = -1;
    if(PyArg_ParseTupleAndKeywords(args, kwds, "dOOOOOOO", kwlist, &valueX, &ab_ptr[0], &ab_ptr[1], &th_ptr[0], &th_ptr[1], &th_ptr[2], &pt_ptr[0], &pt_ptr[1])) {
        {
            if(parse_arrays(2, NPY_COMPLEX64, ab_ptr, ab_array)) dtype_ab = NPY_COMPLEX64;
        }
        if(dtype_ab<0) {
            if(parse_arrays(2, NPY_COMPLEX128, ab_ptr, ab_array)) dtype_ab = NPY_COMPLEX128;
        }
        {
            if(parse_arrays(3, NPY_FLOAT, th_ptr, th_array)) dtype_th = NPY_FLOAT;
        }
        if(dtype_th<0) {
            if(parse_arrays(3, NPY_DOUBLE, th_ptr, th_array)) dtype_th = NPY_DOUBLE;
        }
        {
            if(parse_arrays(2, NPY_FLOAT, pt_ptr, pt_array)) dtype_pt = NPY_FLOAT;
        }
        if(dtype_pt<0) {
            if(parse_arrays(2, NPY_DOUBLE, pt_ptr, pt_array)) dtype_pt = NPY_DOUBLE;
        }
    } else {
        PyErr_Clear();
    }
    if(dtype_ab<0 || dtype_th<0 || dtype_pt<0) {
        PyErr_SetString(
            PyExc_TypeError,
            "The arguments dtypes do not match, expected x to be float or double, an and bn of same type complex[], theta and dtheta and scatwgts of same type float[] or double[], pin and taun of same type float[][] or double[][]"
        );
        Py_XDECREF(ab_array[0]); Py_XDECREF(ab_array[1]);
        Py_XDECREF(th_array[0]); Py_XDECREF(th_array[1]); Py_XDECREF(th_array[2]);
        Py_XDECREF(pt_array[0]); Py_XDECREF(pt_array[1]);
        return NULL;
    }

    int ndimA = PyArray_NDIM((PyArrayObject *)ab_array[0]);
    int ndimB = PyArray_NDIM((PyArrayObject *)ab_array[1]);
    int sizeA = PyArray_SIZE((PyArrayObject *)ab_array[0]);
    int sizeB = PyArray_SIZE((PyArrayObject *)ab_array[1]);
    int nmax = sizeA;
    if(ndimA!=1 || ndimB!=1 || sizeA!=sizeB) {
        PyErr_SetString(
            PyExc_IndexError,
            "The arrays an and bn have to be both 1dimensional and they have be the same length"
        );
        Py_XDECREF(ab_array[0]); Py_XDECREF(ab_array[1]);
        Py_XDECREF(th_array[0]); Py_XDECREF(th_array[1]); Py_XDECREF(th_array[2]);
        Py_XDECREF(pt_array[0]); Py_XDECREF(pt_array[1]);
        return NULL;
    }
    int ndimH = PyArray_NDIM((PyArrayObject *)th_array[0]);
    int ndimD = PyArray_NDIM((PyArrayObject *)th_array[1]);
    int ndimS = PyArray_NDIM((PyArrayObject *)th_array[2]);
    int sizeH = PyArray_SIZE((PyArrayObject *)th_array[0]);
    int sizeD = PyArray_SIZE((PyArrayObject *)th_array[1]);
    int sizeS = PyArray_SIZE((PyArrayObject *)th_array[2]);
    int nang = sizeH;
    if(ndimH!=1 || ndimD!=1 || ndimS!=1 || sizeH!=sizeD || sizeH!=sizeS) {
        PyErr_SetString(
            PyExc_IndexError,
            "The arrays theta, dtheta and scatwgts have to be all 1dimensional and they have to be the same length"
        );
        Py_XDECREF(ab_array[0]); Py_XDECREF(ab_array[1]);
        Py_XDECREF(th_array[0]); Py_XDECREF(th_array[1]); Py_XDECREF(th_array[2]);
        Py_XDECREF(pt_array[0]); Py_XDECREF(pt_array[1]);
        return NULL;
    }
    int ndimP = PyArray_NDIM((PyArrayObject *)pt_array[0]);
    int ndimT = PyArray_NDIM((PyArrayObject *)pt_array[1]);
    npy_intp *shapeP = PyArray_DIMS((PyArrayObject *)pt_array[0]);
    npy_intp *shapeT = PyArray_DIMS((PyArrayObject *)pt_array[1]);
    if (ndimP!=2 || ndimT!=2) {
        PyErr_SetString(
            PyExc_IndexError,
            "Both arrays pin and taun have to be two-dimensional"
        );
        Py_XDECREF(ab_array[0]); Py_XDECREF(ab_array[1]);
        Py_XDECREF(th_array[0]); Py_XDECREF(th_array[1]); Py_XDECREF(th_array[2]);
        Py_XDECREF(pt_array[0]); Py_XDECREF(pt_array[1]);
        return NULL;
    }
    if (nang!=(int)shapeP[0] || nang!=(int)shapeT[0] || nmax>shapeP[1] || shapeP[1]!=shapeT[1]) {
        PyErr_SetString(
            PyExc_IndexError,
            "Both arrays pin and taun have to be of the same shape (len(theta),>=len(an))"
        );
        Py_XDECREF(ab_array[0]); Py_XDECREF(ab_array[1]);
        Py_XDECREF(th_array[0]); Py_XDECREF(th_array[1]); Py_XDECREF(th_array[2]);
        Py_XDECREF(pt_array[0]); Py_XDECREF(pt_array[1]);
        return NULL;
    }

    std::complex<double> an[nmax];
    std::complex<double> bn[nmax];
    py2c_cplxarr((PyArrayObject *)ab_array[0], an);
    py2c_cplxarr((PyArrayObject *)ab_array[1], bn);
    double theta[nang];
    double dtheta[nang];
    double scatwgts[nang];
    py2c_dblarr((PyArrayObject *)th_array[0], theta);
    py2c_dblarr((PyArrayObject *)th_array[1], dtheta);
    py2c_dblarr((PyArrayObject *)th_array[2], scatwgts);
    int pitau_len = nang*nmax;
    double *pin = new double[pitau_len];
    double *taun = new double[pitau_len];
    py2c_dblarr((PyArrayObject *)pt_array[0], pin);
    py2c_dblarr((PyArrayObject *)pt_array[1], taun);

    double backscat = calcBackscattering(valueX, nmax, an, bn, nang, theta, dtheta, scatwgts, (int)shapeP[1], pin, taun);

    PyObject *res = Py_BuildValue("d", backscat);
    Py_DECREF(ab_array[0]);
    Py_DECREF(ab_array[1]);
    Py_DECREF(th_array[0]);
    Py_DECREF(th_array[1]);
    Py_DECREF(th_array[2]);
    Py_DECREF(pt_array[0]);
    Py_DECREF(pt_array[1]);
    delete[] pin;
    delete[] taun;
    return res;
}

struct Mie_tots {
    double bext;
    double bsca;
    double babs;
    double bback;
    double bawbsc;
    double bssa;
    double bratio;
    double basym;
//    int arr_len;
//    double *ext_arr; //arrays have to be deleted by the caller of size_distribution_optics
//    double *sca_arr;
//    double *abs_arr;
//    double *bck_arr;
//    double *g_arr;
};

//, nephscats=False, nephsensfile=\"\", cut=None, vectorout=False)\n\n
#define sdo_docstring "Size_Distribution_Optics(m, sizepar1, sizepar2, wavelength, /, nMedium=1.0, fcoat=0.0, mc=mp, density=1.0, resolution=10, effcore=True, normalized=True)\n\n\
Parameters\n----------\n\
m : scalar, complex number\n    complex refractive index of the particle (core)\n\
sizepar1 : scalar or 1dimensional array, floating point number(s)\n    mean count diameter (if scalar) or particle sizes (if array) in nanometers\n\
sizepar2 : scalar or 1dimensional array, floating point number(s)\n    geometric std. dev. (if scalar) or dNdlogD in cm$^{-3}$ (if array)\n\
wavelength : scalar, floating point number\n    wavelength of the incident light in nanometers\n\
nMedium : scalar, floating point number, optional\n    refractive index without extinction for the surrounding medium, default 1.0\n\
fcoat : scalar, floating point number, optional\n    coating fraction, ratio of shell thickness to core radius, default 0.0\n\
mc : scalar, complex number, optional\n    complex refractive index of the coating, default m\n\
density : scalar, floating point number, optional\n    particle density in g/cm$^3$, default 1.0\n\
resolution : scalar, floating point number, optional\n    number of bins per power of magnitude within the particle size distribution, default 10\n    ignored when sizepar1 & sizepar2 array-like\n\
effcore : boolean/logical, optional\n    calculates cross-section as nm$^2$/(g of core), default True\n\
normalized : normalized to nm$^2$/g particles, default True\n    setting to False works only with d & dNdlogD (array-like sizeparX)\n\n\
Returns\n-------\n\
mie_tots : dictionary\n    contains the Mie efficiencies of a particle size distribution \"Extinction\", \"Scattering\", \"Absorption\", the \"Asymmetry\" parameter and the \"Backscattering\" efficiency specifically calculated from a weighted average over all scattering angles\n\n\
Important Note\n--------------\n\
The size distribution is currently hardcoded to be log-normal. Other distributions may follow in future versions.\n\
1dimensional arguments for sizepar1 and sizepar2 are not implemented yet, they will come in version 0.2.0"
void size_distribution_optics(std::complex<double> m_core, double mean_diam, double stdev_diam, double wavelength, std::complex<double> m_shell, double fcoating, double resolution, double dens, int effcore, int norm2vol, int debug, Mie_tots *mie_tots) {
    if(debug) {
        PySys_WriteStdout("[DEBUG] SDO-Input: m_core=%.7f+i*%14.7e  m_shell=%.7f+i*%14.7e  psd=%.1f+/-%4f  fcoat=%.4f  wl=%14.7e\n",
            m_core.real(),m_core.imag(),m_shell.real(),m_shell.imag(),mean_diam,stdev_diam,fcoating,wavelength);
        PySys_WriteStdout("[DEBUG]            resolution=%.7f  density=%.7f  effcore=%s  norm2vol=%s\n",
            resolution,dens,effcore?"true":"false",norm2vol?"true":"false");
    }
    double res = 1.0/resolution;
    int dcount = calc_diam_count(mean_diam, stdev_diam, res);
    double core_diams[dcount];
    double shell_diams[dcount];
    double pdf[dcount];
    double crossArea[dcount];
    double normWeight;
    createLogNormalDistribution(mean_diam, stdev_diam, fcoating, res, dens, effcore, norm2vol, core_diams, shell_diams, pdf, crossArea, &normWeight);
    double max_shell_diam = 0.0;
    int idx;
    for(idx=0; idx<dcount; idx++) {
        if(max_shell_diam < shell_diams[idx])
            max_shell_diam = shell_diams[idx];
    }

    double angres = 0.25; //degrees
    int nang = calc_angles_count(angres);
    double theta[nang];
    double dtheta[nang];
    double scatwgts[nang];
    scattering_weights(angres, theta, dtheta, scatwgts);

    double maxy = _PI_*max_shell_diam/wavelength;
    int nmax = calc_nmax(maxy);
    int arr_len = nang*nmax;
    double *pin = new double[arr_len];
    double *taun = new double[arr_len];
    mie_pitau(nang, theta, nmax, pin, taun);
    std::complex<double> *an = new std::complex<double>[nmax];
    std::complex<double> *bn = new std::complex<double>[nmax];

    int is_coated = (fcoating>EPS) && (m_core!=m_shell);

    mie_tots->bext = 0.0;
    mie_tots->bsca = 0.0;
    mie_tots->babs = 0.0;
    mie_tots->bback = 0.0;
    mie_tots->bssa = 0.0;
    mie_tots->basym = 0.0;
    mie_tots->bratio = 0.0;
//    mie_tots->arr_len = dcount;
//    Mie_tots mie_tots = {
//        0.0,
//        0.0,
//        0.0,
//        0.0,
//        0.0,
//        0.0,
//        0
////        new double[dcount],
////        new double[dcount],
////        new double[dcount],
////        new double[dcount],
////        new double[dcount]
//    };

    for(idx=0; idx<dcount; idx++) {
        try {
            double xval = _PI_*core_diams[idx]/wavelength;
            double yval = _PI_*shell_diams[idx]/wavelength;
            int nmax2 = calc_nmax(yval);
            if (is_coated) {
                miecoated_ab(m_core, xval, m_shell, yval, an, bn);
            } else {
                mie_ab(m_core, yval, an, bn);
            }

            MieResult one_result = ab2mie(nmax2, an, bn, wavelength, shell_diams[idx], effcore);
            double backscat = calcBackscattering(yval, nmax2, an, bn, nang, theta, dtheta, scatwgts, nmax, pin, taun);
            if(debug) {
                PySys_WriteStdout("[DEBUG]    (cdia=%.2f) -> one_res{ qext=%.6f, qsca=%.6f, qabs=%.6f, qratio=%.6f, qg=%.6f, ... } + awbsc=%.6e\n",
                                  core_diams[idx], one_result.qext,one_result.qsca,one_result.qabs,one_result.qratio,one_result.qg,backscat);
            }
    //        mie_tots.ext_arr[idx] = one_result.qext;
    //        mie_tots.sca_arr[idx] = one_result.qsca;
    //        mie_tots.abs_arr[idx] = one_result.qabs;
    //        mie_tots.bck_arr[idx] = backscat;
    //        mie_tots.g_arr[idx] = one_result.qg;

            mie_tots->bext   += one_result.qext * crossArea[idx];
            mie_tots->bsca   += one_result.qsca * crossArea[idx];
            mie_tots->babs   += one_result.qabs * crossArea[idx];
            mie_tots->bback  += one_result.qback * crossArea[idx];
            mie_tots->bawbsc += backscat * crossArea[idx];
            mie_tots->basym  += one_result.qg * one_result.qsca * crossArea[idx];
        } catch(const std::exception& e) {
            PySys_WriteStdout("[exception] %s\n", e.what());
        }
    }
    if(debug) {
        PySys_WriteStdout("[DEBUG]    ext=%.6e, sca=%.6e, abs=%.6e, asy=%.6e, normWeight=%.6e\n",
                          mie_tots->bext, mie_tots->bsca, mie_tots->babs, mie_tots->basym, normWeight);
    }
//    mie_tots->arr_len = dcount;
    mie_tots->basym  /= mie_tots->bsca;
    mie_tots->bratio  = mie_tots->bback / mie_tots->bsca;
    mie_tots->bssa    = mie_tots->bsca / mie_tots->bext;
    mie_tots->bext   *= normWeight;
    mie_tots->bsca   *= normWeight;
    mie_tots->babs   *= normWeight;
    mie_tots->bback  *= normWeight;
    mie_tots->bawbsc *= normWeight;

    delete[] pin;
    delete[] taun;
    delete[] an;
    delete[] bn;
}
PyObject* mie_art_sdo(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"m", (char*)"sizepar1", (char*)"sizepar2", (char*)"wavelength", (char*)"nMedium", (char*)"fcoat", (char*)"mc", (char*)"density", (char*)"resolution", (char*)"effcore", (char*)"normalized", (char*)"debug", NULL };

    Py_complex valueNpMcore;
    Py_complex valueNpMshell = nanPyCplx();
    double valueDmu;
    double valueDstd;
    double valueW;
    double valueNmedium;
    double valueFcoat;
    double valueDens = 1.0;
    double valueRes = 10.0;
    int valueN2core = true;
    int valueAsCrossSec = true;
    int valueDebug = false;
    Mie_tots *mie_tots = new Mie_tots();
//    int array_sizepar = 0;
    if(PyArg_ParseTupleAndKeywords(args, kwds, "Dddd|ddDddppp", kwlist, &valueNpMcore, &valueDmu, &valueDstd, &valueW, &valueNmedium, &valueFcoat, &valueNpMshell, &valueDens, &valueRes, &valueN2core, &valueAsCrossSec, &valueDebug)) {
        std::complex<double> valueMcore  = py2c_cplx(valueNpMcore);
        std::complex<double> valueMshell = py2c_cplx(valueNpMshell);
        if(std::isnan(valueNpMshell.real) || std::isnan(valueNpMshell.imag)) {
            valueMshell = py2c_cplx(valueNpMcore);
        }
        size_distribution_optics(valueMcore, valueDmu, valueDstd, valueW, valueMshell, valueFcoat, valueRes, valueDens, valueN2core, valueAsCrossSec, valueDebug, mie_tots);
    } else {
//        array_sizepar = 1;
//        PyErr_Clear();
    }

//    if(array_sizepar) {
//        PyObject *arr_ptr[] = { NULL, NULL };
//        PyObject *array[] =   { NULL, NULL };
//        int dtype = -1;
//        if(PyArg_ParseTupleAndKeywords(args, kwds, "DOOd|ddDddpp", kwlist, &valueNpMcore, &arr_ptr[0], &arr_ptr[1], &valueW, &valueNmedium, &valueFcoat, &valueNpMshell, &valueDens, &valueRes, &valueN2core, &valueAsCrossSec)) {
//            {
//                if(parse_arrays(2, NPY_FLOAT, arr_ptr, array)) dtype = NPY_FLOAT;
//            }
//            if(dtype<0) {
//                if(parse_arrays(2, NPY_DOUBLE, arr_ptr, array)) dtype = NPY_DOUBLE;
//            }
//        } else {
//            PyErr_Clear();
//        }
//
//        int ndim1 = PyArray_NDIM((PyArrayObject *)array[0]);
//        int ndim2 = PyArray_NDIM((PyArrayObject *)array[1]);
//        if(ndim1!=1 || ndim2!=1) {
//            PyErr_SetString(
//                PyExc_TypeError,
//                "sizepar1 and sizepar2 have to be both 1dimensional arrays of type float[] or double[]"
//            );
//            Py_XDECREF(array[0]);
//            Py_XDECREF(array[1]);
//            return NULL;
//        }
//        int size1 = PyArray_SIZE((PyArrayObject *)array[0]);
//        int size2 = PyArray_SIZE((PyArrayObject *)array[1]);
//        if(size1!=size2) {
//            PyErr_SetString(
//                PyExc_IndexError,
//                "sizepar1 and sizepar2 have to be arrays of the same length"
//            );
//            Py_XDECREF(array[0]);
//            Py_XDECREF(array[1]);
//            return NULL;
//        }
//
////        std::complex<double> valueMcore  = py2c_cplx(valueNpMcore);
////        std::complex<double> valueMshell = py2c_cplx(valueNpMshell);
////        if(std::isnan(valueNpMshell.real) || std::isnan(valueNpMshell.imag)) {
////            valueMshell = py2c_cplx(valueNpMcore);
////        }
//
//        PyErr_SetString(
//            PyExc_NotImplementedError,
//            "array-like input for sizepar1 and sizepar2 not implemented yet."
//        );
//        Py_XDECREF(array[0]);
//        Py_XDECREF(array[1]);
//        return NULL;
//    }

//    PyObject *res = Py_BuildValue("{s:d,s:d,s:d,s:d,s:d,s:d,s:O,s:O,s:O,s:O,s:O}",
//        "Extinction", mie_tots.bext,
//        "Scattering", mie_tots.bsca,
//        "Absorption", mie_tots.babs,
//        "Backscattering", mie_tots.bback,
//        "SSA", mie_tots.bssa,
//        "Asymmetry", mie_tots.basym,
//        "Extinction Coefficients", c2py_dblarr(mie_tots.arr_len, mie_tots.ext_arr),
//        "Scattering Coefficients", c2py_dblarr(mie_tots.arr_len, mie_tots.sca_arr),
//        "Absorption Coefficients", c2py_dblarr(mie_tots.arr_len, mie_tots.abs_arr),
//        "Backscattering Coefficients", c2py_dblarr(mie_tots.arr_len, mie_tots.bck_arr),
//        "Asymmetry Coefficients", c2py_dblarr(mie_tots.arr_len, mie_tots.g_arr)
//    );
    PyObject *res = Py_BuildValue("{s:d,s:d,s:d,s:d,s:d,s:d,s:d,s:d}",
        "Extinction", 0.0+mie_tots->bext,
        "Scattering", 0.0+mie_tots->bsca,
        "Absorption", 0.0+mie_tots->babs,
        "Backscattering", 0.0+mie_tots->bback,
        "AngWgtBackscat", 0.0+mie_tots->bawbsc,
        "SSA", 0.0+mie_tots->bssa,
        "BackscatterRatio", 0.0+mie_tots->bratio,
        "Asymmetry", 0.0+mie_tots->basym
    );

//    delete[] mie_tots.ext_arr;
//    delete[] mie_tots.sca_arr;
//    delete[] mie_tots.abs_arr;
//    delete[] mie_tots.bck_arr;
//    delete[] mie_tots.g_arr;
    delete mie_tots;
    return res;
}

#define sdpf_docstring "Size_Distribution_Phase_Function(m, sizepar1, sizepar2, wavelength, /, nMedium=1.0, fcoat=0.0, mc=mp, density=1.0, resolution=10, effcore=True, normalized=False)\n\n\
Computes the scattering phase function for a log-normal particle size distribution.\n\n\
Parameters\n----------\n\
m : scalar, complex number\n    complex refractive index of the particle (core)\n\
sizepar1 : scalar or 1dimensional array, floating point number(s)\n    mean count diameter (if scalar) or particle sizes (if array) in nanometers\n\
sizepar2 : scalar or 1dimensional array, floating point number(s)\n    geometric std. dev. (if scalar) or dNdlogD in cm$^{-3}$ (if array)\n\
wavelength : scalar, floating point number\n    wavelength of the incident light in nanometers\n\
nMedium : scalar, floating point number, optional\n    refractive index without extinction for the surrounding medium, default 1.0\n\
fcoat : scalar, floating point number, optional\n    coating fraction, ratio of shell thickness to core radius, default 0.0\n\
mc : scalar, complex number, optional\n    complex refractive index of the coating, default m\n\
density : scalar, floating point number, optional\n    particle density in g/cm$^3$, default 1.0\n\
resolution : scalar, floating point number, optional\n    number of bins per power of magnitude within the particle size distribution, default 10\n    ignored when sizepar1 & sizepar2 array-like\n\
effcore : boolean/logical, optional\n    calculates cross-section as nm$^2$/(g of core), default True\n\
normalized : normalized to nm$^2$/g particles, default True\n    setting to False works only with d & dNdlogD (array-like sizeparX)\n\n\
Returns\n-------\n\
theta : array-like, 1dimensional, floating point numbers\n    scattering angles in radians\n\
sl : array-like, 1dimensional, floating point numbers\n    scattering intensities of perpendicular polarized light\n\
sr : array-like, 1dimensional, floating point numbers\n    scattering intensities of parallel polarized light\n\
su : array-like, 1dimensional, floating point numbers\n    scattering intensities of unpolarized light\n\n\
Important Note\n--------------\n\
The size distribution is currently hardcoded to be log-normal. Other distributions may follow in future versions.\n\
1dimensional arguments for sizepar1 and sizepar2 are not implemented yet, they will come in version 0.2.0"
void size_distribution_phase_function(std::complex<double> m_core, double mean_diam, double stdev_diam, double wavelength, std::complex<double> m_shell, double fcoating, double resolution, double dens, int effcore, int norm2vol, int nang, double *outTheta, double *outSL, double *outSR, double *outSU) {
    double res = 1.0/resolution;
    int dcount = calc_diam_count(mean_diam, stdev_diam, res);
    double core_diams[dcount];
    double shell_diams[dcount];
    double pdf[dcount];
    double crossArea[dcount];
    double normWeight;
    createLogNormalDistribution(mean_diam, stdev_diam, fcoating, res, dens, effcore, norm2vol, core_diams, shell_diams, pdf, crossArea, &normWeight);
    double max_shell_diam = 0.0;
    int idx, a;
    for(idx=0; idx<dcount; idx++) {
        if(max_shell_diam < shell_diams[idx])
            max_shell_diam = shell_diams[idx];
    }

    double sl[nang];
    double sr[nang];
    double su[nang];

    double maxy = _PI_*max_shell_diam/wavelength;
    int nmax = calc_nmax(maxy);
    //std::complex<double> maxmy = m_core*maxy;
    //PySys_WriteStdout("%12.6f+i*%12.6f\n",maxmy.real(),maxmy.imag());
    int arr_len = nang*nmax;
    double *pin = new double[arr_len];
    double *taun = new double[arr_len];
    mie_pitau(nang, outTheta, nmax, pin, taun);
    std::complex<double> *an = new std::complex<double>[nmax];
    std::complex<double> *bn = new std::complex<double>[nmax];

    int is_coated = (fcoating>EPS) && (m_core!=m_shell);

    for(a=0; a<nang; a++) {
        outSL[a] = 0.0;
        outSR[a] = 0.0;
        outSU[a] = 0.0;
    }

    for(idx=0; idx<dcount; idx++) {
        double xval = _PI_*core_diams[idx]/wavelength;
        double yval = _PI_*shell_diams[idx]/wavelength;
        int anbn_used_len = calc_nmax(yval);
        if (is_coated) {
            miecoated_ab(m_core, xval, m_shell, yval, an, bn);
        } else {
            mie_ab(m_core, yval, an, bn);
        }

        scattering_function(anbn_used_len, an, bn, nang, outTheta, nmax, pin, taun, sl, sr, su);

        for(a=0; a<nang; a++) {
            outSL[a] += sl[a]*crossArea[idx];
            outSR[a] += sr[a]*crossArea[idx];
            outSU[a] += su[a]*crossArea[idx];
        }
    }

    for(a=0; a<nang; a++) {
        outSL[a] *= normWeight;
        outSR[a] *= normWeight;
        outSU[a] *= normWeight;
    }

    delete[] pin;
    delete[] taun;
    delete[] an;
    delete[] bn;
}
PyObject* mie_art_sdpf(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { (char*)"m", (char*)"sizepar1", (char*)"sizepar2", (char*)"wavelength", (char*)"nMedium", (char*)"fcoat", (char*)"mc", (char*)"density", (char*)"resolution", (char*)"effcore", (char*)"normalized", NULL };

    Py_complex valueNpMcore;
    Py_complex valueNpMshell = nanPyCplx();
    double valueDmu;
    double valueDstd;
    double valueW;
    double valueNmedium;
    double valueFcoat;
    double valueDens = 1.0;
    double valueRes = 10.0;
    int valueN2core = true;
    int valueAsCrossSec = true;
    PyObject *res = NULL;
    //    int array_sizepar = 0;

    if(PyArg_ParseTupleAndKeywords(args, kwds, "Dddd|ddDddpp", kwlist, &valueNpMcore, &valueDmu, &valueDstd, &valueW, &valueNmedium, &valueFcoat, &valueNpMshell, &valueDens, &valueRes, &valueN2core, &valueAsCrossSec)) {
        std::complex<double> valueMcore  = py2c_cplx(valueNpMcore);
        std::complex<double> valueMshell = py2c_cplx(valueNpMshell);
        if(std::isnan(valueNpMshell.real) || std::isnan(valueNpMshell.imag)) {
            valueMshell = py2c_cplx(valueNpMcore);
        }
        double angres = 0.25; //degrees
        int nang = calc_angles_count(angres);
        double theta[nang];
        double pf_sl[nang];
        double pf_sr[nang];
        double pf_su[nang];
        double ares = angres*_PI_/180.0;
        for(int a=0; a<nang; a++) {
            theta[a] = a*ares;
        }
        size_distribution_phase_function(valueMcore, valueDmu, valueDstd, valueW, valueMshell, valueFcoat, valueRes, valueDens, valueN2core, valueAsCrossSec, nang, theta, pf_sl, pf_sr, pf_su);
        res = Py_BuildValue("OOOO",
                c2py_dblarr(nang, theta),
                c2py_dblarr(nang, pf_sl),
                c2py_dblarr(nang, pf_sr),
                c2py_dblarr(nang, pf_su)
            );
    } else {
//        array_sizepar = 1;
//        PyErr_Clear();
    }

//    if(array_sizepar) {
//        PyObject *arr_ptr[] = { NULL, NULL };
//        PyObject *array[] =   { NULL, NULL };
//        int dtype = -1;
//        if(PyArg_ParseTupleAndKeywords(args, kwds, "DOOd|ddDddpp", kwlist, &valueNpMcore, &arr_ptr[0], &arr_ptr[1], &valueW, &valueNmedium, &valueFcoat, &valueNpMshell, &valueDens, &valueRes, &valueN2core, &valueAsCrossSec)) {
//            {
//                if(parse_arrays(2, NPY_FLOAT, arr_ptr, array)) dtype = NPY_FLOAT;
//            }
//            if(dtype<0) {
//                if(parse_arrays(2, NPY_DOUBLE, arr_ptr, array)) dtype = NPY_DOUBLE;
//            }
//        } else {
//            PyErr_Clear();
//        }
//
//        int ndim1 = PyArray_NDIM((PyArrayObject *)array[0]);
//        int ndim2 = PyArray_NDIM((PyArrayObject *)array[1]);
//        if(ndim1!=1 || ndim2!=1) {
//            PyErr_SetString(
//                PyExc_TypeError,
//                "sizepar1 and sizepar2 have to be both 1dimensional arrays of type float[] or double[]"
//            );
//            Py_XDECREF(array[0]);
//            Py_XDECREF(array[1]);
//            return NULL;
//        }
//        int size1 = PyArray_SIZE((PyArrayObject *)array[0]);
//        int size2 = PyArray_SIZE((PyArrayObject *)array[1]);
//        if(size1!=size2) {
//            PyErr_SetString(
//                PyExc_IndexError,
//                "sizepar1 and sizepar2 have to be arrays of the same length"
//            );
//            Py_XDECREF(array[0]);
//            Py_XDECREF(array[1]);
//            return NULL;
//        }
//
////        std::complex<double> valueMcore  = py2c_cplx(valueNpMcore);
////        std::complex<double> valueMshell = py2c_cplx(valueNpMshell);
////        if(std::isnan(valueNpMshell.real) || std::isnan(valueNpMshell.imag)) {
////            valueMshell = py2c_cplx(valueNpMcore);
////        }
//
//        PyErr_SetString(
//            PyExc_NotImplementedError,
//            "array-like input for sizepar1 and sizepar2 not implemented yet."
//        );
//        Py_XDECREF(array[0]);
//        Py_XDECREF(array[1]);
//        return NULL;
//    }

    return res;
}




// **** Module definition ****

PyMethodDef mie_methods[] = {
    {"gamma",            (PyCFunction)(void(*)(void))mie_art_gamma,         METH_VARARGS|METH_KEYWORDS, gm_docstring},
    {"besselj",          (PyCFunction)(void(*)(void))mie_art_besselj,       METH_VARARGS|METH_KEYWORDS, bj_docstring},
    {"bessely",          (PyCFunction)(void(*)(void))mie_art_bessely,       METH_VARARGS|METH_KEYWORDS, by_docstring},
    {"hankel",           (PyCFunction)(void(*)(void))mie_art_hankel,        METH_VARARGS|METH_KEYWORDS, hv_docstring},
    {"besseli",          (PyCFunction)(void(*)(void))mie_art_besseli,       METH_VARARGS|METH_KEYWORDS, bi_docstring},
    {"besselk",          (PyCFunction)(void(*)(void))mie_art_besselk,       METH_VARARGS|METH_KEYWORDS, bk_docstring},
    {"airy",             (PyCFunction)(void(*)(void))mie_art_airy,          METH_VARARGS|METH_KEYWORDS, ai_docstring},

    {"MieQ",             (PyCFunction)(void(*)(void))mie_art_mieq,          METH_VARARGS|METH_KEYWORDS, mieq_docstring},
    {"MieCoatedQ",       (PyCFunction)(void(*)(void))mie_art_miecoatedq,    METH_VARARGS|METH_KEYWORDS, miecoatedq_docstring},
    {"Mie_ab",           (PyCFunction)(void(*)(void))mie_art_mieab,         METH_VARARGS|METH_KEYWORDS, mieab_docstring},
    {"MieCoated_ab",     (PyCFunction)(void(*)(void))mie_art_miecoatedab,   METH_VARARGS|METH_KEYWORDS, miecoatedab_docstring},
    {"Mie_cd",           (PyCFunction)(void(*)(void))mie_art_miecd,         METH_VARARGS|METH_KEYWORDS, miecd_docstring},
    {"Mie_pitau",        (PyCFunction)(void(*)(void))mie_art_miepitau,      METH_VARARGS|METH_KEYWORDS, miepitau_docstring},
    {"ab2mie",           (PyCFunction)(void(*)(void))mie_art_ab2mie,        METH_VARARGS|METH_KEYWORDS, abtomie_docstring},
    {"ScatteringFunction", (PyCFunction)(void(*)(void))mie_art_scatfunc,    METH_VARARGS|METH_KEYWORDS, scatfunc_docstring},

    {"createLogNormalDistribution",      (PyCFunction)(void(*)(void))mie_art_createLgNormDist, METH_VARARGS|METH_KEYWORDS, clnd_docstring},
    {"calcBackscattering",               (PyCFunction)(void(*)(void))mie_art_calcBackScat,     METH_VARARGS|METH_KEYWORDS, cbs_docstring},
    {"Size_Distribution_Optics",         (PyCFunction)(void(*)(void))mie_art_sdo,              METH_VARARGS|METH_KEYWORDS, sdo_docstring},
    {"Size_Distribution_Phase_Function", (PyCFunction)(void(*)(void))mie_art_sdpf,             METH_VARARGS|METH_KEYWORDS, sdpf_docstring},

    {NULL, NULL, 0, NULL} /* sentinel */
};

PyModuleDef artmiemodule = { // @suppress("Invalid arguments")
    PyModuleDef_HEAD_INIT,
    "ARTmie",
    NULL,
    -1,
    mie_methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC
PyInit_ARTmie(void) {
    
    PyObject *m;
    
    import_array();
    
    m = PyModule_Create(&artmiemodule);
    if (!m) {
        return NULL;
    }
    
    return m;
}
