"""
	>>>CcsCal.py<<<
	Dylan H. Ross
	
	!!!ccscal-plusplus!!!

		This program contains several utilities for processing raw mass-spec data with
		a drift time dimension: extracting drift time for a particular mass, creating
		a CCS calibration curve, obtaining calibrated CCS for a mass and drift time 
		using the CCS calibration curve.
		When called directly, this program refers to a specified input file and 
		automagically performs a CCS calibration then obtains calibrated CCS for all
		specified masses, printing a full report containing the results of the 
		calibration and CCS of all compounds. 	

"""

##########################################################################################
# import necessary modules

# need pyplot to make plots and gridspec for subplot configuration
import matplotlib.pyplot as pplt
import matplotlib.gridspec as gs

# need numpy for math stuff and arrays
import numpy

# need curve fit module from scipy for fitting curves
from scipy.optimize import curve_fit

# need the time module to do performance reporting
import time

# need argparse for parsing command-line arguments
import argparse

# need os for some file operations
import os

# need sys for adding input file to python path
import sys

# need subprocess.call for calling external scripts/programs
from subprocess import call

# need savgol_filter to smooth raw data with Savitsky-Golay filter
from scipy.signal import savgol_filter

##########################################################################################
class GetData (object):
	"""
		GetData -- Class
		
		Preprocesses a specified raw data file using a specified mass and rough mass window
		then takes that rough data and extracts from it the dtbin and intensity data for a
		specified mass in a fine mass window, summing the intensities for each dtbin
		
		Data Stored:
			GetData.data			- array with mass, dtbin, and intensity from the
										pre-processsed .txt file (numpy.array)
			GetData.ppFileName		- file name of pre-processed data file (string)
			GetData.dtBinAndIntensity - array with dtbin values and summed intensities 
											for each (numpy.array)
			GetData.specifiedMass 	- the specified mass for which data was extracted (float)
		
		Input(s):
			data_filename			- file name of the raw data file (string)
			specified_mass			- mass to extract data for (float)
			mass_window				- window of masses to bin data together for (float)
	"""	
	def __init__ (self, data_filename, specified_mass, mass_window):
		# create the pre-processed data file
		self.callPreProcessTxt(data_filename, specified_mass, mass_window)
		# store the file name of the pre-processed file
		self.ppFileName = os.path.splitext(data_filename)[0] + ".pp-" + \
											str(specified_mass) + ".txt"
		# generate an array with the mass, dtbin, and intensity values from the pre-processed
		# data file
		self.data = numpy.genfromtxt(self.ppFileName, unpack=True)
		# fine filter extracted data for mass and mass window
		self.fineFilterForMass(specified_mass, mass_window)
		# store the specified mass
		self.specifiedMass = specified_mass
		
	"""
		GetData.callPreProcessTxt -- Method
		
		Calls PreProcessTxt.o using the specified mass and mass window provided as parameters. The
		mass window it actually uses is a rough mass window (i.e. double the mass window provided)
		
		Input(s):
			data_filename		- file name of the raw data file (string)
			specified_mass		- mass to extract data for (float)
			mass_window			- window of masses to bin data together for (float)
	"""	
	def callPreProcessTxt(self, data_filename, specified_mass, mass_window):
		# pre-process the input file using the exact mass window speccified (do not double the mass
		# window anymore)
		# For now I have just specified a relative path to the executable since it is in the same 
		# directory as the main CcsCal.py (this file)
		functionCallLine = "./PreProcessTxt.exe" + " " +\
							data_filename + " " +\
							str(specified_mass) + " " + \
							str(mass_window)
		call(functionCallLine)
	
	"""
		GetData.fineFilterForMass -- Method
		
		Looks through the data array from the pre-processed data file for masses within the 
		fine mass window 
		
		Input(s):
			specified_mass		- mass to extract data for (float)
			mass_window			- window of masses to bin data together for (float)
	"""		
	def fineFilterForMass(self, specified_mass, mass_window):
		# prepare an array with dtbin and intensity values
		self.dtBinAndIntensity = numpy.zeros([2, 200])
		for n in range(1, 201):
			self.dtBinAndIntensity[0][n - 1] = n
		for n in range(len(self.data[0])):
			if (numpy.abs(specified_mass - self.data[0][n]) <= mass_window):
				# add the intensity to its corresponding bin
				self.dtBinAndIntensity[1][int(self.data[1][n]) - 1] += self.data[2][n]

