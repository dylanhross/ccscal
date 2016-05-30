"""
	>>>ccscal_input_TEMPLATE.py<<<
	Dylan H. Ross
"""
###############################
# --> GENERAL INFORMATION <-- #
###############################

# report_file_name:
#		Desired FULL PATH and filename of ccscal report file 
#			e.g. "/home/dilly/workspace/sandbox/20160427_ccscal_report.txt"
#		* Do not forget to use quotes surrounding the path 					*
report_file_name="/Users/DylanRoss/Desktop/ccscal-test-suite/ccscal-report.txt"

# edc:
#		EDC delay coefficient
edc=1.35

# mass_epsilon:
#		mass window to filter for desired masses (+/-)
#		* number MUST BE A DECIMAL not an integer (i.e. 1.0 instead of 1)	*
mass_window=0.5


#################################
# --> CALIBRANT INFORMATION <-- #
#################################

# calibrant_data_file: 
#		FULL PATH to calibrant data file
#			e.g. "/home/dilly/workspace/sandbox/polyALA_CCS_calibration.txt"
#		* Do not forget to use quotes surrounding the path 					*
calibrant_data_file="/Users/DylanRoss/Desktop/ccscal-test-suite/IM_Polyalanine_50-2000-2016-05-11-10-20-1.txt"

# calibrant_masses:
#		A list of the EXACT masses for the calibrants, in ascending order
#		* Each m/z value must end with a ,\ WITH NO SPACES AFTER 			*
#		* The final m/z value must end with a \ with NO SPACES AFTER  		*
calibrant_masses=[\
##########################
# DO NOT EDIT ABOVE HERE #
232.13,\
303.167,\
374.204,\
445.241,\
516.278,\
587.315,\
658.352,\
729.389,\
800.426,\
871.463,\
942.501,\
1013.537,\
1084.574,\
1155.611,\
1226.648,\
1297.685,\
1368.722,\
1439.759\
# DO NOT EDIT BELOW HERE #
##########################
]

# calibrant_literature_ccs:
#		A list of literature CCS values for the calibrants, in ascending order
#		* Units of literature CCS values must be in ANG^2				 	*
#		* each CCS value must end with a ,\ WITH NO SPACES AFTER 			* 
#		* The final CCS value must end with a \ with NO SPACES AFTER  		*
calibrant_literature_ccs=[\
##########################
# DO NOT EDIT ABOVE HERE #
151,\
166,\
181,\
195,\
211,\
228,\
243,\
256,\
271,\
282,\
294,\
306,\
322,\
335,\
348,\
361,\
374,\
387\
# DO NOT EDIT BELOW HERE #
##########################
]

# calibration_figure_file_name:
#		Desired FULL PATH and file name to save the calibration curve figure under
#			e.g. "/home/dilly/workspace/sandbox/20160427_ccs_calibration_curve.png"
#		* Do not forget to use quotes surrounding the path 					*
calibration_figure_file_name="/Users/DylanRoss/Desktop/ccscal-test-suite/cal-curve.png"


################################
# --> COMPOUND INFORMATION <-- #
################################

# compound_root_directory: 
#		PATH to directory data files are contained in
#			e.g. "/home/dilly/workspace/sandbox/"
#		* Do not forget to use quotes surrounding the path 					*
compound_root_directory="/Users/DylanRoss/Desktop/ccscal-test-suite/"

# compound_data_files_and_masses:
#		A list of paired data file names and the masses to extract drift times for
#			e.g. ["data_file1.txt", 232.1320]
#		* Each paired entry must begin with [	     						*
#		* Each paired entry must end with  ],\ WITH NO SPACES AFTER 		*
#		* The final paired entry must end with ]\ with NO SPACES AFTER	  	*
#		* Do not forget to use quotes surrounding the file name				*
#		* Do not forget to separate the file name and mass with a comma		*
compound_data_files_and_masses=[\
##########################
# DO NOT EDIT ABOVE HERE #
["IM_0881Drug.txt",152.066],\
["IM_0881Drug.txt",250.1952],\
["IM_0881Drug.txt",294.1745],\
["IM_0881Drug.txt",343.1425],\
["IM_0881Drug.txt",455.3119],\
["IM_0881Drug.txt",609.3069],\
["IM_0881Drug.txt",734.4884],\
["IM_0881Drug.txt",1072.5385],\
["IM_0881Drug.txt",1448.5166]\
# DO NOT EDIT BELOW HERE #
##########################
]


