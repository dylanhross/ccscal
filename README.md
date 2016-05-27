# ccscal
A program for extracting drift times from ion mobility-mass spec data and obtaining calibrated CCS 

	>>>CcsCal.py<<<
	Dylan H. Ross

		This program contains several utilities for processing raw mass-spec data with
		a drift time dimension: extracting drift time for a particular mass, creating
		a CCS calibration curve, obtaining calibrated CCS for a mass and drift time 
		using the CCS calibration curve.
		When called directly, this program refers to a specified input file and 
		automagically performs a CCS calibration then obtains calibrated CCS for all
		specified masses, printing a full report containing the results of the 
		calibration and CCS of all compounds. 	

		GetData -- Class
		
		Extracts and stores the raw data from a .txt data file:
			GetData.xlst 		- m/z values (list)
			GetData.ylst		- dtbin values (list)
			GetData.zlst		- intensity values (list)
		
		Input(s):
			data_filename		- file name of the raw data file (string)

		GetData.makeGll -- Method
		
		Generates a good_line_list containing only lines which begin with a number or a 
		a space. This allows data to be extracted from files with text headers.
		
		Input(s):
			none
			
		GetData.extract -- Method
		
		Extracts values from the first column into GetData.xlst, values from the second
		column into GetData.ylst, and values from the third column into GetData.zlst
		
		Input(s):
			none

		DtHist -- Class
		
		Uses raw data from a GetData object to generate a histogram of dtbin vs intensity 
		with all data points within an m/z range of a specified m/z:
			DtHist.dtbinlst 	- dtbin values (list)
			DtHist.intenlst		- intensity values (list)
		
		Input(s):
			GetData				- object containing raw data (GetData)
			specified_mass		- m/z value to extract dt histogram for (float)
			mass_epsilon		- the m/z range above and below the specified mass to 
								  collect values for (float)

		DtHist.generateLists -- Method
		
		Adds values from GetData.ylst and GetData.zlst into DtHist.dtbinlst and 
		DtHist.intenlst, respectively, if the corresponding value in GetData.xlst is
		within mass epsilon of the specified mass
		
		Input(s):
			GetData				- object containing raw data (GetData)
			
		DtHist.getAvgDtbin -- Method
		
		Computes the average dtbin, weighted by intensity, of the current dt histogram. 
		Stores this value in:
			DtHist.avg_dtbin	- average dtbin value weighted by intensity (float)
		
		Input(s):
			none
			
		DtHist.dtbinToDt -- Method
		
		Converts DtHist.dtbinlst and DtHist.avg_dtbin into units of dt (ms) instead of 
		dtbin using the conversion factor dtbin_dt_equiv. Converted values are stored in:
			DtHist.dtlst		- dt values (list)
			DtHist.avg_dtb		- average dt value (float)
		
		Input(s):
			dtbin_dt_equiv		- ms/dtbin conversion factor (float)
			
		DtHist.transformHist -- Method
		
		Converts DtHist.dtbinlst and DtHist.avg_dtbin into a single list of dtbin values
		repeated by the corresponding intensity number, which can be used to produce a 
		matplotlib.pyplot.hist() object. The transformed list is stored in:
			DtHist.dtbintransformed	- transformed dtbin values (list)
		
		Input(s):
			none

		DtHist.showDtHist -- Method
		
		Plots the data contained in Dthist.dtbintransformed using matplotlib.pyplot.hist();
		
		Input(s):
			none
			
		GaussFit -- Class
		
		Fits a Gaussian distribution to the dt histogram in a specified DtHist object
		using a least squares fitting method. The results of the least squares fit are
		stored as the optimized parameters for the Gaussian function:
			GaussFit.optparams 		- optimized amplitude, mu, and sigma (tuple)
		
		Input(s):
			DtHist_obj				- object containing the dt histogram to be fit with
									  Gaussian function (DtHist)

		GaussFit.gaussFunc -- Method
		
		Gaussian function of variable x with parameters for amplitude, mu, and sigma
		
		Input(s):
			x					- dtbin (float)
			A					- Gaussian amplitude parameter (float)
			mu					- Gaussian mu parameter (float)
			sigma				- Gaussian sigma parameter (float)
			
		Returns:
								- intensity (float)
								
		GaussFit.doFit -- Method
		
		Fits dt histogram with Gaussian function using curve_fit from scipy.optimize. A
		try/except clause is used to catch an exception that arises when a sufficiently
		good fit is not reached within a maximum number of optimization steps, 
		specifically within 1000 steps. Stores the optimized mu parameter for easy 
		reference by other objects:
			GaussFit.opt_mean	- optimized mean dtbin (float) 
		
		Input(s):
			dthistobj			- object containing dt histogram (DtHist)
		
		GaussFit.saveGaussFitFig -- Method
		
		Outputs a Figure showing the CCS calibration curve fitted to the CCS 
		calibration data 
		
		Input(s):
			figure_file_name 	- choose a filename to save the figure under (string)	
			
		DataCollector -- Class
		
		Performs all of the steps necessary to extract drift time from a raw data file
		for a specified mass then stores the extracted drift time:
			DataCollector.drift_times - drift time associated with a m/z (dictionary)
		
		Input(s):
			[optional] mzlistinput	- m/z values to extract drift times for (list or boolean) 
									  [default = False]
			[optional] rawdatafilename	- name of the file to extract data from (string 
										or boolean) [default = False]
			[optional] parallelize	- use parallelization in the data extraction process
									  (boolean) [default = False]
			[optional] massepsilon	- specify a different mass epsilon to use (float) 
									  [default = 0.5]
			[optional] dtbintodt	- conversion factor to go from dtbin to dt in
									  miliseconds, based on TOF pusher frequency (float)
									  [default = 0.0689]
								
			DataCollector.batchProcess -- Method
		
		Performs drift time extraction for a set list of masses from one raw data input
		file by calling the process method for each m/z in the DataCollector.mz_list
		
		Input(s):
			none
			
			DataCollector.process -- Method
		
		Performs drift time extraction for a single m/z 
		
		Input(s):
			specified_mass			- the m/z to extract drift time for (float)
			data_file_name			- name of the raw data file (string)
			[optional] mass_epsilon	- specify a different mass epsilon to use (float) 
									  [default = 0.5]
			[optional] own_get_data	- use a GetData object that has already been 
									  created in this class (GetData or boolean) 
									  [default = False]
									  
		Returns:
									- drift time for the m/z in ms (float)	
									
		CcsCalibration -- Class
		
		Makes use of a DataCollector object to extract the drift times for a list of
		calibrant masses. Then, using a list of calibrant literature ccs values, a 
		ccs calibration curve is generated. Once the curve has been fit, the 
		CcsCalibration.getCalibratedCcs method can be used to get a calibrated ccs for a 
		given m/z and drift time
		
		Input(s):
			data_file				- name of raw data file (string)
			cal_mz					- calibrant m/z values (list)
			cal_lit_ccs				- calibrant literature ccs values (list)
			edc						- edc delay coefficient (float)
			[optional] nonstd_mass_epsilon - specify a different mass epsilon to use
												 other than the default within the 
												 DataCollector.batchProcess method
												 (float or boolean) [default = 0.5]
			[optional] nonstd_dtbin_equiv  - specify a different dtbin equivalent to 
												 use other than the default within the 
												 DataCollector.batchProcess method
												 (float or boolean) [default = 0.0689]
												 
			CcsCalibration.reducedMass -- Method
		
		Calculates reduced mass of an ion using the mass of nitrogen
		
		Input(s):
			specified_mass			- the m/z to use for the calculation (float)
									  
		Returns:
									- reduced mass (float)			
									
		CcsCalibration.correctedDriftTime -- Method
		
		Calculates a drift time corrected for mass-dependent flight time
		
		Input(s):
			dt						- original uncorrected drift time (float)
			mass					- the m/z to use for the calculation (float)
									  
		Returns:
									- corrected drift time (float)	
									
			CcsCalibration.baseCalCurve -- Method
		
		Basic power function for calibration curve
		
		Input(s):
			dt						- drift time (float)
			A, t0, B				- curve parameters (float, float, float)
									  
		Returns:
									- ccs (float)	
									
			CcsCalibration.fitCalCurve -- Method
		
		Performs least squares fit of the power equation CcsCalibration.baseCalCurve(...) to
		the corrected literature ccs data and corrected drift time values 
		
		Input(s):
			none				
			
		CcsCalibration.getCalibratedCcs -- Method
		
		Uses the fitted parameters for the ccs calibration curve and returns a calibrated
		ccs given an m/z and drift time
		
		Input(s):
			mz						- m/z (float)
			dt						- drift time (float)
									  
		Returns:
									- ccs (float)	
									
			CcsCalibration.saveCalCurveFig -- Method
		
		Outputs a Figure showing the CCS calibration curve fitted to the CCS 
		calibration data 
		
		Input(s):
			[optional] figure_file_name - choose a different filename to save the 
										  calibration curve fit figure (string) [default
										  = "cal_curve.png"]				
										  
		GenerateReport -- Class
		
		DESCRIPTION GOES HERE
		
		Input(s):
		
		GenerateReport.writeHeader -- Method
		
		Writes a header for report file with the name of the report file and the date it 
		was generated
		
		Input(s):
			none				
			
		writeDriftTimeTable -- Method
		
		Writes a full report on how the CCS calibration went. This includes:
			- A table of m/z values and their extracted drift times
			- The fit parameters for the CCS calibration curve

		Input(s):
			ccs_calibration_object		- The CcsCalibration object containing all of the
											relevant information about the calibration 
											(CcsCalibration) 
											
		writeDriftTimeTable -- Method
		
		Writes a table of m/z values and their drift times separated by tabs with
		the following format:
			m/z			drift time (ms)
			---------------------------
			mz 1 		dt 1
			mz 2 		dt 2
			...				...
		
		Input(s):
			masses						- m/z values (list)
			drift_times					- drift time values (list)
			
		writeCcsComparisonTable -- Method
		
		Writes a table of m/z values, their literature ccs values, the calculated ccs and residual
		ccs with the following format:
			m/z			lit ccs (Ang^2)		calc ccs (Ang^2)	residual ccs (Ang^2, %)
			---------------------------------------------------------------------------
			mz 1 		lit_ccs 1			calc_ccs 1			resid 1, 	resid% 1						
			mz 2 		lit_ccs 2			calc_ccs 2			resid 2,	resid% 2
			...			...					...					...,		...
		
		Input(s):
			masses						- m/z values (list)
			literature_ccs				- ccs literature values (list)
			calculated_ccs				- calculated ccs values (list)

		writeCompoundDataTableHeader -- Method
		
		Writes the header for a table displaying the extracted drift time and calibrated
		CCS for the datafile/mass pairs with the following format:
			data file name		m/z		drift time (ms)     ccs (Ang^2)
			-----------------------------------------------------------
			data_file_1.txt		mz 1		dt 1			ccs 1 		
			data_file_1.txt		mz 1		dt 1			ccs 1 		
			...					...			...				...								
			
		Input(s):
			none

		writeCompoundDataTableLine -- Method
		
		Writes a single line for a table displaying the extracted drift time and calibrated
		CCS for the datafile/mass pairs with the following format:
			data file name		m/z		drift time (ms)     ccs (Ang^2)
			-----------------------------------------------------------
			data_file_1.txt		mz 1		dt 1			ccs 1 		
			data_file_1.txt		mz 1		dt 1			ccs 1 		
			...					...			...				...	
		
		Input(s):
			data_file_name				- name of the data file (string)
			mz							- mass to charge of compound (float)
			dt							- extracted drift time of the compound (float)
			ccs							- calculated ccs value (float)

		GenerateReport.wLn -- Method
		
		Writes a string to the report file then moves to a new line
		
		Input(s):
			[optional] line_to_write	- line to write to file (string)
			
		GenerateReport.finish -- Method
		
		Closes the report file
		
		Input(s):
			none
			
