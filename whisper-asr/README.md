# Automatic Speech Recognition (ASR) with the KMSAV Dataset

ASR can be conducted using various toolkits such as Whisper, Kaldi, ESPnet,
among others. To use the KMSAV dataset audio data for this purpose, follow the
steps below:

1. Data Preparation: Begin by preparing the data in accordance with the [Data
   Preparation](../HOWTO.md#data-preparation) guidelines.

2. File Preparation: Ensure you have a script or a list that contains both the
   audio and its corresponding transcription, preferably in the Kaldi format.
   Here's a suggested approach:
```
find ../cropped -name "*.wav" | sort > wav.lst
perl -pe 's,(.*/cropped/([^/]+)/utts/([0-9]+).wav),$2_$3 $1,' wav.lst > wav.scp
cat wav.scp | while IFS=" " read -r key f r; do
    echo -n "$key "
    cat ${f%.wav}.txt
done > text
```

3. Dataset Splitting: To split dataset into `train`, `valid` and `test` sets,
   utilize the script below:
```
for split in train valid test; do
    mkdir -p data/$split
    grep -w $split ../data/list.txt | cut -f 1 -d' ' | \
        grep -f - wav.scp > data/$split/wav.scp
    grep -w $split ../data/list.txt | cut -f 1 -d' ' | \
        grep -f - text > data/$split/text
done
```

4. Running the Inference: Finally, proceed to inference. Ensure you consult the
   respective toolkit's guidelines, but provided below is an example for
   OpenAI's Whisper.

# ASR using Whisper

## zero-shot inference

1. **Installation**: Begin by installing Whisper. You can obtain it from [OpenAI's GitHub repository](https://github.com/openai/whisper).

2. **Running Inference on `.wav` Files**: After the installation, you can run the inference command for each `.wav` file. Here's an example on how to proceed:
```bash
cat data/test/wav.scp | while IFS=" " read -r key f r; do
    whisper --model medium --lang ko --task transcribe --beam_size 3 \
        --condition_on_previous_text False \
        --output_format json --output_dir ./result-whisper-medium/ $f
    mv ./result-whisper-medium/$(basename $f .wav).json ./result-whisper-medium/$key.json
done
```

3. **Conversion to Kaldi Text**: The results, saved in JSON format, can be converted to the Kaldi `text` format. Use the `utils/json2text.py` script as illustrated below:
```bash
utils/json2text.py ./result-whisper-medium/ > ./result-whisper-medium/text
```

## Fine-Tuning with ESPnet

1. **Setup**:
   - Clone and install [ESPnet](https://github.com/espnet/espnet).
   - Copy the files from this directory to the ESPnet directory.
   - Note: In addition to the usual ESPnet installation, you'll also need to
     install Whisper.

2. **Running the Fine-tuning Script**:
   - Execute the provided script for fine-tuning. The script and its associated
     configuration files are sourced from [Hugging Face's model
     page](https://huggingface.co/espnet/shihlun_asr_whisper_medium_finetuned_librispeech100).
   - **Note**: If you intend to use the `--tokenizer_language ko` option for
     fine-tuning with Korean data, ensure that your ESPnet version is more
     recent than the `9cdf8f2a9` GitHub commit hash. Otherwise, code
     modifications will be necessary.

```
train_set="train"
valid_set="valid"
test_sets="test"
asr_tag=whisper-ft1
asr_config=conf/tuning/train_asr_whisper_full.yaml
inference_config=conf/decode_asr_whisper_noctc_greedy.yaml

asr_args=(
    --max_epoch 10
    --batch_bins 160000
    --encoder_conf whisper_model=large
    --decoder_conf whisper_model=large
)

./asr.sh \
    --skip_data_prep false \
    --skip_train false \
    --skip_eval false \
    --lang ko \
    --tokenizer_language ko \
    --ngpu 1 \
    --nj 1 \
    --stage 3 \
    --stop_stage 11 \
    --gpu_inference true \
    --inference_nj 1 \
    --token_type whisper_multilingual \
    --feats_normalize '' \
    --max_wav_duration 30 \
    --speed_perturb_factors "" \
    --audio_format "flac.ark" \
    --feats_type raw \
    --use_lm false \
    --cleaner whisper_basic \
    --asr_tag "${asr_tag} \
    --asr_config "${asr_config}" \
    --asr_args "${asr_args[*]}" \
    --inference_config "${inference_config}" \
    --inference_asr_model valid.acc.ave.pth \
    --train_set "${train_set}" \
    --valid_set "${valid_set}" \
    --test_sets "${test_sets}" "$@"
```

## Inference using ESPnet
Given the ESPnet model from fine-tuning or training from scratch,
inference can be accomplished using `inferece.sh` provided.

```
    bash inference.sh \
        --model exp/whisper-ft1/valid.acc.ave_3best.pth \
        --conf conf/decode_asr_whisper_noctc_greedy.yaml \
        --data data/test \
        --beam 3 \
        --odir result/
```

## Evaluating ASR performance

To assess the performance of ASR, the Character Error Rate (CER) is commonly
used as a metric for Korean ASR.

1. **About CER**: The CER quantifies accuracy by:
   - Splitting the recognition result into individual character units.
   - Calculating the edit distance (number of insertions, deletions, and
     substitutions required to change one string into another) between the
     reference and the recognized text.

2. **Calculation**:
   - Use the following command to compute the CER:
     ```bash
     compute-wer --mode=present ark:"utils/split_char.py data/test/text|" ark:"utils/split_char.py result/text|"
     ```
   - Note: The `compute-wer` tool used here is part of the Kaldi toolkit.

