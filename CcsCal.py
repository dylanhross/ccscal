"""
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

"""

##########################################################################################
# import necessary modules

# need pyplot to make plots and gridspec for subplot configuration
import matplotlib.pyplot as pplt
import matplotlib.gridspec as gs

# need numpy for math stuff
import numpy

# need curve fit module from scipy for fitting curves
from scipy.optimize import curve_fit

# need sys for making progress bar that refreshes and for altering the python paths
import sys

# need the time module to do performance reporting
import time

# need argparse for parsing command-line arguments
import argparse

# need os for some file operations
import os

##########################################################################################
class GetData (object):
	"""
		GetData -- Class
		
		Extracts and stores the raw data from a .txt data file:
			GetData.xlst 		- m/z values (list)
			GetData.ylst		- dtbin values (list)
			GetData.zlst		- intensity values (list)
		
		Input(s):
			data_filename		- file name of the raw data file (string)
	"""
	def __init__ (self, data_filename):
		self.fn = data_filename
		self.open_data = open(self.fn, "r+")
		self.line_list = self.open_data.readlines()
		self.makeGll()
		self.extract()
		self.num_vals = len(self.xlst)
		self.open_data.close()
		self.line_list = []
		self.good_line_list = []
		self.good_x_values = []
		self.good_y_values = []
		self.good_z_values = []

	"""
		GetData.makeGll -- Method
		
		Generates a good_line_list containing only lines which begin with a number or a 
		a space. This allows data to be extracted from files with text headers.
		
		Input(s):
			none
	"""
	def makeGll (self):
		self.good_line_list = []		
		for n in self.line_list:
			self.tempL = []
			for e in n:	
				self.tempL.append(e)
			if self.tempL[0] == "0"\
			or self.tempL[0] == "1"\
			or self.tempL[0] == "2"\
			or self.tempL[0] == "3"\
			or self.tempL[0] == "4"\
			or self.tempL[0] == "5"\
			or self.tempL[0] == "6"\
			or self.tempL[0] == "7"\
			or self.tempL[0] == "8"\
			or self.tempL[0] == "9"\
			or self.tempL[0] == " " :
				self.good_line_list.append(n)
		self.line_list = []

	"""
		GetData.extract -- Method
		
		Extracts values from the first column into GetData.xlst, values from the second
		column into GetData.ylst, and values from the third column into GetData.zlst
		
		Input(s):
			none
	"""
	def extract (self):
		self.good_x_values = []
		self.good_y_values = []
		self.good_z_values = []				
		for n1 in range(0, (len(self.good_line_list) )) :
			self.Lchop = []
			self.Lchop = self.good_line_list[n1].strip().split()
			self.good_x_values.append(self.Lchop[0])
			self.good_y_values.append(self.Lchop[1])
			self.good_z_values.append(self.Lchop[2])
		for n3 in range (0, len(self.good_x_values)) :
			self.good_x_values[n3] = float (self.good_x_values[n3])
			self.good_y_values[n3] = float (self.good_y_values[n3])
			self.good_z_values[n3] = float (self.good_z_values[n3])
		self.xlst = self.good_x_values
		self.ylst = self.good_y_values
		self.zlst = self.good_z_values	
		self.good_x_values = []
		self.good_y_values = []
		self.good_z_values = []
		
