BeautifyFileHeader
==================

A python tool that unifies and beautifies all source-file-headers in a directory

Features
--------

* Scan a folder and all its subfolders for source files
	* Specify file extensions 
	* Specify ignore patterns
* Reads file-headers of the found files
	* Reads author, company, creation date and file name
	* Other information (brief, details, other doxygen tags) are currently discarded
* Replaces header with a unified doxygen style header
	* Ability to overwrite authors and company information 
	* Future improvements: specify the header format