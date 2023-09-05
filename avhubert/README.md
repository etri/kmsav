# Prerequisites

## Video Cropping from YouTube Data

1. Download YouTube data using the `kmsav` list file.
2. Process the data to extract and crop the face area from the YouTube videos.
3. For detailed instructions, refer to the document at [kmsav/DataPrepare](../../DataPre
pare.md).

# Steps to Prepare Data

## Set up the avhubert Environment

1. Visit the [avhubert GitHub page](https://github.com/facebookresearch/av_hubert).
2. Follow the provided instructions to download and install `avhubert`.

## Data preparation
See [prepration/README.md](preparation/README.md)

# Fine tuning
Run following script after preparation with proper modification.

```
python ./launch.py \
    --ngpu 8 \
    --master_port 12345 \
    --envfile ./path.sh \
    --expname exp1 \
    -- \
    fairseq-hydra-train \
    --config-dir ./conf/finetune \
    --config-name kmsav_large_av.yaml \
    task.data=./preparation/kmsav \
    task.label_dir=./preparation/kmsav \
    task.tokenizer_bpe_model=./preparation/kmsav/spm5000/spm_unigram5000.model \
    model.w2v_path=./lrs3_vox/clean-pretrain/large_vox_iter5.pt \
    dataset.max_tokens=8000 \
    model.freeze_finetune_updates=4000 \
    common.user_dir=`pwd`
```

## Inference

```
python -B infer_s2s.py \
    --config-dir ./conf \
    --config-name s2s_decode.yaml \
    dataset.gen_subset=test \
    common_eval.path=./exp/exp1/checkpoints/checkpoint100.pt \
    common_eval.results_path=./result/exp1 \
    override.modalities='["audio","video"]' \
    common.user_dir=`pwd` \
    +override.data=./avhubert/preparation/kmsav \
    +override.label_dir=./avhubert/preparation/kmsav
```

## Fine-tuning with noise augmentation
Add noise augmentation option while fine-tuning like
```
    task.noise_prob=0.25 \
    task.noise_snr=0 \
    task.noise_wav=./musan/tsv/all \
```

## Inference with noise interference
Add the following option:
```
+override.noise_wav=/path/to/noise override.noise_prob=1 override.noise_snr={snr}
```
