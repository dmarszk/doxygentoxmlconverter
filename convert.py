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

def dataFromString(sString, sCommentOpen, iStart = 0):
	"""
	@brief Parse data out of a line which may or may not end in an '*/'.
	@param sString The string to parse.
	@param sCommentOpen What was opening tag for the comment.
	@param iStart The starting index to parse from.  Default = 0 which is the start of the string.
	@return The data (without the ending '*/' is present.
	"""
	iEnd = len(sString)
	if sCommentOpen == "/*" and CLOSE_COMMENT in sString:
		iEnd = sString.find(CLOSE_COMMENT)
	return sString[iStart : iEnd].rstrip()

def dataFromLine(sLine, sCommentOpen):
	"""
	@brief Parse data from a comment line.
	@param sLine The comment line to parse.
	@param sCommentOpen What was opening tag for the comment.
	@return A rstrip'ed string of data after the '* ' in a comment line.
	"""
	if sCommentOpen == "/*":
		iStart = sLine.find("* ")
		if iStart < 0:
			return ""
		iStart += 2
	elif sCommentOpen == "///":		
		iStart = sLine.find("/// ")
		if iStart < 0:
			return ""
		iStart += 4
	else:
		print("dataFromLine - unknown comment opening: \"" + sCommentOpen + "\"")
		sys.exit()
	return dataFromString(sLine, sCommentOpen, iStart)
		
def handleCommentLine(sLine, iLine, sCommentOpen):
	"""
	@brief Write data from a comment line back to the thingy.
	@param sLine The line data.
	@param iLine The line number.
	@param sCommentOpen What was opening tag for the comment.
	@return Is the end of the comment block on this line.
	"""
	global sEType, sEVar, sEData, iIndent

	if (sCommentOpen == "///" and not sLine.strip().startswith("///")):		
		handleExistingData(iIndent)
		endComment()
		# write the line as-is
		pOutFile.write(sLine)
		return False
	# Work out the indentation level to operate at.
	# This is only done once for each comment block.
	if iIndent < 0:
		iIndent = int((len(sLine) - len(sLine.lstrip())) / 4)

	# If there is no '@' symbol, save as much data as we can from the commentline.
	if re.search(START_SYMBOL, sLine) is None:

		# If we are a directive which only accepts single line values then anything extra is a remark.
		if sEType in (PARAM, RETURN, AUTHOR, DATE):
			handleExistingData(iIndent)
			sEType = REMARK
			sEData = ""

		# Get the data from the line and append it if it is exists.
		sData = dataFromLine(sLine, sCommentOpen)
		if len(sData) > 0:
			# If we already have data, insert a breakline.
			if sEData:
				sEData += BREAK + sData

			# Otherwise do not.
			else:
				sEData = sData
		
		# If we have an end comment on this line, exit the comment by returning false.
		if (sCommentOpen == "/*" and CLOSE_COMMENT in sLine):
			handleExistingData(iIndent)
			endComment()
			return False
		return True

	# Since the line does contain an '@' symbol, push any existing data.
	handleExistingData(iIndent)

	# If this line contains an '@' symbol then work out what is after it.
	sEType = re.split(START_SYMBOL, sLine)[2].split()[0]
	

	# If the comment data type is BRIEF
	if sEType == BRIEF:
		sEData = dataFromString(sLine, sCommentOpen, sLine.find(BRIEF) + len(BRIEF) + 1)

	elif sEType == PARAM:
		sTemp = dataFromString(sLine, sCommentOpen, sLine.find(PARAM) + len(PARAM) + 1)
		spaceMatch = re.search(r"\s+", sTemp)
		iChop  = spaceMatch.span()[1]
		sEData = sTemp[iChop:]
		sEVar  = sTemp[:iChop].rstrip()

	elif sEType == RETURN:
		sEData = dataFromString(sLine, sCommentOpen, sLine.find(RETURN) + len(RETURN) + 1)

	elif sEType == DATE:
		sEData = dataFromString(sLine, sCommentOpen, sLine.find(DATE) + len(DATE) + 1)

	elif sEType == AUTHOR:
		sEData = dataFromString(sLine, sCommentOpen, sLine.find(AUTHOR) + len(AUTHOR) + 1)
	# If we have an end comment on this line, exit the comment by returning false.
	if sCommentOpen == "/*" and CLOSE_COMMENT in sLine:
		handleExistingData(iIndent)
		endComment()
		return False
	return True

## Modules
import time
import shutil
import os
import re

## Constants
## Look for @/n or \
START_SYMBOL  = r"(@|\\)"
## Look for /* or ///
OPEN_COMMENT  = r"(/\*\*|///)"
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
	sCommentOpen = ""

	# Open the files.
	pOutFile = open(sOutFile, "w")
	with open(sInFile) as pIn:								  
		# For each line in the file.
		for sLine in pIn:
			# Increment counter.
			iLine += 1								   
			# If we are in a comment, handle the line.
			if bInComment:
				bInComment = handleCommentLine(sLine, iLine, sCommentOpen)
			else:
				# Check the new line to see if it opens a comment line.
				openMatch = re.search(OPEN_COMMENT, sLine)
				if openMatch:
					sCommentOpen = openMatch.group(0)
					iComments += 1
					bInComment = handleCommentLine(sLine, iLine, sCommentOpen)
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
		print (sInFile)
		print (str(iComments) + " comment blocks converted within "+str(iLine)+" lines in approx "+str(round(time.clock() - iStartTime, 2))+" seconds.")


if __name__ == "__main__":
	import sys
	if len(sys.argv) == 1:
		print ("Please specify an input file.")
	else:
		lFiles = sys.argv[1:]
		for sFile in lFiles:
			convert(sFile)
			print ("-----")
		#input("Done")
