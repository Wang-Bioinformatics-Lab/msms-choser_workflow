nextflow.enable.dsl=2

params.annotations = "data/annotations.tsv"
params.path_to_spectra = "data/"

params.ppm_tolerance = 10.0

// Workflow Boiler Plate
params.OMETALINKING_YAML = "flow_filelinking.yaml"
params.OMETAPARAM_YAML = "job_parameters.yaml"

TOOL_FOLDER = "$baseDir/bin"

process processCandidates {
    publishDir "./nf_output", mode: 'copy'

    conda "$TOOL_FOLDER/conda_env.yml"

    input:
    path annotations
    path path_to_spectra
    
    output:
    path "batchfile.tsv"

    """
    which python
    python $TOOL_FOLDER/prepare_library_addtions_gnps_collections.py \
    $annotations $path_to_spectra \
    batchfile.tsv \
    --ppm_tolerance $params.ppm_tolerance
    """
}


workflow{
    annotations_ch = Channel.fromPath(params.annotations) 
    spectra_folder_ch = Channel.fromPath(params.path_to_spectra) 

    processCandidates(annotations_ch, spectra_folder_ch)
}
