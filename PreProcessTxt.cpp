// This program is meant to pre-process the raw data text files prior to CcsCal.py importing them
// via its GetData() object. It will take a specified mass, mass window, and data file name as 
// arguments, then it will create a pre-processed file containing only lines with masses that are 
// within double the mass window of the specified mass. This should speed up data file import by 
// CcsCal.py

#include<iostream>
#include<fstream>
#include<string>
#include<cmath>



// parameters required by main are, in order:
//		1. data file name 
//		2. specified mass 	
// 		3. mass window 	
int main(int argc, char* argv[]) {
	// store the input file name as a string
	std::string inputFileName = argv[1];
	// create the outputfile name
	std::string outputFileName = inputFileName.substr(0, (inputFileName.length() - 4)) + ".pp-" + argv[2] + ".txt";
	// start an input file stream
	std::ifstream inputFile (inputFileName);
	// start on output file stream
	std::ofstream outputFile (outputFileName);
	
	// take in the specified mass and mass window
	double specifiedMass = std::stod(argv[2]);
	double massWindow = std::stod(argv[3]);
	// minimum mass to accept
	double minMass = specifiedMass - massWindow;
	// the maximum mass to accept before the input file stops being read
	double maxMass = specifiedMass + massWindow;
	// process the file, write only lines with masses within the mass window to the output file
	std::string line1, line2, line3;
	while (inputFile >> line1 >> line2 >> line3) {
		inputFile >> line1 >> line2 >> line3;
		if (std::stod(line1) > maxMass) {
			break;
		} else if (std::stod(line1) > minMass) {
			outputFile << line1 << " "<< line2 << " " << line3 << "\n";
		}
	}
	
	return 0;
}