##########################################################################################
class GaussFit (object):
	"""
		GaussFit -- Class
		
		Fits a Gaussian distribution to the dt distribution in a specified GetData object
		using a least squares fitting method. The results of the least squares fit are
		stored as the optimized parameters for the Gaussian function
		
		Data Stored:
			GaussFit.optparams 		- optimized amplitude, mu, and sigma (tuple)
			GaussFit.opt_mean		- optimized mean of Gaussian distribution fit to data
		
		Input(s):
			get_data				- object containing the dt distribution to be fit with 
										Gaussian function (GetData)
			[optional] sg_smooth	- use a Savitsky-Golay smoothing function on the raw data
										prior to gaussian fitting. If set, provides the smooth
										window and polynomial order to use for smoothing 
										(boolean or tuple) [default = False]
									  
	"""
	def __init__ (self, get_data, sg_smooth=False):
		# generate the initial parameters, initial sigma is set to 10 dtbins ARBITRARILY
		# TODO: figure out a non-arbitrary initial setting for the sigma parameter
		# 		tests with some data suggest that maybe 5.0 bins would work better than 10.0...
		self.initparams = ((numpy.amax(get_data.dtBinAndIntensity[1])),\
							(numpy.sum(get_data.dtBinAndIntensity[0] * \
								get_data.dtBinAndIntensity[1]) / \
								numpy.sum(get_data.dtBinAndIntensity[1])),\
							(10.0))
		# set fit failed flag
		fitFailed = False
		# make internal copies of the specified mass and data filename
		self.mass = get_data.specifiedMass
		self.filename = get_data.ppFileName
		if sg_smooth:
			# perform smoothing of raw data using Savitsky-Golay filter
			# smooth window is sg_smooth[0], polynomial order is sg_smooth[1]
			get_data.dtBinAndIntensity[1] = savgol_filter(get_data.dtBinAndIntensity[1], sg_smooth[0], sg_smooth[1])
		# fit the (smoothed or unsmoothed) data 
		self.doFit(get_data)
		if not fitFailed:
			self.opt_mean = self.optparams[1]	
		#create an array with the raw dtbin and intensity values
		# and fitted intensity values
		self.rawandfitdata = numpy.array([get_data.dtBinAndIntensity[0], \
											get_data.dtBinAndIntensity[1], \
											get_data.dtBinAndIntensity[1]])
		self.rawandfitdata[2] = self.gaussFunc(get_data.dtBinAndIntensity[0], \
												self.optparams[0], \
												self.optparams[1], \
												self.optparams[2])
		self.saveGaussFitFig(self.filename, get_data)
		
	"""
		GaussFit.gaussFunc -- Method
		
		Gaussian function of variable x with parameters for amplitude, mu, and sigma
		
		Input(s):
			x					- dtbin (float)
			A					- Gaussian amplitude parameter (float)
			mu					- Gaussian mu parameter (float)
			sigma				- Gaussian sigma parameter (float)
			
		Returns:
								- intensity (float)
	"""	
	def gaussFunc (self,x, A, mu, sigma):
		return A*numpy.exp(-(x-mu)**2/(2.*sigma**2))
	
	"""
		GaussFit.doFit -- Method
		
		Fits dt histogram with Gaussian function using curve_fit from scipy.optimize. A
		try/except clause is used to catch an exception that arises when a sufficiently
		good fit is not reached within a maximum number of optimization steps, 
		specifically within 1000 steps. Stores the optimized mu parameter for easy 
		reference by other objects:
			GaussFit.opt_mean		- optimized mean dtbin (float) 
		
		Input(s):
			get_data				- object containing the dt distribution to be fit with 
										Gaussian function (GetData)
	"""	
	def doFit (self, get_data):
		try:
			self.optparams,self.covar = curve_fit(self.gaussFunc,\
													get_data.dtBinAndIntensity[0],\
													get_data.dtBinAndIntensity[1],\
													p0=self.initparams,\
													maxfev=1000)
		except RuntimeError:
			# if fit was not achieved..
			self.fit_failed = True
			self.opt_mean = self.initparams[1]
			self.optparams = self.initparams
			print "failed to fit gaussian for mass", self.mass, "in", self.filename
			
	"""
		GaussFit.saveGaussFitFig -- Method
		
		Outputs a Figure showing the CCS calibration curve fitted to the CCS 
		calibration data 
		
		Input(s):
			figure_file_name 		- choose a filename to save the figure under (string)
			get_data				- object containing the dt distribution to be fit with 
										Gaussian function (GetData)					
	"""		
	def saveGaussFitFig (self, figure_file_name, get_data):
		p = pplt
		p.plot(self.rawandfitdata[0],\
				self.rawandfitdata[1],\
				color='blue',\
				ls='--',\
				marker='o',\
				ms=5,\
				mec='blue',\
				mfc='blue',\
				label="raw data\n(smoothed)")
		p.plot(self.rawandfitdata[0],\
				self.rawandfitdata[2],\
				color='black',\
				ls='-',\
				label="gaussian fit")
		p.legend(loc="best")
		p.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
		p.xlabel("dt bin")
		p.ylabel("intensity")
		p.title(os.path.split(os.path.splitext(figure_file_name)[0])[1] + \
												"\nmass: " + \
												str(self.mass))
		p.savefig(os.path.splitext(figure_file_name)[0] + \
									"_mass-" + \
									str(int(self.mass)) + \
									".png", bbox_inches='tight')
		p.close()