##########################################################################################
class DtHist (object):
	"""
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
	"""
	def __init__ (self,\
				  GetData,\
				  specified_mass,\
				  mass_epsilon):
		self.specmass = float(specified_mass)
		self.mass_epsilon = mass_epsilon
		self.mass_epsilon = float(self.mass_epsilon)
		self.dtbinlst = []
		self.intenlst = []
		self.generateLists(GetData)
		self.getAvgDtbin()
		self.dtbintransformed = []
		self.filename = GetData.fn
	
	"""
		DtHist.generateLists -- Method
		
		Adds values from GetData.ylst and GetData.zlst into DtHist.dtbinlst and 
		DtHist.intenlst, respectively, if the corresponding value in GetData.xlst is
		within mass epsilon of the specified mass
		
		Input(s):
			GetData				- object containing raw data (GetData)
	"""
	def	generateLists (self, GetData):
		for n in range (GetData.num_vals):
			if abs(GetData.xlst[n] - self.specmass) <= self.mass_epsilon:
				self.dtbinlst.append(GetData.ylst[n])
				self.intenlst.append(GetData.zlst[n])
	
	"""
		DtHist.getAvgDtbin -- Method
		
		Computes the average dtbin, weighted by intensity, of the current dt histogram. 
		Stores this value in:
			DtHist.avg_dtbin	- average dtbin value weighted by intensity (float)
		
		Input(s):
			none
	"""
	def getAvgDtbin (self):
		self.dtbinintenmultlst = []
		for n in range (len (self.dtbinlst)):
			self.dtbinintenmultlst.append(self.dtbinlst[n] * self.intenlst[n])
		self.avg_dtbin = sum (self.dtbinintenmultlst) / sum (self.intenlst)
	
	"""
		DtHist.dtbinToDt -- Method
		
		Converts DtHist.dtbinlst and DtHist.avg_dtbin into units of dt (ms) instead of 
		dtbin using the conversion factor dtbin_dt_equiv. Converted values are stored in:
			DtHist.dtlst		- dt values (list)
			DtHist.avg_dtb		- average dt value (float)
		
		Input(s):
			dtbin_dt_equiv		- ms/dtbin conversion factor (float)
	"""
	def dtbinToDt (self, dtbin_dt_equiv):
		self.dtlst = []
		for n in range (len(self.dtbinlst)):
			self.dtlst.append(self.dtbinlst[n] * self.dtbin_dt_equiv)
		self.avg_dt = self.avg_dtbin * self.dtbin_dt_equiv
	
	"""
		DtHist.transformHist -- Method
		
		Converts DtHist.dtbinlst and DtHist.avg_dtbin into a single list of dtbin values
		repeated by the corresponding intensity number, which can be used to produce a 
		matplotlib.pyplot.hist() object. The transformed list is stored in:
			DtHist.dtbintransformed	- transformed dtbin values (list)
		
		Input(s):
			none
	"""	
	def transformHist (self):
		for i in range(len(self.dtbinlst) -1):
			for j in range (int(self.intenlst[i])):
				self.dtbintransformed.append(self.dtbinlst[i])
	
	"""
		DtHist.showDtHist -- Method
		
		Plots the data contained in Dthist.dtbintransformed using matplotlib.pyplot.hist();
		
		Input(s):
			none
	"""	
	def showDtHist (self):
		if self.dtbintransformed == []:
			self.transformHist()
		pplt.hist(self.dtbintransformed,100)
		pplt.xlabel("dt bin")
		pplt.ylabel("intensity")
		pplt.show()
		
