Keyword Spotting Tool

This tool will spot search terms in the PyLaia ConfMats.ark and 
will enhance the results with Data from the corresponding PageXML 
files to be able to quickly show line-snippet images and will write 
those enhanced results to a CSV file. 

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Getting Started

Download the Project from GIT and, in case of a binary download, unzip it into a folder on your System. 

### Prerequisites

Python3 has to be installed

### Installation
git clone https://github.com/your-username/your-project.git
cd your-project


```bash
# Example for installing dependencies
pip install -r requirements.txt

## Usage
There are several tools included in this package:

KWS.py - The CLI to spot search terms in a given ConfMats.ark
KWSGUI.py - A GUI to run the keyword spotting
KWSBacth.py - A batch processing tool, able to process multiple ConfMats at once
MergeResults.py - A tool to merge Results from multiple runs with the same RUN_ID


All tools can be executed using python, for example:

python -m iui.cli.KWS -h
python -m iui.core.KWSBatch -h
python -m iui.core.MergeResults -h
python -m iui.gui.KWSGUI -h



## License
This project is published under the GNU General Public License 3.0, for details see: https://www.gnu.org/licenses/


## Acknowledgements
Thanks to the Guenter Muehlberger, Andy Stauder, Sebastian Colutto, Gregor Lamzinger and in general the entire READCoop Team
Thanks to Mario Klarer, Aaron Tratter and Hubert Alisande  from the University of Innsbruck
Thanks to Diego Calvanese from the Free University of Bozen








