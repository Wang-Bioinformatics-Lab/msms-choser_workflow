nextflow.enable.dsl=2

params.annotations = "data/annotations.tsv"
params.path_to_spectra = "data/"
params.publishdir = "./nf_output"
params.ppm_tolerance = 10.0

// Workflow Boiler Plate
params.OMETALINKING_YAML = "flow_filelinking.yaml"
params.OMETAPARAM_YAML = "job_parameters.yaml"

TOOL_FOLDER = "$baseDir/bin"

process processCandidates {
    publishDir "$params.publishdir", mode: 'copy', overwrite: false

    input:
    path annotations, name: params.annotations
    path path_to_spectra, name: params.path_to_spectra
    val ppm_tolerance

    
    output:
    path "batchfile.tsv"

    """

    python $TOOL_FOLDER/prepare_library_addtions_gnps_collections.py $annotations $path_to_spectra batchfile.tsv --ppm_tolerance $ppm_tolerance
    """
}


workflow{
    ch1 = Channel.fromPath(params.annotations) 
    ch2 = Channel.fromPath(params.path_to_spectra) 
    processCandidates(ch1,ch2,params.ppm_tolerance)
}