##########################################################################################
class DataCollector (object):
	"""
		DataCollector -- Class
		
		Performs all of the steps necessary to extract drift time from a raw data file
		for a specified mass
		
		Data Stored:
			TODO: fill this description in
		
		Input(s):
			[optional] dtbin_to_dt	- conversion factor for going from dtbin to drift time
										in milliseconds, based on the TOF pusher frequency
										[default = 0.069]
			[optional] sg_smooth	- use a Savitsky-Golay smoothing function on the raw data
										prior to gaussian fitting. If set, provides the smooth
										window and polynomial order to use for smoothing 
										(boolean or tuple) [default = False]
	"""
	def __init__ (self, dtbin_to_dt=0.069, sg_smooth=False):
		self.dtBinToDt = dtbin_to_dt
		self.sg_smooth = sg_smooth
	
	"""
		DataCollector.process -- Method
		
		Performs drift time extraction for a single mass using a single mass window from a 
		specified data file
		
		Input(s):
			data_file_name			- name of the raw data file (string)
			specified_mass			- the m/z to extract drift time for (float)
			mass_epsilon			- specify a different mass epsilon to use (float)
									  
		Returns:
									- drift time for the specified mass in ms (float)						
	"""		
	def process (self, data_file_name, specified_mass, mass_window):
		gauss = GaussFit(GetData(data_file_name, specified_mass, mass_window), sg_smooth=self.sg_smooth)
		return gauss.opt_mean * self.dtBinToDt

