#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Copyright 2014 Meteo France
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
This module provides a function (ctypesForFortranFactory) which return a decorator
and another function (fortran2signature) which helps at building signature.
See these function documentations for more help on them.

The module also exposes a dlclose function to try closing lib
"""
import subprocess
import os
import re
import ctypes
from functools import wraps
import numpy

from _ctypes import dlclose

__all__ = []

__version__ = "2.2.1"

__license__ = 'Apache-2.0'

__authors__ = ['Sébastien Riette']


# Static values used to define input/output status of arguments
IN = 1
OUT = 2
INOUT = 3
MISSING = object()
#Mandatory arguments can appear after optional ones in FORTRAN but not
#with python. Those arguments are intialialised in python with this constant
MANDATORY_AFTER_OPTIONAL = object()

def addReturnCode(func):
    """
    This decorator adds an integer at the beginning of the "returned"
    signature of the Python function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs): # pylint: disable=redefined-outer-name
        out = func(*args, **kwargs)
        out[1].insert(0, (numpy.int64, None, OUT))
        return out
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def treatReturnCode(func):
    """
    This decorator raises a Python error if the integer returned by
    addReturnCode is different from 0.
    """
    @wraps(func)
    def wrapper(*args): # pylint: disable=redefined-outer-name
        result = func(*args)
        try:
            nout = len(result)
        except TypeError:
            nout = 1
        if nout == 1:
            result = (result,)
        if result[0] != 0:
            raise RuntimeError("Error code " + str(result[0]) + " was raised.")
        result = result[1:]
        if len(result) == 1:
            result = result[0]
        elif len(result) == 0:
            result = None
        return result
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def string2array(s, length=None):
    """
    Portability is better with character arrays than with character strings
    This function makes the conversion string to array
    """
    if isinstance(s, str):
        if length is not None:
            s = s.ljust(length)
        return numpy.array([c for c in s], dtype='S1')
    else:
        if length is not None:
            strlen = length
        else:
            strlen = max(len(ones) for ones in s)
        return numpy.array([[c for c in ones.ljust(strlen)] for ones in  s], dtype='S1')


def array2string(pos, decode=True):
    """
    Portability is better with character arrays than with character strings
    This function is a decorator builder to make the conversion array to string
    :param pos: position or list of positions of returned values
                that must be converted from array to string
    :param decode: - True to decode all strings and string arrays into utf-8
                   - False to not decode them
                   - position or list of positions of returned values to decode
    """
    if not isinstance(pos, list):
        pos = [pos]
    if decode is True:
        decode = pos
    elif decode is False:
        decode = []
    elif not isinstance(decode, list):
        decode = [decode]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, (tuple, list)):
                nout = len(result)
                result = list(result)
            else:
                nout = 1
                result = [result]
            for p in pos:
                if len(result[p].shape) == 1:
                    result[p] = b''.join(result[p])
                    if p in decode:
                        result[p] = result[p].decode('utf-8')
                else:
                    result[p] = numpy.array([b''.join(result[p][i]).rstrip()
                                          for i in range(result[p].shape[0])])
                    if p in decode:
                        result[p] = numpy.array([s.decode('utf-8') for s in result[p]])
            if nout == 1:
                result = result[0]
            else:
                result = tuple(result)
            return result
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator


def get_dynamic_libs(obj):
    """Get dynamic libs from a shared object lib or executable."""
    libs = {}
    osname = str(os.uname()[0])
    if osname == 'Linux':
        _re = re.compile(r'((?P<libname>lib.*) => )?(?P<libpath>/.*/.*\.so(\.\d+)*)\s\(0x.*\)')
        with subprocess.Popen(['ldd', obj], stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE) as proc:
            ldd_out = [line.decode().strip() for line in proc.stdout.readlines()]
        for line in ldd_out:
            match = _re.match(line)
            if match:
                matchdict = match.groupdict()
                if matchdict.get('libname') is None:
                    matchdict['libname'] = matchdict.get('libpath').split('/')[-1]
                libs[matchdict['libname']] = matchdict.get('libpath')
    elif osname == 'Darwin':
        _re = re.compile(r'\s*(?P<libdir>/.*/)(?P<libname>.*(\.\d+)?\.dylib)\s+.*')
        with subprocess.Popen(['otool', '-L', obj], stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE) as proc:
            otool_out = [line.decode().strip() for line in proc.stdout.readlines()]
        for line in otool_out:
            match = _re.match(line)
            if match:
                libs[match.group('libname')] = match.group('libdir') + match.group('libname')
    else:
        raise NotImplementedError("OS: " + osname)
    return libs


class Logical():
    """
    Interoperability between C and FORTRAN is not easy for bool/LOGICAL.
    We assume that the false value is always 0 and we test the returned values
    from FORTRAN against this zero: 'python value' = 'fortran value' != 0
    In the other way, values given to the FORTRAN subroutine are guessed from
    the compiler used, hoping that the options used haven't changed the default
    behavior

    This class computes the true/false value to use, only when needed
    """
    def __init__(self, filename):
        self._filename = filename
        self._true = None
        self._false = None

    def _compute(self):
        """
        Guess the compiler and the true/false values
        """
        compiler = set()
        libs = get_dynamic_libs(self._filename)
        for lib in libs.keys():
            if lib.startswith('libgfortran'):
                compiler.add('gfortran')
            if lib.startswith('libifport'):
                compiler.add('ifort')
            if lib.startswith('libnvf'):
                compiler.add('nvfortran')
        if len(compiler) == 0:
            raise IOError("Don't know which compiler was used to build the shared library")
        self._true, self._false = {'ifort': (-1, 0),
                                   'gfortran': (1, 0),
                                   'nvfortran': (-1, 0),
                                   'nfort': (1, 0),
                                  }[compiler.pop()]

    @property
    def true(self):
        "Returns the 'true' value used by default by this compiler"
        if self._true is None:
            self._compute()
        return self._true

    @property
    def false(self):
        "Returns 0, the 'false' value used by defaults by the different compilers tested"
        return 0


