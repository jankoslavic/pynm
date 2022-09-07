1. Details of the experiment can be found here:

  J. Slavič, A. Brković and M. Boltežar
  Typical bearing-fault rating using force measurements: application to real data.
  Journal of Vibration and Control, December 2011 vol. 17 no. 14 2164-2174.
  dx.doi.org/10.1016/j.ymssp.2011.01.008
  
  In this directory the original data (http://goo.gl/g4Eyyi) was shortened from 10s to 2s.

  Please cite the above reference if you use the data.
  For more info, please contact me: janko.slavic@fs.uni-lj.si

2. The filenames are coded as: fault severity number side.npy (npy is the numpy binary format)
  For example: torque med 2B is used for the torque fault at med rate, the bearing nr 2 was
  prestressed in the B direction (alternatively to the A direction).


  2.1 The faults tested are

    torque load
    radial load
    axial load
    damaged shield 
    contamination in the lubricant
    a new bearing was also measured.

  2.2 severities tested
    min
    medium
    max
    
    The limits have been prepared with a bearing manufacturer: 
    min is considered OK, medium is considerd at the limit 
    (they would still sell such a bearing), 
    max is considered not ok

  2.3 number of samples
    two bearing have been prepared and measured per fault type

  2.4 presstress direction
    each bearing was prestressed in both directions (A and B)

3. File and data acquisition details

  In the colums are:
    force_x, force_y, force_z, opto_sensor

  force_z is the axial direction.
  opto_sensor has two switches per turn (not equally spaced).

  The sampling frequency is 5000Hz, the samples recorded: 50000 (originally, here only first 10000 samples are given).
  The bearing was always rotating at 4Hz.
