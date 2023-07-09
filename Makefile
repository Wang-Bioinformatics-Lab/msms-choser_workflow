annotations_file=data/annotations.tsv
xmlpath=data/

clean:
	rm -Rf .nextflow* work bin/__pycache__

run:
	nextflow run ./nf_workflow.nf --annotations="$(annotations_file)" --xmlpath="$(xmlpath)" --resume -c nextflow.config

run_hpcc:
	nextflow run ./nf_workflow.nf --annotations="$(annotations_file)" --xmlpath="$(xmlpath)" --resume -c nextflow_hpcc.config

# 
run_docker:
	nextflow run ./nf_workflow.nf --annotations="$(annotations_file)" --xmlpath="$(xmlpath)" --resume -with-docker <CONTAINER NAME>