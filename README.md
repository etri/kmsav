# KMSAV: Korean Multi-speaker Spontaneous Audio-Visaul Speech Recognition Dataset

## Introduction

We are excited to announce the release of our Korean Audio-Visual Speech Recognition
(AVSR) Dataset. This dataset has been collected from a wide range of YouTube videos containing dialoges of multiple participants and is intended for researchers and developers working on audio-visual speech recognition and related fields.

This dataset aims to facilitate advancements in the field of AVSR by providing a diverse and challenging collection of samples. By making this dataset publicly available, we hope to foster collaboration, stimulate new ideas, and contribute to the community's understanding of multimodal speech recognition.

## Dataset Description

The Multimodal AVSR Dataset includes:
- 83 hours of audio-visual content spoken in Korean
- Videos sourced from YouTube, covering various topics and domains
- Various numbers of participants in each video
- Varied background noise levels and acoustic environments
- High-quality manually verified transcriptions for each video

### Data Format

Each data entry in the dataset consists of:
1. URLs to video files
2. Metadata for AVSR containing transcription and face region of active speaker
   for each utterance
3. Set of scripts to extract videos of audio-visual utterances from metadata

## Usage Guidelines

To ensure the responsible use of this dataset, please follow these guidelines: 
1. **Attribution** : Please credit the creators of the dataset by linking back
   to this repository in your research publications or project documentation. 
2. **Privacy** : Do not use the dataset to identify or infer sensitive
   information about individuals featured in the videos. 
3. **Non-commercial use** : This dataset is made available for academic and
   research purposes only. Commercial use of the dataset is prohibited.

## Download and Data Preparation

To access the dataset, clone this repository and follow the [Data Preparation
guidelines](./HOWTO.md#data-prepare) for dataset preprocessing.


## License

* This __dataset__ is licensed under the [Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 International
License](https://creativecommons.org/licenses/by-nc-sa/4.0/).
* The __source code__ is licensed under the MIT License.
See [LICENSE](./LICENSE.md) for details.

## Citation

If you use this dataset in your research, please cite it as follows:

```less
@misc{kmsav,
    title={KMSAV: Korean Multi-speaker Spontaneous Audio-Visual Speech Recognition Dataset},
    author={Kiyoung Park, Changhan Oh and Sunghee Dong},
    year={2024},
    journal={ETRI Journal},
}
```


## Acknowledgements

This work is supported by Institute for Information \& communications
Technology Planning \& Evaluation(IITP) grant funded by the Korea
government(MSIT) (No.2019-0-01376, Development of the multi-speaker
conversational speech recognition technology)

## Contact

For any questions or concerns related to this dataset, please reach out to us
by opening an issue on this repository or by contacting us at
[pkyoung@etri.re.kr](mailto:pkyoung@etri.re.kr) .