##########################################################################################
class GaussFit (object):
	"""
		GaussFit -- Class
		
		Fits a Gaussian distribution to the dt histogram in a specified DtHist object
		using a least squares fitting method. The results of the least squares fit are
		stored as the optimized parameters for the Gaussian function:
			GaussFit.optparams 		- optimized amplitude, mu, and sigma (tuple)
		
		Input(s):
			DtHist_obj				- object containing the dt histogram to be fit with
									  Gaussian function (DtHist)
	"""
	def __init__ (self, DtHist_obj):
		DtHist_obj.transformHist()
		self.initparams = (\
		numpy.amax(DtHist_obj.intenlst),\
		numpy.mean(DtHist_obj.dtbintransformed),\
		numpy.std(DtHist_obj.dtbintransformed))
		self.fit_failed = False
		
		self.dtbinandcombinedintensity = numpy.zeros([max(DtHist_obj.dtbinlst) + 1, max(DtHist_obj.dtbinlst) + 1])
		for n in range (len(DtHist_obj.dtbinlst)):
			self.dtbinandcombinedintensity[0][DtHist_obj.dtbinlst[n]] = DtHist_obj.dtbinlst[n]
			self.dtbinandcombinedintensity[1][DtHist_obj.dtbinlst[n]] += DtHist_obj.intenlst[n]
		
		self.mass = DtHist_obj.specmass
		self.filename = DtHist_obj.filename
		self.doFit()
		
		if not self.fit_failed:
			self.opt_mean = self.optparams[1]
			
		#create an array with the raw dtbin and intensity values
		# and fitted intensity values
		self.rawandfitdata = numpy.array([self.dtbinandcombinedintensity[0], self.dtbinandcombinedintensity[1], self.dtbinandcombinedintensity[0]])
		self.rawandfitdata[2] = self.gaussFunc(self.rawandfitdata[2], self.optparams[0], self.optparams[1], self.optparams[2])
		
		self.saveGaussFitFig(DtHist_obj.filename)
		
	
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
			GaussFit.opt_mean	- optimized mean dtbin (float) 
		
		Input(s):
			none
	"""	
	def doFit (self):
		try:
			self.optparams,self.covar = curve_fit(self.gaussFunc,\
												  self.dtbinandcombinedintensity[0],\
			    								  self.dtbinandcombinedintensity[1],\
												  p0=self.initparams,
												  maxfev=1000)
		except RuntimeError:
			self.fit_failed = True
			self.opt_mean = self.initparams[1]
			# if fit was not achieved..
			self.optparams = self.initparams
                        print "failed to fit gaussian for mass", self.mass, "in", self.filename
			
	"""
		GaussFit.saveGaussFitFig -- Method
		
		Outputs a Figure showing the CCS calibration curve fitted to the CCS 
		calibration data 
		
		Input(s):
			figure_file_name 	- choose a filename to save the figure under (string)					
	"""		
	def saveGaussFitFig (self, figure_file_name):
		p = pplt
		p.plot(self.rawandfitdata[0], self.rawandfitdata[1], 'bo', label="raw")
		p.plot(self.rawandfitdata[0], self.rawandfitdata[2],'g--', label="gaussian fit")
		p.legend(loc="best")
		p.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
		p.xlabel("dt bin")
		p.ylabel("intensity")
		p.title(os.path.split(os.path.splitext(figure_file_name)[0])[1] + "\nmass: " + str(self.mass))
		p.savefig(os.path.splitext(figure_file_name)[0] + "_mass-" + str(int(self.mass)) + ".png", bbox_inches='tight')
		p.close()
		
##########################################################################################
class DataCollector (object):
	"""
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
	"""
	def __init__ (self,\
				  mzlistinput=False,\
				  rawdatafilename=False,\
				  parallelize=False,\
				  massepsilon=0.5,\
				  dtbintodt=0.0689):
		self.mz_list = mzlistinput
		self.m_epsilon = massepsilon
		self.bin_ms_equiv = dtbintodt
		
		
		if not rawdatafilename:
			pass
		else:
			#only make a GetData object for the class if a rawdatafilename has been provided
			self.own_GetData = GetData(rawdatafilename)
			

			
		self.parallelize = parallelize
		
	"""
		DataCollector.batchProcess -- Method
		
		Performs drift time extraction for a set list of masses from one raw data input
		file by calling the process method for each m/z in the DataCollector.mz_list
		
		Input(s):
			none
	"""
	def batchProcess (self):
		if not self.parallelize:
			self.dt_list = []
			for mass in self.mz_list:
				self.dt_list.append(self.process(mass,\
											have_GetData=True,\
											mass_epsilon=self.m_epsilon))

		else:
			print "Sorry, parallelization has not been implemented yet."
	
	"""
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
	"""		
	def process (self,\
				 specified_mass,\
				 data_file_name="name",\
				 mass_epsilon=0.5,\
				 have_GetData=False):
		dfname = data_file_name
		smass = specified_mass
		mepsilon = mass_epsilon
		if not have_GetData:
			gd = GetData(dfname)
			dth = DtHist(gd, smass, mepsilon)
			gf = GaussFit(dth)
			return gf.opt_mean * self.bin_ms_equiv
				
		else:
			dth = DtHist(self.own_GetData,\
						  smass,\
						  mepsilon)
			gf = GaussFit(dth)
			
			return gf.opt_mean * self.bin_ms_equiv

##########################################################################################
class CcsCalibration (object):
	"""
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
	"""
	def __init__ (self, 
				  data_file,\
				  cal_mz,\
				  cal_lit_ccs,\
				  edc,\
				  nonstd_mass_epsilon=False,\
				  nonstd_dtbin_equiv=False):
				  
		if (nonstd_dtbin_equiv):
			dtbin_equiv = nonstd_dtbin_equiv
		else:
			dtbin_equiv = 0.0689

		self.data = DataCollector(mzlistinput=cal_mz,\
								  rawdatafilename=data_file,\
								  dtbintodt=dtbin_equiv,\
								  massepsilon=nonstd_mass_epsilon)
		self.data.batchProcess()
		
		
		self.cal_lit_ccs = cal_lit_ccs
		self.edc = edc
		
		self.n2_mass = 28.0134	
		
		# make array with mass, dt, and litccs
		self.mass_dt_litccs = numpy.array([cal_mz, self.data.dt_list, cal_lit_ccs])
		
		# make a new array with corrected drift time
		self.corrected_dt = numpy.array(self.mass_dt_litccs[1])
		# and correct it
		self.corrected_dt = self.correctedDriftTime(self.corrected_dt, self.mass_dt_litccs[0])
		
		# make another new array with corrected lit ccs
		self.corrected_lit_ccs = numpy.array(self.mass_dt_litccs[2])
		# and correct it
		self.corrected_lit_ccs = self.corrected_lit_ccs * numpy.sqrt(self.reducedMass(self.mass_dt_litccs[0]))
		
	
		# Optimized parameters A, t0, B (starts as the initial parameters [0, 0, 1])
		self.optparams = [0, 0, 1]
		
		
		#perform the calibration
		self.fitCalCurve()
		
		# make an array with calibrant calculated ccs
		self.calibrant_calc_ccs = numpy.array(self.getCalibratedCcs(self.mass_dt_litccs[0], self.mass_dt_litccs[1]))

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
			self.corrected_dt,\
			self.corrected_lit_ccs,\
			p0=self.optparams,\
			maxfev=2000)
		except RuntimeError:
			self.fit_failed = True
			print "FIT FAILED WITH RUNTIME ERROR..."
	
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
		p.plot(self.corrected_dt,\
			   self.corrected_lit_ccs, \
			   'ko' , \
			   fillstyle='none', \
			   markeredgewidth=1.0, \
			   label="calibrants")
		p.plot(self.corrected_dt, self.baseCalCurve(self.corrected_dt, self.optparams[0], self.optparams[1], self.optparams[2]), 'black', label="fitted curve")
		p.legend(loc="best")
		p.title("CCS Calibration")
		p.ylabel("corrected CCS")
		p.subplot(g[1])
		p.bar(self.corrected_dt, \
			  numpy.array((100 * (self.mass_dt_litccs[2] - self.calibrant_calc_ccs) / self.mass_dt_litccs[2])), 
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
		
		DESCRIPTION GOES HERE
		
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
		self.writeDriftTimeTable(ccs_calibration_object.mass_dt_litccs[0],\
								 ccs_calibration_object.mass_dt_litccs[1])
		self.wLn()
		self.wLn("Optimized calibration curve fit parameters:")
		self.wLn("\tcorrected ccs = A * ((corrected drift time) + t0) ** B")
		self.wLn("\t\tA = " + str(ccs_calibration_object.optparams[0]))
		self.wLn("\t\tt0 = " + str(ccs_calibration_object.optparams[1]))
		self.wLn("\t\tB = " + str(ccs_calibration_object.optparams[2]))
		self.wLn()
		
		self.wLn("Calibrant CCS, calculated vs. literature:")
		self.writeCcsComparisonTable(ccs_calibration_object.mass_dt_litccs[0],\
									 ccs_calibration_object.mass_dt_litccs[2],\
									 ccs_calibration_object.calibrant_calc_ccs)
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
			[optional] line_to_write	- line to write to file (string)
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



# ***EXECUTION IF THIS SCRIPT IS CALLED DIRECTLY*** #
if __name__ == '__main__' :
	"""
		This is the execution path to follow if this program is called directly through
		the commmand line. 

		The following argument is required:
			-i, --input			full path to ccscal_input.py
	"""	
	#
	### PARSE THE COMMAND-LINE ARGUMENTS
	#	
	print ""
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
						help='full path to ccscal_input.py',\
						dest="path_to_input",\
						metavar='"/full/path/to/ccscal_input.py"')
	# parse arguments 
	args = parser.parse_args()
	# print the help message at the beginning of each run
	parser.print_help()
	print ""
	# all of the command-line arguments are stored in args
	#
	### IMPORT THE CCSCAL_INPUT FILE
	#	
	# store the ccscal_input file name and ccscal_input file path as strings
	ccscal_input_file_path, ccscal_input_file_name = os.path.split(\
													 os.path.splitext(\
													 args.path_to_input)[0])
	# add ccscal_input path to python's path 
	sys.path.append(ccscal_input_file_path)
	# import ccscal_input file
	ccscal_input = __import__(ccscal_input_file_name)
	# ccscal_input contains run information from ccscal_input file
	#
	### INITIALIZE THE REPORT GENERATOR
	#
	report = GenerateReport(ccscal_input.report_file_name)
	#	
	### PERFORM CCS CALIBRATION
	#
	print "Performing CCS Calibration..."
	# create CcsCalibration object
	calibration = CcsCalibration(ccscal_input.calibrant_data_file,\
								 ccscal_input.calibrant_masses,\
								 ccscal_input.calibrant_literature_ccs,\
								 ccscal_input.edc,\
								 nonstd_mass_epsilon=ccscal_input.mass_epsilon)

	# save a graph of the fitted calibration curve
	calibration.saveCalCurveFig(figure_file_name=ccscal_input.calibration_figure_file_name)
	# write the calibration statistics to the report file
	report.writeCalibrationReport(calibration)
	print "...DONE"
	#
	### EXTRACT DRIFT TIMES OF COMPOUNDS AND GET THEIR CALIBRATED CCS
	#
	# initialize a DataCollector object
	collector = DataCollector()
	# write the header for the compound data table in the report
	report.writeCompoundDataTableHeader()
	# cycle through each compound input filename/mass pair and perform drift time extraction
	count = 0
	for pair in (ccscal_input.compound_data_files_and_masses):
		count += 1
		print "Extracting Drift Time for Mass:", pair[1], "from Data File:", pair[0],\
			  "(" + str(count), "of", str(len(ccscal_input.compound_data_files_and_masses)) + ")..."
		# extract drift time and get calibrated CCS for the filename/mass pair
		driftTime = collector.process(pair[1], data_file_name=(ccscal_input.compound_root_directory + pair[0]))
		print "...DONE"
		print "Getting Calibrated CCS..."
		ccs =  calibration.getCalibratedCcs(pair[1], driftTime)
		report.writeCompoundDataTableLine(pair[0], pair[1], driftTime, ccs)
		print "...DONE"
	#
	### CLOSE THE REPORT FILE
	report.finish()
	#
	print ""
	print "CcsCal Complete."
	#
	### COMPLETE

