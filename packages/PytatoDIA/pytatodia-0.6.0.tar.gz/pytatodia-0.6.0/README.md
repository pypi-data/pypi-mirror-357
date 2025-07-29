# Pytato: A Toolbox for for DIA Proteomics

Pytato is a dual-enzyme proteomics search engine that leverages the information provided by complementary proteolysis to improve peptide and protein identification in data-independent proteomics experiments. 

![logo_small](https://user-images.githubusercontent.com/36017084/229610464-03d73a08-c55e-4e9f-8dec-ac0af352a945.png)


## Experimental Example

Enyzme1=Trypsin
Enzyme2=Thermolysin

## Features

- Custom Python-based pipeline for streamlined analysis
- Support for multiple proteases to improve protein identification confidence
- Generation of theoretical spectra for improved peptide matching



## Installation

```bash
git clone https://github.com/TTCooper-PhD/Pytato.git
```

Install the required python packages:

```bash
pip install -r requirements.txt
```

## Usage
- Prepare your Enzyme1 and Enzyme2-digested samples and acquire LC-MS/MS data in DIA mode.
### For a list of available enzymes and their cleavage rules, see the [Available Enzymes](enzymes.md) document.

- Process raw data files and generate spectral libraries for both Enzyme1 and Enzyme2 samples.
- Run Pytato by providing the necessary input files and parameters.

```bash
python pytato.py --enzyme1_data trypsin_data.mzML --enzyme2_data thermolysin_data.mzML  --output output_directory
```
## Output
Pytato generates multiple output files containing the results of the analysis. (Add specific details about the output files here).

## Examples
(Provide a detailed example command with input and expected output)

## Contribution
We welcome contributions to the Pytato project. Please see our contribution guidelines for more details.

## License
(Provide details about the project's license)

## Contact
For questions or feedback, please contact us at (Your contact info).


