annotations=data/annotations.tsv
path_to_spectra=data/
ppm_tolerance=10.0

clean:
	rm -Rf .nextflow* work bin/__pycache__ nf_output/*

run:
	nextflow run ./nf_workflow.nf --annotations="$(annotations)" --path_to_spectra="$(path_to_spectra)" --ppm_tolerance=$(ppm_tolerance) --resume -c nextflow.config

run_hpcc:
	nextflow run ./nf_workflow.nf --annotations="$(annotations)" --path_to_spectra="$(path_to_spectra)" --ppm_tolerance=$(ppm_tolerance) --resume -c nextflow_hpcc.config


run_docker:
	nextflow run ./nf_workflow.nf --annotations="$(annotations)" --path_to_spectra="$(path_to_spectra)" --ppm_tolerance=$(ppm_tolerance) --resume -with-docker <CONTAINER NAME>