def ctypesForFortranFactory(solib):
    """
    solib is a shared library already opened (with ctypes) or a filename to use.

    This function returns a tuple (function, handle). The handle can be used with dlclose.

    The returned function will return a decorator used to call fortran routines or functions
    contained in <solib> using ctypes. The function can take up to four arguments:
      - prefix and suffix which will be added to the python function name to build the name
        of the function in the shared library. By default prefix is the empty string whereas
        suffix is '_'.
      - if castInput is True, input values are cast into the right dtype before being used.
      - indexing controls the index order. If 'C', indexes are in C order (arrays
        can be passed directly to and from the FORTRAN routine). If 'F' (default), array index order
        is the same as in the FORTRAN routine (arrays are automatically transposed).

    The actual python function that is decorated must return the signature of the fortran routine.
    The signature is a tuple. Fisrt element is the actual list of arguments which will be used
    to call the fortran routine.
    The arguments must be put in the same order as the one declared in the fortran routine.
    With BIND(C) subroutine, optional arguments can be set to MISSING.
    The second element of the signature tuple is also a list, each element of the list is
    a tuple (type, shape, in_out_intent), where:
      - type must be one of str, bool, np.float64, np.int64, np.float32, np.int32
        With BIND(C) subroutine, type can also be MISSING (only for OUT arguments).
      - shape is - None in case of a scalar value
                 - a tuple which represent the shape of the array
                 - in case of str, first (regardless of the value of 'indexing') shape element
                   is the string size; if other elements are present, the variable is a string
                   array whose shape is given by shape[1:]
      - in_out_intent is one of IN, OUT or INOUT constant declared in the module
    The third, and last, element of the signature tuple is None or a tuple representing the
    output value for a function. It is a tuple with (type, shape) as described above but
    without the in_out_intent element. None must be used for subroutine.

    For input arguments, type checking is done against this signature.
    All elements must be declared using numpy classes except str and bool but scalar arguments
    are expected to be true python scalars (for instance (np.float64, None, IN) is the signature
    for a python float variable)

    The decorated function will call the fortran routine (or function) and return:
      - a tuple of all OUT and INOUT arguments (in the declaration order,
                                                with function output in first position)
      - a single value if only one argument is OUT or INOUT

    Note on strings: scalars strings are converted from and to unicode; which isn't always wise
                     strings arrays are declared (in signature) with str but must be
                     created with the 'S' dtype with python3 (str is OK with python2)

    Note 2 on strings: compatibility is better with 1-char arrays than with strings
                       one example below show how to convert strings and arrays

    Note on inout arrays: if a subroutine takes array arguments with the INOUT intent, the input
                          array may be, or not, the same object as the returned array. For example,
                          if the argument 'a' in "new_a = FOO(a)" has the INOUT intent, 'a' and
                          'new_a' are not guaranteed to be the same object, but can be.

    Known limitations:
      - only some types have been tested, other raise an exception but this
        could normally be extended easily
      - logical arrays must be declared with KIND=1 in the fortran routine
        as bool numpy array elements are 1 byte (and not 1 bit) values
      - fortran assumed-shape arrays, assumed-rank arrays or asterisk length strings are
        not callable
      - there is no support for optional fortran argument except if 'BIND(C)' is used in
        the FORTRAN code. In this case missing argument must receive the MISSING value.
        Note that, we can always use python optional arguments but the default python value
        (if not MISSING will be passed to the fortran routine (it then will appear as present)
      - unicode/ASCCI issue is more than likely... (for scalars and string arrays)
      - only scalars (integer, real and logical) can be returned by functions
      - because integer value of boolean variables vary among compilers, we need to determine the
        compiler used. For now only gfortran and ifort are supported.

    Usage:
        Fortran code:
<<BEGIN FORTRAN
            FUNCTION F_INT(KIN)
              IMPLICIT NONE
              INTEGER(KIND=8), INTENT(IN) :: KIN
              INTEGER(KIND=8) :: F_INT
              F_INT=KIN+1
            END FUNCTION

            FUNCTION F_REAL(PIN)
              IMPLICIT NONE
              REAL(KIND=8), INTENT(IN) :: PIN
              REAL(KIND=8) :: F_REAL
              F_REAL=PIN+1.
            END FUNCTION

            FUNCTION F_BOOL(LIN)
              IMPLICIT NONE
              LOGICAL(KIND=1), INTENT(IN) :: LIN
              LOGICAL(KIND=1) :: F_BOOL
              F_BOOL=.NOT. LIN
            END FUNCTION

            SUBROUTINE FOO(KIN, KOUT, KINOUT,       & !Integer scalars
                           KAIN, KAOUT, KAINOUT,    & !Integer arrays
                           CDIN, CDOUT, CDINOUT,    & !Strings
                           CDAIN, CDAOUT, CDAINOUT, & !String arrays
                           PIN, POUT, PINOUT,       & !Float scalars
                           PAIN, PAOUT, PAINOUT,    & !Float arrays
                           LIN, LOUT, LINOUT,       & !Logical scalars
                           LAIN, LAOUT, LAINOUT,    & !Logical arrays
                           KAIN2, KAOUT2)             !2D integer arrays

              INTEGER(KIND=8), INTENT(IN) :: KIN
              INTEGER(KIND=8), INTENT(OUT) :: KOUT
              INTEGER(KIND=8), INTENT(INOUT) :: KINOUT

              INTEGER(KIND=8), DIMENSION(KIN), INTENT(IN) :: KAIN
              INTEGER(KIND=8), DIMENSION(KIN), INTENT(OUT) :: KAOUT
              INTEGER(KIND=8), DIMENSION(KIN), INTENT(INOUT) :: KAINOUT

              CHARACTER(LEN=10), INTENT(IN) :: CDIN
              CHARACTER(LEN=20), INTENT(OUT) :: CDOUT
              CHARACTER(LEN=20), INTENT(INOUT) :: CDINOUT

              CHARACTER(LEN=10), DIMENSION(2, 3), INTENT(IN) :: CDAIN
              CHARACTER(LEN=10), DIMENSION(2, 3), INTENT(OUT) :: CDAOUT
              CHARACTER(LEN=10), DIMENSION(2, 3), INTENT(INOUT) :: CDAINOUT

              REAL(KIND=8), INTENT(IN) :: PIN
              REAL(KIND=8), INTENT(OUT) :: POUT
              REAL(KIND=8), INTENT(INOUT) :: PINOUT

              REAL(KIND=8), DIMENSION(KIN), INTENT(IN) :: PAIN
              REAL(KIND=8), DIMENSION(KIN), INTENT(OUT) :: PAOUT
              REAL(KIND=8), DIMENSION(KIN), INTENT(INOUT) :: PAINOUT

              LOGICAL(KIND=1), INTENT(IN) :: LIN
              LOGICAL(KIND=1), INTENT(OUT) :: LOUT
              LOGICAL(KIND=1), INTENT(INOUT) :: LINOUT

              LOGICAL(KIND=1), DIMENSION(40), INTENT(IN) :: LAIN
              LOGICAL(KIND=1), DIMENSION(40), INTENT(OUT) :: LAOUT
              LOGICAL(KIND=1), DIMENSION(40), INTENT(INOUT) :: LAINOUT

              INTEGER(KIND=8), DIMENSION(4, 5), INTENT(IN) :: KAIN2
              INTEGER(KIND=8), DIMENSION(4, 5), INTENT(OUT) :: KAOUT2

              KOUT=KIN+1
              KINOUT=KINOUT+1

              KAOUT(:)=KAIN(:)+1
              KAINOUT(:)=KAINOUT(:)+1

              CDOUT=CDIN // "Foo"
              CDINOUT=CDINOUT(1:5) // CDINOUT(1:15)
              CDAOUT(1,:) = CDAIN(2, 3:1:-1)
              CDAOUT(2,:) = CDAIN(1, 3:1:-1)
              CDAINOUT(1,:) = CDAINOUT(2,:)
              CDAINOUT(2,:) = CDAINOUT(1,:)

              POUT=PIN+1.
              PINOUT=PINOUT+1.

              PAOUT(:)=PAIN(:)+1.
              PAINOUT(:)=PAINOUT(:)+1.

              LOUT=.NOT.LIN
              LINOUT=.NOT.LINOUT

              LAOUT(1:10)=LAIN(1:10)
              LAOUT(11:20)=.NOT. LAIN(11:20)
              LAOUT(21:30)=LAIN(21:30)
              LAOUT(31:40)=.NOT. LAIN(31:40)
              LAINOUT(:)=.NOT. LAINOUT(:)

              KAOUT2(1,:)=KAIN2(1,:)
              KAOUT2(2,:)=-KAIN2(2,:)
              KAOUT2(3,:)=KAIN2(3,:)
              KAOUT2(4,:)=-KAIN2(4,:)
            END SUBROUTINE

            !Example with string-array conversion
            SUBROUTINE CONVERT(CARRAYIN, CARRAYOUT)
              USE, INTRINSIC :: ISO_C_BINDING, ONLY: C_CHAR
              IMPLICIT NONE
              CHARACTER(KIND=C_CHAR), DIMENSION(10), INTENT(IN) :: CARRAYIN
              CHARACTER(KIND=C_CHAR), DIMENSION(12), INTENT(OUT) :: CARRAYOUT
              !
              CHARACTER(LEN=SIZE(CARRAYIN)) :: CSTRINGIN
              CHARACTER(LEN=SIZE(CARRAYOUT)) :: CSTRINGOUT
              !
              CALL ARRAY2STRING(CARRAYIN, CSTRINGIN)
              CSTRINGOUT='X' // CSTRINGIN // 'Y'
              CALL STRING2ARRAY(CSTRINGOUT, CARRAYOUT)
              CONTAINS
                SUBROUTINE ARRAY2STRING(CARRAY, CSTRING)
                  USE, INTRINSIC :: ISO_C_BINDING, ONLY: C_CHAR
                  IMPLICIT NONE
                  CHARACTER(KIND=C_CHAR), DIMENSION(:), INTENT(IN) :: CARRAY
                  CHARACTER(LEN=SIZE(CARRAY)), INTENT(OUT) :: CSTRING
                  !
                  INTEGER :: JK
                  !
                  DO JK=1, SIZE(CARRAY)
                    CSTRING(JK:JK)=CARRAY(JK)
                  ENDDO
                END SUBROUTINE ARRAY2STRING
                SUBROUTINE STRING2ARRAY(CSTRING, CARRAY)
                  USE, INTRINSIC :: ISO_C_BINDING, ONLY: C_CHAR
                  IMPLICIT NONE
                  CHARACTER(LEN=*), INTENT(IN) :: CSTRING
                  CHARACTER(KIND=C_CHAR), DIMENSION(LEN(CSTRING)), INTENT(OUT) :: CARRAY
                  !
                  INTEGER :: JK
                  !
                  DO JK=1, LEN(CSTRING)
                    CARRAY(JK)=CSTRING(JK:JK)
                  ENDDO
                END SUBROUTINE STRING2ARRAY
            END SUBROUTINE CONVERT
>>END FORTRAN
          compiled to create foo.so shared library (ex with gfortran:
          "gfortran -c -fPIC foo.F90 && gfortran -shared -g -o foo.so foo.o",
          or with ifort:
          "ifort -c -fpic foo.F90 && ifort -shared -g -o foo.so foo.o"
          )

        Python code:
<<BEGIN PYTHON
            import numpy
            import ctypesForFortran

            IN = ctypesForFortran.IN
            OUT = ctypesForFortran.OUT
            INOUT = ctypesForFortran.INOUT

            ctypesFF, handle = ctypesForFortran.ctypesForFortranFactory("./foo.so")

            #With gfortran, if f_int was inside module 'toto', we would use
            #@ctypesFF(prefix='__toto_MOD_', suffix='')
            @ctypesFF()
            def f_int(KIN):
                return ([KIN],
                        [(numpy.int64, None, IN)], #INTEGER(KIND=8), INTENT(IN) :: KIN
                        (numpy.int64, None))

            @ctypesFF()
            def f_real(PIN):
                return ([PIN],
                        [(numpy.float64, None, IN)], #REAL(KIND=8), INTENT(IN) :: PIN
                        (numpy.float64, None))

            @ctypesFF()
            def f_bool(LIN):
                return ([LIN],
                        [(bool, None, IN)], #LOGICAL(KIND=1), INTENT(IN) :: LIN
                        (bool, None))

            @ctypesFF(indexing='F') # In this example, index order is the same in FORTRAN and python
            def foo(KIN, KINOUT,    # Integer scalars  # Only IN and INOUT variabes.
                    PIN, PINOUT,    # Float scalars    #
                    LIN, LINOUT,    # Logical scalars  # The order can be different than the
                    CDIN, CDINOUT,  # Strings          # one expected by the fortran routine.
                    CDAIN, CDAINOUT,# String arrays    # Here we put the scalars first, then
                    KAIN, KAINOUT,  # Integer arrays   # the arrays, whereas this is not the
                    PAIN, PAINOUT,  # Float arrays     # order declared in fortran code.
                    LAIN, LAINOUT,  # Logical arrays   #
                    KAIN2):         # 2D integer arrays#
                return ([KIN, KINOUT,     #
                         KAIN, KAINOUT,   # Only IN and INOUT variabes.
                         CDIN, CDINOUT,   #
                         CDAIN, CDAINOUT, #
                         PIN, PINOUT,     # Here, this *must* be the same order
                         PAIN, PAINOUT,   # as the one in the fortran declaration
                         LIN, LINOUT,     #
                         LAIN, LAINOUT,   #
                         KAIN2],          #
                        [(numpy.int64, None, IN), #INTEGER(KIND=8), INTENT(IN) :: KIN
                         (numpy.int64, None, OUT), #INTEGER(KIND=8), INTENT(OUT) :: KOUT
                         (numpy.int64, None, INOUT), #INTEGER(KIND=8), INTENT(INOUT) :: KINOUT

                         (numpy.int64, (KIN, ), IN), #INTEGER(KIND=8), DIMENSION(KIN), INTENT(IN) :: KAIN
                         (numpy.int64, (KIN, ), OUT), #INTEGER(KIND=8), DIMENSION(KIN), INTENT(OUT) :: KAOUT
                         (numpy.int64, (KIN, ), INOUT), #INTEGER(KIND=8), DIMENSION(KIN), INTENT(INOUT) :: KAINOUT

                         (str, (10, ), IN), #CHARACTER(LEN=10), INTENT(IN) :: CDIN
                         (str, (20, ), OUT), #CHARACTER(LEN=20), INTENT(OUT) :: CDOUT
                         (str, (20, ), INOUT), #CHARACTER(LEN=20), INTENT(INOUT) :: CDINOUT

                         (str, (10, 2, 3), IN), #CHARACTER(LEN=10), DIMENSION(2, 3),, INTENT(IN) :: CDAIN
                         (str, (10, 2, 3), OUT), #CHARACTER(LEN=10), DIMENSION(2, 3),, INTENT(OUT) :: CDAOUT
                         (str, (10, 2, 3), INOUT), #CHARACTER(LEN=10), DIMENSION(2, 3),, INTENT(INOUT) :: CDAINOUT

                         (numpy.float64, None, IN), #REAL(KIND=8), INTENT(IN) :: PIN
                         (numpy.float64, None, OUT), #REAL(KIND=8), INTENT(OUT) :: POUT
                         (numpy.float64, None, INOUT), #REAL(KIND=8), INTENT(INOUT) :: PINOUT

                         (numpy.float64, (KIN, ), IN), #REAL(KIND=8), DIMENSION(KIN), INTENT(IN) :: PAIN
                         (numpy.float64, (KIN, ), OUT), #REAL(KIND=8), DIMENSION(KIN), INTENT(OUT) :: PAOUT
                         (numpy.float64, (KIN, ), INOUT), #REAL(KIND=8), DIMENSION(KIN), INTENT(INOUT) :: PAINOUT

                         (bool, None, IN), #LOGICAL(KIND=1), INTENT(IN) :: LIN
                         (bool, None, OUT), #LOGICAL(KIND=1), INTENT(OUT) :: LOUT
                         (bool, None, INOUT), #LOGICAL(KIND=1), INTENT(INOUT) :: LINOUT

                         (bool, (40, ), IN), #LOGICAL(KIND=1), DIMENSION(40), INTENT(IN) :: LAIN
                         (bool, (40, ), OUT), #LOGICAL(KIND=1), DIMENSION(40), INTENT(OUT) :: LAOUT
                         (bool, (40, ), INOUT), #LOGICAL(KIND=1), DIMENSION(40), INTENT(INOUT) :: LAINOUT

                         (numpy.int64, (4, 5), IN), #INTEGER(KIND=8), DIMENSION(4, 5), INTENT(IN) :: KAIN2
                         (numpy.int64, (4, 5), OUT), #INTEGER(KIND=8), DIMENSION(4, 5), INTENT(OUT) :: KAOUT2
                        ],
                        None)

            @ctypesForFortran.array2string(0)
            @ctypesFF()
            def convert(carrayin):
               return ([ctypesForFortran.string2array(carrayin, 10)],
                       [(str,(1, 10, ),IN),
                        (str,(1, 12, ),OUT)],
                       None)

            assert f_int(5) == 6, "f_int"
            assert f_real(5.) == 6., "f_real"
            assert f_bool(True) == False and f_bool(False) == True, "f_bool"

            kin = 5
            kinout = 8
            kain = numpy.arange(kin, dtype=numpy.int64)
            kainout = numpy.arange(kin, dtype=numpy.int64) * 10
            cdin = "blabla"
            cdinout = "azertyuiop"
            cdain = numpy.ndarray((2, 3), dtype=('S', 10))
            cdainout = numpy.ndarray((2, 3), dtype=('S', 10))
            for j in range(cdain.shape[0]):
                for i in range(cdain.shape[1]):
                    cdain[j, i] = str(i) + "_" + str(j)
                    cdainout[j, i] = str(i*10) + "_" + str(j*10)
            pin = 12.
            pinout = 53.
            pain = numpy.arange(kin, dtype=numpy.float64)
            painout = numpy.arange(kin, dtype=numpy.float64) * 10.
            lin = True
            linout = False
            lain = numpy.array([True, False] * 20)
            lainout = numpy.array([True, False, False, False] * 10)
            kain2 = numpy.arange(20, dtype=numpy.int64).reshape((4, 5))

            #IN/OUT test
            args = [kin, kinout, pin, pinout, lin, linout, cdin, cdinout,
                    cdain, cdainout, kain, kainout, pain, painout]
            kwargs = dict(LAIN=lain, LAINOUT=lainout, KAIN2=kain2)

            result = foo(*args, **kwargs) #We can call the python function with keyword arguments
            (kout, kinout, kaout, kainout,
             cdout, cdinout, cdaout, cdainout,
             pout, pinout, paout, painout,
             lout, linout, laout, lainout,
             kaout2) = result

            assert kout == kin + 1, "k 1"
            assert kinout == 8 + 1, "k 2"
            assert numpy.all(kaout == kain + 1), "k 3"
            assert numpy.all(kainout == numpy.arange(kin, dtype=numpy.int64) * 10 + 1), "k 4"

            assert cdout == (cdin.ljust(10) + "Foo").ljust(20), "cd 1"
            assert cdinout == "azertyuiop".ljust(20)[0:5] + "azertyuiop".ljust(20)[0:15], "cd 2"
            assert numpy.all(cdaout[0, :] == numpy.char.ljust(cdain, 10)[1, ::-1]) and \
                   numpy.all(cdaout[1, :] == numpy.char.ljust(cdain, 10)[0, ::-1]), "cd 3"
            assert numpy.all(cdainout[0, :] == numpy.char.ljust(cdainout, 10)[1, :]) and \
                   numpy.all(cdainout[1, :] == numpy.char.ljust(cdainout, 10)[0, :]), "cd 4"

            assert pout == pin + 1., "p 1"
            assert pinout == 53. + 1., "p 2"
            assert numpy.all(paout == pain + 1.), "p 3"
            assert numpy.all(painout == numpy.arange(kin, dtype=numpy.float64) * 10. + 1.), "p 4"

            assert lout == (not lin), "l 1"
            assert linout == (not False), "l 2"
            assert numpy.all(laout[0:10] == lain[0:10]) and \
                   numpy.all(laout[10:20] == (numpy.logical_not(lain[10:20]))) and \
                   numpy.all(laout[20:30] == lain[20:30]) and \
                   numpy.all(laout[30:40] == (numpy.logical_not(lain[30:40]))), "l 3"
            assert numpy.all(lainout == numpy.logical_not(numpy.array([True, False,
                                                                       False, False] * 10))), "l 4"

            assert numpy.all(kaout2[0, :] == kain2[0, :]) and \
                   numpy.all(kaout2[1, :] == -kain2[1, :]) and \
                   numpy.all(kaout2[2, :] == kain2[2, :]) and \
                   numpy.all(kaout2[3, :] == -kain2[3, :]), "K 5"

            #Checks
            #Normal order args = [kin, kinout, pin, pinout, lin, linout, cdin, cdinout, cdain,
            #                     cdainout, kain, kainout, pain, painout, lain, lainout, kain2]

            for args in [[kin, kinout*1., pin, pinout, lin, linout, cdin, cdinout, cdain,
                          cdainout, kain, kainout, pain, painout,
                          lain, lainout, kain2], # wrong type for kinout
                         [kin, kinout, pin, pinout, lin, linout, cdin.ljust(500), cdinout, cdain,
                          cdainout, kain, kainout, pain, painout, lain,
                          lainout, kain2], # cdin string too long
                         [kin, kinout, pin, pinout, lin, linout, cdin, cdinout, cdain,
                          cdainout, kain, kainout, pain, painout,
                          lain, lainout, kain2.reshape((5, 4))], # wrong shape for kain2
                         [kin, kinout, pin, pinout, lin, linout, cdin, cdinout, cdain,
                          cdainout, kain*1., kainout, pain, painout,
                          lain, lainout, kain2], # wrong type for kain array
                         [kin, kinout, pin, pinout, lin, linout, cdin, cdinout, cdain,
                          cdainout, kain, kainout, pain, painout,
                          lain.reshape((40, 1)), lainout, kain2], # wrong rank for lain
                         [kin, kinout, pin, pinout, lin, linout, cdin, cdinout, cdain,
                          cdainout, list(kain), kainout, pain, painout,
                          lain, lainout, kain2], # type not implemented for kain
                        ]:
                try:
                    result = foo(*args)
                    raise IOError("fake IOError")
                except IOError:
                    raise RuntimeError("call has not raise error; not normal")
                except:
                    #It is normal for call to raise an error
                    pass

            assert convert('ABC') == 'XABC       Y'
            ctypesForFortran.dlclose(handle)
>>END PYTHON
          if OK must execute without any output
    """
    if isinstance(solib, str):
        filename = solib
        my_solib = ctypes.CDLL(solib, ctypes.RTLD_GLOBAL)
    else:
        my_solib = solib
        filename = my_solib._name  # pylint: disable=protected-access

    logical = Logical(filename)

    def ctypesFF(prefix="", suffix="_", castInput=False, indexing='C'):
        """
        This function returns the decorator to use.
        prefix (resp. suffix) is the string that we must put before (resp. after)
        the python function name to build the name of the function contained
        in the shared library.

        If castInput is True, input values are cast into the right dtype before
        being used.

        If indexing is 'C' (default), array indexes are in the C order whereas if it is 'F'
        indexes are in the same order as in the FORTRAN subroutine.

        Please refer to ctypesForFortranFactory for a complete documentation.
        """

        assert indexing in ('F', 'C'), "indexing must be 'F' or 'C'"

        def decorator(func):
            """
            This function must be used as a decorator.
            True python function is called to determine the signature of the
            underlying fortran function of same name contained in the shared library.
            Input values are checked against the signature.
            Arguments are preapred to be passed to the fortran routine and
            output arguments are processed to be retrun by the python function.

            Please refer to ctypesForFortranFactory for a complete documentation.
            """

            def wrapper(*args, **kwargs):
                sorted_args, signature, ret = func(*args, **kwargs)
                assert isinstance(signature, list), "signature must be a list"
                assert all(sig is None or isinstance(sig, tuple) for sig in signature), \
                    "all elements of the signature must be a tuple"
                if not all(sig[0] in [str, bool, numpy.int64,
                                    numpy.float64, numpy.int32, numpy.float32,
                                    MISSING] for sig in signature):
                    raise NotImplementedError("This type is not (yet?) implemented")
                assert all(sig[1] is None or isinstance(sig[1], tuple) for sig in signature), \
                    "second element of argument signature must be None or a tuple"
                assert all(len(sig[1]) > 0 for sig in signature if isinstance(sig[1], tuple)), \
                    "if second element of argument is a tuple, it must not be empty"
                assert all(all((isinstance(item, (int, numpy.int64)) and
                                item >= 0) for item in sig[1])
                            for sig in signature if isinstance(sig[1], tuple)), \
                    "if second element of argument is a tuple, it must contain " + \
                    "only positive or null integer values"
                assert all(sig[2] in [IN, INOUT, OUT] for sig in signature), \
                    "third element of argument signature must be IN, INOUT or OUT"

                assert len(sorted_args) == len([sig for sig in signature
                                                if sig[2] in [IN, INOUT]]), \
                    "Get " + str(len(sorted_args)) + " arguments, " + \
                    str(len([sig for sig in signature if sig[2] in [IN, INOUT]])) + " expected."

                argtypes = []
                effective_args = []
                result_args = []
                iarg_in = 0
                for sig in signature:
                    if sig[2] in (IN, INOUT) and sorted_args[iarg_in] is MANDATORY_AFTER_OPTIONAL:
                        raise ValueError("Arguments intiailised with " + \
                                         "MANDATORY_AFTER_OPTIONAL must be set")
                    if sig[0] == str:
                        if not isinstance(sig[1], tuple):
                            raise ValueError("Signature for string must provide a length")
                    if sig[2] in (IN, INOUT) and sorted_args[iarg_in] is MISSING:
                        iarg_in += 1
                        argtypes.append(ctypes.POINTER(ctypes.c_voidp))
                        effective_args.append(None)
                        if sig[2] == INOUT:
                            result_args.append(None)
                    elif sig[2] == OUT and sig[0] is MISSING:
                        argtypes.append(ctypes.POINTER(ctypes.c_voidp))
                        effective_args.append(None)
                        result_args.append(None)
                    elif sig[0] == str and len(sig[1]) == 1:
                        argtypes.append(ctypes.c_char_p)
                        if sig[2] in [IN, INOUT]:
                            argument = sorted_args[iarg_in].encode("utf-8")
                            iarg_in += 1
                            if len(argument) > sig[1][0]:
                                raise ValueError("String is too long (#arg " + str(iarg_in) + ")")
                            argument = ctypes.create_string_buffer(argument.ljust(sig[1][0]))
                        else:
                            argument = ctypes.create_string_buffer(sig[1][0])
                        effective_args.append(argument)
                        if sig[2] in [OUT, INOUT]:
                            result_args.append(argument)
                    else:
                        if sig[1] is None:
                            # scalar value
                            if sig[0] == bool:
                                cl = ctypes.c_int8
                            elif sig[0] == numpy.int64:
                                cl = ctypes.c_longlong
                            elif sig[0] == numpy.float64:
                                cl = ctypes.c_double
                            elif sig[0] == numpy.int32:
                                cl = ctypes.c_long
                            elif sig[0] == numpy.float32:
                                cl = ctypes.c_float
                            else:
                                raise NotImplementedError("This scalar type is not yet implemented")
                            argtypes.append(ctypes.POINTER(cl))
                            if sig[2] in [IN, INOUT]:
                                if sig[0] == bool:
                                    if sorted_args[iarg_in]:
                                        argument = logical.true
                                    else:
                                        argument = logical.false
                                else:
                                    argument = sorted_args[iarg_in]
                                if castInput:
                                    argument = sig[0](argument)
                                argument = cl(argument)
                                iarg_in += 1
                            else:
                                argument = cl()
                            effective_args.append(ctypes.byref(argument))
                            if sig[2] in [OUT, INOUT]:
                                result_args.append(argument)
                        else:
                            # Arrays
                            if sig[0] == str:
                                expected_dtype = numpy.dtype(('S', sig[1][0]))
                                effective_dtype = expected_dtype
                                expected_shape = sig[1][1:]
                            else:
                                if sig[0] == bool:
                                    expected_dtype = sig[0]
                                    effective_dtype = numpy.int8
                                else:
                                    expected_dtype = sig[0]
                                    effective_dtype = expected_dtype
                                expected_shape = sig[1]
                            if sig[2] in [IN, INOUT]:
                                argument = sorted_args[iarg_in]
                                if castInput:
                                    argument = argument.astype(expected_dtype)
                                iarg_in += 1
                                if not isinstance(argument, numpy.ndarray):
                                    raise ValueError("Arrays must be numpy.ndarrays " +
                                                     "(argument #" + str(iarg_in - 1) + ")")
                                if argument.dtype != expected_dtype:
                                    raise ValueError("Wrong dtype for #arg " + str(iarg_in - 1))
                                if len(expected_shape) != len(argument.shape):
                                    raise ValueError("Wrong rank for input array (#arg " +
                                                     str(iarg_in - 1) + ")")
                                if expected_shape != argument.shape:
                                    raise ValueError("Wrong shape for input array (#arg " +
                                                     str(iarg_in - 1) + "), get " +
                                                     str(argument.shape) +
                                                     ", expected " + str(expected_shape))
                                if sig[0] == str:
                                    argument = numpy.char.ljust(argument, sig[1][0])
                                elif sig[0] == bool:
                                    arr = numpy.empty_like(argument, dtype=numpy.int8,
                                                           order=indexing)
                                    arr[argument] = logical.true
                                    arr[numpy.logical_not(argument)] = logical.false
                                    argument = arr
                                if indexing == 'F' and not argument.flags['F_CONTIGUOUS']:
                                    argument = numpy.asfortranarray(argument)
                                elif indexing == 'C' and not argument.flags['C_CONTIGUOUS']:
                                    argument = numpy.ascontiguousarray(argument)
                            else:
                                argument = numpy.ndarray(expected_shape, dtype=effective_dtype,
                                                         order=indexing)
                                if indexing == 'F' and sig[0] == str:
                                    argument = numpy.char.ljust(argument, sig[1][0])
                                    argument = numpy.asfortranarray(argument)
                            contiguity = 'F_CONTIGUOUS' if indexing == 'F' else 'C_CONTIGUOUS'
                            contiguity = str(contiguity) # Note: str() needed in Python2 for
                                                         # unicode/str obscure incompatibility
                            argtypes.append(numpy.ctypeslib.ndpointer(dtype=effective_dtype,
                                                                      ndim=len(argument.shape),
                                                                      flags=contiguity))
                            effective_args.append(argument)
                            if sig[2] in [OUT, INOUT]:
                                result_args.append(argument)
                sub = my_solib.__getitem__(prefix + func.__name__ + suffix)
                sub.argtypes = argtypes
                if ret is not None:
                    assert len(ret) == 2, "returned value must be described by a two-values tuple"
                    if ret[1] is None or (ret[0] == str and len(ret[1]) == 1):
                        if ret[0] == bool:
                            cl = ctypes.c_int8
                        elif ret[0] == numpy.int64:
                            cl = ctypes.c_longlong
                        elif ret[0] == numpy.float64:
                            cl = ctypes.c_double
                        elif ret[0] == numpy.int32:
                            cl = ctypes.c_long
                        elif ret[0] == numpy.float32:
                            cl = ctypes.c_float
                        elif ret[0] == str:
                            cl = ctypes.c_char_p
                            raise NotImplementedError("Functions with string as output " + \
                                                      "value are not working")
                        else:
                            raise NotImplementedError("This scalar type is not (yet?) implemented")
                        argument = cl
                    else:
                        raise NotImplementedError("Functions with arrays as output are not working")
                        #assert isinstance(ret[1], tuple), \
                        #    "if second element of returned value " + \
                        #    "signature is not None, it must be a tuple"
                        #if ret[0] == str:
                        #    dtype = numpy.dtype(('S', ret[1][0]))
                        #    ctype = ctypes.c_char_p
                        #    shape = ret[1][1:]
                        #elif ret[0] == bool:
                        #    dtype = numpy.int8
                        #    ctype = ctypes.c_int8
                        #    shape = ret[1]
                        #else:
                        #    dtype = ret[0]
                        #    shape = ret[1]
                        #    if ret[0] == numpy.int64:
                        #        ctype = ctypes.c_longlong
                        #    elif ret[0] == numpy.float64:
                        #        ctype = ctypes.c_double
                        #result = numpy.ndarray(shape=shape, dtype=dtype)
                        #argument = result.ctypes.data_as(ctypes.POINTER(ctype))
                        #argument = ctypes.POINTER(ctype)
                        #argument = numpy.ctypeslib.ndpointer(dtype=dtype, shape=shape)

                    sub.restype = argument

                val = sub(*effective_args)

                if ret is not None:
                    if ret[0] == bool:
                        result = [val != logical.false]
                    else:
                        result = [val]
                else:
                    result = []
                iarg_out = 0
                for sig in signature:
                    if sig[2] in [OUT, INOUT]:
                        argument = result_args[iarg_out]
                        iarg_out += 1
                        if argument is not None:  # missing optional argument
                            if sig[0] == str and len(sig[1]) == 1:
                                argument = argument.value.decode('utf-8')
                            elif sig[1] is None:
                                # scalar
                                if sig[0] == bool:
                                    argument = argument.value != logical.false
                                else:
                                    argument = argument.value
                            else:
                                # array
                                if sig[0] == bool:
                                    argument = argument != logical.false
                                # If needed, we could reverse contiguity here
                                # (we then would need to track those changes)
                            # FIXME The use of repr fixes problems that occur
                            #       with epygram's testing procedure.
                            repr(argument)
                            result.append(argument)
                if len(result) > 1:
                    return tuple(result)
                if len(result) == 1:
                    return result[0]
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper
        return decorator
    return ctypesFF, my_solib._handle  # pylint: disable=protected-access


