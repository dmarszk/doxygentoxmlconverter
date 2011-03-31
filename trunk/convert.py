# Quick to write and slow to run Doxygen to XML Comment converter.
# John Hardy 2011

def endComment():
	"""
	@brief Reset the values for the next comment block.
	"""
	global sEType, sEVar, sEData, iIndent
	sEType = BRIEF
	sEVar = None
	sEData = ""
	iIndent = -1

def handleExistingData(iIndent):
	"""
	@brief Write out any existing data.
	@param iIndent The indent level.
	"""
	global sEType, sEVar, sEData

	# If none, quit.
	if not sEType:
		return

	# Skip if we have no data.
	if not sEData:
		return

	# Insert tab level and comments into a header.
	sHead = ("    " * iIndent) + "/// "

	# Sanitise data.
	sEData.rstrip()

	# Swap breaks for heads.
	sEData = sEData.replace(BREAK, "\n" + sHead)

	# Write out the respective blocks.
	if sEType == BRIEF:
		#sEData = sEData.replace("<summary>", "")
		#sEData = sEData.replace("</summary>", "")
		pOutFile.write(sHead + "<summary>\n")
		pOutFile.write(sHead + sEData + "\n")
		pOutFile.write(sHead + "</summary>\n")

	elif sEType == PARAM:
		pOutFile.write(sHead + "<param name=\"" + str(sEVar) + "\">" + str(sEData) + "</param>\n")

	elif sEType == RETURN:
		pOutFile.write(sHead + "<returns>" + str(sEData) + "</returns>\n")

	elif sEType == AUTHOR:
		pOutFile.write(sHead + "<author>" + str(sEData) + "</author>\n")
		
	elif sEType == DATE:
		pOutFile.write(sHead + "<date>" + str(sEData) + "</date>\n")
		
	elif sEType == RETURN:
		pOutFile.write(sHead + "<returns>" + str(sEData) + "</returns>\n")

	elif sEType == REMARK:
		pOutFile.write(sHead + str(sEData) + "\n")

	# Zap any leftover data.
	sEType = None
	sEVar = None
	sEData = ""

def dataFromString(sString, iStart = 0):
	"""
	@brief Parse data out of a line which may or may not end in an '*/'.
	@param sString The string to parse.
	@param iStart The starting index to parse from.  Default = 0 which is the start of the string.
	@return The data (without the ending '*/' is present.
	"""
	iEnd = len(sString)
	if CLOSE_COMMENT in sString:
		iEnd = sString.find(CLOSE_COMMENT)
	return sString[iStart : iEnd].rstrip()

def dataFromLine(sLine):
	"""
	@brief Parse data from a comment line.
	@param sLine The comment line to parse.
	@return A rstrip'ed string of data after the '* ' in a comment line.
	"""
	iStart = sLine.find("* ")
	if iStart < 0:
		return ""
	iStart += 2
	return dataFromString(sLine, iStart)
		