##########################################################################################
class CcsCalibration (object):
	"""
		CcsCalibration -- Class
		
		Makes use of a DataCollector object to extract the drift times for a list of
		calibrant masses. Then, using a list of calibrant literature ccs values, a 
		ccs calibration curve is generated. Once the curve has been fit, the 
		CcsCalibration.getCalibratedCcs method can be used to get a calibrated ccs for a 
		given mass and drift time
		
		TODO: add Data Stored section
		
		Input(s):
			data_file				- name of raw data file (string)
			cal_masses				- calibrant m/z values (list)
			cal_lit_ccs				- calibrant literature ccs values (list)
			mass_window 			- specify a mass window to extract values from (float)
			[optiona] edc  			- edc delay coefficient (float) [default = 1.35]
			[optional] dtbin_to_dt  - specify a different dtbin equivalent to use other than 
										the default (float) [default = 0.0689]
			[optional] sg_smooth	- use a Savitsky-Golay smoothing function on the raw data
										prior to gaussian fitting. If set, provides the smooth
										window and polynomial order to use for smoothing 
										(boolean or tuple) [default = False]
	"""
	def __init__ (self, 
				  data_file,\
				  cal_masses,\
				  cal_lit_ccs_vals,\
				  mass_window,\
				  edc=1.35,\
				  dtbin_to_dt=0.0689,\
				  sg_smooth=False):
		# store some calculation constants
		self.edc = edc
		self.n2_mass = 28.0134	
		# create an empty DataCollector object
		self.collector = DataCollector(dtbin_to_dt=dtbin_to_dt, sg_smooth=sg_smooth)
		# make an array with calibrant masses
		self.calMasses = numpy.array(cal_masses)
		# make an array with calibrant lit ccs values
		self.calLitCcs = numpy.array(cal_lit_ccs_vals)
		# make an array with calibrant drift times
		self.calDriftTimes = numpy.zeros([len(self.calMasses)])
		for n in range(len(self.calMasses)):
			self.calDriftTimes[n - 1] = self.collector.process(data_file, self.calMasses[n - 1], mass_window)
		# make an array with corrected drift time
		self.correctedDt = self.correctedDriftTime(self.calDriftTimes, self.calMasses)
		# make an array with corrected lit ccs
		self.correctedLitCcs = self.calLitCcs * numpy.sqrt(self.reducedMass(self.calMasses))
		# Optimized parameters A, t0, B (starts as the initial parameters [0, 0, 1])
		self.optparams = [0, 0, 1]
		#perform the calibration
		self.fitCalCurve()
		# make an array with calibrant calculated ccs
		self.calCalcCcs = self.getCalibratedCcs(self.calMasses, self.calDriftTimes)

	"""
		CcsCalibration.reducedMass -- Method
		
		Calculates reduced mass of an ion using the mass of nitrogen
		
		Input(s):
			specified_mass			- the m/z to use for the calculation (float)
									  
		Returns:
									- reduced mass (float)						
	"""
	def reducedMass(self, mass):
		return (mass * self.n2_mass) / (mass + self.n2_mass)
	
	"""
		CcsCalibration.correctedDriftTime -- Method
		
		Calculates a drift time corrected for mass-dependent flight time
		
		Input(s):
			dt						- original uncorrected drift time (float)
			mass					- the m/z to use for the calculation (float)
									  
		Returns:
									- corrected drift time (float)						
	"""	
	def correctedDriftTime(self, dt, mass):
		return dt - ((numpy.sqrt(mass) * self.edc) / 1000.0)

	"""
		CcsCalibration.baseCalCurve -- Method
		
		Basic power function for calibration curve
		
		Input(s):
			dt						- drift time (float)
			A, t0, B				- curve parameters (float, float, float)
									  
		Returns:
									- ccs (float)						
	"""
	def baseCalCurve (self, dt, A, t0, B):
		return (A  * (dt + t0)**B)	

	"""
		CcsCalibration.fitCalCurve -- Method
		
		Performs least squares fit of the power equation CcsCalibration.baseCalCurve(...) to
		the corrected literature ccs data and corrected drift time values 
		
		Input(s):
			none					
	"""
	def fitCalCurve(self):		
		self.fit_Failed = False
		try:
			self.optparams,self.covar=\
			curve_fit(\
			self.baseCalCurve,\
			self.correctedDt,\
			self.correctedLitCcs,\
			p0=self.optparams,\
			maxfev=2000)
		except RuntimeError:
			self.fit_failed = True
			print "CCS CALIBRATION CURVE FIT FAILED WITH RUNTIME ERROR..."
	
	"""
		CcsCalibration.getCalibratedCcs -- Method
		
		Uses the fitted parameters for the ccs calibration curve and returns a calibrated
		ccs given an m/z and drift time
		
		Input(s):
			mz						- m/z (float)
			dt						- drift time (float)
									  
		Returns:
									- ccs (float)						
	"""	
	def getCalibratedCcs(self, mass, dt):
		if not self.fit_Failed:
			return (self.optparams[0] / numpy.sqrt(self.reducedMass(mass))) \
					* ((self.correctedDriftTime(dt, mass)\
					+ self.optparams[1])**self.optparams[2])
		else:
			raise ValueError ("optimized fit parameters have not been generated,\
							  \nfitCalCurve() must be successfully run first")
		
	"""
		CcsCalibration.saveCalCurveFig -- Method
		
		Outputs a Figure showing the CCS calibration curve fitted to the CCS 
		calibration data 
		
		Input(s):
			[optional] figure_file_name - choose a different filename to save the 
										  calibration curve fit figure (string) [default
										  = "cal_curve.png"]					
	"""					  
	def saveCalCurveFig(self, figure_file_name="cal_curve.png"):
		g = gs.GridSpec(2,1,height_ratios=[5,2])
		p = pplt
		p.subplot(g[0])
		p.plot(self.correctedDt,\
			   self.correctedLitCcs, \
			   'ko' , \
			   fillstyle='none', \
			   markeredgewidth=1.0, \
			   label="calibrants")
		p.plot(self.correctedDt, 
				self.baseCalCurve(self.correctedDt,\
									self.optparams[0],\
									self.optparams[1],\
									self.optparams[2]),\
				'black', \
				label="fitted curve")
		p.legend(loc="best")
		p.title("CCS Calibration")
		p.ylabel("corrected CCS")
		p.subplot(g[1])
		p.bar(self.correctedDt, \
				numpy.array((100 * (self.calLitCcs - self.calCalcCcs) / self.calLitCcs)), 
			  	0.25, \
			  	color='black', \
			  	align='center')
		p.xlabel("corrected drift time (ms)")
		p.ylabel("residual CCS (%)")
		p.axhline(y=0, color='black')
		p.savefig(figure_file_name, bbox_inches='tight')
		p.close()
		