def fortran2signature(filename=None, fortran_code=None, as_string=True,
                      kind_real=None, kind_logical=None, kind_integer=None,
                      prefix="", suffix="", solib=None, only=None, indexing='C', **kwargs):
    """
    This functions returns the signature as a string (if as_string) or as a python object.
    In this later case, in variables must be put in **kwargs.
    The default kind (specified by compilation options) can be provided for real,
    logical and integer.
    prefix and suffix are used to build the symbol name to use in the shared lib (use %s in
    these strings as a placeholder for the module name)

    By default, signature for all symbols are built, you can limit to one subroutine or function
    by specifying its name in the only argument.
    When using this function with as_string, this argument becomes mandatory.

    signature is the signature as expected by ctypesForFortran.

    one of filename or fortran_code is mandatory

    Function was tested only against fortran code with relatively simple formatting,
    there are certainly issues with real fortran code.

    With indexing='C' (default) the index order of python arrays is the reverse of the
    index order of FORTRAN arrays. Index order is the same if indexing=='F'.

    Example: the command line
    ctypesForFortran.py --solib=./foo.so --suffix="_" --kind_real 8 \
                        --kind_integer 8 --kind_logical 1 foo.F90
    outputs a python script that may be used in place of the signature part of the python code
    given as example in the ctypesForFortranFactory function (except that, in the example,
    order of argument for foo subroutine have been changed).

    Alternatively, the signature part of the same example (given in the ctypesForFortranFactory
    function) can be replaced by something like:
    with open('foo.F90', 'r') as f:
        fortran = f.read()

    @ctypesFF()
    def f_int(KIN):
        return ctypesForFortran.fortran2signature(fortran_code=fortran, as_string=False,
                                                  prefix="", suffix="_", only='f_int', kin=KIN)

    @ctypesFF()
    def f_real(PIN):
        return ctypesForFortran.fortran2signature(fortran_code=fortran, as_string=False,
                                                  prefix="", suffix="_", only='f_real', PIN=PIN)

    @ctypesFF()
    def f_bool(LIN):
        return ctypesForFortran.fortran2signature(fortran_code=fortran, as_string=False,
                                                  prefix="", suffix="_", only='f_bool', LIN=LIN)

    @ctypesFF()
    def foo(KIN, KINOUT,    # Integer scalars  # Only IN and INOUT variabes.
            PIN, PINOUT,    # Float scalars    #
            LIN, LINOUT,    # Logical scalars  # The order can be different than the
            CDIN, CDINOUT,  # Strings          # one expected by the fortran routine.
            CDAIN, CDAINOUT,# String arrays    # Here we put the scalars first, then
            KAIN, KAINOUT,  # Integer arrays   # the arrays, whereas this is not the
            PAIN, PAINOUT,  # Float arrays     # order declared in fortran code.
            LAIN, LAINOUT,  # Logical arrays   #
            KAIN2):         # 2D integer arrays#
        return ctypesForFortran.fortran2signature(fortran_code=fortran, as_string=False,
                                                  prefix="", suffix="_", only='foo',
                                                  kind_logical=1,
                                                  KIN=KIN, KINOUT=KINOUT,
                                                  PIN=PIN, PINOUT=PINOUT,
                                                  LIN=LIN, LINOUT=LINOUT,
                                                  CDIN=CDIN, CDINOUT=CDINOUT,
                                                  CDAIN=CDAIN, CDAINOUT=CDAINOUT,
                                                  KAIN=KAIN, KAINOUT=KAINOUT,
                                                  PAIN=PAIN, PAINOUT=PAINOUT,
                                                  LAIN=LAIN, LAINOUT=LAINOUT,
                                                  KAIN2=KAIN2)
    """
    assert filename is not None or fortran_code is not None, \
           "one of filename or fortran_code must be provided"
    assert not (filename is not None and fortran_code is not None), \
           "one of filename or fortran_code must be None"
    assert len(kwargs) == len({k.lower() for k in kwargs}), \
           "fortran variables are case-insensitive"
    assert as_string is False or solib is not None, "solib is required if as_string"
    assert as_string or only is not None, "only must be specified when as_string is False"

    if filename is not None:
        with open(filename, 'r') as f:
            fortran_code = f.read()

    # lines will contain the source code split by instructions
    lines_tmp = fortran_code.splitlines()
    lines = []
    line = ''
    ind = 0
    in_str = False
    while len(lines_tmp) > 0:
        if line == '':
            line = lines_tmp.pop(0).strip()
            ind = 0
        # Look for first (if any) interesting character among ', ", #, &
        sep = re.search('\'|"|&|!|;', line[ind:])
        if sep is None:
            if line.strip() != "":
                lines.append(line.strip())
            line = ''
        else:
            char = sep.group()
            if char == '!' and not in_str:
                lines.append(line.strip())
                line = ''
            elif char == '&':
                if in_str and line[ind + line[ind:].find(char) - 1] == '\\':
                    # do not count
                    ind = ind + line[ind:].find(char) + 1
                else:
                    # not in str or true continuation character
                    after = line[(ind + line[ind:].find(char) + 1):].strip()
                    if not (after == "" or after[0] == "!"):
                        raise RuntimeError("& followed by something")
                    line = line[:ind + line[ind:].find(char)].strip()
                    nextline = lines_tmp.pop(0).strip()
                    if not in_str:
                        line += " "
                    if nextline.startswith('&'):
                        line += nextline[nextline.find('&') + 1:]
                    else:
                        line += nextline
            elif char == ';' and not in_str:
                lines.append(line[:ind + line[ind:].find(char)].strip())
                line = line[ind + line[ind:].find(char) + 1:]
                ind = 0
            elif char in ['"', "'"]:
                if not in_str:
                    # Beginning of string
                    ind = ind + line[ind:].find(char) + 1
                    in_str = char
                else:
                    if char != in_str:
                        # quote or double quote in string
                        ind = ind + line[ind:].find(char) + 1
                    elif line[ind + line[ind:].find(char) - 1] == '\\':
                        # not the end of string
                        ind = ind + line[ind:].find(char) + 1
                    else:
                        # This is the end of string
                        ind = ind + line[ind:].find(char) + 1
                        in_str = False

    objs = []  # each item is a dict with keys: module, name,
               # in_var_names (list of in var names), signatures (list of signatures),
               # result (result signature)
    low_kwargs = {k.lower():v for k, v in kwargs.items()}
    in_module = False
    in_function = False
    in_subroutine = False
    path = []
    select = {('real', 2): numpy.float16,
              ('real', 4): numpy.float32,
              ('real', 8): numpy.float64,
              ('integer', 1): numpy.int8,
              ('integer', 2): numpy.int16,
              ('integer', 4): numpy.int32,
              ('integer', 8): numpy.int64,
              ('logical', 1): bool}
    for line in lines:
        if line.lower().startswith('module') and line[6] in [" ", "\t"]:
            if in_module:
                raise RuntimeError("Already in module")
            in_module = line[6:].lower().strip()
        elif line.lower().startswith('subroutine') and line[10] in [" ", "\t"]:
            name = line[10:]
            name = name[:name.find('(')].lower().strip()
            path.append(name)
            if len(path) == 1 and only in [None, name]:
                in_subroutine = name
                subargs = [arg.strip().lower()
                        for arg in line[line.find("(") + 1:line.find(")")].split(",")]
                current_obj = {'module': in_module if in_module else "",
                               'name': in_subroutine,
                               'var_names': subargs,
                               'signature': {},
                               'result': None,
                               'must_be_in': set(),
                               'intents': {},
                               'result_name': None}
        elif line.lower().startswith('function') and line[8] in [" ", "\t"]:
            name = line[8:]
            name = name[:name.find('(')].lower().strip()
            path.append(name)
            if len(path) == 1 and only in [None, name]:
                in_function = name
                subargs = [arg.strip().lower()
                        for arg in line[line.find("(") + 1:line.find(")")].split(",")]
                current_obj = {'module': in_module if in_module else "",
                               'name': in_function,
                               'var_names': subargs,
                               'signature': {},
                               'result': None,
                               'must_be_in': set(),
                               'intents': {},
                               'result_name': None}
                result_name = line[line.find(")") + 1:].strip()
                if len(result_name) > 0:
                    if not result_name.startswith("result"):
                        raise RuntimeError("Something after the function definition " + \
                                           "which is not the result?")
                    result_name = result_name[result_name.find("(") + 1:result_name.find(")")]
                    current_obj['result_name'] = result_name
                else:
                    current_obj['result_name'] = in_function
        elif '::' in line and (in_subroutine or in_function) and len(path) == 1:
            end = len(line) if '!' not in line else line.find('!')
            subargs = [arg.strip().lower() for arg in line[line.find('::') + 2:end].split(',')]
            options_tmp = [opt.strip().lower() for opt in line[:line.find('::')].split(',')]
            options = []
            while len(options_tmp) > 0:
                opt = options_tmp.pop(0)
                if '(' in opt:
                    while ')' not in opt:
                        opt += ", " + options_tmp.pop(0)
                options.append(opt)
            dtype = None
            shape = []
            intent = None
            for arg in subargs:
                if arg in current_obj['var_names'] + \
                          ([current_obj['result_name']] if in_function else []):
                    if arg in current_obj['signature']:
                        raise RuntimeError("arg already declared: " + arg)
                    if dtype is None:
                        decode_kind = False
                        for opt in options:
                            decode_kind = False
                            if opt.startswith("dimension") and opt[9] in [' ', '\t', '(']:
                                dimshape = []
                                dimensions = [item.strip() for item
                                              in opt[opt.find('(') + 1:opt.find(')')].split(',')]
                                for dim in dimensions:
                                    if dim in current_obj['var_names']:
                                        current_obj['must_be_in'].add(dim)
                                        if not as_string:
                                            if dim not in low_kwargs:
                                                raise ValueError(dim + "must be in kwargs")
                                            dim = low_kwargs[dim]
                                    else:
                                        dim = int(dim)
                                    dimshape.append(str(dim) if as_string else dim)
                                shape = shape + (dimshape if indexing == 'F' else dimshape[::-1])
                            elif opt.startswith("intent") and opt[6] in [' ', '\t', '(']:
                                intent = opt[opt.find('(') + 1:opt.find(')')].upper()
                                if intent not in ['IN', 'OUT', 'INOUT']:
                                    raise RuntimeError("intent must be IN, OUT or INOUT")
                                if not as_string:
                                    intent = {'IN':IN, 'OUT':OUT, 'INOUT':INOUT}[intent]
                                current_obj['intents'][arg] = intent
                            elif opt == 'optional':
                                raise RuntimeError("optional argument are not allowed")
                            elif opt.startswith("real") and \
                                 (len(opt) == 4 or opt[4] in [' ', '\t', '(']):
                                dtype = "real"
                                decode_kind = True
                            elif opt.startswith("integer") and \
                                 (len(opt) == 7 or opt[7] in [' ', '\t', '(']):
                                dtype = "integer"
                                decode_kind = True
                            elif opt.startswith("logical") and \
                                 (len(opt) == 7 or opt[7] in [' ', '\t', '(']):
                                dtype = "logical"
                                decode_kind = True
                            elif opt.startswith("character") and \
                                 (len(opt) == 9 or opt[9] in [' ', '\t', '(']):
                                if as_string:
                                    dtype = "str"
                                else:
                                    dtype = str
                                length = '1'
                                if '(' in opt:
                                    for char_opt in opt[opt.find('(') + 1:opt.find(')')
                                                       ].replace(' ', '').split(','):
                                        if char_opt.split('=')[0] == 'kind':
                                            pass
                                        else:
                                            if not char_opt.startswith('len'):
                                                raise RuntimeError(
                                                    "character length must start with len")
                                            length = char_opt[3:].strip()
                                            if length[0] != '=':
                                                raise RuntimeError(
                                                    "character length must start with len=")
                                            length = length[1:]
                                if length in current_obj['var_names']:
                                    current_obj['must_be_in'].add(length)
                                    if not as_string:
                                        if length not in low_kwargs:
                                            raise ValueError(length + "must be in kwargs")
                                        length = low_kwargs[length]
                                else:
                                    length = int(length)
                                shape = [str(length) if as_string else length] + shape
                            if decode_kind:
                                kind = None
                                if '(' in opt:
                                    kind = opt[opt.find('(') + 1:opt.find(')')].strip()
                                    if not kind.startswith('kind'):
                                        raise RuntimeError("kind specification must " + \
                                                           "start with kind")
                                    kind = kind[4:].strip()
                                    if kind[0] != "=":
                                        raise RuntimeError("kind specification must " + \
                                                           "start with kind=")
                                    kind = kind[1:].strip()
                                    if kind in current_obj['var_names']:
                                        current_obj['must_be_in'].add(kind)
                                        if not as_string:
                                            if kind not in low_kwargs:
                                                raise ValueError(kind + "must be in kwargs")
                                            kind = low_kwargs[kind]
                                    else:
                                        # kind must be an int
                                        kind = int(kind)
                                else:
                                    if dtype == 'real' and kind_real is not None:
                                        kind = kind_real
                                    elif dtype == 'integer' and kind_integer is not None:
                                        kind = kind_integer
                                    elif dtype == 'logical' and kind_logical is not None:
                                        kind = kind_logical
                                if as_string:
                                    dtype = "select[('" + dtype + "', " + str(kind) + ")]"
                                else:
                                    if (dtype, kind) not in select:
                                        raise NotImplementedError("This kind is not " + \
                                                                  "implemented: " + \
                                                                  str((dtype, kind)))
                                    dtype = select[(dtype, kind)]
                        if dtype is None:
                            raise RuntimeError("declaration of arg " + arg + \
                                               " does not provide type information")
                        if intent is None and arg != current_obj['result_name']:
                            raise RuntimeError("declaration of arg " + arg + \
                                               " does not provide intent IN/OUT information")
                    if as_string:
                        if len(shape) == 0:
                            shape = "None"
                        else:
                            shape = '(' + ', '.join(shape) + ', )'
                        if arg == current_obj['result_name']:
                            current_obj['signature'][arg] = "(" + dtype + "," + shape + ")"
                        else:
                            current_obj['signature'][arg] = "(" + dtype + "," + shape + \
                                                            "," + intent + ")"
                    else:
                        shape = tuple(shape)
                        if arg == current_obj['result_name']:
                            current_obj['signature'][arg] = (dtype, shape)
                        else:
                            current_obj['signature'][arg] = (dtype, shape, intent)
        elif len(line.lower().split()) > 1 and \
             line.lower().split()[0:2] in [['end', 'subroutine'], ['end', 'function']]:
            if len(path) == 1 and (in_subroutine or in_function):
                current_obj['in_var_names'] = []
                current_obj['signatures'] = []
                for arg in current_obj['var_names']:
                    if arg not in current_obj['signature']:
                        raise RuntimeError("arg not found in declaration: " + arg)
                    if current_obj['intents'][arg] in ['IN', 'INOUT', IN, INOUT]:
                        current_obj['in_var_names'].append(arg)
                    current_obj['signatures'].append(current_obj['signature'][arg])
                if in_function:
                    current_obj['result'] = current_obj['signature'][current_obj['result_name']]
                    del current_obj['signature'][current_obj['result_name']]
                if current_obj['result'] is None and as_string:
                    current_obj['result'] = "None"
                for arg in current_obj['must_be_in']:
                    if arg not in current_obj['in_var_names']:
                        raise RuntimeError("An argument (" + arg + ") with INTENT(OUT) " + \
                                           "has been used for kind or dimension")
                del current_obj['signature'], current_obj['var_names'], \
                    current_obj['must_be_in'], current_obj['intents']
                objs.append(current_obj)
                in_subroutine = False
                in_function = False
            path = path[:-1]
        elif line == 'contains':
            pass

    if as_string:
        result = "import numpy\nimport ctypesForFortran\n\n"
        result += "IN = ctypesForFortran.IN\n"
        result += "OUT = ctypesForFortran.OUT\n"
        result += "INOUT = ctypesForFortran.INOUT\n\n"
        result += "select = {('real', 2): numpy.float16,\n"
        result += "          ('real', 4): numpy.float32,\n"
        result += "          ('real', 8): numpy.float64,\n"
        result += "          ('integer', 1): numpy.int8,\n"
        result += "          ('integer', 2): numpy.int16,\n"
        result += "          ('integer', 4): numpy.int32,\n"
        result += "          ('integer', 8): numpy.int64,\n"
        result += "          ('logical', 1): bool}\n\n"
        result += "pre_suf = {}\n"
        for module_name in {obj['module'] for obj in objs}:
            result += "pre_suf['" + module_name + "'] = ('"
            result += ((prefix % module_name) if '%s' in prefix else prefix) + "', '"
            result += ((suffix % module_name) if '%s' in suffix else suffix) + "')\n"
        result += "\n\n"
        result += "ctypesFF, handle = ctypesForFortran.ctypesForFortranFactory('" + solib + "')\n\n"
        for obj in objs:
            result += "@ctypesFF(*pre_suf['" + obj['module'] + "'], indexing='" + indexing + "')\n"
            result += "def " + obj['name'] + "(" + ', '.join(obj['in_var_names']) + "):\n"
            result += "    return ([" + ', '.join(obj['in_var_names']) + "],\n"
            result += "            [" + ',\n             '.join(obj['signatures']) + "],\n"
            result += "            " + obj['result'] + ")\n\n"
    else:
        if len(objs) != 1:
            raise ValueError("The searched symbol was not found")
        obj = objs[0]
        result = ([low_kwargs[arg] for arg in obj['in_var_names']],
                  obj['signatures'],
                  obj['result'])

    return result


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Simple fortran parser which produce signature")
    parser.add_argument('filename', metavar='filename', type=str, nargs=1,
                        help='file name of the file containing the fortran code to parse')
    parser.add_argument('--kind_real', type=int, default=None,
                        help='Kind to use for reals when not specified in declaration')
    parser.add_argument('--kind_integer', type=int, default=None,
                        help='Kind to use for integers when not specified in declaration')
    parser.add_argument('--kind_logical', type=int, default=None,
                        help='Kind to use for logicals when not specified in declaration')
    parser.add_argument('--prefix', type=str, default="",
                        help='prefix to add to the python function name to build the symbol ' + \
                             'name as found in the shared lib')
    parser.add_argument('--suffix', type=str, default="",
                        help='suffix to add to the python function name to build the symbol ' + \
                             'name as found in the shared lib')
    parser.add_argument('--Findexing', default=False, action='store_true',
                        help='Use FORTRAN indexing instead of C indexing')
    parser.add_argument('--solib', type=str, required=True,
                        help='path the shared lib')
    args = parser.parse_args()
    print(fortran2signature(filename=args.filename[0], kind_real=args.kind_real,
                            kind_logical=args.kind_logical, kind_integer=args.kind_integer,
                            prefix=args.prefix, suffix=args.suffix, solib=args.solib,
                            indexing='F' if args.Findexing else 'C'))
