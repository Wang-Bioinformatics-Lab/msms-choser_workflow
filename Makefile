annotations_file=data/annotations.tsv
xmlpath=data/

run:
	nextflow run ./nf_workflow.nf --annotations="$(annotations_file)" --xmlpath="$(xmlpath)" --resume 

# The tasks for the NP-Classifier are performed using small python scripts and web services requests, therefore a docker instance does not make sense
#run_docker:
#	nextflow run ./nf_workflow.nf --resume -with-docker <CONTAINER NAME>