##########################################################################################
class GenerateReport (object):
	"""
		GenerateReport -- Class
		
		TODO: class description
		
		Input(s):
			
	"""
	def __init__ (self, report_file_name):
		self.report_file_name = report_file_name
		self.report_file = open(self.report_file_name, "w")
		self.writeHeader()

	"""
		GenerateReport.writeHeader -- Method
		
		Writes a header for report file with the name of the report file and the date it 
		was generated
		
		Input(s):
			none				
	"""
	def writeHeader(self):
		self.wLn(os.path.split(os.path.splitext(self.report_file_name)[0])[1])
		self.wLn("Generated by CcscCal.py on " + time.strftime("%c"))
		self.wLn("====================================================")
		self.wLn()
		self.wLn()

	
	"""
		writeDriftTimeTable -- Method
		
		Writes a full report on how the CCS calibration went. This includes:
			- A table of m/z values and their extracted drift times
			- The fit parameters for the CCS calibration curve

		Input(s):
			ccs_calibration_object		- The CcsCalibration object containing all of the
											relevant information about the calibration 
											(CcsCalibration) 
	"""
	def writeCalibrationReport(self, ccs_calibration_object):
		self.wLn("+-----------------+")		
		self.wLn("| CCS CALIBRATION |")
		self.wLn("+-----------------+")
		self.wLn()
		self.wLn("CCS calibrants extracted drift times:")
		self.writeDriftTimeTable(ccs_calibration_object.calMasses,\
								 ccs_calibration_object.calDriftTimes)
		self.wLn()
		self.wLn("Optimized calibration curve fit parameters:")
		self.wLn("\tcorrected ccs = A * ((corrected drift time) + t0) ** B")
		self.wLn("\t\tA = " + str(ccs_calibration_object.optparams[0]))
		self.wLn("\t\tt0 = " + str(ccs_calibration_object.optparams[1]))
		self.wLn("\t\tB = " + str(ccs_calibration_object.optparams[2]))
		self.wLn()
		
		self.wLn("Calibrant CCS, calculated vs. literature:")
		self.writeCcsComparisonTable(ccs_calibration_object.calMasses,\
									 ccs_calibration_object.calLitCcs,\
									 ccs_calibration_object.calCalcCcs)
		self.wLn()
	
	"""
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
	"""
	def writeDriftTimeTable(self, masses, drift_times):
		self.wLn("m/z\t\tdrift time (ms)")
		self.wLn("---------------------------")
		for n in range (len(masses)):
			outstr = str(round(masses[n], 3)) + "\t\t" + str(round(drift_times[n], 3)) 
			self.wLn(outstr)
		self.wLn()

	"""
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
	"""
	def writeCcsComparisonTable(self, masses, literature_ccs, calculated_ccs):
		self.wLn("m/z\t\tlit ccs (Ang^2)\t\tcalc ccs (Ang^2)\t\tresidual ccs (Ang^2, %)")
		self.wLn("----------------------------------------------------------------------------")
		for n in range (len(masses)):
			outstr = str(round(masses[n], 3)) + "\t\t" \
					 + str(round(literature_ccs[n], 3)) + "\t\t\t\t" \
					 + str(round(calculated_ccs[n], 3)) + "\t\t\t\t\t" \
					 + str(round((literature_ccs[n] - calculated_ccs[n]), 3)) + ", " \
					 + str(round((100.0 *(literature_ccs[n] - calculated_ccs[n]) / (literature_ccs[n])), 3))
			self.wLn(outstr)
		self.wLn()	

	"""
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
	"""
	def writeCompoundDataTableHeader(self):
		self.wLn("+---------------+")		
		self.wLn("| COMPOUND DATA |")
		self.wLn("+---------------+")
		self.wLn()
		self.wLn("Compounds extracted drift times and calibrated CCS:")
		self.wLn("data file name\t\t\t\tm/z\t\t\t\tdrift time (ms)\t\tccs (Ang^2)")
		self.wLn("----------------------------------------------------------------------------")
		

	"""
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
	"""
	def writeCompoundDataTableLine(self, data_file_name, mz, dt, ccs):
		outstr = data_file_name + "\t\t\t" \
				 + str(round(mz, 3)) + "\t\t\t\t" \
				 + str(round(dt, 3)) + "\t\t\t\t" \
				 + str(round(ccs, 3)) 
		self.wLn(outstr)
			

	"""
		GenerateReport.wLn -- Method
		
		Writes a string to the report file then moves to a new line
		
		Input(s):
			[optional] line_to_write	- line to write to file (string) [default = ""]
	"""
	def wLn(self, line_to_write=""):
		self.report_file.write(line_to_write + "\n")		

	"""
		GenerateReport.finish -- Method
		
		Closes the report file
		
		Input(s):
			none
	"""
	def finish(self):
		self.report_file.close()

