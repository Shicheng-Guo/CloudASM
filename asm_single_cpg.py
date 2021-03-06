#!/usr/bin/env python

import os
import scipy.stats as stats
import numpy as np
import pandas as pd

# The schema of the cpg genotype file is the following and the header is included
# chr	STRING
# pos	INTEGER
# snp_id	STRING
# snp_pos INT
# ref_cov	INTEGER
# ref_meth	INTEGER
# alt_cov	INTEGER
# alt_meth	INTEGER

CPG_GENOTYPE = os.environ['CPG_GENOTYPE']
OUTPUT_FILE = os.environ['CPG_ASM']

# Import CpG file into Python
df = pd.read_csv(CPG_GENOTYPE) 

# Function to extract Fisher p-value (5-digit rounding)
def fisher_pvalue(row):
  _, pvalue =  stats.fisher_exact([[row['ref_meth'], \
                                row['alt_meth']], \
                              [row['ref_cov']-row['ref_meth'], \
                                row['alt_cov']-row['alt_meth'] \
                            ]])
  return round(pvalue,5)

# Create a column with the Fisher p-value
df['fisher_pvalue'] = df.apply(fisher_pvalue, axis = 1)

# Save to CSV
df.to_csv (OUTPUT_FILE, index = None, header = False)
