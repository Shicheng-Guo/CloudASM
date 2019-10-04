# Cloud-powered, highly-scalable, cluster-free bioinformatics pipeline to call allele-specific methylation on bisulfite-converted whole genomes


dsub is simply a wrapper around the pipelines API (which uses docker images as execution environments) 


## Table of contents

[Introduction](#introduction)

[Prerequisites](#prerequisites)

[Pipeline overview](#pipeline-overview)

[Bucket organization](#Bucket-organization)

## Introduction

This repository is companion to the paper `Google Cloud-powered, scalable, low-cost bioinformatics pipeline to call allele-specific methylation on bisulfite-converted whole genomes`, published on XX/XX/2019 on bioRxiv.org.

This pipeline starts from the zipped fastq files of a paired-end sequenced sample and outputs a bedgraph of allele-specific methylation. The reference genome is hg19 (also called GRCh37) released in February 2009. The variant database to call SNPs is dbSNP147, the latest database of variants for hg19, cleaned from the SNPs which did not make it to dbSNP150.

We ran the pipeline on 10 ENCODE samples. The cost of running this whole pipeline on an ENCODE samples is about $250.

The advantage of using the Google's genomics pipeline tool (still in alpha as of August 2019) is that it takes care of two cumbersome tasks: 1/ create, deploy, monitor, and delete a cluster and 2/ download files from buckets and upload results of a pipeline step to a bucket.

## Prerequisites

You need a ref genome.

it needs to be prepared by bismark

Clone the repository locally

do not use any dash in the sample name (underscores are ok)

### Installation

Docker
etc.
dos2unix


# Install Docker 
https://docs.docker.com/install/

# Install dsub

git clone https://github.com/googlegenomics/dsub.git
cd dsub

python setup.py install

# Install virtualenv, a tool to create isolated Python environments. 
# Install https://virtualenv.pypa.io/en/stable/installation/

# Go into any folder and type:
virtualenv --python=python2.7 dsub_libs

# Launch the virtual environment
source dsub_libs/bin/activate

### Prepare a file with the names of the files.

To run this pipeline, you need an account with [Google Cloud](https://cloud.google.com/).

All samples you want to analyze need to be in the same bucket (which we call here `gs://SAMPLES`) with one folder per sample. In the bucket, at `gs://SAMPLES/lanes.csv`, upload a CSV file with the correspondance of each zipped fastq file to the lane ID, read, and size in GB of the zipped fastq file. For ENCODE samples, it looks like this:

| Sample_name  |     ENCODE_ID |  ENCODE_file_name | Lane_ID   |   Read | Rename |  Size_GB |
| ------------- | ------------- | ------------- |------------- | ------------- | ------------- |  ------------- |
| A549  | ENCFF327QCK    | ENCFF327QCK.fastq.gz | L01 |  R1 | A549_L01.R1 | 84 |
| A549 | ENCFF986UWM | ENCFF986UWM.fastq.gz | L01 | R2 | A549_L01.R2 | 84 |
| A549 | ENCFF327QCK | ENCFF327QCK.fastq.gz | L01 | R1 | A549_L01.R1 | 84 |
| A549 | ENCFF986UWM | ENCFF986UWM.fastq.gz | L01 | R2 | A549_L01.R2 | 84 |
| A549 | ENCFF565VHN | ENCFF565VHN.fastq.gz | L02 | R1 | A549_L02.R1 | 84 |
| A549 | ENCFF251FLW | ENCFF251FLW.fastq.gz | L02 | R2 | A549_L02.R2 | 84 |


sample	bucket_url	lane_id	read_id	file_new_name
gm12878	gs://encode-wgbs/gm12878/ENCFF113KRQ.fastq.gz	L01	R2	gm12878_L01.R2
gm12878	gs://encode-wgbs/gm12878/ENCFF585BXF.fastq.gz	L02	R1	gm12878_L02.R1
gm12878	gs://encode-wgbs/gm12878/ENCFF798RSS.fastq.gz	L01	R1	gm12878_L01.R1
gm12878	gs://encode-wgbs/gm12878/ENCFF851HAT.fastq.gz	L02	R2	gm12878_L02.R2

The output of the analysis will be done in a different bucket (which we call here `gs://ASM`). 

Our pipeline requires a very specific combination of genomics packages. We have put together a Docker-generated image on Cloud Build at `gcr.io/hackensack-tyco/wgbs-asm`. 

## Pipeline overview

The pipeline follows these steps:

1. Unzip fastq files and trim them in 12M-row fastq files.
2. Trim and align each pair of fastq files. Split the output BAM file in chromosome-specific BAM files.
3. Merge all BAM files per chromosome. Remove duplicates. Perform net methylation.
4. Perform SNP calling.
5. Compute allele-specific methylation.

## Bucket organization

The structure of the data, in each sample folder in `gs://ASM`, is the following:

- `<SAMPLE>`
  - `split`
    - `fastq`: folder containing the 12M-row FastQ files. 
    - `trimmed`: folder containing the TrimGalore's output of the 12M-row FastQ files. 
    - `aligned`: folder containing the Bismark's alignment output for the 12M-row FastQ files as well as the BAM files without the duplicates. 
    - `per_chr`: BAM files chunks re-organized by chromosome. 
    - The file SAMPLE.laneXXX.list that contain, for each lane, the names of the files for the R1 files. 
  - `merged`: 
    - All BAM files per chromosome (see below a detailed description of all BAM files)
    - The reports by chromosome of the MarkDuplicate function.
    - All context files per chromosome (CpG* files and Non_CpG* files, see below details)
    - All the other files generated by Bismark's net methylation call (see `merge_bam_net_methyl` pipeline below)
  - `snp_call`: this folder contains all the files listing the SNPs found the recal BAM (~55 files per chrosomosome + a master file per chromosome) as well as all VCF files (several per chromsome)
    - `recal_reports`: contains the reports generated by bis-snp recalibration (one subfolder per chromosome)
  - `asm`: one subfolder for each chromosomes and sub-sub-folders for each of the 53 or 54 lists of SNP on which we compute a SAM file for REF and ALT alleles.











RUN mkdir -p /ref_genome

# We use hg19 (also called GRCh37) released in February 2009.
RUN gsutil -m cp -r gs://ref_genomes/grc37 /ref_genome

# Variant database (dbSNP150)
RUN gsutil -m cp gs://ref_genomes/dbSNP150_grc37_GATK/no_chr_dbSNP150_GRCh37.vcf /ref_genome




Important stuff
- we filter out the reads where the confidence in the SNP letter is less than 30
- we remove CpGs from the context file where the C or G overlap with the SNP
- we remove all SNPs that are not within 500 bp of at least a CpG


DMR: 
3 significant ASM CpG in the same direction
2 consecutive significant CpGs in the same direction
at least 20% difference between the REF reads and the ALT reads and FDR < 0.05

Bis-SNP reports SNPs in positive strand of the reference genome (it's NOT bisulfite-converted)
Bismark reports in positive strand but it is bisulfite-converted, requiring careful handling of the Bis-SNP variant call data.



nochr file for dbSNP: we renamed chr21 into '21' to agree with the SAM files.


## Prepare the databases required to run the pipeline

### Reference genome: GRCh38.p7

The reference genome (unmasked genomic DNA sequences) was downloaded from here:

Download all files.

```
wget ftp://ftp.ensembl.org/pub/release-87/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.chromosome.*.fa.gz
```


### dbSNP database (dbSNP151)

https://ftp.ncbi.nih.gov/snp/organisms/human_9606_b151_GRCh38p7/VCF/All_20180418.vcf.gz

Download to a computer, unzip and upload to the bucket REF_DATA_B

Note that the header of this VCF file is:

```
##fileformat=VCFv4.0
##fileDate=20180418
##source=dbSNP
##dbSNP_BUILD_ID=151
##reference=GRCh38.p7
```


### Bisulfite-converted reference genome.


gatk



####


Test on gm12878
174 GB of zipped fastq files.


## Re-run failed jobs

```
JOB="align_rerun"
dstat --provider google-v2 --project PROJECT --jobs 'JOB-ID' --users 'USER' --status '*' > JOB.log
cat $JOB.log | grep -v Success | tail -n +3 | awk '{print $2}' > ${JOB}_failed.txt
sed -i '$ d' ${JOB}_failed.txt


head -1 ${JOB}.tsv > ${JOB}_rerun.tsv

while read INDEX ; do
  ROW=$(($INDEX +1))
  sed -n "${ROW}p" ${JOB}.tsv >> ${JOB}_rerun.tsv
done < ${JOB}_failed.txt