def handleCommentLine(sLine, iLine):
	"""
	@brief Write data from a comment line back to the thingy.
	@param sLine The line data.
	@param iLine The line number.
	@return Is the end of the comment block on this line.
	"""
	global sEType, sEVar, sEData, iIndent

	# Work out the indentation level to operate at.
	# This is only done once for each comment block.
	if iIndent < 0:
		iIndent = (len(sLine) - len(sLine.lstrip())) / 4

	# If there is no '@' symbol, save as much data as we can from the commentline.
	if START_SYMBOL not in sLine:

		# If we are a directive which only accepts single line values then anything extra is a remark.
		if sEType in (PARAM, RETURN, AUTHOR, DATE):
			handleExistingData(iIndent)
			sEType = REMARK
			sEData = ""

		# Get the data from the line and append it if it is exists.
		sData = dataFromLine(sLine)
		if len(sData) > 0:
			# If we already have data, insert a breakline.
			if sEData:
				sEData += BREAK + sData

			# Otherwise do not.
			else:
				sEData = sData
		
		# If we have an end comment on this line, exit the comment by returning false.
		if CLOSE_COMMENT in sLine:
			handleExistingData(iIndent)
			endComment()
			return False
		return True

	# Since the line does contain an '@' symbol, push any existing data.
	handleExistingData(iIndent)

	# If this line contains an '@' symbol then work out what is after it.
	sEType = sLine.split(START_SYMBOL)[1].split(" ")[0]

	# If the comment data type is BRIEF
	if sEType == BRIEF:
		sEData = dataFromString(sLine, sLine.find(BRIEF) + len(BRIEF) + 1)

	elif sEType == PARAM:
		sTemp = dataFromString(sLine, sLine.find(PARAM) + len(PARAM) + 1)
		iChop  = sTemp.find(" ") + 1
		sEData = sTemp[iChop:]
		sEVar  = sTemp[:iChop].rstrip()

	elif sEType == RETURN:
		sEData = dataFromString(sLine, sLine.find(RETURN) + len(RETURN) + 1)

	elif sEType == DATE:
		sEData = dataFromString(sLine, sLine.find(DATE) + len(DATE) + 1)

	elif sEType == AUTHOR:
		sEData = dataFromString(sLine, sLine.find(AUTHOR) + len(AUTHOR) + 1)

	# If we have an end comment on this line, exit the comment by returning false.
	if CLOSE_COMMENT in sLine:
		handleExistingData(iIndent)
		endComment()
		return False
	return True

## Modules
import time
import shutil
import os

## Constants
START_SYMBOL  = "@"
OPEN_COMMENT  = "/**"
CLOSE_COMMENT = "*/"
BRIEF         = "brief"
PARAM         = "param"
RETURN        = "return"
AUTHOR        = "author"
DATE          = "date"

REMARK = "remark"
BREAK = "!BREAK!"

## Define globals.
global sEType, sEVar, sEData, pOutFile

## Main function.
def convert(sInFile, sOutFile = None, bReport = True):
	"""
	@brief A function which will convert the contents of one file and write them to an output file.
	@param sInFile The file to convert from doxycomments to xml comments.
	@param sOutFile OPTIONAL The file to save them in.  Default is a _d appended version of the old one.
	@param bReport Report the number of comments and time it took etc.
	"""

	# Globals
	global pOutFile

	# File jiggery.
	if not sOutFile:
		sOutFile = sInFile.replace(".", "_dtemp.")

	# Some initial state and a line counter.
	endComment()
	bInComment = False
	iLine = 0
	iComments = 0
	iStartTime = time.clock()

	# Open the files.
	pOutFile = open(sOutFile, "w")
	with open(sInFile) as pIn:
								  
		# For each line in the file.
		for sLine in pIn:

			# Increment counter.
			iLine += 1
								   
			# If we are in a comment, handle the line.
			if bInComment:
				bInComment = handleCommentLine(sLine, iLine)

			# Check the new line to see if it opens a comment line.
			elif OPEN_COMMENT in sLine:
				iComments += 1
				bInComment = handleCommentLine(sLine, iLine)

			# We are neither a comment so write the line back to the source.
			else:
				pOutFile.write(sLine)

	# Close the output file.
	pOutFile.close()
	
	# Backup the old file.
	#shutil.copy(sInFile, sInFile + "_dbackup")
	
	# Copy the new file over the old file.
	shutil.copy(sOutFile, sInFile)
	
	os.remove(sOutFile)
	
	# Report.
	if bReport:
		print sInFile
		print str(iComments) + " comment blocks converted within "+str(iLine)+" lines in approx "+str(round(time.clock() - iStartTime, 2))+" seconds."


if __name__ == "__main__":
	import sys
	if len(sys.argv) == 1:
		print "Please specify an input file."
	else:
		lFiles = sys.argv[1:]
		for sFile in lFiles:
			convert(sFile)
			print "-----"
		raw_input("Done")
