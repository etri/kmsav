# KMSAV: Korean Multi-speaker Spontaneous Audio-Visaul Speech Recognition Dataset

## Introduction

We are excited to announce the release of our Korean Audio-Visual Automatic Speech Recognition (AV ASR) Dataset. This dataset has been collected from a wide range of YouTube videos containing dialoges of multiple participants and is intended for researchers and developers working on audio-visual speech recognition and related fields.

This dataset aims to facilitate advancements in the field of AV ASR by providing a diverse and challenging collection of samples. By making this dataset publicly available, we hope to foster collaboration, stimulate new ideas, and contribute to the community's understanding of multimodal speech recognition.

## Dataset Description

The Multimodal AV ASR Dataset includes:
- 83 hours of audio-visual content spoken in Korean
- Videos sourced from YouTube, covering various topics and domains
- Various numbers of participants in each video
- Varied background noise levels and acoustic environments
- High-quality manually verified transcriptions for each video

### Data Format

Each data entry in the dataset consists of:
1. Video file (.mp4)
2. Audio file (.wav)
3. Metadata for ASR containing transcription and segments information in Kaldi format
4. Metadata for AV-ASR containing transcription and face region of active speaker for each utterance

## Usage Guidelines

To ensure the responsible use of this dataset, please follow these guidelines: 
1. **Attribution** : Please credit the creators of the dataset by linking back to this repository in your research publications or project documentation. 
2. **Privacy** : Do not use the dataset to identify or infer sensitive information about individuals featured in the videos. 
3. **Non-commercial use** : This dataset is made available for academic and research purposes only. Commercial use of the dataset is prohibited.
## Download and Access

You can download the dataset by cloning this repository or by using the following link:

[Download Korean AV-ASR Dataset](https://github.com/etri/kmsav/archive/refs/heads/kmsav_asd_v0.2.zip) 


## Data Preparation

See the [Data Preparation](./HOWTO.md#data-prepare) to pre-process dataset.

## License

This dataset is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/) .
## Citation

If you use this dataset in your research, please cite it as follows:

```less
@misc{kmsav,
    title={KMSAV: Korean Multi-speaker Spontaneous Audio-Visual Speech Recognition Dataset},
    author={},
    year={2023},
    howpublished={\url{https://github.com/etri/kmsav}},
}
```


## Acknowledgements

We would like to thank all the content creators whose videos were used to create this dataset. Your contributions have made this resource possible.
## Contact

For any questions or concerns related to this dataset, please reach out to us by opening an issue on this repository or by contacting us at [pkyoung@etri.re.kr](mailto:pkyoung@etri.re.kr) .

