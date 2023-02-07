nextflow.enable.dsl=2

params.annotations = "data/annotations.tsv"
params.spectra = "data/"
params.publishdir = "./nf_output"


// Workflow Boiler Plate
params.OMETALINKING_YAML = "flow_filelinking.yaml"
params.OMETAPARAM_YAML = "job_parameters.yaml"

TOOL_FOLDER = "$baseDir/bin"

process processCandidates {
    publishDir "$params.publishdir", mode: 'copy', overwrite: false

    input:
    path annotations, name: params.annotations
    path spectra, name: params.spectra
    
    output:
    path "batchfile.tsv"

    """
    python $TOOL_FOLDER/prepare_library_addtions_gnps_collections.py $annotations $spectra batchfile.tsv
    """
}


workflow{
    ch1 = Channel.fromPath(params.annotations) 
    ch2 = Channel.fromPath(params.spectra) 
    processCandidates(ch1,ch2)
}