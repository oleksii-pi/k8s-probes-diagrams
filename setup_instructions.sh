#!/bin/bash

# chmod +x setup_instructions.sh
# ./setup_instructions.sh

# On macOS, you can follow these steps in a Terminal window to set up a local Python environment
# and run the 'diagrams.py' script:

# 1. Ensure you have Python 3 installed. macOS typically includes Python 2.x by default,
#    so you may need to install Python 3. One convenient way is via Homebrew:
#    brew install python

# 2. Create and activate a virtual environment (so that your dependencies remain isolated):
python3 -m venv venv
source venv/bin/activate

# 3. Install required Python packages:
pip install matplotlib numpy

# 4. Put the code from diagrams.py into a file named diagrams.py in the same directory,
#    or clone it from your repo, etc.

# 5. Run the diagrams script:
python diagrams.py
