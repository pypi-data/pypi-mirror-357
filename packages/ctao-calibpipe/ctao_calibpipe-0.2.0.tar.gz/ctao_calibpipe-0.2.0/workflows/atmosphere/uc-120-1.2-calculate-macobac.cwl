#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool

label: Compute 12-Month Average CO2 Background Concentration (12-MACOBAC)

doc: >
  This tool implements UC-120-1.2. It downloads CO2 concentration data from the Scripps Institution of
  Oceanography (measured at Mauna Loa Observatory, Hawaii) and computes the 12-month average CO2
  background concentration (12-MACOBAC). The `--config` input specifies the
  configuration file for the tool, and the optional `--log-level` input sets
  the logging verbosity. The output is used in atmospheric modeling workflows.

inputs:
  configuration:
    type: File
    inputBinding:
      prefix: --config
  log-level:
    type: string?
    inputBinding:
      prefix: --log-level

outputs:
  macobac_table:
    type: File
    outputBinding:
      glob: macobac.ecsv

baseCommand: calibpipe-calculate-macobac