##########################################################################################
class ParseInputFile (object):
	"""
		ParseInputFile -- Class
		
		TODO: class description
		TODO: data stored section
		
		Input(s):
			input_filename				- name (and path) of CcsCalInput.txt file (string)
	"""
	def __init__(self, input_filename):
		# take in the input parameters
		self.rawData = self.getInputParams(input_filename)
		# unpack the single parameters into easy to access fields
		self.unpackSingleParams()
		# create arrays with the list input parameters
		self.unpackListParams()
		
	"""
		ParseInputFile.getInputParams -- Method
	
		Searches through the specified input file for the (all) parameters and returns an
		array of the parameters grouped by categories (general, calibrants, and compounds):
	
		params contents by index:
			params[0][0]			- path and file name to save reoprt under
			params[0][1]			- mass window to extract drift time data from
			params[0][2]			- edc parameter
			params[0][3]			- dtbin to dt conversion factor (based on TOF pusher interval)
			params[0][4]			- Savitsky-Golay smooth window parameter (or 0 for no smoothing)
			params[0][5]			- Savitsky-Golay polynomial parameter
			params[1][0]			- full path and name to save calibration curve file under
			params[1][1]			- full path and name of the CCS calibration data file
			params[2][0]			- full path to the directory containing the compound data files
			params[3]				- array containing the list data (calibrant masses and lit ccs
										values, compound data file names and masses)
		
		Input(s):
			filename			- file name (and full path to) CcsCalInput file (string)
		
		Returns:
			params				- an array (list of three lists and one numpy.array() object) 
										containing the parameters from the input file
	"""	
	def getInputParams(self, filename):
		params = [[],[],[]]
		with open(filename) as input:
			done = False
			for line in input:
				if not done:
					if line.split()[0] == ";rfn":
						params[0].append(line.split()[2])
					elif line.split()[0] == ";mwn":
						params[0].append(line.split()[2])
					elif line.split()[0] == ";edc":
						params[0].append(line.split()[2])
					elif line.split()[0] == ";tpi":
						params[0].append(line.split()[2])
					elif line.split()[0] == ";sgw":
						params[0].append(line.split()[2])
					elif line.split()[0] == ";sgp":
						params[0].append(line.split()[2])
					elif line.split()[0] == ";cff":
						params[1].append(line.split()[2])
					elif line.split()[0] == ";cdf":
						params[1].append(line.split()[2])
					elif line.split()[0] == ";crd":
						params[2].append(line.split()[2])
						done = True
				else:
					break
		params.append(numpy.genfromtxt(filename, dtype=str, comments=";"))
		return params
		
	"""
		ParseInputFile.unpackSingleParams -- Method
		
		Unpack the paramters from the params array into fields with names that make sunse for easy
		access from the main execution. Cast the values into the proper types that they should be
		for how they are going to be used.
		
		Input(s):
			none
	"""
	def unpackSingleParams(self):
		self.reportFileName = self.rawData[0][0]
		# cast massWindow and edc to type float
		self.massWindow = float(self.rawData[0][1])
		self.edc = float(self.rawData[0][2])
		# convert TOF pusher interval to dtbin_to_dt (divide by 1000) and cast dtbin_to_dt to float
		self.dtbin_to_dt = float(self.rawData[0][3]) / 1000.0
		# set sg_smooth to False if the first parameter in the input file (sgw) is 0
		if int(self.rawData[0][4]) == 0:
			self.sg_smooth = False
		else:
			# otherwise set it to be a tuple containing the smooth window and polynomial order from 
			# the input file (both cast to ints)
			self.sg_smooth = (int(self.rawData[0][4]), int(self.rawData[0][5])) 
		self.calCurveFileName = self.rawData[1][0]
		self.calDataFile = self.rawData[1][1]
		self.compoundDataDir = self.rawData[2][0]
	
	"""
		ParseInputFile.unpackListParams -- Method
		
		Breaks the rawData[3] array into two easy to access arrays with calibration data and 
		compound data separated from one another
		
		Input(s):
			none
	"""
	def unpackListParams(self):
		# temporary lists to build the arrays from
		templist1 = []
		templist2 = []
		templist3 = []
		templist4 = []
		flag = False
		for thing in self.rawData[3]:
			if flag:
				templist3.append(thing[0])
				# need to cast compound mass to float
				templist4.append(float(thing[1]))
			elif thing[0] == "compound":
				flag = True
			else:
				# temporary list values for ccs data are cast to floats so that the resulting array
				# will have type float
				templist1.append(float(thing[0]))
				templist2.append(float(thing[1]))
		# array of floats
		self.calibrantData = numpy.array([templist1, templist2])
		# make separate lists for the compound file names and compound masses
		self.compoundFileNames = templist3
		self.compoundMasses = templist4

