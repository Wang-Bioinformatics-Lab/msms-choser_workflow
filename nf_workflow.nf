nextflow.enable.dsl=2

params.annotations = "data/annotations.tsv"
params.xmlpath = "data/"
params.publishdir = "./nf_output"


// Workflow Boiler Plate
params.OMETALINKING_YAML = "flow_filelinking.yaml"
params.OMETAPARAM_YAML = "job_parameters.yaml"

TOOL_FOLDER = "$baseDir/bin"

process processCandidates {
    publishDir "$params.publishdir", mode: 'copy', overwrite: false

    input:
    path annotations, name: params.annotations
    path xmlpath, name: params.xmlpath
    
    

    output:
    path "batchfile.tsv"

    """
    python $TOOL_FOLDER/prepare_library_addtions_gnps_collections.py $annotations $xmlpath batchfile.tsv
    """
}



workflow{
    ch1 = Channel.fromPath(params.annotations) 
    ch2 = Channel.fromPath(params.xmlpath) 
    processCandidates(ch1,ch2)
}