===========================                         ============================
                         ASTRONOMIE ET SYSTEMES DYNAMIQUES
                         
                         INSTITUT DE MECANIQUE CELESTE

                                    la2003

                                2010, January 18 
===========================                         ============================



The program insola is derived from the same program from
the Earth paleoclimate solution La93 (Laskar, Joutel, Boudin, 1993) with 
several differences.

The utilisation has been greatly simplified, as everything is now 
in a single application, insola, that allows to compute all 
insolation quantities for any time interval between the limits 
of the input files defined in insola.par (nomclimapos, nomclimaneg).

Once the application is generated, the only file to edit is 
insola.par.


We have provided two solutions with very close initial parameters
La2003, and La2004. from -20 to + 10 Myr.
La2004 should be the most up to date solution, but the difference
gives an idea of the precision of the solution.

We have also provide solutions over much longer times (200 Myr)
for the same quantities for 5 different examples taken from 
(Laskar et al., 2003) which represent some typical and extreme 
behavior of the obliquity. They could be use to test climate models 
under  various obliquity regimes.





La2003    : 
==========

Main reference :
Laskar, J., Gastineau, M., Joutel, F., Robutel, P., Levrard, B., Correia, A.,: 2003,
Long term evolution and chaotic diffusion of the insolation quantities of Mars.
{\it in preparation}


********************************************************************************
*  Authors: J. Laskar, M. Gastineau, F. Joutel                                 *
*  (c) Astronomie et Systemes Dynamiques, Institut de Mecanique Celeste,       *
*      Paris (2003)                                                            *
*                                                                              *
*                               Jacques Laskar                                 *
*                               Astronomie et Systemes Dynamiques,             *
*                               Institut de Mecanique Celeste                  *
*                               77 av. Denfert-Rochereau                       *
*                               75014 Paris                                    *
*                       email:  laskar@imcce.fr                                *
*                                                                              *
********************************************************************************




CONTAINS:
=========



File Summary:
--------------------------------------------------------------------------------
 FileName                 Explanations
--------------------------------------------------------------------------------
README                    This file
INSOLN.LA2003.MARS.ASC    Nominal solution La2003,
                                    before present years (-21Myr to 0)
INSOLP.LA2003.MARS.ASC    Nominal solution La2003
                                    after present years (0 to +11Myr)

INSOLN.LA2004.MARS.ASC    solution La2004,
                                    before present years (-21Myr to 0)
INSOLP.LA2004.MARS.ASC    solution La2004
                                    after present years (0 to +11Myr)

Makefile                  to compile and generate derived files
insola.par                Parameter file for insola.
insola.f                  FORTRAN program for computations of various
                                    insolation quantities
insolsub.f                subroutines for insola.f
prepsub.f                 FORTRAN subroutine for insola.f
prepinsol.f               FORTRAN subroutine for preparation step for insola.f
--------------------------------------------------------------------------------


Byte-per-byte Description of file: INSOLN.LA2003.MARS.ASC
Byte-per-byte Description of file: INSOLN.LA2003.MARS.ASC
Byte-per-byte Description of file: INSOLN.LA2004.MARS.ASC
Byte-per-byte Description of file: INSOLN.LA2004.MARS.ASC
--------------------------------------------------------------------------------
   Bytes Format  Units   Label    Explanations
--------------------------------------------------------------------------------
   1-14   F8.3   1000yr  t        Time from J2000  in 1000 years
  18-39   D23.16 ---     e        eccentricity
  43-64   D23.16 rad     eps      obliquity (radians)
  68-89   D23.16 rad     pibar    longitude of perihelion from moving equinox
                                  (radians)
--------------------------------------------------------------------------------


Description:

  La2003 is the nominal solution for precessional quantities and orbital quantities of 
  Mars. The solution La2003 is provided with fortran subroutine in order to 
  compute the insolation quantities of Mars.
  
  The nominal solution La2003 of Mars is obtained with the following constants
  (p from Folkner et al., 1997 ) :
  - tidal coefficents       : k2 = 0.14 
                              Q  = 50
  - initial precession rate : p  = -7.576 arcsec/year
  

  La2004 is the up to date insolation solution with initial conditions 
  from (Yoder et al, 2003).
  
  The nominal solution La2003 of Mars is obtained with the following constants :
  - tidal coefficents       : k2 = 0.149 
                              Q  = 92
  - initial precession rate : p  = -7.597 arcsec/year


BIBLIOGRAPHY:
============



  La90: Laskar, J.: 1990, The chaotic motion of the solar system.
                  A numerical estimate of the chaotic zones
                  Icarus, 88, 266

  La93: Laskar, J., Joutel, F., Boudin, F.: 1993, Orbital, precessional
                  and insolation quantities for the Earth
                  from -20 Myr to + 10Myr
                  Astron. Astrophys. 270, 522

  La2003 :Laskar, J., Gastineau, M., Joutel, F., Robutel, P., Levrard, B., 
                  Correia, A.,
                  Long term evolution and chaotic diffusion of the insolation 
                  quantities of Mars. {\it in preparation}



================================================================================


================================================================================
Compilation of the Program
--------------------------

  Edit the makefile to choose a fortran-90 compiler and run "make".




Detailed Description of the Program
-----------------------------------

  insola.par : THE USER should edit the file insola.par to set
          all parameters.

  insola : interactive insolation computations


--------------------------------------------------------------------------------
INSOLA.PAR

The user should edit the parameter file insola.par.

 datefin   : ending   time (Myr)
 datedebut : starting time (Myr)
 pas       : sampling step (in years). 
             The default value is 1000. The minimum step is 1 year
             (it is usually not necessary for pas to be smaller than 100 (yr)). 
 nominsolbin   : Binary intermediate file for insolation
 nomclimapos : ASCII file for climatic variables for positive time  
 nomclimaneg : ASCII file for climatic variables for negative time
 so          : Solar constant expressed in W/m2 
               for Mars mean semimajor axis  a4= 1.523679335D0 AU
               and solar constant at 1 AU so0 =1368 W/m2
               so = so0 /a4^2 = 589.2 W/m2
 

Starting and ending date must verify :   -10 <= datedebut <= 0 <= datefin <= +20 
The user may restrict himself to e.g. -2Myr to 0 by putting instead
     datedebut=-2.D0
     datefin=0.D0



--------------------------------------------------------------------------------
INSOLA

  The routines insola are designed to compute all
  necessary insolation quantities derived from the orbital and
  precessional quantities computed above.

  They are given on the form of FORTRAN code, so the user can check
  if they correspond to his needs. He can also design his own insolation
  routines.

  Insola will construct a binary intermediate file 
  when this file is not present before computations.

  insola is a self documented program
  For more details, the user can refer to  (Laskar et al, 2003)

================================================================================
History
-------
 2010/01/15 : fix bug in the function vraimoy and truncate the developpement at the order 5

================================================================================
User feed-back is encouraged. Unless otherwise specified, send comments and bug 
reports to:                    E-mail     : laskar@imcce.fr
                               Fax        : (33) 1 40 51 20 55
                               Postal mail: Institut de Mecanique Celeste
                                            77 avenue Denfert Rochereau
                                            F-75014 PARIS
================================================================================
