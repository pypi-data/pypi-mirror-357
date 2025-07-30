# Quicklst

Quicklst ist a python library for reading .lst files produced by FAST ComTec's mpa system. It uses numba to accelerate
the reading of the file and supports block or chunk wise loading of large files.

Limitations: Both MPA3 and MPA4A files are supported, but they need to be in binary form not in ASCII encoding, the real
time clock is not implemented either.

Basic usage is demonstrated in `examples/Quickstart.ipynb`.