##########################################################################################
# ***EXECUTION IF THIS SCRIPT IS CALLED DIRECTLY*** #
if __name__ == '__main__' :
	"""
		This is the execution path to follow if this program is called directly through
		the commmand line. 

		The following argument is required:
			-i, --input			full path to ccscal_input.py
	"""
	start_time = time.time()
	#
	### PARSE THE COMMAND-LINE ARGUMENTS
	#	
	print
	# string containing program description
	pdesc = "This program refers to a specified input file and automagically \
			performs a CCS calibration then obtains calibrated CCS for all \
			specified masses, finally printing a full report containing the \
			results of the calibration and CCS of all compounds"
	# create an ArgumentParser object 
	parser = argparse.ArgumentParser(description=pdesc)
	# add arguments
	parser.add_argument('-i',\
						'--input',\
						required=True,\
						help='full path to ccscal_input.txt',\
						dest="path_to_input",\
						metavar='"/full/path/to/ccscal_input.txt"')
	# parse arguments 
	args = parser.parse_args()
	# print the help message at the beginning of each run
	parser.print_help()
	print
	# all of the command-line arguments are stored in args
	#
	### PARSE THE INPUT FILE
	#
	input_data = ParseInputFile(args.path_to_input)
	#
	### INITIALIZE THE REPORT GENERATOR
	#
	report = GenerateReport(input_data.reportFileName)
	#	
	### PERFORM CCS CALIBRATION
	#
	print "Performing CCS Calibration..."
	# create CcsCalibration object
	calibration = CcsCalibration(input_data.calDataFile,\
								 input_data.calibrantData[0],\
								 input_data.calibrantData[1],\
								 mass_window=input_data.massWindow,\
								 edc=input_data.edc,\
								 dtbin_to_dt=input_data.dtbin_to_dt,\
								 sg_smooth=input_data.sg_smooth)
	# save a graph of the fitted calibration curve
	calibration.saveCalCurveFig(figure_file_name=input_data.calCurveFileName)
	# write the calibration statistics to the report file
	report.writeCalibrationReport(calibration)
	print "...DONE"
	#
	### EXTRACT DRIFT TIMES OF COMPOUNDS AND GET THEIR CALIBRATED CCS
	#
	# initialize a DataCollector object
	collector = DataCollector(dtbin_to_dt=input_data.dtbin_to_dt, sg_smooth=input_data.sg_smooth)
	# write the header for the compound data table in the report
	report.writeCompoundDataTableHeader()
	# cycle through each compound input filename/mass pair and perform drift time extraction
	for n in range(len(input_data.compoundFileNames)):
		print "Extracting Drift Time for Mass:", input_data.compoundMasses[n], \
				"from Data File:", input_data.compoundFileNames[n], "(" + str(n + 1), \
				"of", str(len(input_data.compoundFileNames)) + ")..."
		# extract drift time and get calibrated CCS for the filename/mass pair
		driftTime = collector.process((input_data.compoundDataDir + input_data.compoundFileNames[n]), \
										input_data.compoundMasses[n], \
										input_data.massWindow)
		print "...DONE"
		print "Getting Calibrated CCS..."
		ccs =  calibration.getCalibratedCcs(input_data.compoundMasses[n], driftTime)
		report.writeCompoundDataTableLine(input_data.compoundFileNames[n], \
											input_data.compoundMasses[n], \
											driftTime, \
											ccs)
		print "...DONE"
	#
	### CLOSE THE REPORT FILE
	report.finish()
	#
	print
	print "CcsCal Complete."
	#
	### COMPLETE
	#
	# report the total time taken to the user
	end_time = time.time()
	print
	print "total time: ", round((end_time - start_time), 3), "seconds"
