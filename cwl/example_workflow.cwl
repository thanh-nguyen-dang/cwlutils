class: Workflow
label: "example workflow"
description: "Example workflow to download files, print, and upload"

inputs: 
  - id: "#s3creds-path"
    type: File
    inputBinding:
      prefix: --s3creds-path


  - id: "#keys"
    default: null
    type:
      type: array
      items: string
    inputBinding:
      prefix: --keys


outputs:
  - id: "#message"
    source: "#download.files"
    type:
      type: array
      items: File

steps:
  - id: "#download"
    run: {import : "s3download.cwl"}
    inputs:
      - id: "#download.keys"
        source: "#keys"
      - id: "#download.s3creds-path"
        source: "#s3creds-path"
    outputs:
      - id: "#download.files"

